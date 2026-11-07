import re
p = 'index.html'
s = open(p, encoding='utf-8').read()

# ---- CSS: replace old hook css
a = s.index('      #hook {')
b = s.index('      .stamp {')
css = """      #hook { position: absolute; inset: 0; z-index: 45; background: #0b0b12; overflow: hidden; }
      #hook .lab { position: absolute; left: 0; top: 190px; width: 1080px; text-align: center; font-size: 64px; font-weight: 800; color: #9aa0b4; }
      #hook .cnt { position: absolute; left: 0; top: 250px; width: 1080px; text-align: center; font-size: 400px; line-height: 1.05; font-weight: 800; color: #fff; font-variant-numeric: tabular-nums; }
      #hook .cnt.r { color: #ff3b52; mix-blend-mode: screen; }
      #hook .cnt.c { color: #20e0ff; mix-blend-mode: screen; }
      #hook .chip { position: absolute; left: 190px; width: 700px; padding: 8px 0 16px; border-radius: 26px; background: var(--red); border: 8px solid #fff; color: #fff; text-align: center; font-size: 84px; font-weight: 800; }
      #hook .flash { position: absolute; inset: 0; background: #fff; opacity: 0; }
"""
s = s[:a] + css + s[b:]

# ---- HTML: replace hook div
a = s.index('      <div id="hook">')
b = s.index('      <!-- S1 : wake up')
html = """      <div id="hook"><div class="lab">ระบบทั้งประเทศ</div><div class="cnt r" id="hr">100%</div><div class="cnt c" id="hc">100%</div><div class="cnt" id="hn">100%</div><div class="chip" id="hc1" style="top: 720px; transform: rotate(-3deg)">ธนาคาร ✗</div><div class="chip" id="hc2" style="top: 850px; transform: rotate(2deg)">ไฟฟ้า ✗</div><div class="chip" id="hc3" style="top: 980px; transform: rotate(-2deg)">อินเทอร์เน็ต ✗</div><svg id="hsky" class="abs" style="left: 0; top: 1100px; width: 1080px; height: 420px" viewBox="0 0 1080 420"></svg><div class="flash" id="hf"></div></div>

"""
s = s[:a] + html + s[b:]

# ---- skyline builder for hook
sky = """      (function () {
        var r = mulberry(11), x = 0, o = "";
        while (x < 1080) {
          var w = 70 + Math.round(r() * 60), h = 160 + Math.round(r() * 220);
          o += '<rect x="' + x + '" y="' + (420 - h) + '" width="' + (w - 8) + '" height="' + h + '" fill="#1b1d2e" stroke="#333650" stroke-width="4"/>';
          for (var wy = 420 - h + 18; wy < 400; wy += 30) for (var wx = x + 12; wx < x + w - 30; wx += 24) o += '<rect class="win" x="' + wx + '" y="' + wy + '" width="12" height="16" fill="#ffd23f"/>';
          x += w;
        }
        document.getElementById("hsky").innerHTML = o;
      })();
      document.querySelectorAll(".stamp")"""
s = s.replace('      document.querySelectorAll(".stamp")', sky, 1)

