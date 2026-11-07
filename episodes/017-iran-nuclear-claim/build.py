"""Builds index.html and mix.py for episode 017 from the 016 stickman engine."""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = (ROOT.parent / '016-cyber-war' / 'index.html').read_text(encoding='utf-8').split('\n')
L = lambda a, b: '\n'.join(SRC[a - 1:b])  # 1-based inclusive

import json as _json
_vd = _json.loads((ROOT / 'voice-durations.json').read_text())
_floor = [4.6, 6.4, 0, 6.6, 6.2, 0, 5.7, 4.9, 0, 0, 0, 0, 0, 8.4, 5.4]
T = [0.0]
for _d, _f in zip(_vd, _floor):
    T.append(round(T[-1] + max(round(_d + 1.2, 1), _f), 1))
TOTAL = T[-1]

head = L(1, 49).replace('<title>', '<title>')
# extra css
head = head.replace('      .stamp {', '''      .card { position: absolute; background: #fff; border: 6px solid var(--ink); border-radius: 30px; box-shadow: 0 8px 0 rgba(30,30,36,.15); }
      .row { position: absolute; display: flex; align-items: center; gap: 22px; }
      .row .stamp { position: relative; flex: none; }
      .stamp {''', 1)

scenes = '''    <div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="@@D@@">

      <div id="hook"><div class="lab">ข่าวด่วน?</div><div id="hrad" class="ic" data-icon="rad" style="left: 270px; top: 290px; width: 540px; height: 540px"></div><div class="chip" id="hc1" style="top: 850px; transform: rotate(-3deg)">Carlson อ้าง</div><div class="chip" id="hc2" style="top: 990px; transform: rotate(2deg)">ยังไม่ยืนยัน ?</div><div class="chip" id="hc3" style="top: 1130px; transform: rotate(-2deg)">ยังไม่มีประกาศ</div><svg id="hmt" class="abs" style="left: 0; top: 1300px; width: 1080px; height: 360px" viewBox="0 0 1080 360"><path d="M0,360 L0,230 L120,150 L220,210 L380,60 L520,190 L640,120 L780,220 L900,110 L1080,230 L1080,360Z" fill="#1b1d2e" stroke="#333650" stroke-width="5"/></svg><div class="flash" id="hf"></div></div>

      <!-- S1 -->
      <div id="s1" class="scene">
        <div class="tags"><div id="t1a" class="tag">จะเกิดอะไรขึ้นถ้า</div><div id="t1b" class="tag"><r>สหรัฐฯ ใช้นิวเคลียร์</r></div></div>
        <div id="c1" class="char" data-kind="me" style="left: 80px; top: 760px"></div>
        <div id="rad1" class="ic" data-icon="rad" style="left: 580px; top: 780px; width: 360px; height: 360px"></div>
        <div id="p1" class="pill red abs" style="left: 620px; top: 1170px">ข่าวด่วน ?</div>
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- S2 -->
      <div id="s2" class="scene">
        <div class="tags"><div id="t2a" class="tag">ที่มาของข่าว</div></div>
        <div id="card2" class="card" style="left: 80px; top: 470px; width: 920px; height: 330px">
          <div class="abs" style="left: 30px; top: 28px; width: 86px; height: 86px; border-radius: 50%; background: #1e1e24; color: #fff; font-size: 52px; font-weight: 800; text-align: center; line-height: 86px">X</div>
          <div class="abs" style="left: 136px; top: 24px; font-size: 44px; font-weight: 800; color: #1e1e24">Tucker Carlson</div>
          <div class="abs" style="left: 136px; top: 78px; font-size: 30px; font-weight: 600; color: #777">โพสต์บน X (ตามที่สื่อรายงาน)</div>
          <div class="abs" style="left: 30px; top: 140px; width: 860px; font-size: 44px; font-weight: 800; color: #1e1e24; line-height: 1.3">อ้างว่ารัฐบาลทรัมป์ <span style="color: var(--red)">อาจเข้าใกล้</span> การใช้นิวเคลียร์กับอิหร่าน</div>
        </div>
        <div id="u2" class="pill abs" style="left: 250px; top: 850px; background: #ffd23f; font-size: 50px">คำอ้าง · ยังไม่ยืนยัน</div>
        <div id="c2" class="char" data-kind="me" style="left: 90px; top: 900px; width: 280px; height: 480px"></div>
        <div id="q2" class="mark" style="left: 470px; top: 940px; font-size: 200px">?</div>
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- sA : who is Carlson -->
      <div id="sA" class="scene">
        <div class="tags"><div id="tAa" class="tag">คำเตือน <r>≠</r> ประกาศ</div></div>
        <div id="micA" class="ic" data-icon="mic" style="left: 90px; top: 520px; width: 200px; height: 200px"></div>
        <div id="bkA" class="ic" data-icon="bank" style="left: 700px; top: 500px; width: 280px; height: 280px"></div>
        <div id="neA" class="mark" style="left: 440px; top: 540px; font-size: 230px">≠</div>
        <div id="plA" class="pill abs" style="left: 60px; top: 760px; font-size: 38px">นักวิจารณ์ / พิธีกร</div>
        <div id="prA" class="pill abs" style="left: 700px; top: 800px; font-size: 38px">รัฐบาลสหรัฐฯ</div>
        <div id="cAl" class="char" data-kind="me" style="left: 90px; top: 880px; width: 280px; height: 480px"></div>
        <div id="cAr" class="char" data-kind="biz" style="left: 700px; top: 880px; width: 280px; height: 480px"></div>
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- S3 -->
      <div id="s3" class="scene">
        <div class="tags"><div id="t3a" class="tag">เป้าหมายที่เขาอ้างถึง</div></div>
        <svg id="mt3" class="abs" style="left: 20px; top: 680px; width: 800px; height: 670px" viewBox="0 0 800 670">
          <path d="M0,670 L400,40 L800,670Z" fill="#c9b79a" stroke="#1e1e24" stroke-width="7" stroke-linejoin="round"/>
          <path d="M400,40 L340,150 L400,130 L450,170 L430,100Z" fill="#fff" stroke="#1e1e24" stroke-width="5" stroke-linejoin="round"/>
          <rect x="320" y="470" width="160" height="90" rx="10" fill="#3a3f52" stroke="#1e1e24" stroke-width="7"/>
          <path d="M610,70 V500" stroke="#E0243A" stroke-width="7" stroke-dasharray="14 10"/>
          <path d="M592,92 L610,64 L628,92 M592,478 L610,506 L628,478" fill="none" stroke="#E0243A" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <div id="rad3" class="ic" data-icon="rad" style="left: 345px; top: 1155px; width: 110px; height: 110px"></div>
        <div id="p3a" class="pill abs" style="left: 60px; top: 610px; font-size: 40px">Pickaxe Mountain</div>
        <div id="p3b" class="pill red abs" style="left: 560px; top: 640px; font-size: 44px">ลึกราว 91 ม.</div>
        <div id="c3" class="char" data-kind="me" style="left: 790px; top: 890px; width: 260px; height: 450px"></div>
        <div id="n3" class="pill abs" style="left: 560px; top: 1380px; font-size: 38px; background: #ffd23f">ตามคำอ้างของ Carlson</div>
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- S3b : cutaway, bomb, boom -->
      <div id="s3b" class="scene">
        <div class="tags"><div id="t3b" class="tag">ตามคำอ้าง <r>ลงไปใต้ภูเขา</r></div></div>
        <div id="cutwin" class="abs" style="left: 0; top: 420px; width: 1080px; height: 1050px; clip-path: inset(-700px 0 0 0)"><div id="cut" class="abs" style="left: 0; top: 0; width: 1080px; height: 1700px">
          <svg class="abs" style="left: 0; top: 0; width: 1080px; height: 1700px" viewBox="0 0 1080 1700">
            <rect x="-10" y="170" width="1100" height="460" fill="#c9b79a" stroke="#1e1e24" stroke-width="7"/>
            <rect x="-10" y="630" width="1100" height="380" fill="#a8a1a8" stroke="#1e1e24" stroke-width="7"/>
            <rect x="-10" y="1010" width="1100" height="700" fill="#6d6a78" stroke="#1e1e24" stroke-width="7"/>
            <g fill="#1e1e24" opacity=".35"><circle cx="120" cy="300" r="7"/><circle cx="300" cy="420" r="9"/><circle cx="800" cy="340" r="8"/><circle cx="950" cy="520" r="7"/><circle cx="200" cy="760" r="9"/><circle cx="700" cy="820" r="8"/><circle cx="900" cy="930" r="9"/><circle cx="150" cy="1120" r="9"/><circle cx="880" cy="1180" r="8"/><circle cx="400" cy="1480" r="9"/><circle cx="760" cy="1520" r="8"/></g>
            <rect x="320" y="1180" width="440" height="180" rx="14" fill="#3a3f52" stroke="#1e1e24" stroke-width="7"/>
            <g fill="#cfd6e4" stroke="#1e1e24" stroke-width="5"><rect x="350" y="1215" width="36" height="110" rx="10"/><rect x="396" y="1215" width="36" height="110" rx="10"/><rect x="442" y="1215" width="36" height="110" rx="10"/></g>
            <path d="M560,1010 V1180" stroke="#1e1e24" stroke-width="7" stroke-dasharray="10 8"/>
            <path d="M60,170 V1180" stroke="#E0243A" stroke-width="7" stroke-dasharray="14 10"/>
            <path d="M42,196 L60,166 L78,196 M42,1154 L60,1184 L78,1154" fill="none" stroke="#E0243A" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
            <ellipse id="crater" cx="540" cy="172" rx="90" ry="26" fill="#3a2f28" stroke="#1e1e24" stroke-width="6"/>
            <path id="crack" d="M540,176 L520,260 L556,330 L516,410 L548,490 L526,560" fill="none" stroke="#1e1e24" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="460" stroke-dashoffset="460"/>
          </svg>
          <div id="rad3b" class="ic" data-icon="rad" style="left: 600px; top: 1215px; width: 110px; height: 110px"></div>
          <div id="d0" class="pill abs" style="left: 90px; top: 150px; font-size: 34px">0 ม.</div>
          <div id="d1" class="pill red abs" style="left: 90px; top: 1100px; font-size: 38px">91 ม.</div>
          <div id="e1" class="pill abs" style="left: 640px; top: 1075px; font-size: 38px; background: #ffd23f">ฐานใต้ภูเขา</div>
          <div id="e2" class="pill red abs" style="left: 600px; top: 640px; font-size: 46px">ยังไปไม่ถึง</div>
          <div id="bomb3b" class="ic" data-icon="bomb" style="left: 470px; top: 30px; width: 140px; height: 140px"></div>
          <div id="boomfx" class="abs" style="left: 290px; top: -80px; width: 500px; height: 400px; opacity: 0">
            <svg class="abs" style="left: 0; top: 0; width: 500px; height: 400px" viewBox="0 0 500 400"><polygon points="480,200 368,223 462,288 350,267 413,363 317,300 338,412 273,318 250,430 227,318 162,412 183,300 87,363 150,267 38,288 132,223 20,200 132,177 38,112 150,133 87,37 183,100 162,-12 227,82 250,-30 273,82 338,-12 317,100 413,37 350,133 462,112 368,177" fill="#ffd23f" stroke="#1e1e24" stroke-width="8" stroke-linejoin="round"/><polygon points="400,200 328,216 389,257 317,244 356,306 294,267 307,339 266,278 250,350 234,278 193,339 206,267 144,306 183,244 111,257 172,216 100,200 172,184 111,143 183,156 144,94 206,133 193,61 234,122 250,50 266,122 307,61 294,133 356,94 317,156 389,143 328,184" fill="#E0243A"/></svg>
            <div class="abs" style="left: 0; top: 112px; width: 500px; text-align: center; font-size: 150px; font-weight: 800; color: #fff; -webkit-text-stroke: 16px #1e1e24; paint-order: stroke fill; transform: rotate(-8deg)">ตูม!</div>
          </div>
          <svg id="wave" class="abs" style="left: 0; top: 0; width: 1080px; height: 400px; opacity: 0" viewBox="0 0 1080 400"><circle cx="540" cy="172" r="120" fill="none" stroke="#fff" stroke-width="14"/><circle cx="540" cy="172" r="190" fill="none" stroke="#ffd23f" stroke-width="9"/></svg>
          <div class="deb abs" id="deb0" style="left: 520px; top: 150px; width: 26px; height: 22px; background: #c9b79a; border: 4px solid #1e1e24; transform: rotate(0deg)"></div><div class="deb abs" id="deb1" style="left: 520px; top: 150px; width: 34px; height: 32px; background: #a8a1a8; border: 4px solid #1e1e24; transform: rotate(40deg)"></div><div class="deb abs" id="deb2" style="left: 520px; top: 150px; width: 42px; height: 22px; background: #6d6a78; border: 4px solid #1e1e24; transform: rotate(80deg)"></div><div class="deb abs" id="deb3" style="left: 520px; top: 150px; width: 26px; height: 32px; background: #c9b79a; border: 4px solid #1e1e24; transform: rotate(120deg)"></div><div class="deb abs" id="deb4" style="left: 520px; top: 150px; width: 34px; height: 22px; background: #a8a1a8; border: 4px solid #1e1e24; transform: rotate(160deg)"></div><div class="deb abs" id="deb5" style="left: 520px; top: 150px; width: 42px; height: 32px; background: #6d6a78; border: 4px solid #1e1e24; transform: rotate(200deg)"></div><div class="deb abs" id="deb6" style="left: 520px; top: 150px; width: 26px; height: 22px; background: #c9b79a; border: 4px solid #1e1e24; transform: rotate(240deg)"></div><div class="deb abs" id="deb7" style="left: 520px; top: 150px; width: 34px; height: 32px; background: #a8a1a8; border: 4px solid #1e1e24; transform: rotate(280deg)"></div><div class="deb abs" id="deb8" style="left: 520px; top: 150px; width: 42px; height: 22px; background: #6d6a78; border: 4px solid #1e1e24; transform: rotate(320deg)"></div><div class="deb abs" id="deb9" style="left: 520px; top: 150px; width: 26px; height: 32px; background: #c9b79a; border: 4px solid #1e1e24; transform: rotate(360deg)"></div>
        </div></div>
        <div id="bf" class="abs" style="inset: 0; background: #fff; opacity: 0"></div>
        <div id="n3b" class="pill abs" style="left: 290px; top: 1405px; font-size: 36px; background: #ffd23f; z-index: 20">ภาพจำลอง ตามคำอ้างของ Carlson</div>
        <svg class="gline" viewBox="0 0 1080 30" style="display:none"></svg>
      </div>

      <!-- sB : enrichment claim -->
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
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- S4 -->
      <div id="s4" class="scene">
        <div class="tags"><div id="t4a" class="tag">ตอนนี้ยืนยันได้แค่ไหน?</div></div>
        <div id="r4a" class="row" style="left: 70px; top: 520px"><div id="ok4a" class="stamp" style="width: 120px; height: 120px"></div><div class="pill" style="font-size: 50px">Carlson โพสต์เตือน</div></div>
        <div id="r4b" class="row" style="left: 70px; top: 710px"><div id="x4b" class="stamp" style="width: 120px; height: 120px"></div><div class="pill" style="font-size: 50px">สหรัฐฯ ประกาศใช้นิวเคลียร์</div></div>
        <div id="p4b" class="pill red abs" style="left: 220px; top: 850px; font-size: 46px">ยังไม่มี</div>
        <div id="c4" class="char" data-kind="me" style="left: 380px; top: 940px; width: 280px; height: 420px"></div>
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- S5 -->
      <div id="s5" class="scene">
        <div class="tags"><div id="t5a" class="tag">ที่มีรายงานจริง</div></div>
        <div id="lb5" class="pill abs" style="left: 120px; top: 760px; font-size: 38px">อิหร่าน</div>
        <div id="rb5" class="pill abs" style="left: 760px; top: 760px; font-size: 38px">สหรัฐฯ</div>
        <div id="c5l" class="char" data-kind="me" style="left: 60px; top: 850px; width: 300px; height: 500px"></div>
        <div id="c5r" class="char" data-kind="biz" style="left: 720px; top: 850px; width: 300px; height: 500px"></div>
        <div id="b5" class="bubble" style="left: 470px; top: 600px; background: #E0243A; color: #fff; font-size: 44px">ถ้าเจรจาไม่สำเร็จ<br>จะโจมตี</div>
        <div id="m5" class="mark" style="left: 150px; top: 600px; font-size: 150px">?</div>
        <div id="p5" class="pill red abs" style="left: 250px; top: 1390px; font-size: 40px; display: none">รายงาน</div>
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- sC : public disagreement -->
      <div id="sC" class="scene">
        <div class="tags"><div id="tCa" class="tag">ไม่ลงรอยกันต่อสาธารณะ</div></div>
        <div id="lbC" class="pill abs" style="left: 70px; top: 760px; font-size: 38px">เนทันยาฮู</div>
        <div id="rbC" class="pill abs" style="left: 760px; top: 760px; font-size: 38px">ทรัมป์</div>
        <div id="cCl" class="char" data-kind="me" style="left: 50px; top: 850px; width: 300px; height: 500px"></div>
        <div id="cCr" class="char" data-kind="biz" style="left: 730px; top: 850px; width: 300px; height: 500px"></div>
        <div id="bCl" class="bubble" style="left: 70px; top: 560px; font-size: 40px">ข่าวกรองน่ากังวล!</div>
        <div id="bCr" class="bubble" style="left: 560px; top: 560px; font-size: 40px; background: #ffd23f">รู้อยู่แล้ว</div>
        <div id="pnC" class="pill abs" style="left: 330px; top: 1000px; font-size: 40px">ตามรายงานของสื่อ</div>
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- sD : domino claim -->
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
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- sE : deadline -->
      <div id="sE" class="scene">
        <div class="tags"><div id="tEa" class="tag">กำหนดเวลาที่อ้าง</div></div>
        <div id="calE" class="ic" data-icon="cal" style="left: 250px; top: 480px; width: 580px; height: 580px"></div>
        <div id="qE" class="mark" style="left: 770px; top: 520px; font-size: 200px">?</div>
        <div id="pE" class="pill red abs" style="left: 250px; top: 1090px; font-size: 48px">ไม่มีหลักฐานสาธารณะ</div>
        <div id="cE" class="char" data-kind="me" style="left: 60px; top: 960px; width: 240px; height: 400px"></div>
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- sF : three scenarios -->
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
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- sG : markets watchlist -->
      <div id="sG" class="scene">
        <div class="tags"><div id="tGa" class="tag">ตลาดการเงินต้องจับตา</div></div>
        <div id="rG1" class="row" style="left: 80px; top: 520px"><div class="ic" data-icon="chart" style="position: relative; width: 150px; height: 150px"></div><div class="pill" style="font-size: 50px">ราคาพลังงาน</div></div>
        <div id="rG2" class="row" style="left: 80px; top: 710px"><div class="ic" data-icon="ship" style="position: relative; width: 150px; height: 150px"></div><div class="pill" style="font-size: 50px">เส้นทางขนส่ง</div></div>
        <div id="rG3" class="row" style="left: 80px; top: 900px"><div class="ic" data-icon="drum" style="position: relative; width: 150px; height: 150px"></div><div class="pill" style="font-size: 50px">ความผันผวนสินทรัพย์</div></div>
        <div id="cG" class="char" data-kind="me" style="left: 760px; top: 1050px; width: 240px; height: 310px"></div>
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- S6 -->
      <div id="s6" class="scene">
        <div class="tags"><div id="t6a" class="tag">แต่ไทยก็โดนด้วย</div></div>
        <div id="i6a" class="item" style="left: 50px; top: 520px"><div class="ic" data-icon="drum"></div><div class="pill">น้ำมัน</div></div>
        <div id="i6b" class="item" style="left: 420px; top: 520px"><div class="ic" data-icon="truck"></div><div class="pill">ค่าขนส่ง</div></div>
        <div id="i6c" class="item" style="left: 790px; top: 520px"><div class="ic" data-icon="basket"></div><div class="pill">ของกิน</div></div>
        <svg id="ar6a" class="abs" style="left: 290px; top: 600px; width: 130px; height: 80px" viewBox="0 0 130 80"><path d="M10,40 H100 M76,14 L106,40 L76,66" fill="none" stroke="#E0243A" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <svg id="ar6b" class="abs" style="left: 660px; top: 600px; width: 130px; height: 80px" viewBox="0 0 130 80"><path d="M10,40 H100 M76,14 L106,40 L76,66" fill="none" stroke="#E0243A" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <div id="u6a" class="pill red abs" style="left: 70px; top: 800px; font-size: 38px">↑ ขึ้น</div>
        <div id="u6b" class="pill red abs" style="left: 440px; top: 800px; font-size: 38px">↑ ขึ้น</div>
        <div id="u6c" class="pill red abs" style="left: 770px; top: 800px; font-size: 38px">↑ แพงขึ้น</div>
        <div id="n6" class="pill abs" style="left: 120px; top: 900px; font-size: 44px">ไทยนำเข้าน้ำมันเป็นส่วนใหญ่</div>
        <div id="c6" class="char" data-kind="me" style="left: 380px; top: 960px; width: 270px; height: 400px"></div>
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

      <!-- S7 -->
      <div id="s7" class="scene">
        <div class="tags"><div id="t7a" class="tag">ก่อนแชร์ ถามตัวเอง</div></div>
        <div id="r7a" class="row" style="left: 80px; top: 520px"><div class="pill" style="background: #ffd23f; font-size: 56px">1</div><div class="pill" style="font-size: 54px">ใครพูด ?</div></div>
        <div id="r7b" class="row" style="left: 80px; top: 650px"><div class="pill" style="background: #ffd23f; font-size: 56px">2</div><div class="pill" style="font-size: 54px">มีหลักฐานไหม ?</div></div>
        <div id="r7c" class="row" style="left: 80px; top: 780px"><div class="pill" style="background: #ffd23f; font-size: 56px">3</div><div class="pill" style="font-size: 50px">แหล่งอิสระยืนยันไหม ?</div></div>
        <div id="mag7" class="ic" data-icon="mag" style="left: 640px; top: 960px; width: 310px; height: 310px"></div>
        <div id="c7" class="char" data-kind="me" style="left: 170px; top: 960px; width: 300px; height: 420px"></div>
        <svg class="gline" viewBox="0 0 1080 30"><path d="M0,14 Q200,6 420,15 T820,13 T1080,16" fill="none" stroke="#1e1e24" stroke-width="5" stroke-linecap="round" opacity=".75"/></svg>
      </div>

'''.replace('@@D@@', str(TOTAL))

