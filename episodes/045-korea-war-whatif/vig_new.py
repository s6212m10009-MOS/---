VIG = {
    # 0: ทุ่นระเบิดที่ชายแดน
    0: W("v0t", txt(480, 80, "ทุ่นระเบิดที่ชายแดน", 56))
       + W("v0m", '<g transform="translate(200,290)"><path d="M-95,0 H95 M0,-95 V95 M-67,-67 L67,67 M-67,67 L67,-67" stroke="#fff" stroke-width="10" stroke-linecap="round"/><circle r="70" fill="#3b3b44" stroke="#fff" stroke-width="6"/><circle r="16" fill="#e0243a"/></g>')
       + W("v0w", '<path d="M760,190 L860,370 H660Z" fill="#ffd23f" stroke="#fff" stroke-width="8" stroke-linejoin="round"/>' + txt(760, 335, "!", 110, "#e0243a"))
       + W("v0n", txt(480, 450, "ทหารใต้เจ็บ 2 นาย", 58, "#ffd23f") + txt(480, 505, "โซลชี้ว่าฝั่งเหนือฝัง", 38, "#9fd8ff")),
    # 1: ยิงขีปนาวุธ
    1: W("v1t", txt(480, 80, "ยิงขีปนาวุธหลายลูก", 56))
       + W("v1r", '<g transform="translate(200,290) rotate(40)"><path d="M0,-100 Q34,-45 26,55 H-26 Q-34,-45 0,-100Z" fill="#e8e8ef" stroke="#fff" stroke-width="6"/><path d="M-26,30 L-58,76 L-26,60Z M26,30 L58,76 L26,60Z" fill="#e0243a" stroke="#fff" stroke-width="5" stroke-linejoin="round"/><path d="M-14,58 L0,125 L14,58Z" fill="#ff9a2e"/><circle cy="-30" r="12" fill="#2f9fe0" stroke="#fff" stroke-width="4"/></g>')
       + W("v1d", '<rect x="520" y="200" width="380" height="150" rx="26" fill="#1e1e24" stroke="#fff" stroke-width="8"/>' + txt(710, 305, "4 พ.ย.", 96, "#ffd23f"))
       + W("v1k", txt(480, 455, "คิม โยจอง: ไม่สนใจเจรจา", 48)),
    # 2: โซลห่างชายแดน
    2: W("v2n", txt(480, 135, "&lt;50 กม.", 150, "#ffd23f") + txt(480, 215, "โซล → ชายแดน", 50))
       + W("v2p", stick(330, 350, 0.9) + stick(480, 350, 0.9) + stick(630, 350, 0.9))
       + W("v2l", txt(480, 500, "คนไทยในเกาหลีใต้ ทำงาน+เที่ยว", 40, "#9fd8ff")),
    # 3: สถานทูต + แจ้งญาติ
    3: W("v3t", txt(480, 65, "ติดตามประกาศสถานทูตไทย", 50))
       + W("v3b", '<path d="M480,110 V190" stroke="#fff" stroke-width="6"/><rect x="480" y="106" width="70" height="14" fill="#e0243a"/><rect x="480" y="120" width="70" height="14" fill="#fff"/><rect x="480" y="134" width="70" height="14" fill="#1f4fa0"/>'
                  '<path d="M360,260 L480,185 L600,260Z" fill="#1f6fd0" stroke="#fff" stroke-width="6" stroke-linejoin="round"/><rect x="380" y="260" width="200" height="130" fill="#e8e8ef" stroke="#fff" stroke-width="6"/>'
                  '<rect x="400" y="285" width="26" height="80" fill="#8f98a8"/><rect x="448" y="285" width="26" height="80" fill="#8f98a8"/><rect x="496" y="285" width="26" height="80" fill="#8f98a8"/><rect x="544" y="285" width="26" height="80" fill="#8f98a8"/>')
       + W("v3r", '<path d="M770,235 Q705,245 705,320 L685,352 H855 L835,320 Q835,245 770,235Z" fill="#ffd23f" stroke="#fff" stroke-width="6" stroke-linejoin="round"/><circle cx="770" cy="372" r="16" fill="#ffd23f" stroke="#fff" stroke-width="5"/>')
       + W("v3a", txt(480, 460, "บอกญาติ: เราอยู่ตรงไหน", 52, "#ffd23f")),
    # 4: พาสปอร์ต + เงินสด + ประกัน
    4: W("v4t", txt(480, 70, "เที่ยวบินอาจถูกยกเลิก", 52, "#ffd23f"))
       + W("v4a", '<rect x="95" y="170" width="150" height="200" rx="14" fill="#1f4fa0" stroke="#fff" stroke-width="7"/><circle cx="170" cy="255" r="34" fill="none" stroke="#fff" stroke-width="6"/><path d="M136,255 H204 M170,221 V289" stroke="#fff" stroke-width="5"/>' + txt(170, 440, "พาสปอร์ต", 42))
       + W("v4b", '<rect x="380" y="205" width="200" height="120" rx="14" fill="#1f9d55" stroke="#fff" stroke-width="7"/><circle cx="480" cy="265" r="34" fill="#fff"/>' + txt(480, 282, "฿", 50, "#1f9d55") + txt(480, 440, "เงินสดสำรอง", 42))
       + W("v4c", '<path d="M790,170 l80,28 v70 q0,60 -80,90 q-80,-30 -80,-90 v-70Z" fill="#2f9fe0" stroke="#fff" stroke-width="7" stroke-linejoin="round"/><path d="M752,272 l28,28 l50,-56" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>' + txt(790, 440, "ประกันเดินทาง", 42)),
}

