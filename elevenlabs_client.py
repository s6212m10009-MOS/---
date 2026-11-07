from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv(".env.local")

# SDK อ่านคีย์จาก ELEVENLABS_API_KEY อัตโนมัติ
client = ElevenLabs()
