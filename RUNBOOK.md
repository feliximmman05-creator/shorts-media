# Daily Shorts runbook (Peak Dumb, @peakdumbtv)

One Short per day (morning run; the evening run only when `log/learnings.md` starts with `two_per_day: yes`), every one a **"What If" scenario**, 20-35 seconds, full-screen drawn scenes that show what the narration says (scene format, section 2), cold open, built to loop.

## Channel strategy (lane changed from "dumbest decisions" to "What If" on 2026-11-12 by the owner's request; overrides anything below that conflicts)
**Goal:** YouTube Partner Program: 1,000 subscribers + 10 million Shorts views inside a 90-day window. No guarantee exists; the job is to maximise the odds every day.

**Where we are (2026-11-12):** 6 subs, 4,149 lifetime views, 9 Shorts before the change. 96% of views come from the Shorts feed. Only ~53% of feed views become engaged views (target 70%+). 2 subs per ~2,500 views (0.08%).

**Why one lane:** topics were all over the place, so a viewer who likes one Short has no reason to subscribe. The owner chose "What If" as the single lane. First What If Short: "What If Earth Stopped Spinning for 5 Seconds?" (2026-11-12); no stats for the lane yet, so the Sunday report must judge it on real numbers.

1. **One lane, every Short:** a "What If" question about something impossible, extreme or huge (space, Earth, physics, animals, tech/AI, games, cars, the internet, money at absurd scale), answered step by step with real science and real numbers. Prefer a question tied to what is trending this week (a launch, a game, a movie, a viral clip, a science story). If the week's trend gives no good question, use an evergreen one that has not been used in 30 days. No old-history topics.
2. **Hook formula:** "What if [impossible thing] for just [short time / one change]?" The question is on screen and spoken in the first 2 seconds. Then the chain: each beat = what happens next -> the real number behind it -> something worse or stranger. Twist or survival answer at the end, loop.
3. **Rotate the structure** so uploads are never near-identical (YouTube demonetises templated, mass-produced channels): (a) countdown timeline ("Second 1... Second 3... Second 5", or minute/day/year), (b) second-person survival ("You're standing in [place] when [it happens]"), (c) "Which would be worse: A or B?" Never the same structure three runs in a row. Every script is original research and original wording.
4. **Titles:** start with "What If", then the subject, under 60 characters, always a question ("What If the Moon Vanished Tonight?"). End `#shorts`.
5. **Subscribe reason:** the lane itself. No subscribe sticker, voice line or outro anywhere. Description line 1 ends with "New What If every day."
6. **Per-Short targets:** engaged views ÷ views ≥ 70%, average viewed ≥ 85%. First 2 seconds decide it: start on the question and the most extreme consequence, never on setup. If three Shorts in a row miss both targets, change the hook style, not the niche.
7. **Real science, clearly hypothetical.** Every number comes from a reliable source; estimates are said as estimates. Nothing a viewer could copy and get hurt by (no "what if you stopped eating/sleeping/breathing" body challenges, no drugs, no stunts). No real person shown being harmed.
8. **One per day (the morning run) from 2026-11-14** until the Sunday report writes the line `two_per_day: yes` at the top of `log/learnings.md` (it does that when engaged views ÷ views reaches 65% over the week). Only then does the evening run make a second Short. Two weak Shorts a day add no reach.
9. **Checkpoints** (the Sunday report grades these): day 14: one Short over 10K views and engaged ratio ≥ 65%. Day 30: 100K total views, 100 subs. Day 60: 1M views, 500 subs. If a checkpoint is missed, the Sunday report must propose one concrete change to hook, length or structure and list it under "Changes that need your OK".

