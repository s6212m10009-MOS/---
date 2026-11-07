from pathlib import Path
L = Path("build.py").read_text(encoding="utf-8").split("\n")
head = "\n".join(L[:65])
h_start = next(i for i, l in enumerate(L) if l.startswith("def txt("))
h_end = next(i for i, l in enumerate(L) if l.startswith("VIG = {"))
helpers = "\n".join(L[h_start:h_end])
tail_i = next(i for i, l in enumerate(L) if l.startswith("VGS ="))
tail = "\n".join(L[tail_i:])
mid = '''TAGS = ["สองเกาหลี <r>ตึงเครียด</r>", "ขีปนาวุธ <r>4 พ.ย.</r>", "ถ้ารบจริง <r>คนไทยทำไง?</r>", "<r>1</r> ติดตามสถานทูต", "<r>2</r> เอกสาร + เงินสด + ประกัน", "ยังไม่มีสงคราม <r>อย่าตื่นตระหนก</r>"]

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
INK = "#1E1E24"
# id, lon, lat, ป้าย, ฉากที่เปิด
PINS = [("dmz", 127.0, 38.1, "DMZ ชายแดน", 0), ("seoul", 126.98, 37.57, "โซล", 2), ("bkk", 100.5, 13.75, "กรุงเทพ", 4)]
# กล้อง: lon, lat, k, y ของหมุดบนวิวพอร์ต
CAM = [(127.4, 38.0, 8.0, 800), (129.5, 39.5, 7.0, 800), (127.0, 37.57, 24.0, 800), (127.0, 37.57, 24.0, 800), (113.7, 25.7, 2.6, 800), (100.5, 13.75, 3.5, 800)]


def cam_xy(i):
    lon, lat, k, py = CAM[i]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]

'''
tail = tail.replace("HOOK0 = [round(540 - mx(25) * 1.8, 1), -450, 1.8]", "HOOK0 = [round(540 - mx(127) * 1.1, 1), -30, 1.1]")
tail = tail.replace("TOTAL=TOTAL)", "TOTAL=TOTAL, PLANE0=PLANE0, PLANE1=PLANE1)")
tail = tail.replace('"%%PINS%%": pin_html,', '"%%PINS%%": pin_html, "%%GEO%%": GEO,')
out = head + "\n" + mid + helpers + "\n" + Path("vig_new.py").read_text(encoding="utf-8") + "\n" + tail
Path("build.py").write_text(out, encoding="utf-8")