# ---- timeline: replace S1 block
a = s.index('      // ===== S1 =====')
b = s.index('      // ===== S2 =====')
tlcode = """      // ===== S1 =====
      // wow hook 0-1.5s: whole country 100% -> 0%, lights-out sweep, slam chips, flash cut
      var hk = { v: 100 };
      tl.from("#hook .cnt", { scale: 1.8, opacity: 0, duration: 0.2, ease: "power4.out", transformOrigin: "50% 50%" }, 0.05);
      tl.from("#hook .lab", { y: -40, opacity: 0, duration: 0.2 }, 0.1);
      tl.from("#hsky", { y: 160, duration: 0.25, ease: "power3.out" }, 0.05);
      tl.to(hk, { v: 0, duration: 0.9, ease: "power2.in", onUpdate: function () { var t = Math.round(hk.v) + "%"; document.getElementById("hn").textContent = t; document.getElementById("hr").textContent = t; document.getElementById("hc").textContent = t; } }, 0.25);
      tl.to("#hn", { color: "#ff3b52", duration: 0.1 }, 0.7);
      tl.to("#hr", { x: -14, duration: 0.04, yoyo: true, repeat: 23, ease: "none" }, 0.25);
      tl.to("#hc", { x: 14, duration: 0.05, yoyo: true, repeat: 17, ease: "none" }, 0.25);
      tl.to("#hsky .win", { opacity: 0.06, duration: 0.05, stagger: { each: 0.004, from: "start" } }, 0.3);
      tl.to("#hook", { x: 12, y: -8, duration: 0.04, yoyo: true, repeat: 25, ease: "none" }, 0.3);
      tl.from("#hc1", { scale: 2.6, opacity: 0, duration: 0.14, ease: "power4.out" }, 0.45);
      tl.from("#hc2", { scale: 2.6, opacity: 0, duration: 0.14, ease: "power4.out" }, 0.7);
      tl.from("#hc3", { scale: 2.6, opacity: 0, duration: 0.14, ease: "power4.out" }, 0.95);
      tl.fromTo("#hf", { opacity: 0 }, { opacity: 1, duration: 0.08, ease: "none" }, 1.18);
      tl.set("#hook", { display: "none" }, 1.3);
      tagIn("#t1a", 1.45); tagIn("#t1b", 1.75); charIn("#c1", 1.5); popIn("#ph1", 1.65);
      breathe("#c1", 2.0, 2.5);
      tl.to("#ph1", { rotation: -6, duration: 0.07, yoyo: true, repeat: 5, transformOrigin: "50% 50%" }, 2.1);
      tl.set("#ph1 .bars", { opacity: 0 }, 2.5);
      tl.set("#ph1 .nosig", { opacity: 1 }, 2.5);
      shake("#ph1", 2.5, 7);
      pose("#c1", { eyes: "shock", mouth: "o", arms: "phone", blush: 0, sweat: 1 }, 2.5);
      popIn("#p1", 2.8);

"""
s = s[:a] + tlcode + s[b:]
s = s.replace('popIn("#clk1", 1.2); popIn("#win1", 1.4);', 'popIn("#clk1", 1.7); popIn("#win1", 1.9);')
s = s.replace('tl.to("#clk1", { rotation: 8, duration: 0.06, yoyo: true, repeat: 9, transformOrigin: "50% 60%" }, 1.5);', 'tl.to("#clk1", { rotation: 8, duration: 0.06, yoyo: true, repeat: 9, transformOrigin: "50% 60%" }, 2.0);')
open(p, 'w', encoding='utf-8').write(s)

m = open('mix.py', encoding='utf-8').read()
a = m.index('# S1 hook')
b = m.index('# S2')
new = """# S1 wow hook: boom, long power-down, slams, flash
def riser(l=1.1):
    x = tt(l); f = 80 + 900 * (x / l) ** 2
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (x / l) ** 1.5
def longdown(l=1.0):
    x = tt(l); f = 1400 * np.exp(-x * 4.2) + 38
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 1.2)
add(0.0, boom(), .4); add(0.0, riser(1.15), .12)
add(0.25, longdown(1.0), .26)
for k in range(10): add(0.3 + k * .08, zap(), .07)
for o in (0.45, 0.7, 0.95): add(o, thud(), .55); add(o, ding(1200), .08); add(o, static(.18), .2)
add(1.18, whoosh(.3), .35); add(1.2, boom(), .3); add(1.2, static(.3), .25)
add(1.45, pop(), .12); add(1.75, pop(), .12); add(1.65, pop(), .1)
for o in (2.1, 2.3, 2.5): add(o, buzz(.1, 90), .18)
add(2.5, static(.5), .22); add(2.8, pop(), .14)
"""
m = m[:a] + new + m[b:]
m = m.replace('for k in range(10): add(1.5+k*.1,tick(2400),.05)\nadd(T[0]+1.2,pop(),.08); add(T[0]+1.4,pop(),.08)', 'for k in range(10): add(2.0+k*.1,tick(2400),.05)\nadd(T[0]+1.7,pop(),.08); add(T[0]+1.9,pop(),.08)')
open('mix.py', 'w', encoding='utf-8').write(m)
print('ok')
