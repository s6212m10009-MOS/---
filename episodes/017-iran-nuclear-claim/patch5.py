import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
b = (ROOT / 'build.py').read_text(encoding='utf-8')

GL = '<svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>'

# ---------- 1. T computed from voice durations ----------
old_T = 'T = [0, 4.6, 11.0, 17.6, 23.8, 29.5, 34.4, 42.8, 47.6]'
assert old_T in b
new_T = '''import json as _json
_vd = _json.loads((ROOT / 'voice-durations.json').read_text())
_floor = [4.6, 6.4, 0, 6.6, 6.2, 0, 5.7, 4.9, 0, 0, 0, 0, 0, 8.4, 5.4]
T = [0.0]
for _d, _f in zip(_vd, _floor):
    T.append(round(T[-1] + max(round(_d + 1.2, 1), _f), 1))'''
b = b.replace(old_T, new_T, 1)
b = b.replace("TOTAL = T[-1]", "TOTAL = T[-1]")  # (TOTAL defined right after T)

# ---------- 2. remap T indices in timeline + events ----------
MAP = {0: 0, 1: 1, 2: 3, 3: 4, 4: 6, 5: 7, 6: 13, 7: 14}


def remap(text):
    return re.sub(r'T\[(\d)\]', lambda m: 'T[%d]' % MAP[int(m.group(1))], text)


a = b.index('      // ===== S2 =====')
z = b.index('      window.__timelines["main"] = tl;')
b = b[:a] + remap(b[a:z]) + b[z:]
a = b.index("events = '''")
z = b.index("(ROOT / 'mix.py').write_text")
b = b[:a] + remap(b[a:z]) + b[z:]

# ---------- 3. captions ----------
CAPMAP = {1: 1, 2: 2, 3: 4, 4: 5, 5: 7, 6: 8, 7: 14, 8: 15}
for k in sorted(CAPMAP, reverse=True):
    b = b.replace('id="k%d"' % k, 'id="kk%d"' % CAPMAP[k])
b = b.replace('id="kk', 'id="k')
newcaps = {
    3: 'คาร์ลสัน [ไม่ใช่โฆษกรัฐบาล] คำเตือน [ไม่เท่ากับ] ประกาศทางการ',
    6: 'อ้างว่าข่าวกรองอิสราเอลเชื่อว่า [กลับมาเสริมสมรรถนะ] ยูเรเนียม แต่ [ยังต้องตรวจสอบ]',
    9: 'ทรัมป์ [ตอบโต้เนทันยาฮู] ต่อสาธารณะ เรื่องข่าวกรองอิหร่าน',
    10: 'เขาเตือนว่าอาจลุกลามเป็น [สงครามโลก] แต่นี่คือ [ความเห็น] ไม่ใช่ข้อเท็จจริง',
    11: 'อ้างว่าอาจตัดสินใจ [ภายใน 7 พ.ย.] แต่ [ไม่มีหลักฐาน] รองรับ',
    12: 'ลองคิดสามทาง [เจรจาได้] [ขู่ต่อ] [โจมตีจริง] ผลต่อตลาดต่างกัน',
    13: 'ตลาดต้องจับตา [ราคาพลังงาน] [เส้นทางขนส่ง] และ [ความผันผวน]',
}
# the last caption (k15) text update
b = b.replace('ก่อนแชร์ ถาม [ใครพูด] และ [มีหลักฐานไหม]', 'ก่อนแชร์ ถาม [ใครพูด] [มีหลักฐานไหม] และ [แหล่งอิสระ] ยืนยันไหม')
# insert new caption divs in order after their predecessors
order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
cap_start = b.index('      <div class="caps">')
cap_end = b.index('      </div>\n    </div>\n', cap_start)
caps_block = b[cap_start:cap_end]
lines = {}
for ln in caps_block.split('\n'):
    m = re.search(r'id="k(\d+)"', ln)
    if m:
        lines[int(m.group(1))] = ln
for k, txt in newcaps.items():
    lines[k] = '        <div class="cap" id="k%d">%s</div>' % (k, txt)
