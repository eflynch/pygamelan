import numpy as np

from generator import Generator
from config import kSamplingRate

class ADSREnvelope(Generator):
   def __init__(self, attack_time=4410, attack_order=2.0, decay_time=44100,
                decay_order=1.5, sustain=0.3, release_time=4410, release_order=0.75,
                duration=None):
      self.attack_time = attack_time
      self.attack_order = attack_order
      self.decay_time = decay_time
      self.decay_order = decay_order
      self.sustain = sustain
      self.release_time = release_time
      self.release_order = release_order
      self.release_frame = float('inf')
      if duration:
         self.release_frame = duration * kSamplingRate - release_time
      Generator.__init__(self)

   def length(self):
      return self.release_frame + self.release_time

   def release(self):
      #Check if release already set
      if self.release_frame != float('inf'):
         return

      self.release_frame = self._frame

   def set_release_frame(self, frame):
      self.release_frame = frame

   def generate(self, frame_count):
      domain = np.arange(self._frame, self._frame + frame_count, dtype= np.float32)

      conditions = [
         domain < self.attack_time,
         (self.attack_time + self.decay_time > domain) * (domain >= self.attack_time),
         domain >= self.attack_time + self.decay_time
      ]
      functions = [
         lambda x: (x/self.attack_time)**(1/self.attack_order),
         lambda x: 1 - (1-self.sustain)*((x-self.attack_time)/self.decay_time)**(1/self.decay_order),
         lambda x: self.sustain
      ]
      signal = np.piecewise(domain, conditions, functions)

      conditions = [
         domain < self.release_frame,
         (self.length() > domain) * (domain >= self.release_frame),
         domain > self.length()
      ]
      functions = [
         lambda x: 1.0,
         lambda x: 1.0 - ((x-self.release_frame)/self.release_time)**(1/self.release_order),
         lambda x: 0.0
      ]
      signal *= np.piecewise(domain, conditions, functions)

      self._frame = self._frame + frame_count
      continue_flag = self.length() > self._frame

      return signal, continue_flag

if __name__ == "__main__":
   import matplotlib.pyplot as plt
   default_ADSR = {
      'attack_time': 4410,
      'attack_order': 1.5,
      'decay_time': 22050,
      'decay_order': 5.0,
      'sustain': 0.3,
      'release_time': 4410,
      'release_order': 5.0
   }

   envelope = ADSREnvelope(**default_ADSR)
   plt.figure()
   plt.plot(envelope.generate(44100)[0])
   envelope.release()
   plt.plot(envelope.generate(44100)[0])
   plt.show()


