import math, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
b = (ROOT / 'build.py').read_text(encoding='utf-8')

# 1. timings
b = b.replace('T = [0, 4.6, 11.0, 17.6, 23.3, 28.2, 36.6, 41.4]', 'T = [0, 4.6, 11.0, 17.6, 23.8, 29.5, 34.4, 42.8, 47.6]')


def shift(text):
    return re.sub(r'T\[(\d)\]', lambda m: 'T[%d]' % (int(m.group(1)) + (1 if int(m.group(1)) >= 3 else 0)), text)


# 2. shift T indices in timeline + mix events
a = b.index('      // ===== S2 =====')
z = b.index('      window.__timelines["main"] = tl;')
b = b[:a] + shift(b[a:z]) + b[z:]
a = b.index("events = '''")
z = b.index("(ROOT / 'mix.py').write_text")
b = b[:a] + shift(b[a:z]) + b[z:]

# 3. remove bomb/x from S3 markup + timeline
b = b.replace('''        <div id="bomb3" class="ic" data-icon="bomb" style="left: 340px; top: 430px; width: 130px; height: 130px"></div>
        <div id="x3" class="stamp" style="left: 480px; top: 800px; width: 110px; height: 110px"></div>
''', '')
for line in [
    '      tl.from("#bomb3", { y: -300, opacity: 0, duration: 0.6, ease: "power2.in" }, a + 3.3);\n',
    '      tl.to("#bomb3", { y: "+=40", rotation: 25, duration: 0.15, ease: "power2.out", transformOrigin: "50% 50%" }, a + 3.9);\n',
    '      popIn("#x3", a + 4.1);\n',
    '      tl.to("#bomb3", { x: -120, y: "+=200", opacity: 0, duration: 0.5, ease: "power1.in" }, a + 4.3);\n',
]:
    assert line in b, line
    b = b.replace(line, '')
b = b.replace('popIn("#n3", a + 4.8);', 'popIn("#n3", a + 3.4);')
b = b.replace('add(T[2]+3.3,whoosh(.6),.2); add(T[2]+3.9,thud(),.5); add(T[2]+4.1,errtone(),.16); add(T[2]+4.8,pop(),.1)', 'add(T[2]+3.4,pop(),.1)')

# 4. S3b markup
star = ''
pts = []
for i in range(32):
    r = 230 if i % 2 == 0 else 120
    ang = math.pi * 2 * i / 32
    pts.append('%.0f,%.0f' % (250 + r * math.cos(ang), 200 + r * math.sin(ang)))
star = ' '.join(pts)
debris = ''.join('<div class="deb abs" id="deb%d" style="left: 520px; top: 150px; width: %dpx; height: %dpx; background: %s; border: 4px solid #1e1e24; transform: rotate(%ddeg)"></div>' % (i, 26 + (i % 3) * 8, 22 + (i % 2) * 10, ['#c9b79a', '#a8a1a8', '#6d6a78'][i % 3], i * 40) for i in range(10))
s3b = '''      <!-- S3b : cutaway, bomb, boom -->
      <div id="s3b" class="scene">
        <div class="tags"><div id="t3b" class="tag">ตามคำอ้าง <r>ลงไปใต้ภูเขา</r></div></div>
        <div id="cut" class="abs" style="left: 0; top: 420px; width: 1080px; height: 1700px">
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
            <svg class="abs" style="left: 0; top: 0; width: 500px; height: 400px" viewBox="0 0 500 400"><polygon points="''' + star + '''" fill="#ffd23f" stroke="#1e1e24" stroke-width="8" stroke-linejoin="round"/><polygon points="''' + ' '.join('%.0f,%.0f' % (250 + (150 if i % 2 == 0 else 80) * math.cos(math.pi * 2 * i / 32), 200 + (150 if i % 2 == 0 else 80) * math.sin(math.pi * 2 * i / 32)) for i in range(32)) + '''" fill="#E0243A"/></svg>
            <div class="abs" style="left: 0; top: 112px; width: 500px; text-align: center; font-size: 150px; font-weight: 800; color: #fff; -webkit-text-stroke: 16px #1e1e24; paint-order: stroke fill; transform: rotate(-8deg)">ตูม!</div>
          </div>
          <svg id="wave" class="abs" style="left: 0; top: 0; width: 1080px; height: 400px; opacity: 0" viewBox="0 0 1080 400"><circle cx="540" cy="172" r="120" fill="none" stroke="#fff" stroke-width="14"/><circle cx="540" cy="172" r="190" fill="none" stroke="#ffd23f" stroke-width="9"/></svg>
          ''' + debris + '''
        </div>
        <div id="bf" class="abs" style="inset: 0; background: #fff; opacity: 0"></div>
        <div id="n3b" class="pill abs" style="left: 290px; top: 1400px; font-size: 36px; background: #ffd23f; z-index: 20">ภาพจำลอง ตามคำอ้างของ Carlson</div>
        <svg class="gline" viewBox="0 0 1080 30" style="display:none"></svg>
      </div>

'''
b = b.replace('      <!-- S4 -->', s3b + '      <!-- S4 -->', 1)