new_caps_block = '      <div class="caps">\n' + '\n'.join(lines[k] for k in order) + '\n'
b = b[:cap_start] + new_caps_block + b[cap_end:]

# ---------- 4. SC / loops ----------
b = b.replace('var SC = ["#s1", "#s2", "#s3", "#s3b", "#s4", "#s5", "#s6", "#s7"];',
              'var SC = ["#s1", "#s2", "#sA", "#s3", "#s3b", "#sB", "#s4", "#s5", "#sC", "#sD", "#sE", "#sF", "#sG", "#s6", "#s7"];')
b = b.replace('for (var i = 1; i < 8; i++) crossTo', 'for (var i = 1; i < 15; i++) crossTo')
b = b.replace('for (var j = 0; j < 8; j++) caption', 'for (var j = 0; j < 15; j++) caption')

# ---------- 5. s7 : third row ----------
b = b.replace('''<div id="r7b" class="row" style="left: 80px; top: 690px"><div class="pill" style="background: #ffd23f; font-size: 56px">2</div><div class="pill" style="font-size: 54px">มีหลักฐานไหม ?</div></div>''',
              '''<div id="r7b" class="row" style="left: 80px; top: 650px"><div class="pill" style="background: #ffd23f; font-size: 56px">2</div><div class="pill" style="font-size: 54px">มีหลักฐานไหม ?</div></div>
        <div id="r7c" class="row" style="left: 80px; top: 780px"><div class="pill" style="background: #ffd23f; font-size: 56px">3</div><div class="pill" style="font-size: 50px">แหล่งอิสระยืนยันไหม ?</div></div>''')
b = b.replace('id="r7a" class="row" style="left: 80px; top: 520px"', 'id="r7a" class="row" style="left: 80px; top: 520px"')
b = b.replace('id="mag7" class="ic" data-icon="mag" style="left: 640px; top: 880px; width: 330px; height: 330px"', 'id="mag7" class="ic" data-icon="mag" style="left: 640px; top: 960px; width: 310px; height: 310px"')
b = b.replace('id="c7" class="char" data-kind="me" style="left: 170px; top: 880px; width: 320px; height: 490px"', 'id="c7" class="char" data-kind="me" style="left: 170px; top: 960px; width: 300px; height: 420px"')
b = b.replace('tl.from("#r7b", { x: -300, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 1.4);',
              'tl.from("#r7b", { x: -300, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 1.4);\n      tl.from("#r7c", { x: -300, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 2.4);')
b = b.replace('charIn("#c7", a + 0.8); popIn("#mag7", a + 1.8);', 'charIn("#c7", a + 0.8); popIn("#mag7", a + 3.0);')
b = b.replace('}, a + 2.4);\n      breathe("#c7", a + 1.5, 3);', '}, a + 3.6);\n      breathe("#c7", a + 1.5, 3);')

