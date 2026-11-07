"""พากย์เสียงไทยให้คลิป samphat_king_john_60s_v2.mp4 ด้วย Microsoft Edge TTS

สร้างเสียงทีละช่วงตามการ์ดซับ (จาก subtitles_th.srt) แล้ววางลงตามเวลาเริ่มของการ์ด
ถ้าเสียงช่วงไหนยาวเกินการ์ด จะขึ้น "คำเตือน: ยาวเกิน" และเร่งด้วย atempo ให้พอดีช่อง

ตัวอย่าง:
  python make_voiceover.py --dry-run
  python make_voiceover.py --video samphat_king_john_60s_v2.mp4
  python make_voiceover.py --video ... --edge-rate +10%
  python make_voiceover.py --video ... --edge-voice th-TH-NiwatNeural --workdir vo_niwat
"""

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path

# (เริ่ม, จบ, ข้อความที่อ่าน) — ตัดป้ายอย่าง [ข้อเท็จจริง] ออก
SEGMENTS = [
    (0.000, 3.950, "สมบัติของพระเจ้าจอห์น ที่ทะเลกลืนไปในอ่าววอช"),
    (4.000, 10.950, "ปี 1216 อังกฤษอยู่ในสงครามกลางเมือง พระเจ้าจอห์นต้องเคลื่อนทัพไปทั่วประเทศ"),
    (11.000, 17.950, "กลางเดือนตุลาคม พระองค์ผ่านอ่าววอช ปากอ่าวกว้างที่น้ำขึ้นลงเร็วมาก"),
    (18.000, 24.950, "นักพงศาวดารบันทึกว่า ขบวนสัมภาระ ถูกน้ำและโคลนกลืนไปบางส่วน"),
    (25.000, 30.950, "ไม่กี่วันต่อมา พระองค์ประชวรหนัก และสวรรคตที่เมืองนวร์ก"),
    (31.000, 38.950, "นักประวัติศาสตร์หลายคนเห็นว่า สิ่งที่หายอาจเป็นสัมภาระของกองทัพ ไม่ใช่คลังสมบัติทั้งหมด"),
    (39.000, 45.450, "เรื่องเล่ายุคหลังว่า มงกุฎและเครื่องประดับล้ำค่าจมหายไปทั้งหมด"),
    (45.500, 51.950, "แนวชายฝั่งเปลี่ยนไปมากตั้งแต่ปี 1216 จึงไม่มีใครรู้ตำแหน่งที่แน่ชัด"),
    (52.000, 56.450, "ทะเลไม่เคยบอกว่ามันเก็บอะไรไว้ และแผนที่ที่เปลี่ยนไปทุกปี ทำให้กุญแจดอกนี้ยิ่งหายาก"),
    (56.500, 59.950, "เล่าไม่รู้บ้าง...รู้บ้าง"),
]

# เผื่อท้ายช่องไว้เล็กน้อยไม่ให้เสียงชนการ์ดถัดไป
TAIL_GAP = 0.05


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


async def synth(text, voice, rate, out_path):
    import edge_tts

    await edge_tts.Communicate(text, voice, rate=rate).save(str(out_path))


def build_segments(args, workdir):
    """สร้างเสียงแต่ละช่วง คืนค่า [(เริ่ม, ไฟล์ที่พอดีช่อง, อัตราเร่ง)]"""
    results = []
    for i, (start, end, text) in enumerate(SEGMENTS, 1):
        raw = workdir / f"seg{i:02d}_raw.mp3"
        fit = workdir / f"seg{i:02d}.wav"
        if not (args.reuse and raw.exists()):
            asyncio.run(synth(text, args.edge_voice, args.edge_rate, raw))
        dur = probe_duration(raw)
        slot = end - start - TAIL_GAP
        tempo = 1.0
        if dur > slot:
            tempo = dur / slot
            print(f"คำเตือน: ยาวเกิน ช่วง {i}: เสียง {dur:.2f}s > ช่อง {slot:.2f}s -> เร่ง x{tempo:.3f}")
        afilter = f"atempo={tempo:.5f}," if tempo > 1.0 else ""
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(raw),
             "-af", f"{afilter}aresample=48000", "-ac", "2", str(fit)],
            check=True,
        )
        print(f"ช่วง {i:2d}: {start:6.2f}-{end:6.2f}s  เสียง {dur:5.2f}s  ช่อง {slot:5.2f}s  x{tempo:.3f}")
        results.append((start, fit, tempo))
    return results


def mix(video, segs, out_path, bg_volume):
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(video)]
    for _, fit, _ in segs:
        cmd += ["-i", str(fit)]
    parts = [f"[0:a]volume={bg_volume}[bg]"]
    labels = ["[bg]"]
    for n, (start, _, _) in enumerate(segs, 1):
        ms = int(round(start * 1000))
        parts.append(f"[{n}:a]adelay={ms}|{ms}[v{n}]")
        labels.append(f"[v{n}]")
    parts.append(
        f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0,"
        "alimiter=limit=0.95[aout]"
    )
    cmd += [
        "-filter_complex", ";".join(parts),
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", str(out_path),
    ]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", help="คลิปต้นฉบับ (ไม่ถูกแก้ไข)")
    ap.add_argument("--output", help="ไฟล์ผลลัพธ์ (ค่าเริ่มต้น: <ชื่อคลิป>_voiced.mp4 ข้างคลิปต้นฉบับ)")
    ap.add_argument("--edge-voice", default="th-TH-PremwadeeNeural")
    ap.add_argument("--edge-rate", default="+0%", help="เช่น +10%%")
    ap.add_argument("--workdir", default="vo_premwadee", help="โฟลเดอร์เก็บเสียงแต่ละช่วง")
    ap.add_argument("--reuse", action="store_true", help="ใช้ไฟล์เสียงเดิมใน workdir ถ้ามีอยู่แล้ว")
    ap.add_argument("--bg-volume", type=float, default=0.5, help="ระดับเสียงบรรยากาศเดิม")
    ap.add_argument("--dry-run", action="store_true", help="แสดงช่วงข้อความแล้วจบ")
    args = ap.parse_args()

    if args.dry_run:
        print(f"{len(SEGMENTS)} ช่วงข้อความ  เสียง {args.edge_voice}  rate {args.edge_rate}")
        for i, (start, end, text) in enumerate(SEGMENTS, 1):
            print(f"{i:2d}. {start:6.2f}-{end:6.2f}s ({end - start:4.2f}s)  {text}")
        return

    if not args.video:
        ap.error("ต้องระบุ --video")
    video = Path(args.video).resolve()
    if not video.exists():
        sys.exit(f"ไม่พบไฟล์วิดีโอ: {video}")
    out_path = Path(args.output) if args.output else video.with_name(
        video.stem.removesuffix("_v2") + "_voiced.mp4"
    )
    if out_path.resolve() == video:
        sys.exit("ไฟล์ผลลัพธ์ต้องไม่ทับคลิปต้นฉบับ")

    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    segs = build_segments(args, workdir)
    mix(video, segs, out_path, args.bg_volume)
    print(f"เสร็จแล้ว: {out_path.resolve()}")


if __name__ == "__main__":
    main()