audio = '''      <div id="brand"><img src="assets/watermark.png" alt="">เล่าไม่รู้บ้าง...รู้บ้าง</div>

      <audio id="aMix" data-start="0" data-duration="@@D@@" data-track-index="2" src="soundtrack.wav" data-volume="1"></audio>

      <div class="caps">
        <div class="cap" id="k1">จะเกิดอะไรขึ้น ถ้า [สหรัฐฯ ใช้นิวเคลียร์] โจมตีอิหร่าน</div>
        <div class="cap" id="k2">โพสต์ของ [Carlson] อ้างว่ารัฐบาลทรัมป์ [อาจพิจารณา] เรื่องนี้</div>
        <div class="cap" id="k3">คาร์ลสัน [ไม่ใช่โฆษกรัฐบาล] คำเตือน [ไม่เท่ากับ] ประกาศทางการ</div>
        <div class="cap" id="k4">ฐานใต้ภูเขา ลึกราว [90 เมตร] อาวุธทั่วไป [อาจเอาไม่อยู่]</div>
        <div class="cap" id="k5">ตามคำอ้าง ระเบิดทั่วไป [อาจไปไม่ถึง] ชั้นล่างสุด</div>
        <div class="cap" id="k6">อ้างว่าข่าวกรองอิสราเอลเชื่อว่า [กลับมาเสริมสมรรถนะ] ยูเรเนียม แต่ [ยังต้องตรวจสอบ]</div>
        <div class="cap" id="k7">ยืนยันได้แค่ว่า [มีคนเตือน] สหรัฐฯ [ยังไม่ประกาศ]</div>
        <div class="cap" id="k8">ที่มีรายงาน คือ [ขู่โจมตี] ถ้าเจรจา [ไม่สำเร็จ]</div>
        <div class="cap" id="k9">ทรัมป์ [ตอบโต้เนทันยาฮู] ต่อสาธารณะ เรื่องข่าวกรองอิหร่าน</div>
        <div class="cap" id="k10">เขาเตือนว่าอาจลุกลามเป็น [สงครามโลก] แต่นี่คือ [ความเห็น] ไม่ใช่ข้อเท็จจริง</div>
        <div class="cap" id="k11">อ้างว่าอาจตัดสินใจ [ภายใน 7 พ.ย.] แต่ [ไม่มีหลักฐาน] รองรับ</div>
        <div class="cap" id="k12">ลองคิดสามทาง [เจรจาได้] [ขู่ต่อ] [โจมตีจริง] ผลต่อตลาดต่างกัน</div>
        <div class="cap" id="k13">ตลาดต้องจับตา [ราคาพลังงาน] [เส้นทางขนส่ง] และ [ความผันผวน]</div>
        <div class="cap" id="k14">ไทยนำเข้าน้ำมันเป็นส่วนใหญ่ [น้ำมันขึ้น] ค่าขนส่งขึ้น [ของแพง]</div>
        <div class="cap" id="k15">ก่อนแชร์ ถาม [ใครพูด] [มีหลักฐานไหม] และ [แหล่งอิสระ] ยืนยันไหม</div>
      </div>
    </div>

'''.replace('@@D@@', str(TOTAL))