# ---------- 6. new icons ----------
new_icons = r"""
        mic: '<rect x="68" y="12" width="64" height="104" rx="32" fill="#9aa5b1" ' + W + '/><path d="M44,88 Q44,152 100,152 Q156,152 156,88" fill="none" ' + W + '/><path d="M100,152 V186 M66,186 H134" fill="none" ' + W + '/><path d="M80,44 H120 M80,66 H120" stroke="' + INK + '" stroke-width="5"/>',
        cent: '<rect x="14" y="150" width="172" height="26" rx="8" fill="#6d6a78" ' + W + '/><g fill="#cfd6e4" ' + W + '><rect x="26" y="40" width="40" height="112" rx="14"/><rect x="80" y="40" width="40" height="112" rx="14"/><rect x="134" y="40" width="40" height="112" rx="14"/></g>',
        cal: '<rect x="14" y="26" width="172" height="162" rx="16" fill="#fff" ' + W + '/><path d="M14,42 Q14,26 30,26 H170 Q186,26 186,42 V76 H14Z" fill="#E0243A" ' + W + '/><path d="M54,10 V40 M146,10 V40" fill="none" ' + W + '/><text x="100" y="158" font-family="Kanit" font-weight="800" font-size="76" fill="' + INK + '" text-anchor="middle">7</text><text x="100" y="64" font-family="Kanit" font-weight="800" font-size="30" fill="#fff" text-anchor="middle">พ.ย.</text>',
        chart: '<path d="M20,20 V176 H184" fill="none" ' + W + '/><path d="M34,140 L70,100 L100,126 L142,60 L170,36" fill="none" stroke="#E0243A" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/><path d="M150,34 H174 V58" fill="none" stroke="#E0243A" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>',
        ship: '<path d="M20,120 H180 L156,170 H44Z" fill="#E0243A" ' + W + '/><rect x="56" y="74" width="62" height="46" rx="6" fill="#fff" ' + W + '/><rect x="76" y="40" width="26" height="34" rx="5" fill="#f5b83d" ' + W + '/><g fill="#6bbce6" stroke="' + INK + '" stroke-width="4"><rect x="66" y="88" width="14" height="14"/><rect x="92" y="88" width="14" height="14"/></g><path d="M10,184 Q40,170 70,184 T130,184 T190,184" fill="none" stroke="#6bbce6" stroke-width="8" stroke-linecap="round"/>',
"""
mk = '"""' + ".replace('RADPATH', rad_paths())"
assert mk in b, 'radpath marker'
b = b.replace(mk, new_icons.strip(chr(10)) + chr(10) + mk, 1)

