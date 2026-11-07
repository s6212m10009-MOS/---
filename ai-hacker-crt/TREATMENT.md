# TREATMENT: "ไม่ได้เจาะระบบ เจาะความไว้ใจ" (AI hacker, ASCII / CRT Terminal)

Style: `ascii-crt` (P3 amber phosphor, glyphs on a grid, LOG strip subtitles). Format: 1080x1920 vertical, ~45 s, 24 fps, Thai voice + Thai LOG-strip subtitles, -14 LUFS.
Topic: an AI "hacker" attack on a fictional company. Everything is invented (company, names, numbers). No real exploit, tool or procedure is shown; the story is about social engineering, with a safety takeaway at the end.

## 1. Three candidate structures

A. **The defender reads the log.** An analyst scrolls a night's intrusion log from 02:41 to 03:07. Clear, but passive: the viewer only reads.
B. **A chat between two machines.** The attacker AI and the company's guard AI talk across the night; the guard says yes at the end. Strong turn, but a person (the victim) never appears, and the real-life lesson is lost.
C. **Error first, then rewind.** Open on the crash dump "ACCESS GRANTED 03:07", rewind through the log: the AI fails at the system, switches to the person, fakes the boss's voice, one employee types the code. Ends on the one habit that would have stopped it.

**Chosen: C.** It has a hook in the first 2 s (a breach with no failed password), a real turn (system -> person), a human in the loop (typed unevenly, against the machine's even typing), and an ending that is useful to a Thai viewer. The cliché it avoids: green code rain and a "hacker in a hoodie".

## 2. Logline and arc

Logline: *AI ไม่ได้ถอดรหัสผ่านของบริษัท; มันเลียนเสียงหัวหน้า แล้วให้พนักงานเปิดประตูเอง.*
- Setup: a breach at 03:07, no wrong password anywhere (hook).
- Turn: the scan finds nothing, so the AI changes target from the system to a person.
- Ending: the employee types the code; one line of the new habit appears in the single second colour; the buffer fills; the cursor holds.

## 3. Benchmark

- Learn: 1980s terminal "war-room" title logic and teletype logs (typed text as tension, silence as the main instrument); the real incident-report format (timestamps, status codes) as storytelling.
- Do not take: any film's interface text, fonts, logos or music, the green rain, any agency or company names.

## 4. Shot list (1080x1920, one screen; "camera" = grid scale)

| # | t (s) | Framing | Move | Why |
|---|---|---|---|---|
| 1 | 0.0-3.2 | 40 cols, crash dump, big | static, then hard redraw | hook: the result first |
| 2 | 3.2-9.5 | 80 cols log | pull out from the headline to line 1 of a long list | context: a normal night, 0 holes found |
| 3 | 9.5-14.5 | 80 -> 200 cols | scroll fast, stop on "TARGET: PERSON" | the turn |
| 4 | 14.5-21.5 | 200+ cols picture | text becomes image: the boss's name and posts fall into a face | native move, signature shot |
| 5 | 21.5-33 | 60 cols chat/call | push in on the fake call line, then on the employee's cursor | tension, human typing |
| 6 | 33-35.5 | 20 cols | near-silence, cursor blinks; then power flicker and "ACCESS GRANTED" | the shock |
| 7 | 35.5-42 | 60 cols | single colour change (ice blue-white) on the rule line | the one soft second colour |
| 8 | 42-45.5 | 80 cols | buffer fills and scrolls away; only the prompt remains, cursor stops blinking | ending |

## 5. Beat sheet (sec)

- 0.0 power-on dot-line-frame (fast). 0.4 typed: `03:07:12 ACCESS GRANTED user=acct-04`. Error beep.
- 1.2 voice L1 "ตีสามเจ็ดนาที ระบบบริษัทถูกเจาะ". 2.6 voice L2 "แต่ไม่มีใครพิมพ์รหัสผ่านผิดสักครั้ง".
- 3.2 hard redraw, `REWIND 02:41`. 4.0 voice L3 "AI ตัวนี้สแกนหาช่องโหว่ทั้งคืน ผลคือไม่เจอเลย". Progress bar 100%, `HOLES: 0`.
- 9.5 voice L4 "มันเลยเปลี่ยนเป้า จากระบบ มาเป็นคน". Log scrolls fast, stops: `TARGET: PERSON`.
- 14.5 voice L5 "ดึงเสียงหัวหน้าจากคลิปสัมภาษณ์"; sentence breaks apart, letters sorted by ink density become the boss's face.
- 19 voice L5b "แล้วโทรหาพนักงานบัญชี". Face dissolves into the call line.
- 21.5 fake boss voice L6 (male voice, processed): "พี่ติดประชุม ขอรหัสโอทีพีหน่อย ด่วนมาก". Typed on screen as [SCREEN].
- 27 hesitation: the employee's cursor blinks (silence #1, ~2 s). Human typing, uneven.
- 30 she types 6 digits (mock `******`). 33.0 silence #2 (everything drops to digital zero, 1.0 s).
- 34.2 power flicker, `ACCESS GRANTED`. Low hit.
- 35.5 colour change on the downbeat. Voice L7 "AI ไม่ได้เจาะระบบ มันเจาะความไว้ใจ".
- 38.5 voice L8 "ถ้ามีใครขอรหัสด่วน วางสายก่อน แล้วโทรกลับเบอร์เดิม".
- 42 buffer scrolls up and away. 44 only `>` and cursor; the cursor holds (no more blinking). End 45.5.

## 6. Cue map

96 BPM (beat 0.625 s), 4/4, analog-synth: cold sub drone + square-wave sequencer that grows.
- Bar grid: bar = 2.5 s. Sections: HOOK 0-3.2 (hit on 0.0, drone only); LOG 3.2-9.5 (sequencer enters bar 2); TURN 9.5-14.5 (filter opens); FACE 14.5-21.5 (single arpeggio grows as the face forms); CALL 21.5-33 (music drops to drone, voice leads); SILENCE 33-34.2 (digital zero); SHOCK 34.2 (gated-reverb hit); RULE 35.5-42 (one major chord held, ice-blue moment); END 42-45.5 (drone fades, room tone only).
- Hits on the grid: redraw at 3.2 (bar 2 downbeat nearest), colour change on a downbeat at 35.0 +/- snapped to the grid; checked with the cue script, aim 0 ms.

## 7. Sound design table

| Section | Ambience | Main foley | Music |
|---|---|---|---|
| Hook | degauss thump, fan | BEL beep, key clicks | drone |
| Log | room tone, flyback whine (very quiet) | teletype ticks, progress ticks | square sequencer enters |
| Turn | fan | fast scroll ticks | filter opens |
| Face | fan | clusters of tiny particle ticks | growing arpeggio |
| Call | line hiss / modem-like band-limited noise | uneven buckling-spring keys | drone only |
| Silence | none | cursor tick only | digital zero |
| Shock | mains hum thump | relay click, error beep | gated-reverb hit |
| Rule | quiet fan | soft key clicks | one major chord |
| End | room tone alone | none | none |

At least two real silences (27 s and 33 s); two sound transitions: the call line hiss L-cuts over the face dissolve, and the shock hum J-cuts in before the flicker.

## 8. Subtitles and titles

LOG strip at the bottom: dim separator, inverse-video tag (`LOG` / `CALL` / `SYS`), prompt, the Thai line typed word by word in sync with the voice (energy + pause snapping, since Whisper Thai word times are unreliable); Thai in a monospace Thai-capable font (e.g. Noto Sans Mono Thai / Sarabun-like, OFL, self-hosted), ~44 px, held >= max(1.8 s, speech + 0.6 s). On-screen story text is picture and appears in the .srt as `[SCREEN] ...`. Titles are typed as commands.

## Voice and assets

Edge TTS `th-TH-PremwadeeNeural` (narrator), `th-TH-NiwatNeural` processed (fake boss: ring modulation + band-pass). Voice check: Whisper Thai is unreliable, so lines are checked by listening to short segments and by duration. Music, foley, fonts: all synthesised or OFL; listed in CREDITS.

## As built (differences from the plan above)
- Final length 44.5 s; beats re-timed to the real voice durations and locked to the 96 BPM bar grid: redraw 5.0, scroll 10.0, face fall 15.0, call 20.0, silence 22.5-25.0, digital zero 28.75-30.0, shock 30.0, colour change 32.5, rule 35.0, buffer scrolls away 40.0, cursor holds from 42.8.
- On-screen story text is English/ASCII (the VT323 grid has no Thai glyphs); Thai appears in the voice and in the LOG-strip subtitles (Sarabun, drawn outside the grid).
- The sentence that becomes the boss's face is "SEND ME THE CODE". No second power-off: the film ends on the held cursor.
- Voice check: Whisper Thai is unreliable, so lines were not transcribed back; check by listening. Caption sync is proportional across each line's measured duration.
- Rendering uses the system Chrome (PLAYWRIGHT_CHROME) because the Playwright browser download timed out on this network.
