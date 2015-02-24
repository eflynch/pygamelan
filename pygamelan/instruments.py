import numpy as np

from dspy import ADSREnvelope, ExpEnvelope, ReleaseEnvelope
from dspy import Note, Tone, FM
from dspy import DC, Sine, Generator
from dspy.dsp import LowPassDSP, Clip, Abs
from dspy.lib import t2f
from dspy.overtones import SINE_AMPLITUDES, SQUARE_AMPLITUDES, TRI_AMPLITUDES

class DurationEnvelope(Generator):
    def __init__(self, duration):
        Generator.__init__(self)
        self.duration = t2f(duration)

    def _length(self):
        return self.duration

    def _generate(self, frame_count):
        output = np.arange(self.frame, self.frame + frame_count,
                           dtype=np.float32)
        output[output >= self.duration] = 0
        output[output < self.duration] = 1
        return output
  
def num_to_pitch(num, octave=4):
    pitches = [-2, 0, 1, 5, 6]
    detunes = [0, -20, 0, -20, +20]
    return (15 + octave*12 + pitches[num], detunes[num])

class Gangsa(Generator):
    def __new__(cls, num, octave, detune=0):
        p, d = num_to_pitch(num, octave)
        envelope = ADSREnvelope(attack_time=1000, attack_order=2.0, decay_time=44100*20,
                                decay_order=5.0, sustain=0.00, release_time=4410,
                                release_order=0.75, duration=None)
        tone = Tone(p, SQUARE_AMPLITUDES, detune + d)
        return tone * envelope * DC(0.5)

class Pokok(Generator):
    def __new__(cls, num, octave, detune=0):
        p, d = num_to_pitch(num, octave)
        envelope1 = ADSREnvelope(attack_time=3000, attack_order=1.5, decay_time=44100*20,
                                decay_order=3.0, sustain=0.00, release_time=4410,
                                release_order=0.75, duration=None)
        tone1 = Tone(p, TRI_AMPLITUDES, detune + d)
        return tone1 * envelope1

class SpecialGong(Generator):
    def __new__(cls, detune=0):
        d = -20
        p = 45

        envelope = ExpEnvelope([
            (1.0, 500, 1.5),
            (0.6, 1.0, 0.75),
            (0.0, 10.0, 1.5)
        ], initial=0.0) * DurationEnvelope(11.1)

        tone = Tone(p-12, [(1,0.2,0)], detune + d) + \
               Tone(p, [(1,1,0)], detune + d) * Abs(Sine(1.00, 0, 1.0)) + \
               Tone(p, [(2,0.4,0)], detune + d) * Abs(Sine(1.00, 0, 1.0)) + \
               Tone(p, [(3,0.3,0)], detune + d) * Abs(Sine(12.5, 0, 1.0)) + \
               Tone(p, [(5,0.1,0)], detune + d) * Abs(Sine(3.2, 0, 1.0))

        return LowPassDSP(envelope * tone, 700) * DC(2.0)

class Gong(Generator):
    def __new__(cls, detune=0):
        d = 75
        p = 47
        envelope = ExpEnvelope([
            (1.0, 500, 1.5),
            (0.6, 1.0, 0.75),
            (0.0, 10.0, 1.5)
        ], initial=0.0) * DurationEnvelope(11.1)

        tone = Tone(p-12, [(1,0.6,0)], detune + d) + \
               Tone(p, [(1,1,0)], detune + d) * Abs(Sine(1.67, 0, 1.0)) + \
               Tone(p, [(2,0.4,0)], detune + d) * Abs(Sine(1.67, 0, 1.0)) + \
               Tone(p, [(3,0.3,0)], detune + d) * Abs(Sine(12.5, 0, 1.0)) + \
               Tone(p, [(5,0.1,0)], detune + d) * Abs(Sine(3.2, 0, 1.0))

        return LowPassDSP(envelope * tone, 700) * DC(2.0)