# ---------- 7. scene markup ----------
sA = '''      <!-- sA : who is Carlson -->
      <div id="sA" class="scene">
        <div class="tags"><div id="tAa" class="tag">คำเตือน <r>≠</r> ประกาศ</div></div>
        <div id="micA" class="ic" data-icon="mic" style="left: 90px; top: 520px; width: 200px; height: 200px"></div>
        <div id="bkA" class="ic" data-icon="bank" style="left: 700px; top: 500px; width: 280px; height: 280px"></div>
        <div id="neA" class="mark" style="left: 440px; top: 540px; font-size: 230px">≠</div>
        <div id="plA" class="pill abs" style="left: 60px; top: 760px; font-size: 38px">นักวิจารณ์ / พิธีกร</div>
        <div id="prA" class="pill abs" style="left: 700px; top: 800px; font-size: 38px">รัฐบาลสหรัฐฯ</div>
        <div id="cAl" class="char" data-kind="me" style="left: 90px; top: 880px; width: 280px; height: 480px"></div>
        <div id="cAr" class="char" data-kind="biz" style="left: 700px; top: 880px; width: 280px; height: 480px"></div>
        ''' + GL + '''
      </div>

'''
sB = '''      <!-- sB : enrichment claim -->
      <div id="sB" class="scene">
        <div class="tags"><div id="tBa" class="tag">เขาอ้างว่า…</div></div>
        <div id="magB" class="ic" data-icon="mag" style="left: 60px; top: 520px; width: 260px; height: 260px"></div>
        <svg id="arB" class="abs" style="left: 330px; top: 600px; width: 140px; height: 80px" viewBox="0 0 130 80"><path d="M10,40 H100 M76,14 L106,40 L76,66" fill="none" stroke="#1e1e24" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <div id="cenB" class="ic" data-icon="cent" style="left: 500px; top: 500px; width: 300px; height: 300px"></div>
        <div id="qB" class="mark" style="left: 840px; top: 540px; font-size: 220px">?</div>
        <div id="pmB" class="pill abs" style="left: 60px; top: 800px; font-size: 38px">ข่าวกรองอิสราเอล</div>
        <div id="pcB" class="pill abs" style="left: 500px; top: 820px; font-size: 38px">เสริมสมรรถนะยูเรเนียม</div>
        <div id="puB" class="pill abs" style="left: 250px; top: 930px; font-size: 46px; background: #ffd23f">ยังต้องตรวจสอบ</div>
        <div id="cB" class="char" data-kind="me" style="left: 380px; top: 1000px; width: 260px; height: 360px"></div>
        ''' + GL + '''
      </div>

'''
sC = '''      <!-- sC : public disagreement -->
      <div id="sC" class="scene">
        <div class="tags"><div id="tCa" class="tag">ไม่ลงรอยกันต่อสาธารณะ</div></div>
        <div id="lbC" class="pill abs" style="left: 70px; top: 760px; font-size: 38px">เนทันยาฮู</div>
        <div id="rbC" class="pill abs" style="left: 760px; top: 760px; font-size: 38px">ทรัมป์</div>
        <div id="cCl" class="char" data-kind="me" style="left: 50px; top: 850px; width: 300px; height: 500px"></div>
        <div id="cCr" class="char" data-kind="biz" style="left: 730px; top: 850px; width: 300px; height: 500px"></div>
        <div id="bCl" class="bubble" style="left: 70px; top: 560px; font-size: 40px">ข่าวกรองน่ากังวล!</div>
        <div id="bCr" class="bubble" style="left: 560px; top: 560px; font-size: 40px; background: #ffd23f">รู้อยู่แล้ว</div>
        <div id="pnC" class="pill abs" style="left: 330px; top: 1000px; font-size: 40px">ตามรายงานของสื่อ</div>
        ''' + GL + '''
      </div>

'''
sD = '''      <!-- sD : domino claim -->
      <div id="sD" class="scene">
        <div class="tags"><div id="tDa" class="tag">คำเตือนของ Carlson</div></div>
        <div id="dm1" class="abs" style="left: 90px; top: 620px; width: 150px; height: 300px; background: #E0243A; border: 7px solid #1e1e24; border-radius: 16px; transform-origin: 100% 100%"></div>
        <div id="dm2" class="abs" style="left: 300px; top: 620px; width: 150px; height: 300px; background: #f5b83d; border: 7px solid #1e1e24; border-radius: 16px; transform-origin: 100% 100%"></div>
        <div id="dm3" class="abs" style="left: 510px; top: 620px; width: 150px; height: 300px; background: #6bbce6; border: 7px solid #1e1e24; border-radius: 16px; transform-origin: 100% 100%"></div>
        <div id="dm4" class="abs" style="left: 720px; top: 620px; width: 150px; height: 300px; background: #7fcf7a; border: 7px solid #1e1e24; border-radius: 16px; transform-origin: 100% 100%"></div>
        <div id="dl1" class="pill abs" style="left: 60px; top: 940px; font-size: 34px">ใช้ก่อน</div>
        <div id="dl2" class="pill abs" style="left: 250px; top: 940px; font-size: 34px">ชาติอื่นทำตาม</div>
        <div id="dl3" class="pill abs" style="left: 540px; top: 940px; font-size: 34px">ลุกลาม?</div>
        <div id="dl4" class="pill red abs" style="left: 700px; top: 1010px; font-size: 34px">สงครามโลก?</div>
        <div id="opD" class="pill abs" style="left: 200px; top: 1130px; font-size: 48px; background: #ffd23f">ความเห็น ≠ ข้อเท็จจริง</div>
        <div id="cD" class="char" data-kind="me" style="left: 780px; top: 1010px; width: 220px; height: 340px; display: none"></div>
        ''' + GL + '''
      </div>

'''
sE = '''      <!-- sE : deadline -->
      <div id="sE" class="scene">
        <div class="tags"><div id="tEa" class="tag">กำหนดเวลาที่อ้าง</div></div>
        <div id="calE" class="ic" data-icon="cal" style="left: 250px; top: 480px; width: 580px; height: 580px"></div>
        <div id="qE" class="mark" style="left: 770px; top: 520px; font-size: 200px">?</div>
        <div id="pE" class="pill red abs" style="left: 250px; top: 1090px; font-size: 48px">ไม่มีหลักฐานสาธารณะ</div>
        <div id="cE" class="char" data-kind="me" style="left: 60px; top: 960px; width: 240px; height: 400px"></div>
        ''' + GL + '''
      </div>

'''
sF = '''      <!-- sF : three scenarios -->
      <div id="sF" class="scene">
        <div class="tags"><div id="tFa" class="tag">สมมติ 3 ทาง</div></div>
        <div id="f1" class="item" style="left: 50px; top: 520px"><div id="okF" class="stamp" style="position: relative; width: 170px; height: 170px"></div><div class="pill" style="font-size: 38px">เจรจาได้</div></div>
        <div id="f2" class="item" style="left: 420px; top: 520px"><div class="ic" data-icon="chart" style="width: 180px; height: 180px"></div><div class="pill" style="font-size: 38px">ขู่ต่อ</div></div>
        <div id="f3" class="item" style="left: 790px; top: 520px"><div class="ic" data-icon="bomb" style="width: 180px; height: 180px"></div><div class="pill" style="font-size: 38px">โจมตีจริง</div></div>
        <div id="g1" class="pill grn abs" style="left: 20px; top: 820px; font-size: 36px">ตลาดน่าจะสงบ</div>
        <div id="g2" class="pill abs" style="left: 400px; top: 820px; font-size: 36px; background: #ffd23f">ราคาผันผวน</div>
        <div id="g3" class="pill red abs" style="left: 740px; top: 820px; font-size: 36px">แรงกว่านั้นมาก</div>
        <div id="nF" class="pill abs" style="left: 330px; top: 1000px; font-size: 40px">ภาพสมมติ ไม่ใช่การทำนาย</div>
        <div id="cF" class="char" data-kind="me" style="left: 400px; top: 1060px; width: 260px; height: 300px; display: none"></div>
        ''' + GL + '''
      </div>

'''
sG = '''      <!-- sG : markets watchlist -->
      <div id="sG" class="scene">
        <div class="tags"><div id="tGa" class="tag">ตลาดการเงินต้องจับตา</div></div>
        <div id="rG1" class="row" style="left: 80px; top: 520px"><div class="ic" data-icon="chart" style="position: relative; width: 150px; height: 150px"></div><div class="pill" style="font-size: 50px">ราคาพลังงาน</div></div>
        <div id="rG2" class="row" style="left: 80px; top: 710px"><div class="ic" data-icon="ship" style="position: relative; width: 150px; height: 150px"></div><div class="pill" style="font-size: 50px">เส้นทางขนส่ง</div></div>
        <div id="rG3" class="row" style="left: 80px; top: 900px"><div class="ic" data-icon="drum" style="position: relative; width: 150px; height: 150px"></div><div class="pill" style="font-size: 50px">ความผันผวนสินทรัพย์</div></div>
        <div id="cG" class="char" data-kind="me" style="left: 760px; top: 1050px; width: 240px; height: 310px"></div>
        ''' + GL + '''
      </div>

'''
assert '      <!-- S3 -->' in b and '      <!-- S4 -->' in b and '      <!-- S6 -->' in b
b = b.replace('      <!-- S3 -->', sA + '      <!-- S3 -->', 1)
b = b.replace('      <!-- S4 -->', sB + '      <!-- S4 -->', 1)
b = b.replace('      <!-- S6 -->', sC + sD + sE + sF + sG + '      <!-- S6 -->', 1)

