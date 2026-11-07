"""ทดลองเสียงพากย์ไทยด้วย Gemini TTS (Google AI Studio) -> gemini-voice-test/*.wav

ต้องตั้ง API key ไว้ในตัวแปร GEMINI_API_KEY ก่อน (ไม่ต้องใส่ key ในไฟล์นี้)

ตัวอย่าง:
  python try_gemini_voice.py                               # เทียบ 4 เสียงด้วยประโยคตัวอย่าง
  python try_gemini_voice.py --voice Charon                # เสียงเดียว
  python try_gemini_voice.py --text "..." --style "เล่าแบบลึกลับ เสียงต่ำ ช้าๆ"
  python try_gemini_voice.py --voice Charon Algenib Sadaltager Kore
"""

import argparse
import os
import sys
from pathlib import Path

from google import genai

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "gemini-voice-test"
MODEL = "gemini-3.8-flash-tts"   # รุ่นนี้รองรับภาษาไทย (รุ่น flash-lite ยังไม่รองรับ)

TEXT = ("อังกฤษมีเรือดำน้ำนิวเคลียร์ สี่ลำ ตอนนี้ สามลำ หายลงไปใต้ทะเล พร้อมกัน "
        "<short pause> แล้วมันเกิดอะไรขึ้นกันแน่?")
STYLE = "เล่าเรื่องสารคดีน่าติดตาม น้ำเสียงลึกลับนิดๆ จังหวะกระชับ ชัดถ้อยชัดคำ"
# เสียงชาย/หญิงที่น่าลองสำหรับช่องเล่าเรื่อง
VOICES = ["Charon", "Algenib", "Sadaltager", "Kore"]


def synth(client, text, voice, style, path):
    part = {"text": text}
    if style:
        part["speech_metadata"] = {"style": style}
    resp = client.models.generate_content(
        model=MODEL,
        contents=[{"role": "user", "parts": [part]}],
        config={
            "response_modalities": ["AUDIO"],
            "speech_config": {"voice_config": {"voice": voice}},
        },
    )
    path.write_bytes(resp.candidates[0].content.parts[0].inline_data.data)  # WAV 24kHz mono


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default=TEXT)
    ap.add_argument("--style", default=STYLE, help='สไตล์การพูด ใส่ "" ถ้าไม่ต้องการ')
    ap.add_argument("--voice", nargs="+", default=VOICES)
    args = ap.parse_args()

    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("ยังไม่ได้ตั้ง GEMINI_API_KEY — ตั้งค่าแล้วเปิด terminal ใหม่")

    client = genai.Client()
    OUT.mkdir(exist_ok=True)
    for v in args.voice:
        path = OUT / f"{v}.wav"
        print("TTS", v, "...", flush=True)
        synth(client, args.text, v, args.style, path)
        print("  ->", path, flush=True)


if __name__ == "__main__":
    main()
