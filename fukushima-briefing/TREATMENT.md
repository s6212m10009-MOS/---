# TREATMENT: "ฟุกุชิมะ ไดอิจิ: 5.7 กับ 14 เมตร" (title changed: 5.7 m is a design-basis tsunami level, not a wall; see FACTS.md)
Style: `satellite-briefing` (real imagery, hairline measurements, one reading per screen). Format: 1080x1920, ~55 s, Thai voice (Gemini TTS) + transcript-strip subtitles, -14 LUFS.
Story kind: a real event told as a lesson. Every number is a claim and goes into FACTS.md with a source and quoted wording; nothing is shown that the sources or the imagery do not support. No casualty or health-effect claims beyond what a cited source says.

## 1. Three candidate structures
A. **Time rings in a locked frame**: the Fukushima coast, dated plates scan in (2010 -> April 2011 -> 2021); the band between rings flashes. Strong picture, but the lesson (why the plant failed) is not in the pixels.
B. **The range line**: mark the plant, grow a ticked line out to 20 km (the evacuation radius) and count it up; then a second measurement, wall height vs wave height, as two readings. Clear numbers, but flat if it is only measuring.
C. **Dive, measure, time, climb**: orbit (Japan) -> dive to the plant on the shore -> one reading (the design wall height) -> the 20 km line -> the evacuation zone as time rings (2011, later years, zone shrinking) -> climb back to orbit with the lesson in one line.

**Chosen: C.** It uses three of the style's native moves in order (dive, range line, time rings) and ends on the climb, so the lesson lands as scale. The cliché avoided: the explosion footage and fear music; the film stays calm and dry.

## 2. Logline and arc
*A plant built for a 5.7 m wave met a much taller one; this is what the satellite saw, and what to learn.*
Setup: orbit, Japan's east coast. Turn: the reading (design height) against the measured reality. Ending: the climb, one line on preparing for the number you think will never come.

## 3. Benchmark
Learn: open-source investigation films that put one measurement on one screen; *Powers of Ten* for the continuous change of scale. Do not take: any layout, typeface, music or wording of those works. Never named in the film.

## 4. Shot list (all on the same continuous camera)
| # | t (s) | Framing | Move | Why |
|---|---|---|---|---|
| 1 | 0-6 | orbit, oblique, Japan with the limb | slow orbit | context; hook line over the first image |
| 2 | 6-14 | dive to the Fukushima coast, tilt to nadir | log zoom | going to look for yourself |
| 3 | 14-22 | nadir on the plant site, reticle locks | push-in | singling out; reading 1 |
| 4 | 22-32 | locked nadir, range line from the plant to 20 km | track along a line | the number lands, counter rolls |
| 5 | 32-44 | locked frame, dated plates scan over the zone | time rings, slow creep | consequence over time |
| 6 | 44-55 | climb to orbit, grey -> true colour on the last frame | climb | lesson and ending |

## 5. Beat sheet (to be locked to the real voice durations)
0 orbit + title-free hook line / 6 dive / 14 lock-on, reading 1 / 22 range line to 20 km / 32 time rings / 44 climb, last line, held silence / 55 end.

## 6. Cue map
Tempo ~84 BPM, bar 2.86 s: dive on a riser into a bar line; lock-on ping on beat 1 of bar 5; range-line ratchet accelerates with the counter and lands on a pitched hit; scans = noise sweeps; the one designed impact at the reading; silence before the last line.

## 7. Sound design
Dry palette (FM pings, ticks, timpani, pulse bass) plus one wet timbre (bowed metal / water) only at the turn; orbit hum bed, a distant sea ambience as an L-cut at the coast; two real silences (before reading 1, before the last line).

## 8. Subtitles
Transcript strip bottom-left, one line per cue, Thai in Sarabun (OFL), dates/instruments in IBM Plex Mono, imagery credit burned in (>= 20 px).

## Imagery plan (needs your OK before any download)
- Orbit/regional: NASA Blue Marble or MODIS via GIBS (public domain, credit).
- Site and coast, dated plates (2010-08-24, 2011-04-05 (3.5 weeks after the event), 2021-08-06): USGS Landsat (public domain) via Microsoft Planetary Computer STAC, no account; Sentinel-2 only for later years and with the credit line "Contains modified Copernicus Sentinel data [year]".
- Coastline from Natural Earth (110m/50m only, a few MB).
- **Size budget: ~150-300 MB total (was 1-3 GB).** How:
  - Never download whole scenes. Read Landsat COGs by window (HTTP range reads) and save only a ~60x60 km crop around the plant (covers the 20 km radius), bands 4-3-2 only (true colour), 8-bit PNG/JPEG: ~5-15 MB per date.
  - Exactly 3 dated plates (2010-08-24, 2011-04-05, 2021-08-06; done, 21 MB in imagery/); no extra scenes kept.
  - Blue Marble / GIBS: one 2048 px still, plus one regional tile at most (~10-20 MB), not the full 21600 px mosaic.
  - Sentinel-2 only if a later-year plate is needed at better resolution: one 10 m true-colour crop, not the full tile.
  - Delete the intermediate raw crops after the plates are made.
- Risk: Landsat is 15-30 m per pixel: the plant reads as a small footprint, which suits the scale story but not close-ups; no clear scene exists for March 2011, so the "after" plate is 5 April 2011 and must be labelled with its real date.
