import numpy as np

from audio import Audio
from config import kSamplingRate
from core import BaseWidget, run
from note import ToneGenerator, NoteGenerator
from adsr import ADSREnvelope
from dsp import LowPassDSP
from generator import FMapGenerator

SQUARE_AMPLITUDES = [ (i, 1./float(i), 0) for i in xrange(1,20) if i%2==1]
SINE_AMPLITUDES = [(1, 1.0, 0.0)]
SAW_AMPLITUDES = [ (i, (-1)**(i+1) * 1./float(i), 0) for i in xrange(1, 20)]
TRI_AMPLITUDES = [ (i, 1./(float(i)**2), np.pi/2.) for i in xrange(1,20) if i%2==1]

class MainWidget(BaseWidget) :
   def __init__(self):
      super(MainWidget, self).__init__()
      self.audio = Audio()
      self.gap = 20
      self.registered_notes = {}

   def kempli(self):
      fundamental = 47
      envelope = ADSREnvelope(1000, 1.5, 8410, 2.0, 0.005, 4410, 1.0, 1.1)
      tone = ToneGenerator(fundamental+12, SINE_AMPLITUDES, 0) + \
             ToneGenerator(fundamental+12, [(i, 1, 0) for i in xrange(6)], 0) + \
             ToneGenerator(fundamental-24, [ (i, 1./float(i), 0) for i in xrange(1,14) if i%2==1], 0)

      gen = envelope * tone
      return FMapGenerator(gen, LowPassDSP(100))

   def on_key_down(self, keycode, modifiers):
      # Your code here. You can change this whole function as you wish.
      print 'key-down', keycode, modifiers
      gen = False
      if keycode[1] == 'q':
         gen = FMapGenerator(NoteGenerator(59, SQUARE_AMPLITUDES, 0), LowPassDSP(100))
      elif keycode[1] == 'w':
         gen = NoteGenerator(60, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'e':
         gen = NoteGenerator(64, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'r':
         gen = NoteGenerator(65, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 't':
         gen = NoteGenerator(69, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'y':
         gen = NoteGenerator(71, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'u':
         gen = NoteGenerator(72, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'i':
         gen = NoteGenerator(76, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'o':
         gen = NoteGenerator(77, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'p':
         gen = NoteGenerator(81, SQUARE_AMPLITUDES, 0)
      elif keycode[1] == 'a':
         gen = NoteGenerator(59, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 's':
         gen = NoteGenerator(60, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'd':
         gen = NoteGenerator(64, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'f':
         gen = NoteGenerator(65, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'g':
         gen = NoteGenerator(69, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'h':
         gen = NoteGenerator(71, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'j':
         gen = NoteGenerator(72, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'k':
         gen = NoteGenerator(76, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'l':
         gen = NoteGenerator(77, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == ';':
         gen = NoteGenerator(81, SQUARE_AMPLITUDES, self.gap)
      elif keycode[1] == 'spacebar':
         gen = self.kempli()
      elif keycode[1] == 'up':
         self.audio.set_gain(self.audio.get_gain() + 0.1)
      elif keycode[1] == 'down':
         self.audio.set_gain(self.audio.get_gain() - 0.1)
      elif keycode[0] == 61:
         self.gap += 5
      elif keycode[0] == 45:
         self.gap -= 5

      if gen:
         self.registered_notes[keycode[0]] = gen
         self.audio.add_generator(gen)

   def on_key_up(self, keycode):
      # Your code here. You can change this whole function as you wish.
      print 'key up', keycode
      if keycode[0] in self.registered_notes:
         self.registered_notes[keycode[0]].release()
         del self.registered_notes[keycode[0]]


run(MainWidget)
