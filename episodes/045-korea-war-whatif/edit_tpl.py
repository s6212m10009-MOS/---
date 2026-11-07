from pathlib import Path
import re
p = Path("template.html"); s = p.read_text(encoding="utf-8")
s = s.replace("            %%PINS%%", "            %%GEO%%\n            %%PINS%%")
s = s.replace('<div class="h0">ถ้าโลกเกิด</div><div class="h1">มหันตภัย</div><div class="h2">WHAT IF?</div>',
              '<div class="h0">สองเกาหลี</div><div class="h1">ตึงเครียด!</div><div class="h2">ถ้ารบจริง?</div>')
s = s.replace('#hook .h1 { font-size: 200px;', '#hook .h1 { font-size: 190px;').replace('#hook .h2 { font-size: 170px;', '#hook .h2 { font-size: 160px;')
s = s.replace('#doom { position: absolute;', '#m1,#m2,#m3,#boom { display: none; }\n      #doom { position: absolute;')
s = s.replace('fillStamp("st1", "ok", "น้ำจืดเพียงพอ");', 'fillStamp("st1", "ok", "ติดตามสถานทูต");')
s = s.replace('fillStamp("st2", "ok", "อาหารเลี้ยงตัวเองได้");', 'fillStamp("st2", "ok", "พาสปอร์ต + เงินสด");')
s = s.replace('fillStamp("st3", "ok", "พลังงานมั่นคง");', 'fillStamp("st3", "ok", "ประกันเดินทาง");')
s = s.replace('function pinScale(i) { var k = CAM[i][2]; return i === 0 ? 0.6 : 1.1 / k; }', 'function pinScale(i) { return 1.1 / CAM[i][2]; }')
s = s.replace('gsap.set("#flash", { opacity: 1 });', 'gsap.set("#flash", { opacity: 1 });\n      gsap.set("#g_plane", { x: D.PLANE0[0], y: D.PLANE0[1] });')
# การ์ด: ฉาก 0..4, ฉาก 0 เริ่มหลังฮุค
s = s.replace('''        if (i >= 1 && i <= 4) {
          tl.fromTo("#vg" + i, { opacity: 0, y: 70, scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.5)", immediateRender: false }, s + 0.3);''',
'''        if (i <= 4) {
          tl.fromTo("#vg" + i, { opacity: 0, y: 70, scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.5)", immediateRender: false }, s + (i === 0 ? 3.5 : 0.3));''')
# ตัดบล็อกอุกกาบาต
a = s.index("      // hook: โลกถล่ม")
b = s.index("      // hook\n")
s = s[:a] + '''      // hook: ไซเรน — จอแดงกะพริบ + สั่น
      tl.fromTo("#dred", { opacity: 0 }, { opacity: 0.35, duration: 0.25, yoyo: true, repeat: 9, ease: "none" }, 0.1);
      tl.to("#dred", { opacity: 0, duration: 0.5 }, 2.7);
      [0.12, 0.45, 0.8].forEach(function (s0, k) {
        tl.fromTo("#vp", { x: -20 + k * 4, y: 12 }, { x: 0, y: 0, duration: 0.55, ease: "elastic.out(2, 0.25)", immediateRender: false }, s0);
      });

''' + s[b:]
# ฉากเฉพาะ
a = s.index("      // scene 1: NZ")
b = s.index("      // scene 5 stamps")
new = '''      // scene 0: DMZ + ทุ่นระเบิด
      tl.fromTo("#g_dmz", { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: false }, 2.6);
      tl.fromTo("#g_pulse", { attr: { r: 1 }, opacity: 1 }, { attr: { r: 6 }, opacity: 0, duration: 1.0, repeat: 5, ease: "power1.out", immediateRender: false }, 3.0);
      popIn("#v0t", 3.55); slideIn("#v0m", { x: -120 }, 3.7, 0.6); popIn("#v0w", 4.3); fadeIn("#v0n", 4.9);
      tl.to("#v0w", { rotation: 6, transformOrigin: "50% 100%", duration: 0.12, repeat: 7, yoyo: true }, 4.4);
      // scene 1: ขีปนาวุธ
      tl.fromTo("#g_mis", { strokeDashoffset: 1.1 }, { strokeDashoffset: 0, duration: 1.2, ease: "power2.in", immediateRender: false }, at(1, 0.15));
      tl.fromTo("#g_sp1", { attr: { r: 1 }, opacity: 1 }, { attr: { r: 9 }, opacity: 0, duration: 1.1, ease: "power2.out", immediateRender: false }, at(1, 0.15) + 1.15);
      tl.fromTo("#g_sp2", { attr: { r: 1 }, opacity: 1 }, { attr: { r: 6 }, opacity: 0, duration: 1.0, ease: "power2.out", immediateRender: false }, at(1, 0.15) + 1.3);
      popIn("#v1t", at(1, 0.05)); slideIn("#v1r", { x: -150, y: 100 }, at(1, 0.1), 0.7); popIn("#v1d", at(1, 0.4)); fadeIn("#v1k", at(1, 0.65));
      // scene 2: โซลห่างชายแดน
      tl.fromTo("#g_dist", { strokeDashoffset: 1.1 }, { strokeDashoffset: 0, duration: 0.7, ease: "power2.out", immediateRender: false }, at(2, 0.3));
      popIn("#v2n", at(2, 0.05)); slideIn("#v2p", { y: 70 }, at(2, 0.3), 0.6); fadeIn("#v2l", at(2, 0.55));
      tl.to("#vg2", { x: 8, duration: 0.05, repeat: 5, yoyo: true }, at(2, 0.07));
      // scene 3: สถานทูต + แจ้งญาติ
      popIn("#v3t", at(3, 0.05)); slideIn("#v3b", { y: 90 }, at(3, 0.12), 0.7); popIn("#v3r", at(3, 0.4)); fadeIn("#v3a", at(3, 0.6));
      tl.to("#v3r", { rotation: 10, transformOrigin: "50% 10%", duration: 0.1, repeat: 7, yoyo: true }, at(3, 0.45));
      // scene 4: บินกลับไทย + เตรียมของ
      tl.fromTo("#g_fly", { strokeDashoffset: 1.1 }, { strokeDashoffset: 0, duration: 1.4, ease: "power1.inOut", immediateRender: false }, at(4, 0.05));
      tl.fromTo("#g_plane", { x: D.PLANE0[0], y: D.PLANE0[1], opacity: 1 }, { x: D.PLANE1[0], y: D.PLANE1[1], duration: 2.6, ease: "power1.inOut", immediateRender: false }, at(4, 0.05));
      popIn("#v4t", at(4, 0.2)); slideIn("#v4a", { y: 80 }, at(4, 0.3), 0.5); slideIn("#v4b", { y: 80 }, at(4, 0.45), 0.5); slideIn("#v4c", { y: 80 }, at(4, 0.6), 0.5);
      tl.set("#g_plane", { opacity: 0 }, SC[5]);

'''
s = s[:a] + new + s[b:]
p.write_text(s, encoding="utf-8")
print("ok")
