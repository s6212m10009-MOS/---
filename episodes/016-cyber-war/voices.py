import asyncio, json, subprocess
from pathlib import Path
import edge_tts
ROOT=Path(__file__).resolve().parent
LINES=[
"จะเกิดอะไรขึ้น ถ้าพรุ่งนี้ เกิดสงครามไซเบอร์ ในไทย",
"ชั่วโมงแรก แอปธนาคารเปิดไม่ได้ สแกนจ่ายไม่ได้ ตู้เอทีเอ็มก็ดับ",
"วันแรก ปั๊มน้ำมันรับเงินไม่ได้ ร้านสะดวกซื้อปิด ทุกคนแห่หาเงินสด",
"สัปดาห์แรก ไฟฟ้า น้ำประปา และโรงพยาบาล เริ่มรวน ต้องกลับไปใช้กระดาษ",
"ฟังเหมือนนิยาย แต่เกิดขึ้นจริงแล้วที่ยูเครน ปีสองพันสิบห้า ไฟดับกว่าสองแสนคน",
"สิ่งที่ต้องเตรียม เงินสด วิทยุ พาวเวอร์แบงก์ น้ำดื่ม และยาประจำตัว พอใช้สามถึงเจ็ดวัน",
"แล้วคุณล่ะ ตอนนี้ในกระเป๋ามีเงินสดเท่าไร ถ้าพรุ่งนี้สแกนจ่ายไม่ได้",
]
async def main():
    out=[]
    for i,l in enumerate(LINES):
        p=ROOT/'audio'/f'v{i}.mp3'
        await asyncio.wait_for(edge_tts.Communicate(l,'th-TH-NiwatNeural',rate='+6%').save(str(p)),60)
        d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)],text=True))
        out.append(round(d,2)); print(i,d,flush=True)
    (ROOT/'voice-durations.json').write_text(json.dumps(out))
asyncio.run(main())