def rad_paths():
    cx = cy = 100
    out = ''
    for k in range(3):
        a0 = math.radians(-90 + 120 * k - 30)
        a1 = math.radians(-90 + 120 * k + 30)
        r = 70
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        out += 'M%d,%d L%.1f,%.1f A%d,%d 0 0 1 %.1f,%.1f Z ' % (cx, cy, x0, y0, r, r, x1, y1)
    return out

new_icons = r"""
        rad: '<circle cx="100" cy="100" r="92" fill="#ffd23f" ' + W + '/><path d="RADPATH" fill="' + INK + '"/><circle cx="100" cy="100" r="14" fill="' + INK + '"/>',
        mag: '<circle cx="86" cy="86" r="56" fill="#cfe9f7" ' + W + '/><path d="M126,126 L182,182" stroke="' + INK + '" stroke-width="18" stroke-linecap="round"/><path d="M58,76 Q66,56 88,52" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/>',
        bomb: '<circle cx="96" cy="118" r="62" fill="#2b2b33" ' + W + '/><rect x="82" y="36" width="30" height="26" rx="6" fill="#555" ' + W + '/><path d="M112,44 Q138,28 150,12" fill="none" stroke="' + INK + '" stroke-width="7" stroke-linecap="round"/><path d="M150,0 L158,16 L142,16Z" fill="#ffd23f" stroke="' + INK + '" stroke-width="4"/><circle cx="74" cy="100" r="10" fill="#fff" opacity=".5"/>',
        drum: '<ellipse cx="100" cy="44" rx="56" ry="18" fill="#556070" ' + W + '/><path d="M44,44 V158 Q44,178 100,178 Q156,178 156,158 V44" fill="#2d3a4a" ' + W + '/><path d="M44,84 Q100,104 156,84 M44,128 Q100,148 156,128" fill="none" stroke="#9aa5b1" stroke-width="6"/><path d="M100,92 Q122,122 100,136 Q78,122 100,92Z" fill="#ffd23f" stroke="' + INK + '" stroke-width="4"/>',
        truck: '<rect x="10" y="50" width="106" height="84" rx="8" fill="#f5b83d" ' + W + '/><path d="M116,76 H156 L186,104 V134 H116Z" fill="#6bbce6" ' + W + '/><circle cx="56" cy="142" r="20" fill="' + INK + '"/><circle cx="150" cy="142" r="20" fill="' + INK + '"/><circle cx="56" cy="142" r="8" fill="#ccc"/><circle cx="150" cy="142" r="8" fill="#ccc"/>',
        basket: '<path d="M60,70 Q100,10 140,70" fill="none" ' + W + '/><path d="M26,76 H174 L154,170 H46Z" fill="#c9a15a" ' + W + '/><circle cx="70" cy="62" r="18" fill="#E0243A" ' + W + '/><circle cx="104" cy="54" r="18" fill="#7fcf7a" ' + W + '/><circle cx="136" cy="62" r="18" fill="#ffd23f" ' + W + '/>',
        mic: '<rect x="68" y="12" width="64" height="104" rx="32" fill="#9aa5b1" ' + W + '/><path d="M44,88 Q44,152 100,152 Q156,152 156,88" fill="none" ' + W + '/><path d="M100,152 V186 M66,186 H134" fill="none" ' + W + '/><path d="M80,44 H120 M80,66 H120" stroke="' + INK + '" stroke-width="5"/>',
        cent: '<rect x="14" y="150" width="172" height="26" rx="8" fill="#6d6a78" ' + W + '/><g fill="#cfd6e4" ' + W + '><rect x="26" y="40" width="40" height="112" rx="14"/><rect x="80" y="40" width="40" height="112" rx="14"/><rect x="134" y="40" width="40" height="112" rx="14"/></g>',
        cal: '<rect x="14" y="26" width="172" height="162" rx="16" fill="#fff" ' + W + '/><path d="M14,42 Q14,26 30,26 H170 Q186,26 186,42 V76 H14Z" fill="#E0243A" ' + W + '/><path d="M54,10 V40 M146,10 V40" fill="none" ' + W + '/><text x="100" y="158" font-family="Kanit" font-weight="800" font-size="76" fill="' + INK + '" text-anchor="middle">7</text><text x="100" y="64" font-family="Kanit" font-weight="800" font-size="30" fill="#fff" text-anchor="middle">พ.ย.</text>',
        chart: '<path d="M20,20 V176 H184" fill="none" ' + W + '/><path d="M34,140 L70,100 L100,126 L142,60 L170,36" fill="none" stroke="#E0243A" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/><path d="M150,34 H174 V58" fill="none" stroke="#E0243A" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>',
        ship: '<path d="M20,120 H180 L156,170 H44Z" fill="#E0243A" ' + W + '/><rect x="56" y="74" width="62" height="46" rx="6" fill="#fff" ' + W + '/><rect x="76" y="40" width="26" height="34" rx="5" fill="#f5b83d" ' + W + '/><g fill="#6bbce6" stroke="' + INK + '" stroke-width="4"><rect x="66" y="88" width="14" height="14"/><rect x="92" y="88" width="14" height="14"/></g><path d="M10,184 Q40,170 70,184 T130,184 T190,184" fill="none" stroke="#6bbce6" stroke-width="8" stroke-linecap="round"/>',
""".replace('RADPATH', rad_paths())

