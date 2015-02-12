import numpy as np

from config import kSamplingRate


def LowPassDSP(cutoff):
    def dsp(buf):
        L = 50
        omega_cut = float(cutoff) * 2.0 * np.pi / float(kSamplingRate)
        # [radians/sample] = [cycles/sec] * [radians/cycle] * [sec/sample]

        l_range = np.arange(-L, L, dtype=np.float32)
        l_range[L] = 1.0 # to avoid divide by zero error
        h = np.sin(omega_cut * l_range) / ( np.pi * l_range)
        h[L] = omega_cut / np.pi
        filtered = np.convolve(buf, h)[:len(buf)] / sum(h)
        return filtered
    return dsp

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    f = LowPassDSP(100)

    signal = np.sin(200*(2.0*np.pi/kSamplingRate)*np.arange(0,25600, dtype=np.float32))
    signal += np.sin(5*(2.0*np.pi/kSamplingRate)*np.arange(0,25600, dtype=np.float32))
    signal *= 0.5

    plt.figure()
    plt.plot(signal)
    plt.figure()
    plt.plot(f(signal))
    plt.show()
