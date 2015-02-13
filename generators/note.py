import numpy as np

from adsr import ADSREnvelope
from config import kSamplingRate
from generator import Generator

SQUARE_AMPLITUDES = [ (i, 1./float(i), 0) for i in xrange(1,20) if i%2==1]
SINE_AMPLITUDES = [(1, 1.0, 0.0)]
SAW_AMPLITUDES = [ (i, (-1)**(i+1) * 1./float(i), 0) for i in xrange(1, 20)]
TRI_AMPLITUDES = [ (i, 1./(float(i)**2), np.pi/2.) for i in xrange(1,20) if i%2==1]

def pitch_to_frequency(pitch):
   return 440 * 2 ** ((pitch - 69)/12.)


class Note(Generator):
   def __new__(cls, pitch, overtones, detune, duration=None, envelope=None):
      t = Tone(pitch, overtones, detune)
      if envelope == None:
         envelope = ADSREnvelope()
      if duration != None:
         release_frame = duration * kSamplingRate - envelope.release_time
         envelope.set_release_frame(release_frame)

      gen = t * envelope
      return gen

class Tone(Generator):
   def __init__(self, pitch, overtones=[(1,1,0)], detune=0):
      self.freq = pitch_to_frequency(pitch + detune/100.)
      self.overtones = filter(lambda x: x[0] * self.freq < kSamplingRate/2, overtones)
      self.norm = sum(x[1] for x in self.overtones)

      self._factor = self.freq * 2.0 * np.pi / kSamplingRate

      Generator.__init__(self)

   def length(self):
      return float('inf')

   def release(self):
      pass

   def get_buffer(self, frame_count):
      domain = np.arange(self.frame, self.frame + frame_count)

      signal = np.zeros(frame_count, dtype=np.float32)
      for order, amp, phase in self.overtones:
         signal += amp * np.sin(order * self._factor * domain + phase, dtype = np.float32)
      signal *= 1./self.norm

      continue_flag = self.frame + frame_count < self.length()
      return signal, continue_flag
