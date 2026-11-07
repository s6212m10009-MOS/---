# Bright Map News แผนที่ข่าวสว่าง — Style Prompt

Made from a blank page; techniques from Caption News (caption-news) in Lemo-Opuscar.
Default size: 1080×1920.

> Vertical news shorts told on a bright, clean map. A pale-blue map fills the top two thirds; the story's place is outlined in orange, a pin drops with expanding rings and a white data card unfolds from it. The bottom third is a paper-white caption panel: huge navy Thai type slammed in chunks, one keyword on an orange block. Navy and blue explain, orange is the point. It reads with the sound off, in a bright, trustworthy, non-alarmist tone.

## 1. Essence, and what it is not

1. **The map is the ground.** Every beat sits on a map (country, region, world); other graphics are cards that rise over it.
2. **Orange is the point.** Only the subject of the beat is orange: outline, pin, number, keyword block. Everything else is blue, navy or grey.
3. **Sound-off first.** The picture and the caption carry the fact; the voice adds pace.
4. **Evidence tag.** Each number arrives with a source tag.
5. **A hook in the first 0.3 s**: the biggest number or the question lands in the caption panel at once.

Not Caption News (no footage as ground, no yellow, no dark ledger), not a dark TV war room (no neon, no red alarm look), not a dashboard (no multi-chart screens).

## 2. Frame and layout (1080×1920)

| Zone | Position | Content |
|---|---|---|
| Map | y 0–1330, full bleed | pale-blue sea, white/ice land, graticule every 5° |
| Channel bug | x 48, y 92, 430×84 navy block with orange left edge | channel name in white; under it a navy small line (desk · region) |
| Source tag | x 48, y 240, 50 px high | blue label "แหล่งข้อมูล" + white chip with the source; only when a figure is shown |
| Data card | white, radius 26, orange left edge, soft navy shadow | place label (grey 30 px), number (Kanit 800, 96 px, orange), unit navy |
| Caption panel | y 1330–1920, `#F6F9FD`, 10 px orange top rule | Thai chunks baseline y 1500 and 1665; English line y 1768; progress dots y 1840 |

The top 90 px and bottom 80 px stay clear of text (platform UI).

## 3. Colour

Sea `#D3E4F6`, graticule `#BFD5EE`, land `#FFFFFF` / neighbours `#EEF3FA`, land edge `#9FB8D8`, navy `#0B2A5B` (text, bug, leaders), blue `#1F5FD1` (labels, secondary data), orange `#FF7A1A` (the point), orange tint `#FFE3CC` (subject fill), grey `#5F7088`, paper `#F6F9FD`. Maximum one orange subject per beat; a comparison uses blue for "other". Red is not used.

## 4. Type

Kanit (OFL) for Thai and Latin. Caption chunks 800 / 92 px (keyword 112 px), navy; keyword on an orange block `#FF7A1A` with white text, block wipes left → right in 0.12 s. Chunk slam: scale 1.3 → 1 in 0.14 s (back ease), 0.14 s apart. English line Kanit 600 / 34 px grey, fades up 10 px; it is the spoken line, not a translation. Map labels Kanit 600 / 26 px in `#7C93B3`, subject label 800 / 34 px orange. Numbers use fixed-width cells so counters never jitter.

## 5. Motion

Calm and confident: beats 2.5–4 s, no flashing. Map pushes ≤ 1.3× with ease-in-out; the pin drops with back ease (0.4 s) then rings expand every 0.9 s; the card rises 30 px and fades in 0.5 s; routes and arrows draw segment by segment; counters roll with ease-out. Transitions: hard cut on the beat, or a map push from one region into the next; no dissolves or page turns.

## 6. Camera grammar

Only the map camera moves: slow push toward the subject (1.0 → 1.15 over a beat), a pan between two places along the shared edge, a 2-second pull-back to the world view on the verdict. The caption panel never moves except for its chunk slams.

## 7. Sound palette

Light, optimistic news bed at ~110 BPM: soft kit, pizzicato strings, marimba ostinato, warm synth pad; a low bass hit on the hook, a silence before the turn. Foley: chunk click, pin pop, ring ping, card whoosh, counter ticks, soft stamp thump. One brisk narrator, ducked music 45 %. Master −14 LUFS.

## 8. Native moves

1. **Pin and card**: pin drops on the place, rings expand, a data card unfolds from it on a leader line.
2. **Chunk slam with orange keyword** in the caption panel.
3. **Region fill**: countries or provinces fill in five steps of one blue; the subject goes orange.
4. **Route draw**: an orange dashed line draws from A to B with a moving dot.
5. **Push-in**: the map pushes into the subject and its neighbours dim.

## 9. Material

Map geometry from Natural Earth (public domain); disputed borders follow DIRECTOR.md §13. Photos and documents are optional inserts as a card over the map (never full-bleed). All icons and charts are drawn in code. Data is always sourced; mark illustrative numbers "ตัวอย่าง".

## 10. Engine

Page `index.html` in `demo/` draws with Canvas 2D at 1080×1920: `window.render(t)` deterministic, `READY`, `DUR`, `TEXTS(t)`. Map projection is equirectangular with cos(lat) scaling, one function `P(lon, lat)`. Render with `core/render/still.mjs` and `video.mjs --size 1080x1920`. Fonts in `fonts/` (woff2).

## 11. Pitfalls

- Too many orange things on screen: only the subject.
- Map labels under the bug or source tag (move the map centre, not the tag).
- Thai text that wraps: split into two chunks instead.
- Neighbour country labels crowding the subject: drop them.
- Real figures without a source tag.
- Long Thai words past the right margin (x 1008).
