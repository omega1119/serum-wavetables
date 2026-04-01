# Serum Wavetables

Generate Serum-compatible wavetables by driving a sine wave through a modelled **Doepfer A-137-1** wavefolder.

The A-137-1 is a wave multiplier that folds a waveform back on itself as drive increases, creating additional zero crossings and rich harmonics. The script models this as a sinusoidal wavefold (`sin(drive · arcsin(x))`), producing Chebyshev-polynomial-like harmonic content that closely mirrors the analog behaviour.

## Project Structure

```
serum-wavetables/
├── src/
│   └── generate_wavetable.py   # Wavetable generator script
├── output/                     # Generated WAV files (after running)
└── README.md
```

## Usage

```bash
python src/generate_wavetable.py
```

This produces:

- **8 individual single-cycle WAVs** (2048 samples, 32-bit float) at progressively higher fold drives (1.0 → 14.0).
- **1 combined wavetable WAV** with all 8 frames concatenated — ready to drag straight into Serum's oscillator.

Output files are written to the `output/` directory.

## Importing into Serum

Drag the combined `a137_wavefolder_wavetable.wav` onto an oscillator in Serum, or use **Wavetable Editor → Import → Import audio file**.

## Requirements

Python 3.10+ (standard library only — no external dependencies).