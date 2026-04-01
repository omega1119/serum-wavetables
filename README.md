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

1. Drag `a137_wavefolder_wavetable.wav` onto a wavetable oscillator and select **Dynamic Pitch – Zero Snap**.
2. Click **Edit → Process All**:
   - **Remove DC Offset** — strips any constant voltage bias from each frame, centering the waveform around zero. Without this, frames can sit slightly above or below the midline, causing clicks and an unwanted sub-bass rumble when cycling through the wavetable.
   - **Normalize Each** — scales every frame independently so its peak reaches full amplitude. This evens out the perceived loudness across the wavetable, since heavier fold drives can change the peak level.
   - **Nudge All Phases for Fundamental to 50%** — shifts each frame in time so the fundamental's phase sits at 50% (i.e. a cosine alignment). This ensures smooth crossfading between frames by removing phase discontinuities in the lowest harmonic — without it, morphing can introduce cancellation or timbral jumps.
3. Click **Morph**:
   - **Morph Spectral** — interpolates between frames in the frequency domain rather than the time domain. Serum decomposes each frame into its harmonic spectrum and blends magnitudes and phases, producing smooth timbral transitions instead of the waveform-averaging artifacts you'd get from a simple crossfade.

## Patch Idea

- Set **Unison** to **4** for a wider, detuned sound.
- Assign an **LFO** to the **WT Pos** parameter to automatically sweep through the wavefolder drive stages.
- Click the wavetable display to switch to the **3D render** view — this gives a clear visual of how the harmonic content evolves across frames.

## Requirements

Python 3.10+ (standard library only — no external dependencies).