## The format: a "What If" scenario (base structure; see strategy point 3 for the rotation)
Modeled on "What If Elon Musk Took the AI Race to Space?" (Afterhour Theory, 1.7M views). Learn the structure, never reuse its script, characters or artwork.
- **Put the viewer inside it:** second person wherever it fits. Hook = the What If question. Then "Right now, you're..." or "You're standing in..." so the viewer is the one it happens to.
- **A chain of consequences:** each beat = the next thing that happens -> the real number that explains it (speed, distance, temperature, time, size, with a source) -> which causes the next thing. The steps must connect logically, like dominoes.
- **Escalate:** each step bigger than the last. Use turn phrases: "But second three is worse", "And that's the good news", "Then it gets strange", "You survived. But...".
- **Twist ending** that reframes everything (the one safe place, the thing nobody expects, the reason it can't happen), then loop into the hook.
- **Subjects that work:** a What If connected to whatever is hottest THIS WEEK (space news, a game or movie launch, AI, cars, sport, a viral clip), or a big evergreen one (Earth, Moon, Sun, oceans, gravity, speed of light, animals at giant scale). The owner finds history topics boring: never pick a historical subject unless it is directly tied to a huge trend happening now. A good test: would a 16-25 year old stop scrolling for this question?
- **Real people:** only when the trend needs it, shown as the cartoon character with a name tag (`role`), doing public, documented things. No mocking, no claims about private life, no politicians or elections, never shown being hurt.

## Before anything: back-fill, then at most two Shorts per day
1. **Back-fill:** for every row in `log/posts.csv` whose `youtube_url` is `PENDING`, call Metricool `getScheduledPosts` for that date; if PUBLISHED, write the `publicUrl` into the row. If it shows an error, note it for the email.
2. **Guard:** count rows with today's date (IST). Morning run (before 14:00 IST): if there is already one, stop after the back-fill. Evening run (14:00 IST or later): from 2026-11-14, stop after the back-fill unless the first line of `log/learnings.md` is `two_per_day: yes`; if there are already two rows for today, stop after the back-fill. Never make a third.
3. The evening Short must be a different story and a different structure (see strategy point 3) from the morning one.

## 0. Research what's working (every run, before picking a topic)
Learn patterns from other channels and our own stats. Never copy another channel's script, title wording, characters or footage. Copy the pattern (topic type, hook style, length, structure), not the content.

1. **Our own Shorts** (Metricool, brandId `7796937`, last 14 days). "all videos" has been returning nothing, so use two calls: connector "videos published in range" (`YTVP17` title, `YTVP02` date, `YTVP06` views, `YTVP08` avg view duration, `YTVP09` likes, `YTVP11` comments) and connector "evolution" (`YTEV01` subscribers, `YTEV02` daily views, `YTEV05` subs gained). Join with `log/posts.csv` (duration, hook score, topic, structure). Note what our best ones have in common and which days gained subs. Stats lag 1-2 days.
2. **Competitors** (Metricool, connector "competitor videos", last 7 days, one connector per call): `YTCV03` channel, `YTCV06` title, `YTCV04` url, `YTCV01` date, `YTCV07` views, `YTCV08` comments, `YTCV09` likes. Rank by views. If it returns nothing, no competitors are tracked yet: skip it.
3. **vidIQ, max ONE call per day** (free plan: 150 credits/month, 5 per call). First call `vidiq_balance` (free). If total credits ≥ 5, call `vidiq_trending_videos` with videoFormat `short`, sortBy `vph`, videoPublishedAfter = 3 days ago, videoTitleLanguage `en`, limit 25. Otherwise skip.
4. **Web**: 2-3 searches for Shorts/TikTok formats and topics going viral this week.
5. Write `log/research/YYYY-MM-DD.md` (max 40 lines): top 10 videos found (channel, title, views, views/hour if known, length if known), the patterns behind them (topic type, hook phrasing, format), and what we'll borrow today.
6. Add any channel that appears repeatedly with fast-growing Shorts in a similar style (animated, explainer, trending topics, faceless) to `log/competitors.md` with its @handle and why.
7. Update `log/playbook.md`: keep it as max 15 bullets of proven patterns ("question hooks on tech trends", "under 35s", "number in the first line"), each with the evidence and date. Merge, don't just append.

Use today's research to choose the topic and shape the script. The post email must say which pattern(s) today's Short borrowed and from where.

## 1. Find today's trend
Search the web for what is blowing up in the last 24-72 hours. Run several searches in one go, for example:
- `https://trendreport.com/charts/` (today's US YouTube trending chart, fetch it) and `https://viralmint.net/trends/youtube-shorts-tracker/` (this week's breakout Shorts and niches, fetch it)
- `Google Trends trending now` / `trending searches today`
- `trending on YouTube today` / `viral TikTok trend this week`
- `Know Your Meme trending` / `viral video this week`
- `biggest tech news today`, `new movie / game / gadget everyone is talking about`
Use today's real date in queries.

Pick ONE topic that:
- has clearly rising interest right now (several sources mention it), and broad appeal (tech, AI, gadgets, games, movies, internet culture, viral moments, weird science, money/business, sports moments);
- can be turned into one clear What If question whose answer runs 3-4 escalating beats, each backed by a real number;
- is NOT in `log/topics.md` in the last 30 days.

Also read `log/learnings.md` (Sunday report) and `log/playbook.md` (daily research) and apply them to topic choice and script. If research shows a trending topic already getting big views on similar channels, prefer it.

Never pick: real tragedies, real deaths, crimes, real disasters or war (hypothetical science scenarios about Earth, space or physics are fine), elections or party politics, medical or health claims, body challenges a viewer could copy, financial "buy this" advice, real private individuals, anything involving minors, or rumors you can't confirm. Use real people only for public, factual, neutral things they did.

Verify every fact with at least one reliable source. Hedge anything unconfirmed ("reportedly"). Keep the source URLs for the log.

## 2. Write `work/script.json` (scene format, since 2026-11-13)

Why this changed: the old Shorts were one cartoon character standing in the middle with emoji stickers, the same layout every time, and about half of viewers swiped away. Now **every shot is a full-screen drawn scene that shows the thing the narration is saying**, and frame 0 is already the disaster.

The complete working example is `log/example-scenes.json` (format reference only: never reuse its topic, hook or shot list).

```json
{
 "keyword": "solar storm",
 "hook": {"screen": "The Sun just fired at us", "text": "What if one solar storm cut your power for two years?",
  "shots": [{"bg": "space", "cam": "push",
    "actors": [{"art": "sun", "at": [0.5, 0.08], "size": 0.75},
               {"art": "earth", "at": [0.5, 0.66], "size": 0.55, "state": "dark", "state_to": "dark_off", "delay": 0.5, "over": 0.35}],
    "fx": [{"name": "plasma", "t": -0.5, "at": [0.5, 0.16], "to": [0.5, 0.62]}, {"name": "shockwave", "t": 0.45, "at": [0.5, 0.64]}, {"name": "flash", "t": 0.45}]}]},
 "beats": [
  {"text": "Then satellites start falling. ...",
   "shots": [
    {"bg": "space", "cam": "pan_r", "counter": {"from": 0, "to": 38, "unit": "satellites"},
     "actors": [{"art": "earth", "at": [0.5, 1.0], "size": 1.5},
                {"art": "1f6f0", "at": [0.2, 0.2], "to": [0.75, 0.75], "size": 0.22, "count": 6, "spread": 0.3, "spin": 90, "trail": "fire", "ease": "in"}],
     "fx": ["embers"]},
    {"bg": "sky_night", "cam": "tilt_down", "actors": [{"art": "1f6f0", "at": [0.9, -0.1], "to": [0.2, 0.9], "size": 0.5, "spin": 200, "trail": "fire", "ease": "in"}],
     "fx": ["meteors", {"name": "explosion", "t": 0.85, "at": [0.25, 0.85]}]}]}
 ],
 "ask": "Could you last two years with no power?",
 "youtube": {"title": "...", "description": "...", "tags": ["..."], "category": "SCIENCE_TECHNOLOGY"}
}
```

### Shot rules (these decide whether people swipe)
1. **Cold open.** Hook shot 1 must show the most extreme consequence already happening in frame 0: the object is already in frame and already moving. Give its fx a negative `t` (e.g. `"t": -0.5`) so the effect is mid-flight at frame 0, and land an `explosion`, `shockwave` or `flash` inside the first second. Never open on a title card, a character standing there, or an empty sky.
2. **Show what is said.** For every shot, name the noun and the verb in that part of the narration, then put that noun on screen doing that verb ("satellites start falling" = satellites falling with fire trails toward Earth). If a shot could be swapped into another Short without anyone noticing, redo it.
3. **2 shots per beat** (3 if the beat is over 7 seconds), hook 1-2 shots. Use `"w"` (weight) to make a shot longer or shorter. Neighbouring shots must differ in background or actors.
4. **Something moves in every shot:** an actor with `to`, `size_to`, `spin`, `state_to` or `count`, or an fx. Vary `cam` from shot to shot.
5. **The person is a scale reference only:** `size` 0.12-0.2, at most 2 shots per Short, never the centre of the hook.
6. **Emoji art is for moving objects only** (falling, flying, exploding, in a swarm), `size` 0.45 or less. Never a static sticker. Prefer the built-in art below when it fits.
7. **One number per shot:** `counter` for the key number of the beat (it counts up), or `pop` for a short label. Not both.
8. **No template tells:** no permanent title, no watermark, no hidden item, no subscribe sticker (the renderer has none; do not ask for them). `hook.screen` (6 words or fewer) shows for the first 1.9 seconds only.
9. **Do not repeat yourself:** read the last 5 `log/*-script.json` files and use a different hook composition and a different order of backgrounds from each of them.

### Reference
- **`bg`**: `space, sky_day, sky_night, sunset, storm, ocean, ocean_night, deep` (underwater), `city_day, city_night, ground` (grass), `desert, ice, lava, moon_surface, body` (dark x-ray lab), `cells` (inside the bloodstream).
- **`art`** built-in: `earth` (`state` / `state_to`: `normal, frozen, burnt, dry, dark` (night side with city lights), `dark_off` (lights out), `flooded`; `rot_speed`), `sun`, `moon`, `mars`, `planet` (`color`), `asteroid`, `blackhole`, `person` (`pose`: `stand, arms_up, run, fall, float`; `color` = shirt), `body` (x-ray human; `organ`: any of `heart, brain, lungs, stomach, bones, blood, eyes`; `organ_scale` / `organ_scale_to` to grow or shrink them; `bpm` for heart rate). Anything else: an emoji codepoint in lowercase hex (e.g. `1f6f0` satellite, `1f30b` volcano, `1f988` shark); the build downloads it.
- **Actor fields**: `at` [x, y] and `to` [x, y] in 0-1 screen units (values outside 0-1 start or end off screen); `size` and `size_to` (fraction of screen width; for `person` it is the height); `ease` (`in` = accelerating, good for impacts; `out`; `inout`; `linear`); `delay` and `over` (fractions of the shot: when the move starts and how long it takes); `appear` / `vanish` (fractions of the shot); `enter` (`pop`, `fade`); `spin` (degrees per second); `rot`; `trail` (`fire`, `smoke`); `glow` (hex colour); `count` + `spread` (a swarm); `shake`; `bob`; `flip`. Actors draw in list order (last on top).
- **`fx`** (a name, or `{"name": ..., "t": 0-1 start as a fraction of the shot, "at": [x, y], "to": [x, y], "amount": 1, "color": "#rrggbb"}`): `explosion, shockwave, flash, shake, quake, plasma` (stream from `at` to `to`), `fire` (flames from the bottom or `at`), `smoke, embers, crack` (from `at`; give a `color` for glowing cracks), `flood` (`level` 0-1 = how high the water gets), `rain, snow, lightning, aurora, meteors, debris` (wind), `dust, bubbles, speedlines, stars_streak, freeze, heat, dark` (screen tints that build up), `lights_out` (only on `city_night`: the windows go dark).
- **`cam`**: `push, pull, pan_l, pan_r, tilt_up, tilt_down, static`. Optional `focus` [x, y].
- **`counter`**: `{"from": 0, "to": 1670, "unit": "km/h", "decimals": 0}`. **`pop`**: 1-3 words.
- **`ask`** (top level): one debatable question, 8 words or fewer, shown in the last 2 seconds and used as line 2 of the description. It must be about the topic ("Could you last two years with no power?"), never "comment below" or "spot the item".

### Hook (first 2 seconds)
- **Visual:** shot rule 1.
- **Written:** `hook.screen` = the consequence in 6 words or fewer ("The Sun just fired at us"), not the title.
- **Verbal:** `hook.text` starts at 0.25s: the What If question with the most extreme consequence and a number, 12 words or fewer. Write 3 options, score them with `python3 -I pipeline/hooks/hookscore.py hooks.txt`, use the best (75+).

### Retention rules
- **Seamless loop:** the LAST beat ends mid-sentence so its last words run straight into the hook's first words ("...Because" -> "What if one solar storm..."). The picture blends back to frame 0 by itself. No outro, no "follow for more", no thanks.
- **Micro-hooks:** 3-4 beats, each 5-7 seconds (15-20 words). Open each on the most surprising number, not on setup. Every beat after the first opens or ends with a turn: "But second three is worse", "Then it gets strange".
- **Keyword 3-4 times** in the spoken text (it is highlighted in the captions).
- Total spoken length 20-30 seconds (60-85 words). Write numbers as words. No em dashes.

## 3. Build and check
```bash
python3 -I pipeline/scenes.py work --lint        # fix every ERROR and every WARNING first
bash pipeline/make_short.sh work videos/YYYY-MM-DD-<slug>.mp4
```
Then open `work/check.jpg` with the Read tool (frame 0 first, then one frame per shot) and check, honestly:
- Frame 0 shows the event itself, big, and would make a stranger stop scrolling. If it is calm or empty, fix the hook shot and rebuild.
- Every thumbnail shows what its narration says, and no two neighbours look alike.
- Text does not cover the main object; nothing important sits in the bottom quarter (YouTube's buttons cover it).
Rebuild until all three hold (at most 3 rebuilds, then ship the best one and say so in the email).

## 4. Publish
1. Copy `work/script.json` to `log/YYYY-MM-DD-script.json`. Append to `log/topics.md`: `- YYYY-MM-DD | <topic> | <keyword> | <source urls>`.
2. Commit and push to `main`.
3. Video URL: `https://raw.githubusercontent.com/feliximmman05-creator/shorts-media/main/videos/<file>.mp4` (check it returns HTTP 200).
4. Metricool `createScheduledPost`: blogId `7796937`, ~10 minutes ahead, timezone `Asia/Calcutta`, provider `youtube`, autoPublish true. `youtubeData`: type `short`, privacy `public`, madeForKids false, isAiGeneratedContent false, category to fit (`ENTERTAINMENT`, `SCIENCE_TECHNOLOGY`, `COMEDY`, `GAMING`, `SPORTS`), 6-8 tags including the keyword. Title under 70 characters with the keyword near the start, ending `#shorts`. Description: one curiosity line with the keyword, then the `ask` question on its own line, then 4-5 hashtags.

## 5. Confirm and email
1. **Post at peak time, don't wait.** Call Metricool `getBestTimeToPostByNetwork` (brandId `7796937`, network `youtube`, timezone `Asia/Calcutta`, today 00:00 to 23:59). Morning run: schedule for the best hour between 14:00 and 18:00 IST. Evening run: schedule for the best hour between 19:30 and 23:30 IST. If that hour is less than 15 minutes away, schedule 10 minutes ahead. Do NOT sleep or wait for the publish (the 2026-11-12 run errored after 98 minutes, much of it spent waiting).
2. Call `getScheduledPosts` once to confirm the post exists with status PENDING (or PUBLISHED). The next run back-fills the YouTube URL.
3. Append the row in `log/posts.csv`: `date,title,youtube_url,topic,keyword,duration_s,hook_score,file` (duration from `ffprobe`; `youtube_url` = `PENDING` until back-filled; put the structure a/b/c in the topic field, e.g. `(a) Concord shutdown`). Commit and push.
4. Send the email with Gmail `send_message` to `feliximmman05@gmail.com`, `htmlBody`, subject `✅ New Short scheduled: <title>` (or `⚠️ Short failed: <reason>`). Contents:
   - Title, scheduled publish time (IST), status, plus the YouTube links back-filled this run
   - Trend picked and why it's trending (1-2 lines + source links)
   - What today's research found (top 3 videos from other channels with views) and which pattern this Short borrowed
   - Hook: on-screen text, spoken line, hook score
   - Keyword, length, end question (`ask`), and one line on what frame 0 shows
   - Description and tags used
   - Metricool planner link
   Keep it short and clean: one heading, a small table, no images.
