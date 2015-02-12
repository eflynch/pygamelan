import numpy as np

from adsr import ADSREnvelope
from config import kSamplingRate
from generator import Generator


def pitch_to_frequency(pitch):
   return 440 * 2 ** ((pitch - 69)/12.)


class NoteGenerator(Generator):
   def __new__(cls, pitch, overtones, detune, duration=None, envelope=None):
      t = ToneGenerator(pitch, overtones, detune)
      if envelope == None:
         envelope = ADSREnvelope()
      if duration != None:
         release_frame = duration * kSamplingRate - envelope.release_time
         envelope.set_release_frame(release_frame)

      gen = t * envelope
      return gen


class ToneGenerator(Generator):
   def __init__(self, pitch, overtones, detune):
      self.freq = pitch_to_frequency(pitch + detune/100.)
      self.overtones = filter(lambda x: x[0] * self.freq < kSamplingRate/2, overtones)
      self.norm = sum(x[1] for x in self.overtones)

      self._factor = self.freq * 2.0 * np.pi / kSamplingRate
      self._frame = 0

   def length(self):
      return float('inf')

   def release(self):
      pass

   def generate(self, frame_count):
      continue_flag = True
      domain = np.arange(self._frame, self._frame + frame_count)

      self._frame = self._frame + frame_count

      signal = np.zeros(frame_count, dtype=np.float32)
      for order, amp, phase in self.overtones:
         signal += amp * np.sin(order * self._factor * domain + phase, dtype = np.float32)
      signal *= 1./self.norm

      if self._frame >= self.length():
         continue_flag = False

      return signal, continue_flag
