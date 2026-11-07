p = 'index.html'
s = open(p, encoding='utf-8').read()


def ins(before, html):
    global s
    assert before in s, before
    s = s.replace(before, html + '\n        ' + before, 1)


ins('<div id="c1" class="char"', '<div id="clk1" class="ic" data-icon="clock" style="left: 80px; top: 430px; width: 230px; height: 230px"></div>\n        <div id="win1" class="ic" data-icon="window" style="left: 680px; top: 400px; width: 300px; height: 300px"></div>')
ins('<div id="c2" class="char"', '<div id="bk2" class="ic" data-icon="bank" style="left: 60px; top: 410px; width: 320px; height: 320px"></div>\n        <div id="qr2" class="ic" data-icon="qr" style="left: 420px; top: 440px; width: 220px; height: 220px"></div>')
ins('<div id="q0" class="char"', '<div id="car3a" class="ic" data-icon="car" style="left: 10px; top: 900px; width: 250px; height: 170px"></div>\n        <div id="car3b" class="ic" data-icon="car" style="left: 280px; top: 900px; width: 250px; height: 170px"></div>')
ins('<div id="i4a" class="item"', '<svg id="sk4" class="abs" style="left: 0; top: 350px; width: 1080px; height: 170px" viewBox="0 0 1080 170"></svg>')
ins('<div id="n5" class="big"', '<div id="tw5" class="ic" data-icon="tower" style="left: 395px; top: 900px; width: 230px; height: 440px"></div>')
ins('<svg id="div6"', '<div id="bag6" class="ic" data-icon="bag" style="left: 540px; top: 1170px; width: 150px; height: 180px"></div>\n        <div id="z6" class="pill red abs" style="left: 90px; top: 730px; font-size: 46px">เงินสด 0</div>')
ins('<div id="c7" class="char"', '<div id="qr7" class="ic" data-icon="qr" style="left: 90px; top: 420px; width: 240px; height: 240px"></div>\n        <div id="x7" class="stamp" style="left: 250px; top: 400px; width: 110px; height: 110px"></div>')
s = s.replace('<div id="m3" class="mark" style="left: 180px; top: 900px;', '<div id="m3" class="mark" style="left: 520px; top: 960px;')

icons = r"""
        clock: '<path d="M44,20 Q30,6 14,24 M156,20 Q170,6 186,24" fill="none" ' + W + '/><circle cx="100" cy="112" r="72" fill="#fff" ' + W + '/><path d="M100,112 V66 M100,112 L132,128" fill="none" stroke="' + INK + '" stroke-width="9" stroke-linecap="round"/><circle cx="100" cy="112" r="7" fill="' + INK + '"/><path d="M60,186 L76,172 M140,186 L124,172" fill="none" ' + W + '/>',
        window: '<rect x="24" y="14" width="152" height="172" rx="8" fill="#20235a" ' + W + '/><circle cx="62" cy="58" r="16" fill="#ffe27a"/><g fill="#fff"><circle cx="120" cy="40" r="3"/><circle cx="146" cy="70" r="3"/><circle cx="96" cy="84" r="3"/></g><path d="M24,150 V120 H54 V100 H84 V132 H112 V90 H146 V126 H176 V150Z" fill="#343989"/><path d="M100,14 V186 M24,100 H176" stroke="' + INK + '" stroke-width="7"/><rect x="24" y="14" width="152" height="172" rx="8" fill="none" ' + W + '/>',
        bank: '<path d="M16,70 L100,18 L184,70Z" fill="#c9d3dd" ' + W + '/><rect x="26" y="70" width="148" height="16" fill="#c9d3dd" ' + W + '/><g fill="#fff" ' + W + '><rect x="38" y="92" width="22" height="64"/><rect x="89" y="92" width="22" height="64"/><rect x="140" y="92" width="22" height="64"/></g><rect x="20" y="156" width="160" height="22" rx="4" fill="#c9d3dd" ' + W + '/><circle cx="100" cy="52" r="9" fill="#E0243A"/>',
        qr: '<rect x="20" y="20" width="160" height="160" rx="12" fill="#fff" ' + W + '/><g fill="' + INK + '"><rect x="36" y="36" width="44" height="44"/><rect x="120" y="36" width="44" height="44"/><rect x="36" y="120" width="44" height="44"/><rect x="96" y="96" width="20" height="20"/><rect x="128" y="108" width="36" height="14"/><rect x="100" y="136" width="16" height="28"/><rect x="132" y="140" width="32" height="24"/></g><g fill="#fff"><rect x="48" y="48" width="20" height="20"/><rect x="132" y="48" width="20" height="20"/><rect x="48" y="132" width="20" height="20"/></g>',
        car: '<path d="M16,120 V96 Q16,84 30,82 L58,80 Q72,52 100,48 H140 Q166,50 180,80 L192,86 Q196,92 196,104 V120Z" fill="#6bbce6" ' + W + '/><path d="M70,80 Q80,58 100,56 H112 V80Z M120,56 H140 Q156,58 166,80 H120Z" fill="#fff" stroke="' + INK + '" stroke-width="5"/><circle cx="58" cy="128" r="20" fill="' + INK + '"/><circle cx="154" cy="128" r="20" fill="' + INK + '"/><circle cx="58" cy="128" r="8" fill="#ccc"/><circle cx="154" cy="128" r="8" fill="#ccc"/>',
        tower: '<path d="M100,10 L60,190 M100,10 L140,190 M72,130 H128 M80,92 H120 M66,160 H134 M76,130 L128,160 M124,130 L72,160 M84,92 L120,130 M116,92 L80,130" fill="none" ' + W + '/><path d="M40,60 H160 M54,96 H146" fill="none" ' + W + '/>',
        bag: '<path d="M70,50 Q70,10 100,10 Q130,10 130,50" fill="none" ' + W + '/><rect x="40" y="40" width="120" height="150" rx="30" fill="#2fb766" ' + W + '/><rect x="62" y="110" width="76" height="50" rx="10" fill="#1f8a4c" ' + W + '/><path d="M100,60 V92" stroke="' + INK + '" stroke-width="7" stroke-linecap="round"/>',
"""
marker = "        wallet: '<rect"
assert marker in s
s = s.replace(marker, icons + marker, 1)

