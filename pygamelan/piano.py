from datetime import datetime, timedelta
from threading import Thread
from time import sleep

import numpy as np
import pygame.midi as midi
from dspy import PyAudioPlayer, Player
import dspy as gens
from dspy.lib import t2f

import instruments
from core import BaseWidget, run, register_terminate_func

WHITE_KEYS = [i for i in xrange(127) if i%12 in [0, 2, 4, 5, 7, 9, 11]]

def make_sequence(gens, times):
   return Player(zip(map(t2f,times), gens), channels=1, live=False, loop=True)

class MainWidget(BaseWidget) :
   def __init__(self):
      super(MainWidget, self).__init__()
      self.audio = Player(live=True)
      self.pyaudio = PyAudioPlayer(self.audio)
      register_terminate_func(self.pyaudio.close)
      self.gap = 20
      self.registered_notes = {}

      self.quant = timedelta(seconds=2.4*4)

      self._track_times = [timedelta(seconds=0)]

      # Comment out if pygame.midi not installed.
      self.start_midi()
      self.pyaudio.start()

   def start_midi(self):
      midi.init()
      if midi.get_count():
         print "Midi Device Found"
         self.midi_in = midi.Input(0)

         t = Thread(target=self.midi_loop)
         t.daemon = True
         t.start()

   def midi_loop(self):
      while True:
         if not self.midi_in.poll():
            sleep(0.01)
            continue

         midi_event = self.midi_in.read(30)
         for e in midi_event:
            self.on_midi_event(e)


   def schedule_on_track(self, gen, track_number, quants):
      while track_number >= len(self._track_times):
         self._track_times.append(self._track_times[0])

      while t2f(self._track_times[track_number]) < self.audio.frame:
         self._track_times[track_number] += self.quant

      self.audio.add(gen, self._track_times[track_number])
      self._track_times[track_number] += self.quant * quants

   def on_midi_event(self, midi_event):
      event, timestamp = midi_event
      status, data1, data2, data3 = event
      if status == 144: #note_on
         self.on_midi_note(data1, data2)
      elif status == 176: #control
         self.on_midi_control(data1, data2)      
      elif status == 224: #pitch wheel
         self.on_midi_pitch_wheel(data2)
      else:
         print "Unexpected status: %s" % status

   def on_midi_note(self, pitch, velocity):
      if pitch not in WHITE_KEYS:
         print 'Black Key'
         return

      identifier = 'midi_%s' % pitch

      if velocity == 0:
         return
      if velocity < 80:
         self.release_identifier(identifier)
         return

      white_key_number = WHITE_KEYS.index(pitch)

      if 45 <= white_key_number < 50:
         gen = instruments.Chantil(white_key_number % 10 + 1, self.gap)
      elif 35 <= white_key_number < 45:
         gen = instruments.Pamade((white_key_number-5) % 10 + 1, self.gap)
      elif 30 <= white_key_number < 35:
         gen = instruments.Sarang(white_key_number % 5, self.gap)
      elif 25 <= white_key_number < 30:
         gen = instruments.Jublag(white_key_number % 5, self.gap)
      elif 20 <= white_key_number < 25:
         gen = instruments.Jegog(white_key_number % 5, self.gap)
      elif pitch == 48:
         gen = instruments.Tong()
      elif pitch == 47:
         gen = instruments.Pore()
      elif pitch == 46:
         gen = instruments.Gong()
      elif pitch == 45:
         gen = instruments.SpecialGong()
      elif pitch == 44:
         gen = instruments.Kempli()

      if gen:
         gen *= gens.DC(velocity/127.)
         self.handle_new_gen(gen, identifier, overwrite=True)

   def on_midi_control(self, channel, value):
      if channel == 1:
         self.on_midi_modulation_wheel(value)
      elif channel == 7:
         self.on_midi_volume(value)
      else:
         print "Unexpected Control Channel: %s" % channel

   def on_midi_pitch_wheel(self, value):
      print value

   def on_midi_modulation_wheel(self, value):
      print value

   def on_midi_volume(self, value):
      self.audio.gain = 0.2*value/127.

   def release_identifier(self, identifier):
      if identifier in self.registered_notes:
         for gen in self.registered_notes[identifier]:
            gen.release()
         del self.registered_notes[identifier]

   def register_identifier(self, identifier, gen):
      if identifier not in self.registered_notes:
         self.registered_notes[identifier] = []
      self.registered_notes[identifier].append(gen)
      self.audio.add(gen)

   def handle_new_gen(self, gen, identifier, overwrite=False):
      if overwrite:
         self.release_identifier(identifier)
      self.register_identifier(identifier, gen)

   def schedule_new_gen(self, seq, modifiers, quants=1):
      if 'alt' in modifiers:
         self.schedule_on_track(seq, 0, quants)
      elif 'ctrl' in modifiers:
         self.schedule_on_track(seq, 1, quants)
      elif 'meta' in modifiers:
         self.schedule_on_track(seq, 2, quants)
      else:
         self.audio.add(seq)
         

   def on_key_down(self, keycode, modifiers):
      # print 'key-down', keycode, modifiers
      pamade = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']
      chantil = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
      jublag = ['a', 's', 'd', 'f', 'g']
      sarang = ['h', 'j', 'k', 'l', ';']
      jegog = ['z', 'x', 'c', 'v', 'b']
      gong = ['n']
      pore = ['m']
      tong = [',']
      specialgong = ['.']

      gen = False
      if 'shift' in modifiers:
         if keycode[1] == 'spacebar':
            gen = make_sequence([instruments.Kempli() for i in xrange(16)], [timedelta(seconds=i) for i in [0.0, 0.6, 1.2, 1.8, 2.4, 3.0, 3.6, 4.2, 4.8, 5.4, 6.0, 6.6, 7.2, 7.8, 8.4, 9.0]])
         elif keycode[1] == 'z':
            gen = make_sequence([instruments.Gong(), instruments.Pore(), instruments.Tong(), instruments.Pore()], [timedelta(seconds=i) for i in [0.0, 2.4, 4.8, 7.2]])
      else:
         if keycode[1] in pamade:
            gen = instruments.Pamade(pamade.index(keycode[1]), self.gap)
         elif keycode[1] in chantil:
            gen = instruments.Chantil(chantil.index(keycode[1]), self.gap)
         elif keycode[1] in jublag:
            gen = instruments.Jublag(jublag.index(keycode[1]), self.gap)
         elif keycode[1] in sarang:
            gen = instruments.Sarang(sarang.index(keycode[1]), self.gap)
         elif keycode[1] in jegog:
            gen = instruments.Jegog(jegog.index(keycode[1]), self.gap)
         elif keycode[1] in gong:
            gen = instruments.Gong()
         elif keycode[1] in pore:
            gen = instruments.Pore()
         elif keycode[1] in tong:
            gen = instruments.Tong()
         elif keycode[1] in specialgong:
            gen = instruments.SpecialGong()
         elif keycode[1] == 'spacebar':
            gen = instruments.Kempli()
         elif keycode[1] == 'b':
            generators = [instruments.Kempli() for i in xrange(4)]
            schedule = [timedelta(seconds=i) for i in xrange(4)]
            seq = make_sequence(generators, schedule)
         elif keycode[1] == 'n':
            generators = [instruments.Kempli() for i in xrange(4)]
            schedule = [timedelta(seconds=i) for i in [0, 0.25, 0.75, 1.0]]
            seq = make_sequence(generators, schedule)
         elif keycode[1] == 'm':
            generators = [instruments.Pamade(p, self.gap) for p in [0, 1, 2, 3]]
            schedule = [timedelta(seconds=i) for i in [0, 0.25, 0.75, 1.0]]
            seq = make_sequence(generators, schedule)
         elif keycode[1] == 'up':
            self.audio.gain += 0.05
         elif keycode[1] == 'down':
            self.audio.gain  -= 0.05
         elif keycode[0] == 61:
            self.gap += 5
         elif keycode[0] == 45:
            self.gap -= 5

      if gen is not False:
         if 'shift' in modifiers:
            self.schedule_new_gen(gen, modifiers)
         else:
            self.handle_new_gen(gen, keycode[0])

   def on_key_up(self, keycode):
      # print 'key up', keycode
      self.release_identifier(keycode[0])

   def on_close(self):
      pass
      # import matplotlib.pyplot as plt
      # plt.plot(self.data)
      # plt.show()



run(MainWidget)
