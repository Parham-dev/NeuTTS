"""
Voice reference management
"""

import torch
from pathlib import Path
from typing import Dict


class VoiceManager:
    def __init__(self, samples_dir: str = "samples"):
        self.samples_dir = Path(samples_dir)
        self.voices: Dict[str, dict] = {}

    def load_all_voices(self):
        """Load all voice references from samples directory"""
        print("Loading available voices...")

        for pt_file in self.samples_dir.glob("*.pt"):
            voice_name = pt_file.stem
            txt_file = self.samples_dir / f"{voice_name}.txt"
            wav_file = self.samples_dir / f"{voice_name}.wav"

            if txt_file.exists():
                self.voices[voice_name] = {
                    "codes": torch.load(pt_file),
                    "text": txt_file.read_text().strip(),
                    "codes_path": str(pt_file),
                    "text_path": str(txt_file),
                    "audio_path": str(wav_file) if wav_file.exists() else None
                }
                print(f"  ✓ Loaded voice: {voice_name}")

        if not self.voices:
            print("  ⚠ No voices found!")
        else:
            print(f"  Total voices loaded: {len(self.voices)}")

    def get_voice(self, name: str) -> dict:
        """Get voice data by name"""
        return self.voices.get(name.lower())

    def add_voice(self, name: str, codes: torch.Tensor, text: str, audio_path: str):
        """Add new voice reference"""
        codes_path = self.samples_dir / f"{name}.pt"
        text_path = self.samples_dir / f"{name}.txt"

        torch.save(codes, codes_path)
        text_path.write_text(text.strip())

        self.voices[name] = {
            "codes": codes,
            "text": text.strip(),
            "codes_path": str(codes_path),
            "text_path": str(text_path),
            "audio_path": audio_path
        }

    def delete_voice(self, name: str):
        """Delete voice reference"""
        if name not in self.voices:
            raise ValueError(f"Voice '{name}' not found")

        voice_data = self.voices[name]
        for key in ["codes_path", "text_path", "audio_path"]:
            if key in voice_data and voice_data[key]:
                path = Path(voice_data[key])
                if path.exists():
                    path.unlink()

        del self.voices[name]

    def list_voices(self) -> list[dict]:
        """List all voices"""
        return [
            {
                "name": name,
                "text_path": data["text_path"],
                "codes_path": data["codes_path"],
                "audio_path": data.get("audio_path"),
                "has_audio": data.get("audio_path") is not None
            }
            for name, data in self.voices.items()
        ]