# ---------- 8. poses ----------
b = b.replace('      pose("#c7", { eyes: "norm", mouth: "smile", arms: "point", sweat: 0, blush: 0 }, 0);',
              '''      pose("#c7", { eyes: "norm", mouth: "smile", arms: "point", sweat: 0, blush: 0 }, 0);
      pose("#cAl", { eyes: "norm", mouth: "smile", arms: "point", sweat: 0, blush: 0 }, 0);
      pose("#cAr", { eyes: "norm", mouth: "flat", arms: "down", sweat: 0, blush: 0 }, 0);
      pose("#cB", { eyes: "norm", mouth: "flat", arms: "chin", sweat: 1, blush: 0 }, 0);
      pose("#cCl", { eyes: "shock", mouth: "o", arms: "up", sweat: 1, blush: 0 }, 0);
      pose("#cCr", { eyes: "norm", mouth: "flat", arms: "point", sweat: 0, blush: 0 }, 0);
      pose("#cD", { eyes: "norm", mouth: "flat", arms: "shrug", sweat: 1, blush: 0 }, 0);
      pose("#cE", { eyes: "norm", mouth: "flat", arms: "scratch", sweat: 1, blush: 0 }, 0);
      pose("#cF", { eyes: "norm", mouth: "flat", arms: "shrug", sweat: 0, blush: 0 }, 0);
      pose("#cG", { eyes: "norm", mouth: "smile", arms: "point", sweat: 0, blush: 0 }, 0);''', 1)

