from adsr import ADSREnvelope
from note import Tone, SINE_AMPLITUDES, SQUARE_AMPLITUDES
from generator import DC, Generator
from dsp import LowPassDSP

class Kempli(Generator):
    def __new__(cls, pitch=47):
        envelope = ADSREnvelope(1000, 1.5, 8410, 2.0, 0.000, 4410, 1.0, 1.1)
        tone = Tone(pitch+12, SINE_AMPLITUDES, 0) + \
               Tone(pitch-24, SQUARE_AMPLITUDES, 0)
        gen = envelope * tone
        return LowPassDSP(gen, 300) * DC(18.0)
