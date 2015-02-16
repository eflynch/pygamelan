from datetime import datetime, timedelta
from threading import Thread
from time import sleep

import numpy as np

#comment out if pygame.midi not installed
import pygame.midi as midi

from audio import Audio
from config import kSamplingRate
from core import BaseWidget, run
import generators as gens
from generators import instruments
from sequence import Sequence
from generators import SQUARE_AMPLITUDES, SINE_AMPLITUDES, SAW_AMPLITUDES, TRI_AMPLITUDES

WHITE_KEYS = [i for i in xrange(127) if i%12 in [0, 2, 4, 5, 7, 9, 11]]

class MainWidget(BaseWidget) :
   def __init__(self):
      super(MainWidget, self).__init__()
      self.audio = Audio()
      self.gap = 20
      self.registered_notes = {}

      self.quant = timedelta(seconds=4)

      self._track_times = [datetime.now()]

      # Comment out if pygame.midi not installed.
      self.start_midi()


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


   def schedule_on_track(self, seq, track_number):
      while track_number >= len(self._track_times):
         self._track_times.append(self._track_times[0])

      while self._track_times[track_number] < datetime.now():
         self._track_times[track_number] += self.quant

      self.audio.schedule_sequence(seq, self._track_times[track_number])
      self._track_times[track_number] += self.quant

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

      seq = gen = False
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

      self.handle_new_gen_seq(gen, seq, identifier, overwrite=True)

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
      self.audio.set_gain(0.2*value/127.)

   def release_identifier(self, identifier):
      if identifier in self.registered_notes:
         for gen in self.registered_notes[identifier]:
            gen.release()
         del self.registered_notes[identifier]

   def register_identifier(self, identifier, gen):
      if identifier not in self.registered_notes:
         self.registered_notes[identifier] = []
      self.registered_notes[identifier].append(gen)
      self.audio.schedule_generator(gen, datetime.now())

   def handle_new_gen_seq(self, gen, seq, identifier, overwrite=False):
      if seq:
         if 'alt' in modifiers:
            self.schedule_on_track(seq, 0)
         elif 'ctrl' in modifiers:
            self.schedule_on_track(seq, 1)
         elif 'meta' in modifiers:
            self.schedule_on_track(seq, 2)
         else:
            self.audio.schedule_sequence(seq, datetime.now())

      if gen:
         if overwrite:
            self.release_identifier(identifier)
         self.register_identifier(identifier, gen)
         

   def on_key_down(self, keycode, modifiers):
      # print 'key-down', keycode, modifiers
      gen = False
      seq = False

      pamade = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']
      chantil = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
      jublag = ['a', 's', 'd', 'f', 'g']
      sarang = ['h', 'j', 'k', 'l', ';']
      jegog = ['z', 'x', 'c', 'v', 'b']
      gong = ['n']
      pore = ['m']
      tong = [',']
      specialgong = ['.']

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
         seq = Sequence(generators, schedule)
      elif keycode[1] == 'n':
         generators = [instruments.Kempli() for i in xrange(4)]
         schedule = [timedelta(seconds=i) for i in [0, 0.25, 0.75, 1.0]]
         seq = Sequence(generators, schedule)
      elif keycode[1] == 'm':
         generators = [instruments.Pamade(p, self.gap) for p in [0, 1, 2, 3]]
         schedule = [timedelta(seconds=i) for i in [0, 0.25, 0.75, 1.0]]
         seq = Sequence(generators, schedule)
      elif keycode[1] == 'up':
         self.audio.set_gain(self.audio.get_gain() + 0.05)
      elif keycode[1] == 'down':
         self.audio.set_gain(self.audio.get_gain() - 0.05)
      elif keycode[0] == 61:
         self.gap += 5
      elif keycode[0] == 45:
         self.gap -= 5

      self.handle_new_gen_seq(gen, seq, keycode[0])

   def on_key_up(self, keycode):
      # print 'key up', keycode
      self.release_identifier(keycode[0])


run(MainWidget)