# ---------- 9. timelines ----------
tl_new = '''      // ===== sA =====
      a = T[2];
      tagIn("#tAa", a + 0.15);
      popIn("#micA", a + 0.5); popIn("#plA", a + 0.9); charIn("#cAl", a + 0.7);
      popIn("#bkA", a + 1.6); popIn("#prA", a + 2.0); charIn("#cAr", a + 1.8);
      popIn("#neA", a + 3.2);
      tl.to("#neA", { scale: 1.12, duration: 0.4, yoyo: true, repeat: 5, ease: "sine.inOut", transformOrigin: "50% 50%" }, a + 3.7);
      pose("#cAl", { eyes: "happy", mouth: "smile", arms: "point" }, a + 0.9);
      pose("#cAr", { eyes: "norm", mouth: "flat", arms: "point" }, a + 3.2);

      // ===== sB =====
      a = T[5];
      tagIn("#tBa", a + 0.15);
      popIn("#magB", a + 0.5); popIn("#pmB", a + 0.8);
      tl.from("#arB", { x: -40, opacity: 0, duration: 0.3 }, a + 1.5);
      popIn("#cenB", a + 1.9); popIn("#pcB", a + 2.2);
      popIn("#qB", a + 3.6);
      tl.to("#qB", { y: -14, duration: 0.6, yoyo: true, repeat: 5, ease: "sine.inOut" }, a + 4.0);
      popIn("#puB", a + 4.6); charIn("#cB", a + 1.0);

      // ===== sC =====
      a = T[8];
      tagIn("#tCa", a + 0.15);
      charIn("#cCl", a + 0.4); charIn("#cCr", a + 0.6); popIn("#lbC", a + 0.9); popIn("#rbC", a + 1.0);
      tl.from("#bCl", { scale: 0, opacity: 0, duration: 0.45, ease: "back.out(2.4)", transformOrigin: "20% 100%" }, a + 2.0);
      tl.from("#bCr", { scale: 0, opacity: 0, duration: 0.45, ease: "back.out(2.4)", transformOrigin: "80% 100%" }, a + 3.6);
      pose("#cCr", { eyes: "happy", mouth: "smile", arms: "point" }, a + 3.6);
      popIn("#pnC", a + 5.0);

      // ===== sD =====
      a = T[9];
      tagIn("#tDa", a + 0.15);
      ["#dm1", "#dm2", "#dm3", "#dm4"].forEach(function (d, k) { popIn(d, a + 0.4 + k * 0.15); });
      popIn("#dl1", a + 1.0); popIn("#dl2", a + 1.3);
      ["#dm1", "#dm2", "#dm3", "#dm4"].forEach(function (d, k) { tl.to(d, { rotation: 80, duration: 0.35, ease: "power2.in" }, a + 2.4 + k * 0.4); });
      popIn("#dl3", a + 3.2); popIn("#dl4", a + 4.0);
      popIn("#opD", a + 5.4);

      // ===== sE =====
      a = T[10];
      tagIn("#tEa", a + 0.15);
      popIn("#calE", a + 0.5); charIn("#cE", a + 1.0);
      tl.to("#calE", { rotation: -3, duration: 0.5, yoyo: true, repeat: 3, ease: "sine.inOut", transformOrigin: "50% 50%" }, a + 1.5);
      popIn("#qE", a + 3.6); popIn("#pE", a + 4.6);
      tl.to("#qE", { y: -14, duration: 0.6, yoyo: true, repeat: 5, ease: "sine.inOut" }, a + 4.0);

      // ===== sF =====
      a = T[11];
      tagIn("#tFa", a + 0.15);
      popIn("#f1", a + 1.4); popIn("#g1", a + 2.0);
      popIn("#f2", a + 2.8); popIn("#g2", a + 3.4);
      popIn("#f3", a + 4.4); popIn("#g3", a + 5.0);
      popIn("#nF", a + 6.0);

      // ===== sG =====
      a = T[12];
      tagIn("#tGa", a + 0.15);
      tl.from("#rG1", { x: -300, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 1.4);
      tl.from("#rG2", { x: -300, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 2.6);
      tl.from("#rG3", { x: -300, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 3.8);
      charIn("#cG", a + 0.8);

'''
mk = '      // ===== S6 ====='
assert mk in b
b = b.replace(mk, tl_new + mk, 1)

