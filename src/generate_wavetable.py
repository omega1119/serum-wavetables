"""
Generate a Serum-importable wavetable: sine wave progressively driven
through a Doepfer A-137-1-style wavefolder.

The A-137-1 is a wave multiplier that folds the waveform back on itself
as drive increases, creating additional zero crossings and harmonics.
We model this as: output = sin(drive * input)
where input is a sine wave and drive ramps from 1.0 (pure sine) up to
heavy folding territory.

Output: 8 single-cycle WAVs (2048 samples each) + one combined wavetable WAV.
Serum expects 2048-sample cycles concatenated in a single file.
"""

import struct
import math
import os

SAMPLES_PER_CYCLE = 2048
NUM_FRAMES = 8
SAMPLE_RATE = 44100
BIT_DEPTH = 32  # 32-bit float for maximum quality

# Drive amounts: from pure sine (1.0) to heavily folded
# The A-137-1 progressively multiplies zero crossings
DRIVES = [1.0, 1.8, 2.8, 4.0, 5.5, 7.5, 10.0, 14.0]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")


def wavefold_a137(sample: float, drive: float) -> float:
    """
    Model the Doepfer A-137-1 wave multiplier.
    
    Uses a sinusoidal wavefolder: sin(drive * asin(x)) for the core
    folding, which creates Chebyshev-polynomial-like harmonics — very
    close to the analog wavefolder behavior where the signal folds
    back at saturation boundaries.
    """
    # Soft-clip the input to [-1, 1] range before folding
    x = max(-1.0, min(1.0, sample))
    # Sinusoidal wavefold: sin(drive * arcsin(x))
    # This is equivalent to Chebyshev polynomials of the first kind T_n(x)
    # At drive=1 this is identity, at higher drives it folds progressively
    return math.sin(drive * math.asin(x))


def generate_cycle(drive: float) -> list[float]:
    """Generate one 2048-sample cycle of a sine wave through the wavefolder."""
    cycle = []
    for i in range(SAMPLES_PER_CYCLE):
        phase = 2.0 * math.pi * i / SAMPLES_PER_CYCLE
        sine_val = math.sin(phase)
        folded = wavefold_a137(sine_val, drive)
        cycle.append(folded)
    return cycle


def normalize(samples: list[float]) -> list[float]:
    """Normalize to peak amplitude of 1.0."""
    peak = max(abs(s) for s in samples)
    if peak == 0:
        return samples
    return [s / peak for s in samples]


def write_wav_float32(filepath: str, samples: list[float], sample_rate: int = SAMPLE_RATE):
    """Write a 32-bit float WAV file (IEEE float format)."""
    num_samples = len(samples)
    num_channels = 1
    bytes_per_sample = 4
    data_size = num_samples * bytes_per_sample
    fmt_chunk_size = 16
    
    with open(filepath, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        
        # fmt chunk - format 3 = IEEE float
        f.write(b"fmt ")
        f.write(struct.pack("<I", fmt_chunk_size))
        f.write(struct.pack("<H", 3))  # IEEE float
        f.write(struct.pack("<H", num_channels))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", sample_rate * num_channels * bytes_per_sample))
        f.write(struct.pack("<H", num_channels * bytes_per_sample))
        f.write(struct.pack("<H", 32))
        
        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        for s in samples:
            f.write(struct.pack("<f", s))


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_samples: list[float] = []
    
    for i, drive in enumerate(DRIVES):
        cycle = generate_cycle(drive)
        cycle = normalize(cycle)
        all_samples.extend(cycle)
        
        # Write individual cycle
        individual_path = os.path.join(OUTPUT_DIR, f"a137_fold_{i+1:02d}_drive_{drive:.1f}.wav")
        write_wav_float32(individual_path, cycle)
        print(f"Frame {i+1}: drive={drive:5.1f}  -> {individual_path}")
    
    # Write combined wavetable (all 8 cycles concatenated)
    wavetable_path = os.path.join(OUTPUT_DIR, "a137_wavefolder_wavetable.wav")
    write_wav_float32(wavetable_path, all_samples)
    print(f"\nWavetable: {len(DRIVES)} frames x {SAMPLES_PER_CYCLE} samples = {len(all_samples)} total samples")
    print(f"Saved to: {wavetable_path}")
    print("\nImport into Serum: drag the wavetable file onto the oscillator,")
    print("or use the wavetable editor menu -> Import -> Import audio file.")


if __name__ == "__main__":
    main()