class Pore(Generator):
    def __new__(cls, detune=0):
        d = 50
        p = 58
        envelope = ExpEnvelope([
            (1.0, 500, 1.5),
            (0.6, 1.0, 0.75),
            (0.0, 10.0, 1.5)
        ], initial=0.0) * DurationEnvelope(11.1)

        tone = Tone(p-12, [(1,0.2,0)], detune + d) + \
               Tone(p, [(1,1,0)], detune + d) * Abs(Sine(2.67, 0, 1.0)) + \
               Tone(p, [(2,0.3,0)], detune + d) * Abs(Sine(2.67, 0, 1.0)) + \
               Tone(p, [(3,0.05,0)], detune + d) * Abs(Sine(10.5, 0, 1.0)) + \
               Tone(p, [(5,0.05,0)], detune + d) * Abs(Sine(5.2, 0, 1.0))

        return LowPassDSP(envelope * tone, 700) * DC(2.0)

class Tong(Generator):
    def __new__(cls, detune=0):
        p, d = num_to_pitch(1, 5)
        p = 69

        envelope = ExpEnvelope([
            (1.0, 500, 1.5),
            (0.0, 8.0, 5.0)
        ], initial=0.0) * DurationEnvelope(8.1)

        tone = Tone(p-12, [(1,0.2,0)], detune + d) + \
               Tone(p, [(1,1,0)], detune + d) + \
               Tone(p, [(2,0.5,0)], detune + d) + \
               Tone(p, [(3,0.3,0)], detune + d) * Abs(Sine(10.5, 0, 1.0)) + \
               Tone(p, [(5,0.1,0)], detune + d) * Abs(Sine(5.2, 0, 1.0))

        return LowPassDSP(envelope * tone, 700) * DC(2.0)

class Jublag(Generator):
    def __new__(cls, num, detune=0):
        return LowPassDSP(Pokok(num % 5, 4, 0) + Pokok(num % 5, 4, detune), 2000)

class Jegog(Generator):
    def __new__(cls, num, detune=0):
        num = num % 5
        octave = 3
        p, d = num_to_pitch(num, octave)
        envelope = ADSREnvelope(attack_time=5000, attack_order=1.5, decay_time=44100*20,
                                decay_order=3.0, sustain=0.00, release_time=4410,
                                release_order=0.75, duration=None)
        tone1 = Tone(p, TRI_AMPLITUDES, d)
        tone2 = Tone(p, TRI_AMPLITUDES, detune + d)
        return LowPassDSP((tone1 + tone2) * envelope, 500) * DC(1.2)

class Sarang(Generator):
    def __new__(cls, num, detune=0):
        return LowPassDSP(Pokok(num % 5, 5, 0) + Pokok(num % 5, 5, detune), 2000) * DC(1.2)

class Pamade(Generator):
    def __new__(cls, num, detune=0):
        n = num % 5
        octave = (num - n) / 5 + 4
        return Gangsa(n, octave, 0)+ Gangsa(n, octave, detune)

class Chantil(Generator):
    def __new__(cls, num, detune=0):
        n = num % 5
        octave = (num - n) / 5 + 5
        return Gangsa(n, octave, 0) + Gangsa(n, octave, detune)

class Kempli(Generator):
    def __new__(cls, pitch=48):
        envelope = ExpEnvelope([
            (1.0, 600, 1.5),
            (0.0, 20000, 3.0)
        ], initial=0.0) * DurationEnvelope(1.1)
        tone1 = Tone(pitch+12, SINE_AMPLITUDES, 0)
        tone2 = Tone(pitch-12, SQUARE_AMPLITUDES, 0) * DC(0.3)

        return (LowPassDSP(tone2, 500) * DC(0.2) + tone1) * envelope * DC(3.0)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    k = Kempli()

    plt.figure()
    plt.plot(k.generate(44100*4)[0])
    plt.show()