# ---------- 10. sfx events ----------
ev = '''# new scenes
add(T[2]+.3,whoosh(.4),.1)
for o in (.5,.9,1.6,2.0): add(T[2]+o,pop(),.12)
add(T[2]+3.2,thud(),.4); add(T[2]+3.2,errtone(),.12)
add(T[5]+.5,pop(),.1); add(T[5]+.8,pop(),.1); add(T[5]+1.5,whoosh(.3),.1); add(T[5]+1.9,pop(),.1); add(T[5]+2.2,pop(),.1)
add(T[5]+3.6,pop(),.12); add(T[5]+3.6,ding(660),.12); add(T[5]+4.6,pop(),.12)
for o in (.4,.9,1.0,2.0,3.6): add(T[8]+o,pop(),.1)
add(T[8]+2.0,buzz(.12,180),.14); add(T[8]+3.6,ding(523),.12); add(T[8]+5.0,pop(),.1)
for k in range(4): add(T[9]+.4+k*.15,pop(),.08)
add(T[9]+1.0,pop(),.1); add(T[9]+1.3,pop(),.1)
for k in range(4): add(T[9]+2.4+k*.4,thud(),.3); add(T[9]+2.4+k*.4,whoosh(.25),.1)
add(T[9]+3.2,pop(),.1); add(T[9]+4.0,errtone(),.14); add(T[9]+5.4,ding(784),.14)
add(T[10]+.5,pop(),.12); add(T[10]+1.0,whoosh(.4),.1); add(T[10]+3.6,pop(),.12); add(T[10]+3.6,ding(660),.12); add(T[10]+4.6,thud(),.3); add(T[10]+4.6,errtone(),.12)
add(T[11]+1.4,pop(),.12); add(T[11]+1.4,ding(1046),.14); add(T[11]+2.8,pop(),.12); add(T[11]+3.4,ding(660),.1); add(T[11]+4.4,pop(),.12); add(T[11]+5.0,errtone(),.14); add(T[11]+6.0,pop(),.1)
for o in (1.4,2.6,3.8): add(T[12]+o,whoosh(.3),.1); add(T[12]+o+.2,pop(),.1)
add(T[12]+.8,pop(),.1)
add(T[14]+2.4,whoosh(.3),.1)

'''
events_mk = '# S7\n'
assert events_mk in b
b = b.replace(events_mk, ev + events_mk, 1)
b = b.replace("range(1,8): add(T[i]-.25", "range(1,15): add(T[i]-.25")
b = b.replace("for i in range(1,8): add(T[i]-.25,whoosh(.45),.1)", "for i in range(1,15): add(T[i]-.25,whoosh(.45),.1)")
b = b.replace("for s in range(1,8): add(T[s]+.15,pop(),.12)", "for s in range(1,15): add(T[s]+.15,pop(),.12)")
b = b.replace("replace('for i in range(7):', 'for i in range(8):')", "replace('for i in range(7):', 'for i in range(15):')")
b = b.replace("replace('for i in range(7):', 'for i in range(8):')", "replace('for i in range(7):', 'for i in range(15):')")
(ROOT / 'build.py').write_text(b, encoding='utf-8')

