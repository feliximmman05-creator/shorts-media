# Daily Short runbook (Into the Dark Web, @ShadowMan0011)

One Short per day. Format: "Top 5 [funniest / dumbest] moments in [category]", countdown #5 to #1, 45-60 seconds.

## 1. Pick the topic
- Read `log/topics.md`. Never repeat a category or any single moment already listed there.
- Rotate categories, evergreen only (history, science, sports, animals, inventions, military, space, business, food, royalty, police chases, airports, weddings, etc.). No current-news or trend topics.
- Every moment must be real and verifiable. Web-search each one and keep 1 source per moment. Drop any moment you can't verify. No real private individuals; no deaths, injuries or tragedies played for laughs; nothing about minors.
- Hedge contested stories ("legend says", "reportedly").

## 2. Write `script.json`
Work folder: `work/` (gitignored). Format, 7 segments in this order, ids exactly as shown:

```json
[
 {"id":"hook","rank":"","title":"5 FUNNIEST MOMENTS IN SPORTS","emoji":["1f92f"],"text":"..."},
 {"id":"r5","rank":"#5","title":"SHORT CAPS TITLE","emoji":["26bd","1f926"],"text":"Number five. ..."},
 {"id":"r4", ...}, {"id":"r3", ...}, {"id":"r2", ...}, {"id":"r1", ...},
 {"id":"outro","rank":"","title":"FOLLOW FOR MORE","emoji":["1f449"],"text":"Follow for more ... so dumb, it's actually real."}
]
```

- `emoji`: 1-2 lowercase Twemoji codepoints (e.g. `1f407` rabbit, `1f680` rocket). Flags use `1f1e6-1f1fa` style.
- `title`: max ~28 characters, caps.
- `text`: spoken words. Each ranked segment 20-30 words. Write numbers as words when spoken ("twenty thousand"). Total target 50-60 seconds.
- Hook: write 3 options, score with `python3 -I pipeline/hooks/hookscore.py hooks.txt`, use the top one (must score 60+). The "You won't believe number one" pattern scored 79.
- Remove em dashes and filler words.

## 3. Build
```bash
bash pipeline/make_short.sh work videos/YYYY-MM-DD-<slug>.mp4
```
Then check it: extract 4 frames with ffmpeg (`select='eq(n\,200)+...',scale=360:-1,tile=4x1`) and look at them. Text must not overlap or overflow. Fix and rebuild if it does.

## 4. Publish
1. Copy `work/script.json` to `log/YYYY-MM-DD-script.json`, append one line to `log/topics.md`: `- YYYY-MM-DD | category | moment1; moment2; moment3; moment4; moment5`.
2. Commit and push to `main`.
3. Video URL: `https://raw.githubusercontent.com/feliximmman05-creator/shorts-media/main/videos/<file>.mp4` (check it returns HTTP 200).
4. Metricool `createScheduledPost`, blogId `7796937`, ~10 minutes ahead, timezone `Asia/Calcutta`, provider `youtube`, autoPublish true, `youtubeData`: type `short`, privacy `public`, madeForKids false, category `EDUCATION` (or `COMEDY`/`SPORTS` to fit), 6-8 tags, title under 70 chars ending `#shorts`. Description: one curiosity line + question to drive comments + "Follow for more!" + 4-5 hashtags.