# 5. captions: rename k4..k7 -> k5..k8, add new k4
for old in (7, 6, 5, 4):
    b = b.replace('id="k%d"' % old, 'id="k%d"' % (old + 1))
b = b.replace('        <div class="cap" id="k5">ยืนยันได้แค่ว่า', '        <div class="cap" id="k4">ตามคำอ้าง ระเบิดทั่วไป [อาจไปไม่ถึง] ชั้นล่างสุด</div>\n        <div class="cap" id="k5">ยืนยันได้แค่ว่า', 1)

# 6. SC / loops
b = b.replace('var SC = ["#s1", "#s2", "#s3", "#s4", "#s5", "#s6", "#s7"];', 'var SC = ["#s1", "#s2", "#s3", "#s3b", "#s4", "#s5", "#s6", "#s7"];')
b = b.replace('for (var i = 1; i < 7; i++) crossTo', 'for (var i = 1; i < 8; i++) crossTo')
b = b.replace('for (var j = 0; j < 7; j++) caption', 'for (var j = 0; j < 8; j++) caption')

# 7. S3b timeline (inserted before S4 block)
tl3b = '''      // ===== S3b : cutaway, bomb falls, boom, pan down =====
      a = T[3];
      tagIn("#t3b", a + 0.15);
      tl.from("#cut", { y: 120, opacity: 0, duration: 0.5, ease: "power3.out" }, a + 0.3);
      tl.from("#bomb3b", { y: -420, duration: 0.85, ease: "power2.in" }, a + 1.0);
      tl.set("#bomb3b", { opacity: 0 }, a + 1.85);
      tl.fromTo("#bf", { opacity: 0 }, { opacity: 0.95, duration: 0.05, ease: "none" }, a + 1.85);
      tl.to("#bf", { opacity: 0, duration: 0.35, ease: "power2.out" }, a + 1.92);
      tl.fromTo("#boomfx", { opacity: 1, scale: 0.2, rotation: -20 }, { scale: 1.25, rotation: 0, duration: 0.3, ease: "back.out(2.5)", transformOrigin: "50% 60%" }, a + 1.85);
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

'''
b = b.replace('      // ===== S4 =====', tl3b + '      // ===== S4 =====', 1)

# 8. mix events for S3b + loops
mix3b = '''# S3b: whistle, boom, rumble, crack
def whistle(l=.9):
    x = tt(l); f = 2200 - 1500 * (x / l)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (x / l) * .6
def rumble(l=1.6):
    x = tt(l); n0 = rng.normal(0, 1, len(x)); k = np.ones(400) / 400
    return np.convolve(n0, k, mode='same') * 6 * np.exp(-x * 1.8)
add(T[3]+.3,whoosh(.4),.1); add(T[3]+.15,pop(),.12)
add(T[3]+1.0,whistle(.85),.22)
add(T[3]+1.85,boom(),.6); add(T[3]+1.85,static(.35),.35); add(T[3]+1.85,rumble(1.6),.5)
for k in range(8): add(T[3]+2.0+k*.07,tick(300+k*80),.12)
add(T[3]+2.2,zap(),.15); add(T[3]+2.7,whoosh(.9),.2)
add(T[3]+3.4,pop(),.12); add(T[3]+3.9,pop(),.12); add(T[3]+3.9,errtone(),.14)
'''
b = b.replace("# S4\n", mix3b + "# S4\n", 1) if "# S4\n" in b else b
b = b.replace('for i in range(1,7): add(T[i]-.25,whoosh(.45),.1)', 'for i in range(1,8): add(T[i]-.25,whoosh(.45),.1)')
b = b.replace('for s in range(1,7): add(T[s]+.15,pop(),.12)', 'for s in range(1,8): add(T[s]+.15,pop(),.12)')
b = b.replace("head_m = m[:m.index('# scene whooshes')]", "head_m = m[:m.index('# scene whooshes')].replace('for i in range(7):', 'for i in range(8):')")
(ROOT / 'build.py').write_text(b, encoding='utf-8')

# voices
v = (ROOT / 'voices.py').read_text(encoding='utf-8')
v = v.replace('"แต่ตอนนี้ ยืนยันได้แค่ว่า', '"ตามคำอ้าง ระเบิดทั่วไปที่ตกลงไป อาจยังไปไม่ถึงชั้นล่างสุด",\n"แต่ตอนนี้ ยืนยันได้แค่ว่า', 1)
(ROOT / 'voices.py').write_text(v, encoding='utf-8')
print('patched')