# กราฟิกบนแผนที่ (พิกัดภูมิศาสตร์ 1° = 10 หน่วย)
import math
_L_MIS = 125
_L_DIST = round(math.hypot(mx(127.0)-mx(126.98), my(38.0)-my(37.57)), 1)
_L_FLY = round(math.hypot(_bx-_sx, _by-_sy), 1) if False else 0
_sx, _sy, _bx, _by = mx(126.98), my(37.57), mx(100.5), my(13.75)
_LF = round(math.hypot(_bx-_sx, _by-_sy), 1)
_ang = math.degrees(math.atan2(_by - _sy, _bx - _sx))
GEO = (
    f'<path id="g_dmz" d="M{mx(126.6)},{my(37.75)} L{mx(127.0)},{my(38.0)} L{mx(127.7)},{my(38.3)} L{mx(128.37)},{my(38.62)}" fill="none" stroke="#ff2b2b" stroke-width="7" stroke-dasharray="16 10" stroke-linecap="round" vector-effect="non-scaling-stroke" opacity="0"/>'
    f'<circle id="g_pulse" cx="{mx(127.0)}" cy="{my(38.1)}" r="1" fill="none" stroke="#ff2b2b" stroke-width="6" vector-effect="non-scaling-stroke" opacity="0"/>'
    f'<path id="g_mis" d="M{mx(125.7)},{my(39.0)} Q{mx(129.3)},{my(43.5)} {mx(133.0)},{my(40.5)}" fill="none" stroke="#ffd23f" stroke-width="1.3" stroke-linecap="round" stroke-dasharray="{_L_MIS} {_L_MIS*1.3}" stroke-dashoffset="{_L_MIS*1.15}"/>'
    f'<circle id="g_sp1" cx="{mx(133.0)}" cy="{my(40.5)}" r="1" fill="none" stroke="#fff" stroke-width="8" vector-effect="non-scaling-stroke" opacity="0"/>'
    f'<circle id="g_sp2" cx="{mx(133.0)}" cy="{my(40.5)}" r="1" fill="none" stroke="#9fd8ff" stroke-width="6" vector-effect="non-scaling-stroke" opacity="0"/>'
    f'<path id="g_dist" d="M{mx(126.98)},{my(37.57)} L{mx(127.0)},{my(38.0)}" fill="none" stroke="#ffd23f" stroke-width="0.35" stroke-linecap="round" stroke-dasharray="{_L_DIST} {_L_DIST*1.3}" stroke-dashoffset="{_L_DIST*1.15}"/>'
    f'<path id="g_fly" d="M{_sx},{_sy} L{_bx},{_by}" fill="none" stroke="#fff" stroke-width="2.3" stroke-linecap="round" stroke-dasharray="{_LF} {_LF*1.3}" stroke-dashoffset="{_LF*1.15}"/>'
    f'<g id="g_plane" opacity="0"><g transform="rotate({_ang:.1f})"><path d="M24,0 L-16,-14 L-8,0 L-16,14Z" fill="#fff" stroke="#1e1e24" stroke-width="3" stroke-linejoin="round"/></g></g>'
)

PLANE1 = [_bx, _by]
