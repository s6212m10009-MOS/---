import json, os, sys, time, wave, subprocess
from pathlib import Path
from google import genai
H = Path(__file__).parent
S = json.loads((H/"script.json").read_text(encoding="utf-8"))
c = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
STYLE = "ครูสาวใจดี น้ำเสียงสดใส เป็นกันเอง ชัดถ้อยชัดคำ เหมาะกับวิดีโอการเรียนรู้สำหรับนักเรียนมัธยม"
for i, t in enumerate(S):
    out = H/"audio"/f"{i}.wav"
    if out.exists(): continue
    for a in range(6):
        try:
            r = c.models.generate_content(model="gemini-3.8-flash-tts",
                contents=[{"role":"user","parts":[{"text":t,"speech_metadata":{"style":STYLE}}]}],
                config={"response_modalities":["AUDIO"],"speech_config":{"voice_config":{"voice":"Kore"}}})
            raw = r.candidates[0].content.parts[0].inline_data.data
            (H/"audio"/f"{i}_raw.bin").write_bytes(raw); break
        except Exception as e:
            print("retry", str(e)[:120], flush=True); time.sleep(25*(a+1))
    else: sys.exit("fail")
    print("ok", i, flush=True)
