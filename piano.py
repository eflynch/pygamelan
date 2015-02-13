import numpy as np

from datetime import datetime, timedelta

from audio import Audio
from config import kSamplingRate
from core import BaseWidget, run
import generators as gens
from sequence import Sequence
from generators import SQUARE_AMPLITUDES, SINE_AMPLITUDES, SAW_AMPLITUDES, TRI_AMPLITUDES


class MainWidget(BaseWidget) :
   def __init__(self):
      super(MainWidget, self).__init__()
      self.audio = Audio()
      self.gap = 20
      self.registered_notes = {}

      self.quant = timedelta(seconds=4)

      self._track_times = [datetime.now()]

   def schedule_on_track(self, seq, track_number):
      while track_number >= len(self._track_times):
         self._track_times.append(self._track_times[0])

      while self._track_times[track_number] < datetime.now():
         self._track_times[track_number] += self.quant

      self.audio.schedule_sequence(seq, self._track_times[track_number])
      self._track_times[track_number] += self.quant

   def on_key_down(self, keycode, modifiers):
      # print 'key-down', keycode, modifiers
      gen = False
      seq = False
      if keycode[1] == 'q':   gen = gens.Note(59, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'w': gen = gens.Note(60, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'e': gen = gens.Note(64, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'r': gen = gens.Note(65, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 't': gen = gens.Note(69, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'y': gen = gens.Note(71, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'u': gen = gens.Note(72, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'i': gen = gens.Note(76, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'o': gen = gens.Note(77, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'p': gen = gens.Note(81, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'a': gen = gens.Note(59, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 's': gen = gens.Note(60, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'd': gen = gens.Note(64, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'f': gen = gens.Note(65, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'g': gen = gens.Note(69, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'h': gen = gens.Note(71, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'j': gen = gens.Note(72, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'k': gen = gens.Note(76, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'l': gen = gens.Note(77, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == ';': gen = gens.Note(81, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'b':
         generators = [gens.Kempli() for i in xrange(4)]
         schedule = [timedelta(seconds=i) for i in xrange(4)]
         seq = Sequence(generators, schedule)
      elif keycode[1] == 'n':
         generators = [gens.Kempli() for i in xrange(4)]
         schedule = [timedelta(seconds=i) for i in [0, 0.25, 0.75, 1.0]]
         seq = Sequence(generators, schedule)
      elif keycode[1] == 'm':
         generators = [gens.Note(p, SQUARE_AMPLITUDES, 0, duration=0.3) for p in [59, 60, 65, 65]]
         schedule = [timedelta(seconds=i) for i in [0, 0.25, 0.75, 1.0]]
         seq = Sequence(generators, schedule)
      elif keycode[1] == 'up':
         self.audio.set_gain(self.audio.get_gain() + 0.1)
      elif keycode[1] == 'down':
         self.audio.set_gain(self.audio.get_gain() - 0.1)
      elif keycode[0] == 61:
         self.gap += 5
      elif keycode[0] == 45:
         self.gap -= 5

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
         self.registered_notes[keycode[0]] = gen
         self.audio.schedule_generator(gen, datetime.now())

   def on_key_up(self, keycode):
      # print 'key up', keycode
      if keycode[0] in self.registered_notes:
         self.registered_notes[keycode[0]].release()
         del self.registered_notes[keycode[0]]


run(MainWidget)