# ---------- voices ----------
LINES = [
    "จะเกิดอะไรขึ้น ถ้าสหรัฐฯ ใช้นิวเคลียร์ โจมตีอิหร่าน",
    "ข่าวนี้มาจากโพสต์ของ ทัคเกอร์ คาร์ลสัน ที่อ้างว่า รัฐบาลทรัมป์ อาจพิจารณาเรื่องนี้",
    "ต้องแยกให้ออก คาร์ลสันเป็นผู้ดำเนินรายการ และนักวิจารณ์การเมือง ไม่ใช่โฆษกรัฐบาล คำเตือนของเขา จึงไม่เท่ากับประกาศทางการ",
    "เป้าหมายที่เขาอ้างถึง คือฐานใต้ภูเขา ลึกราวเก้าสิบเมตร อาวุธทั่วไปอาจเอาไม่อยู่",
    "ตามคำอ้าง ระเบิดทั่วไปที่ตกลงไป อาจยังไปไม่ถึงชั้นล่างสุด",
    "เขาอ้างว่า ข่าวกรองอิสราเอลเชื่อว่า อิหร่านกลับมาเสริมสมรรถนะยูเรเนียมที่นั่น แต่เรื่องกิจกรรมข้างใน ยังต้องตรวจสอบเพิ่มเติม",
    "แต่ตอนนี้ ยืนยันได้แค่ว่า มีคนออกมาเตือน ฝั่งสหรัฐฯ ยังไม่ประกาศอะไร",
    "ที่มีรายงานจริง คือทรัมป์ขู่โจมตี ถ้าการเจรจาไม่สำเร็จ",
    "นอกจากนั้น มีรายงานว่าทรัมป์ ตอบโต้เนทันยาฮูต่อสาธารณะ เรื่องข้อมูลข่าวกรองของอิหร่าน ว่าไม่จำเป็นต้องมีใครมาบอก",
    "คาร์ลสันยังเตือนว่า ถ้าสหรัฐฯ ใช้ก่อน จะเป็นบรรทัดฐานอันตราย และอาจลุกลามเป็นสงครามโลก แต่นี่คือความเห็นและการคาดการณ์ของเขา ไม่ใช่ข้อเท็จจริง",
    "เขายังอ้างว่า ทรัมป์ฟังฝ่ายที่อยากเจรจา และอาจตัดสินใจภายในวันที่เจ็ดพฤศจิกายน แต่ไม่มีหลักฐานสาธารณะรองรับกำหนดเวลานี้",
    "ลองคิดเป็นสามทางสมมติ ถ้าเจรจาได้ ตลาดน่าจะสงบ ถ้าขู่กันต่อ ราคาพลังงานอาจผันผวน ถ้าเกิดการโจมตีจริง ผลกระทบอาจแรงกว่านั้นมาก",
    "สำหรับตลาดการเงิน ต้องจับตาสามอย่าง คือราคาพลังงาน เส้นทางขนส่ง และความผันผวนของสินทรัพย์",
    "ถึงยังไม่เกิด แต่ข่าวแบบนี้ก็กระทบถึงไทย เพราะเรานำเข้าน้ำมันเป็นส่วนใหญ่ น้ำมันขึ้น ค่าขนส่งขึ้น ของก็แพงตาม",
    "ก่อนแชร์ ถามตัวเองสามข้อ ใครพูด มีหลักฐานไหม และมีแหล่งอิสระยืนยันหรือยัง",
]
v = (ROOT / 'voices.py').read_text(encoding='utf-8')
a = v.index('LINES=[')
z = v.index(']\n', a) + 2
body = 'LINES=[\n' + ''.join('"%s",\n' % s for s in LINES) + ']\n'
(ROOT / 'voices.py').write_text(v[:a] + body + v[z:], encoding='utf-8')
print('patched', len(LINES))