sky = r"""      (function () {
        var r = mulberry(5), x = 0, o = "";
        while (x < 1080) {
          var w = 60 + Math.round(r() * 50), h = 70 + Math.round(r() * 90);
          o += '<rect x="' + x + '" y="' + (170 - h) + '" width="' + (w - 6) + '" height="' + h + '" fill="#d7dce3" stroke="' + INK + '" stroke-width="5"/>';
          for (var wy = 170 - h + 14; wy < 150; wy += 24) for (var wx = x + 10; wx < x + w - 24; wx += 20) o += '<rect class="win" x="' + wx + '" y="' + wy + '" width="10" height="12" fill="#ffd23f"/>';
          x += w;
        }
        document.getElementById("sk4").innerHTML = o;
      })();
      document.querySelectorAll(".stamp")"""
s = s.replace('      document.querySelectorAll(".stamp")', sky, 1)
mb = '      function mulberry(a) { return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; var t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }\n      var INK = "#1E1E24";'
s = s.replace('      var INK = "#1E1E24";', mb, 1)

extra = r"""
      // ===== supporting scenes =====
      popIn("#clk1", 1.2); popIn("#win1", 1.4);
      tl.to("#clk1", { rotation: 8, duration: 0.06, yoyo: true, repeat: 9, transformOrigin: "50% 60%" }, 1.5);
      var b = T[1];
      popIn("#bk2", b + 0.3); popIn("#qr2", b + 0.6);
      tl.to("#bk2", { x: 8, duration: 0.05, yoyo: true, repeat: 5, ease: "none" }, b + 1.1);
      tl.to("#qr2", { rotation: -6, duration: 0.08, yoyo: true, repeat: 5, transformOrigin: "50% 50%" }, b + 1.8);
      b = T[2];
      tl.from("#car3a", { x: -300, opacity: 0, duration: 0.6, ease: "power3.out" }, b + 0.3);
      tl.from("#car3b", { x: -300, opacity: 0, duration: 0.6, ease: "power3.out" }, b + 0.5);
      tl.to(["#car3a", "#car3b"], { y: -6, duration: 0.2, yoyo: true, repeat: 7, ease: "sine.inOut" }, b + 1.4);
      b = T[3];
      tl.from("#sk4", { y: 90, opacity: 0, duration: 0.5, ease: "power3.out" }, b + 0.2);
      tl.to("#sk4 .win", { opacity: 0.1, duration: 0.1, stagger: { each: 0.03, from: "random" } }, b + 1.2);
      b = T[4];
      popIn("#tw5", b + 0.6);
      tl.to("#tw5", { x: 6, duration: 0.05, yoyo: true, repeat: 9, ease: "none" }, b + 2.7);
      b = T[5];
      popIn("#z6", b + 1.0); popIn("#bag6", b + 3.2);
      b = T[6];
      popIn("#qr7", b + 0.5); popIn("#x7", b + 1.0);
"""
s = s.replace('      window.__timelines["main"] = tl;', extra + '\n      window.__timelines["main"] = tl;', 1)
open(p, 'w', encoding='utf-8').write(s)

m = open('mix.py', encoding='utf-8').read()
sfx = """# supporting scene sfx
for k in range(10): add(1.5+k*.1,tick(2400),.05)
add(T[0]+1.2,pop(),.08); add(T[0]+1.4,pop(),.08)
add(T[1]+.3,pop(),.08); add(T[1]+.6,pop(),.08); add(T[1]+1.8,errtone(),.1)
add(T[2]+.3,whoosh(.4),.1); add(T[2]+.5,whoosh(.4),.1)
for k in range(8): add(T[3]+1.2+k*.12,tick(420),.09)
add(T[4]+.6,pop(),.1); add(T[4]+2.7,zap(),.15)
add(T[5]+1.0,pop(),.1); add(T[5]+3.2,pop(),.1)
add(T[6]+.5,pop(),.1); add(T[6]+1.0,thud(),.25)

# music:"""
m = m.replace('# music:', sfx, 1)
open('mix.py', 'w', encoding='utf-8').write(m)
print('patched')
