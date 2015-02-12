import numpy as np

from config import kSamplingRate

class Generator(object):
   def __init__(self):
      self._frame = 0

   def __add__(self, other):
      return SumGenerator([self, other])

   def __mul__(self, other):
      return ProductGenerator([self, other])

   def reset(self):
      self._frame = 0

class ProductGenerator(Generator):
   def __init__(self, generators):
      self.generators = generators

   def length(self):
      return min(g.length() for g in self.generators)

   def release(self):
      for g in self.generators:
         g.release()

   def generate(self, frame_count):
      # Stop when first factor is done
      signal = np.ones(frame_count, dtype=np.float32)
      continue_flag = True
      for g in self.generators:
         data, cf = g.generate(frame_count)
         signal *= data
         if not cf:
            continue_flag = False

      return signal, continue_flag

class SumGenerator(Generator):
   def __init__(self, generators):
      self.generators = generators

   def length(self):
      return max(g.length() for g in self.generators)

   def release(self):
      for g in self.generators:
         g.release()

   def generate(self, frame_count):
      # Continue until all summands are done
      signal = np.zeros(frame_count, dtype=np.float32)
      continue_flag = False
      for g in self.generators:
         data, cf = g.generate(frame_count)
         signal+= data
         if cf:
            continue_flag = True

      return signal, continue_flag

class FMapGenerator(object):
   def __init__(self, generator, function):
      self.generator = generator
      self.function = function

   def length(self):
      return self.generator.length()

   def release(self):
      return self.generator.release()

   def generate(self, frame_count):
      signal, continue_flag = self.generator.generate(frame_count)
      return self.function(signal), continue_flag


   
