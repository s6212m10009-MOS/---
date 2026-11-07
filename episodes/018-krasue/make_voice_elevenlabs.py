"""พากย์เสียงไทยเรื่องกระสือด้วย ElevenLabs ทีละบรรทัดของ script.md

SDK ติดตั้งที่ C:/el (path สั้น เพราะ pip ติดตั้งลง site-packages ไม่ครบบน Windows)
คีย์อ่านจาก ../../.env.local ไม่พิมพ์ออกหน้าจอ

ตัวอย่าง:
  python make_voice_elevenlabs.py --list-voices
  python make_voice_elevenlabs.py --voice-id <id> --only 1
  python make_voice_elevenlabs.py --voice-id <id>
"""

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, "C:/el")
from elevenlabs import ElevenLabs, VoiceSettings  # noqa: E402

HERE = Path(__file__).resolve().parent
ENV_FILE = HERE.parent.parent / ".env.local"


def load_env():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def read_lines():
    text = (HERE / "script.md").read_text(encoding="utf-8")
    body = text.split("## บทพากย์", 1)[1]
    return [m.group(1).strip() for m in re.finditer(r"^\d+\.\s+(.+)$", body, re.M)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-id")
    ap.add_argument("--model", default="eleven_v4")
    ap.add_argument("--only", type=int, help="ทำเฉพาะบรรทัดที่ N")
    ap.add_argument("--list-voices", action="store_true")
    ap.add_argument("--outdir", default=str(HERE / "audio"))
    a = ap.parse_args()

    load_env()
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

    if a.list_voices:
        for v in client.voices.get_all().voices:
            print(v.voice_id, v.name, (v.labels or {}).get("language", ""), sep="\t")
        return

    if not a.voice_id:
        sys.exit("ต้องใส่ --voice-id")

    out = Path(a.outdir)
    out.mkdir(exist_ok=True)
    lines = read_lines()
    for i, text in enumerate(lines, 1):
        if a.only and i != a.only:
            continue
        audio = client.text_to_speech.convert(
            voice_id=a.voice_id,
            text=text,
            model_id=a.model,
            language_code="th",
            voice_settings=VoiceSettings(stability=0.4, similarity_boost=0.75),
            previous_text=lines[i - 2] if i > 1 else None,
            next_text=lines[i] if i < len(lines) else None,
        )
        path = out / f"line-{i:02d}.mp3"
        with open(path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        print("เขียน", path.name)


if __name__ == "__main__":
    main()