js_a = L(165, 236)
marker = "        wallet: '<rect"
assert marker in js_a
js_a = js_a.replace(marker, new_icons + marker, 1)
js_ic = L(237, 237) + '\n' + L(239, 240)
js_cap = L(263, 296)

script = '''    <script>
''' + js_a + '''
''' + js_ic + '''
      document.querySelectorAll(".stamp").forEach(function (el) { el.innerHTML = el.id.charAt(0) === "o" ? OK : XS; });
''' + js_cap + '''
      var T = @@T@@;
      var SC = ["#s1", "#s2", "#sA", "#s3", "#s3b", "#sB", "#s4", "#s5", "#sC", "#sD", "#sE", "#sF", "#sG", "#s6", "#s7"];
      for (var i = 1; i < 15; i++) crossTo(SC[i], SC[i - 1], T[i]);
      for (var j = 0; j < 15; j++) caption("#k" + (j + 1), T[j] + 0.3, T[j + 1] + 0.2);

      pose("#c1", { eyes: "happy", mouth: "smile", arms: "phone", blush: 1, sweat: 0 }, 0);
      pose("#c2", { eyes: "norm", mouth: "flat", arms: "chin", sweat: 0, blush: 0 }, 0);
      pose("#c3", { eyes: "shock", mouth: "o", arms: "point", sweat: 0, blush: 0 }, 0);
      pose("#c4", { eyes: "norm", mouth: "flat", arms: "scratch", sweat: 1, blush: 0 }, 0);
      pose("#c5l", { eyes: "sad", mouth: "frown", arms: "shrug", sweat: 1, blush: 0 }, 0);
      pose("#c5r", { eyes: "norm", mouth: "flat", arms: "point", sweat: 0, blush: 0 }, 0);
      pose("#c6", { eyes: "sad", mouth: "frown", arms: "shrug", sweat: 1, blush: 0 }, 0);
      pose("#c7", { eyes: "norm", mouth: "smile", arms: "point", sweat: 0, blush: 0 }, 0);
      pose("#cAl", { eyes: "norm", mouth: "smile", arms: "point", sweat: 0, blush: 0 }, 0);
      pose("#cAr", { eyes: "norm", mouth: "flat", arms: "down", sweat: 0, blush: 0 }, 0);
      pose("#cB", { eyes: "norm", mouth: "flat", arms: "chin", sweat: 1, blush: 0 }, 0);
      pose("#cCl", { eyes: "shock", mouth: "o", arms: "up", sweat: 1, blush: 0 }, 0);
      pose("#cCr", { eyes: "norm", mouth: "flat", arms: "point", sweat: 0, blush: 0 }, 0);
      pose("#cD", { eyes: "norm", mouth: "flat", arms: "shrug", sweat: 1, blush: 0 }, 0);
      pose("#cE", { eyes: "norm", mouth: "flat", arms: "scratch", sweat: 1, blush: 0 }, 0);
      pose("#cF", { eyes: "norm", mouth: "flat", arms: "shrug", sweat: 0, blush: 0 }, 0);
      pose("#cG", { eyes: "norm", mouth: "smile", arms: "point", sweat: 0, blush: 0 }, 0);

      // ===== S1 : hook 0-1.3s then scene =====
      tl.from("#hrad", { scale: 3.2, rotation: -90, opacity: 0, duration: 0.22, ease: "power4.out", transformOrigin: "50% 50%" }, 0.05);
      tl.from("#hook .lab", { y: -40, opacity: 0, duration: 0.2 }, 0.1);
      tl.from("#hmt", { y: 220, duration: 0.3, ease: "power3.out" }, 0.05);
      tl.to("#hrad", { scale: 1.08, duration: 0.12, yoyo: true, repeat: 7, ease: "sine.inOut", transformOrigin: "50% 50%" }, 0.3);
      tl.to("#hook", { x: 12, y: -8, duration: 0.04, yoyo: true, repeat: 25, ease: "none" }, 0.3);
      tl.from("#hc1", { scale: 2.6, opacity: 0, duration: 0.14, ease: "power4.out" }, 0.45);
      tl.from("#hc2", { scale: 2.6, opacity: 0, duration: 0.14, ease: "power4.out" }, 0.7);
      tl.from("#hc3", { scale: 2.6, opacity: 0, duration: 0.14, ease: "power4.out" }, 0.95);
      tl.fromTo("#hf", { opacity: 0 }, { opacity: 1, duration: 0.08, ease: "none" }, 1.18);
      tl.set("#hook", { display: "none" }, 1.3);
      tagIn("#t1a", 1.45); tagIn("#t1b", 1.75); charIn("#c1", 1.5); popIn("#rad1", 1.65);
      breathe("#c1", 2.0, 2.5);
      tl.to("#rad1", { rotation: 360, duration: 2.4, ease: "none", transformOrigin: "50% 50%" }, 2.0);
      pose("#c1", { eyes: "shock", mouth: "o", arms: "phone", blush: 0, sweat: 1 }, 2.5);
      popIn("#p1", 2.8);

      // ===== S2 =====
      var a = T[1];
      tagIn("#t2a", a + 0.15); tl.from("#card2", { y: 120, opacity: 0, duration: 0.5, ease: "back.out(1.4)" }, a + 0.4);
      charIn("#c2", a + 0.8);
      popIn("#u2", a + 3.0); popIn("#q2", a + 3.6);
      tl.to("#q2", { y: -16, duration: 0.7, yoyo: true, repeat: 3, ease: "sine.inOut" }, a + 4.1);
      pose("#c2", { eyes: "sad", mouth: "frown", arms: "chin", sweat: 1 }, a + 3.4);

      // ===== S3 =====
      a = T[3];
      tagIn("#t3a", a + 0.15);
      tl.from("#mt3", { y: 300, opacity: 0, duration: 0.6, ease: "power3.out" }, a + 0.3);
      popIn("#p3a", a + 0.9); popIn("#rad3", a + 1.3);
      tl.from("#p3b", { x: 80, opacity: 0, duration: 0.4, ease: "power2.out" }, a + 2.2);
      charIn("#c3", a + 0.8);
      popIn("#n3", a + 3.4);

      // ===== S3b : cutaway, bomb falls, boom, pan down =====
      a = T[4];
      tagIn("#t3b", a + 0.15);
      tl.from("#cut", { y: 120, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 0.3);
      tl.from("#bomb3b", { y: -420, duration: 0.85, ease: "power2.in" }, a + 1.0);
      tl.set("#bomb3b", { opacity: 0 }, a + 1.85);
      tl.fromTo("#bf", { opacity: 0 }, { opacity: 0.95, duration: 0.05, ease: "none" }, a + 1.85);
      tl.to("#bf", { opacity: 0, duration: 0.35, ease: "power2.out" }, a + 1.92);
      tl.fromTo("#boomfx", { opacity: 1, scale: 0.2, rotation: -20 }, { opacity: 1, scale: 1.25, rotation: 0, duration: 0.3, ease: "back.out(2.5)", transformOrigin: "50% 60%" }, a + 1.85);
      tl.to("#boomfx", { opacity: 0, duration: 0.3 }, a + 2.65);
      tl.fromTo("#wave", { opacity: 1, scale: 0.3, transformOrigin: "540px 172px" }, { scale: 3, opacity: 0, duration: 0.7, ease: "power2.out" }, a + 1.85);
      tl.from("#crater", { scaleX: 0, scaleY: 0, transformOrigin: "50% 50%", duration: 0.2 }, a + 1.9);
      for (var di = 0; di < 10; di++) {
        tl.fromTo("#deb" + di, { x: 0, y: 0, opacity: 1 }, { x: (di % 2 ? 1 : -1) * (120 + di * 28), y: -(180 + (di % 4) * 70), rotation: "+=300", duration: 0.55, ease: "power2.out" }, a + 1.88);
        tl.to("#deb" + di, { y: "+=380", opacity: 0, duration: 0.5, ease: "power2.in" }, a + 2.43);
      }
      tl.to("#cut", { x: 14, duration: 0.04, yoyo: true, repeat: 17, ease: "none" }, a + 1.9);
      tl.to("#crack", { strokeDashoffset: 0, duration: 1.0, ease: "power1.out" }, a + 2.0);
      tl.to("#cut", { y: -640, duration: 1.0, ease: "power2.inOut" }, a + 2.7);
      popIn("#e1", a + 3.4); popIn("#e2", a + 3.9);
      tl.to("#rad3b", { scale: 1.2, duration: 0.3, yoyo: true, repeat: 5, ease: "sine.inOut", transformOrigin: "50% 50%" }, a + 3.6);
      popIn("#n3b", a + 0.9);

      // ===== S4 =====
      a = T[6];
      tagIn("#t4a", a + 0.15);
      tl.from("#r4a", { x: -300, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 0.4);
      tl.from("#r4b", { x: -300, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 1.6);
      popIn("#p4b", a + 2.6); charIn("#c4", a + 1.0);
      pose("#c4", { eyes: "happy", mouth: "smile", arms: "up", sweat: 0 }, a + 0.9);
      pose("#c4", { eyes: "shock", mouth: "o", arms: "scratch", sweat: 1 }, a + 2.6);

      // ===== S5 =====
      a = T[7];
      tagIn("#t5a", a + 0.15);
      charIn("#c5l", a + 0.4); charIn("#c5r", a + 0.6); popIn("#lb5", a + 0.9); popIn("#rb5", a + 1.0);
      tl.from("#b5", { scale: 0, opacity: 0, duration: 0.45, ease: "back.out(2.4)", transformOrigin: "80% 100%" }, a + 1.4);
      tl.to("#b5", { rotation: -3, duration: 0.5, yoyo: true, repeat: 3, ease: "sine.inOut", transformOrigin: "50% 50%" }, a + 2.0);
      popIn("#m5", a + 2.3);
      pose("#c5r", { eyes: "happy", mouth: "smile", arms: "point" }, a + 1.4);
      pose("#c5l", { eyes: "shock", mouth: "o", arms: "up", sweat: 1 }, a + 2.3);

      // ===== sA =====
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

      // ===== S6 =====
      a = T[13];
      tagIn("#t6a", a + 0.15);
      popIn("#i6a", a + 0.6); popIn("#u6a", a + 1.1);
      tl.from("#ar6a", { x: -40, opacity: 0, duration: 0.3 }, a + 1.5);
      popIn("#i6b", a + 2.0); popIn("#u6b", a + 2.5);
      tl.from("#ar6b", { x: -40, opacity: 0, duration: 0.3 }, a + 2.9);
      popIn("#i6c", a + 3.4); popIn("#u6c", a + 3.9);
      tl.to(["#u6a", "#u6b", "#u6c"], { y: -10, duration: 0.5, yoyo: true, repeat: 5, ease: "sine.inOut" }, a + 4.4);
      charIn("#c6", a + 0.6); popIn("#n6", a + 2.0);

      // ===== S7 =====
      a = T[14];
      tagIn("#t7a", a + 0.15);
      tl.from("#r7a", { x: -300, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 0.5);
      tl.from("#r7b", { x: -300, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 1.4);
      tl.from("#r7c", { x: -300, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 2.4);
      charIn("#c7", a + 0.8); popIn("#mag7", a + 3.0);
      tl.to("#mag7", { rotation: 14, duration: 0.5, yoyo: true, repeat: 5, ease: "sine.inOut", transformOrigin: "50% 50%" }, a + 3.6);
      breathe("#c7", a + 1.5, 3);

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''.replace('@@T@@', str(T))

html = head + '\n' + scenes + audio + script
(ROOT / 'index.html').write_text(html, encoding='utf-8')

# ---------------- mix.py ----------------
m = (ROOT.parent / '016-cyber-war' / 'mix.py').read_text(encoding='utf-8')
m = m.replace('T=[0,4.6,9.9,15.3,21.2,27.8,34.5,40.5]', 'T=%s' % T)
head_m = m[:m.index('# scene whooshes')].replace('for i in range(7):', 'for i in range(15):')
tail_m = m[m.index('# music:'):]
events = '''# scene whooshes + tag pops
for i in range(1,15): add(T[i]-.25,whoosh(.45),.1)
for s in range(1,15): add(T[s]+.15,pop(),.12)
# S1 hook
def riser(l=1.15):
    x = tt(l); f = 80 + 900 * (x / l) ** 2
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (x / l) ** 1.5
add(0.0, boom(), .4); add(0.0, riser(1.15), .14)
for k in range(8): add(0.3 + k * .1, zap(), .06)
for o in (0.45, 0.7, 0.95): add(o, thud(), .55); add(o, ding(1200), .08); add(o, static(.18), .2)
add(1.18, whoosh(.3), .35); add(1.2, boom(), .3)
add(1.45, pop(), .12); add(1.75, pop(), .12); add(1.65, pop(), .1); add(2.5, buzz(.12, 110), .15); add(2.8, pop(), .14)
# S2
add(T[1]+.4,whoosh(.4),.12); add(T[1]+3.0,pop(),.14); add(T[1]+3.6,ding(660),.12); add(T[1]+3.6,pop(),.12)
# S3
add(T[3]+.3,whoosh(.5),.12); add(T[3]+.9,pop(),.1); add(T[3]+1.3,pop(),.1); add(T[3]+2.2,pop(),.1)
add(T[3]+3.4,pop(),.1)
# S3b: whistle, boom, rumble, crack
def whistle(l=.9):
    x = tt(l); f = 2200 - 1500 * (x / l)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (x / l) * .6
