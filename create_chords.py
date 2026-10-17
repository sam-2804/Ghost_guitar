import mido
import subprocess
import os

soundfont = "FluidR3_GM.sf2"
output_dir = "chords"
os.makedirs(output_dir, exist_ok=True)

def generate_strum_wav(chord_name, midi_notes, strum_direction, delay_ms=15, sustain_ms=1500):
    
    midi_filename = f"{chord_name}_{strum_direction}.mid"
    wav_filename = os.path.join(output_dir, f"{chord_name}_{strum_direction}.wav")
    
    # MIDI file and track inialization
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.Message('program_change', program=26, time=0))
    
    
    delay_ticks = int(delay_ms * 1) 
    sustain_ticks = int(sustain_ms * 1)
    
    track.append(mido.Message('note_on', note=midi_notes[0], velocity=100, time=0))
    for note in midi_notes[1:]:
        track.append(mido.Message('note_on', note=note, velocity=100, time=delay_ticks))
        
    track.append(mido.Message('note_off', note=midi_notes[0], velocity=0, time=sustain_ticks))
    for note in midi_notes[1:]:
        track.append(mido.Message('note_off', note=note, velocity=0, time=0))
        
    mid.save(midi_filename)
    
    print(f"Rendering {wav_filename}...")
    result = subprocess.run([
        "fluidsynth", 
        "-F", wav_filename,  # Fast-rendering to file
        "-ni",               # No MIDI input (offline mode)
        "-R", "0",           # Disable Reverb tail
        "-C", "0",            # Disable Chorus tail
        soundfont, 
        midi_filename
    ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW) 
    
    os.remove(midi_filename)
    print(f"Successfully generated: {wav_filename}")


chords = {
    "G_chord": [43, 47, 50, 55, 59, 67],
    "C_chord": [48, 52, 55, 60, 64],      # Standard 5-string open C
    "D_chord": [50, 57, 62, 66],      # Standard 4-string open D
    "Em_chord": [40, 47, 52, 55, 59, 64]
}



for name, notes in chords.items():
    fast_name = f"{name}_fast"
    generate_strum_wav(name, notes, "down", delay_ms=10, sustain_ms = 2500)
    generate_strum_wav(name, notes[::-1], "up", delay_ms=10, sustain_ms = 2500)
    generate_strum_wav(fast_name, notes, "down", delay_ms=10, sustain_ms= 100)
    generate_strum_wav(fast_name, notes[::-1], "up", delay_ms=10, sustain_ms= 100)
print("\nAll chords cached!")