def rumble(l=1.6):
    x = tt(l); n0 = rng.normal(0, 1, len(x)); k = np.ones(400) / 400
    return np.convolve(n0, k, mode='same') * 6 * np.exp(-x * 1.8)
add(T[4]+.3,whoosh(.4),.1); add(T[4]+.15,pop(),.12)
add(T[4]+1.0,whistle(.85),.22)
add(T[4]+1.85,boom(),.6); add(T[4]+1.85,static(.35),.35); add(T[4]+1.85,rumble(1.6),.5)
for k in range(8): add(T[4]+2.0+k*.07,tick(300+k*80),.12)
add(T[4]+2.2,zap(),.15); add(T[4]+2.7,whoosh(.9),.2)
add(T[4]+3.4,pop(),.12); add(T[4]+3.9,pop(),.12); add(T[4]+3.9,errtone(),.14)
# S4
add(T[6]+.4,whoosh(.4),.1); add(T[6]+.9,ding(1046.5),.16); add(T[6]+1.6,whoosh(.4),.1); add(T[6]+2.0,thud(),.35); add(T[6]+2.0,errtone(),.12); add(T[6]+2.6,pop(),.12)
# S5
add(T[7]+.4,pop(),.1); add(T[7]+.6,pop(),.1); add(T[7]+1.4,pop(),.14); add(T[7]+1.4,sweep_up(.4),.08); add(T[7]+2.3,ding(523.25),.12)
# S6
for o,f in [(.6,392.0),(2.0,440.0),(3.4,494.0)]: add(T[13]+o,pop(),.12); add(T[13]+o+.5,ding(f),.1)
for o in (1.1,2.5,3.9): add(T[13]+o,tick(1600),.1); add(T[13]+o,pop(),.1)
for o in (1.5,2.9): add(T[13]+o,whoosh(.25),.1)
add(T[13]+4.8,pop(),.1); add(T[13]+5.2,pop(),.1)
# new scenes
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

# S7
add(T[14]+.5,whoosh(.4),.1); add(T[14]+1.4,whoosh(.4),.1); add(T[14]+1.8,pop(),.12); add(T[14]+2.4,chime(784),.1); add(T[14]+3.0,chime(988),.1)

'''
(ROOT / 'mix.py').write_text(head_m + events + tail_m, encoding='utf-8')
print('built', TOTAL)
