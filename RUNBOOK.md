# Daily Shorts runbook (Peak Dumb, @peakdumbtv)

Two Shorts per day (morning run + evening run), every one a **"What If" scenario** (see the format below), 20-35 seconds, cartoon character in a new scene every step, built to loop.

## Channel strategy (lane changed from "dumbest decisions" to "What If" on 2026-11-12 by the owner's request; overrides anything below that conflicts)
**Goal:** YouTube Partner Program: 1,000 subscribers + 10 million Shorts views inside a 90-day window. No guarantee exists; the job is to maximise the odds every day.

**Where we are (2026-11-12):** 6 subs, 4,149 lifetime views, 9 Shorts before the change. 96% of views come from the Shorts feed. Only ~53% of feed views become engaged views (target 70%+). 2 subs per ~2,500 views (0.08%).

**Why one lane:** topics were all over the place, so a viewer who likes one Short has no reason to subscribe. The owner chose "What If" as the single lane. First What If Short: "What If Earth Stopped Spinning for 5 Seconds?" (2026-11-12); no stats for the lane yet, so the Sunday report must judge it on real numbers.

1. **One lane, every Short:** a "What If" question about something impossible, extreme or huge (space, Earth, physics, animals, tech/AI, games, cars, the internet, money at absurd scale), answered step by step with real science and real numbers. Prefer a question tied to what is trending this week (a launch, a game, a movie, a viral clip, a science story). If the week's trend gives no good question, use an evergreen one that has not been used in 30 days. No old-history topics.
2. **Hook formula:** "What if [impossible thing] for just [short time / one change]?" The question is on screen and spoken in the first 2 seconds. Then the chain: each beat = what happens next -> the real number behind it -> something worse or stranger. Twist or survival answer at the end, loop.
3. **Rotate the structure** so uploads are never near-identical (YouTube demonetises templated, mass-produced channels): (a) countdown timeline ("Second 1... Second 3... Second 5", or minute/day/year), (b) second-person survival ("You're standing in [place] when [it happens]"), (c) "Which would be worse: A or B?" Never the same structure three runs in a row. Every script is original research and original wording.
4. **Titles:** start with "What If", then the subject, under 60 characters, always a question ("What If the Moon Vanished Tonight?"). End `#shorts`.
5. **Subscribe reason:** one `pop` sticker on the second-to-last beat: "DAILY WHAT IF → SUB". Description line 1 ends with "New What If every day."
6. **Per-Short targets:** engaged views ÷ views ≥ 70%, average viewed ≥ 85%. First 2 seconds decide it: start on the question and the most extreme consequence, never on setup. If three Shorts in a row miss both targets, change the hook style, not the niche.
7. **Real science, clearly hypothetical.** Every number comes from a reliable source; estimates are said as estimates. Nothing a viewer could copy and get hurt by (no "what if you stopped eating/sleeping/breathing" body challenges, no drugs, no stunts). No real person shown being harmed.
8. **Two per day, never more.** More than that reads as spam and adds no reach.
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
2. **Guard:** count rows with today's date (IST). Morning run (before 14:00 IST): if there is already one, stop after the back-fill. Evening run (14:00 IST or later): if there are already two, stop after the back-fill. Never make a third.
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

## 2. Write `work/script.json`

```json
{
 "format": "master-plan",
 "role": "Khufu",
 "keyword": "Great Pyramid",
 "hook": {"screen": "Build the impossible tomb", "text": "You're Pharaoh Khufu, and you want the Great Pyramid... But there's a problem.",
          "prop": "1f451", "pose": "point", "scene": "desert", "set": ["1f3dc"]},
 "beats": [
  {"text": "First, you need stone... So you open a quarry right next to the Great Pyramid.", "poses": ["explain", "shock"], "prop": "1f697", "pop": "2.3 MILLION BLOCKS", "scene": "desert", "set": ["1faa8"]},
  {"text": "But the best limestone is across the river. So you...", "poses": ["point", "hold"], "prop": "1f4dc", "pop": "NILE FLOOD", "scene": "ocean", "set": ["26f5"]},
  {"text": "... people still say aliens built the Great Pyramid, when really", "poses": ["celebrate", "shrug"], "prop": "1f47d", "scene": "night", "set": ["1f6f8"]}
 ],
 "hidden": {"emoji": "1f36a", "beat": 2},
 "youtube": {"title": "...", "description": "...", "tags": ["..."], "category": "ENTERTAINMENT"}
}
```
The complete working example is `log/example-script.json` (GTA 6 week; loop: "...Probably another" → "Thirteen years for GTA Six...").

### Triple hook (first 3 seconds; the renderer handles timing)
- **Visual (0-1s):** the stick man slams `hook.prop` (impact, shake, flash). Pick a prop that is the topic's object.
- **Written (0-1.5s):** `hook.screen` = 3-5 words, curiosity or a bold promise ("Stop doing this", "This changes everything", "Birds beat an army"). Big and centered.
- **Verbal (starts ~0.7s):** `hook.text` = one punchy line that confirms the topic and opens a curiosity gap. No greetings, no "hey guys". Write 3 options, score them with `python3 -I pipeline/hooks/hookscore.py hooks.txt`, and use the best (75+; say "you" and keep it under ~15 words).

### Retention rules
- **Seamless loop:** `hook.text` starts mid-thought, and the LAST beat ends mid-sentence so its last words run straight into the hook's first words ("...and it proves" → "The emu war is the only war..."). Read last + first aloud together: it must sound like one sentence. No outro, no "follow for more", no "thanks for watching".
- **Micro-hooks:** 3-4 beats, each 5-7 seconds (about 15-20 words). Open on the most surprising number, not on setup. Every beat after the first opens or ends with a curiosity line: "But that's where things went completely wrong", "And then it got worse", "Here's the part nobody talks about", "But wait, it gets weirder".
- **Keyword 3-4 times:** put the exact `keyword` phrase in the spoken text 3-4 times in total (hook + beats). It is highlighted green in the captions.
- **Comment bait:** set `hidden` to a small unrelated emoji shown for about 1 second during that beat. The video shows "Spot the hidden item? Comment what it was" at the end, and the description asks the same. Never add deliberate factual mistakes.
- Total spoken length 20-30 seconds (about 60-85 words). End the last beat as a question to the viewer so it loops and drives comments. Write numbers as words. No em dashes.

### Visual fields
- `poses` (1-2 per beat, alternated about every 1.8s with camera cuts): `talk, explain, point, shock, shrug, facepalm, celebrate, think, sad, hold, run, idle`. Match the emotion of the words.
- `prop`: one Twemoji codepoint per beat (lowercase hex, e.g. `1f4f1` phone, `1f916` robot, `1f4b8` money, `1f3ae` game controller, `1f525` fire). Flags look like `1f1fa-1f1f8`.
- `pop` (optional, most beats): 1-3 word sticker label, e.g. a number or "BUT WAIT".
- `role`: the name tag above the stick man's head (who "you" are), max ~12 characters.
- `scene` (hook and every beat; change it whenever the plan moves somewhere new, like the reference does): `vice` (neon sunset city), `city, night, lab, factory, stadium, space, moon, earth, ocean, desert, grass, paper`.
- `style`: `cartoon` (big-head cartoon person) or `stick`. `look` (cartoon only): `skin, hair, shirt, pants` hex colours, `hair_style` (`short, long, spiky, bald`), `hat` (an emoji code, e.g. `1f9e2` cap, `1f451` crown, `1fa96` helmet). Pick a bright shirt that stands out from the scene.
- `set` (hook and every beat): 1-2 big Twemoji set pieces behind the stick man that show where we are or what is being built (e.g. `1f3ed` factory, `1f680` rocket, `1f6f0` satellite, `1f697` car, `1f916` robot, `1f3e2` office, `2600` sun, `1f319` moon).

## 3. Build and check
```bash
bash pipeline/make_short.sh work videos/YYYY-MM-DD-<slug>.mp4
```
Extract frames and look at them:
`ffmpeg -i <video> -vf "select='eq(n\,0)+eq(n\,40)+eq(n\,300)+eq(n\,600)',scale=270:-1,tile=4x1" -frames:v 1 check.png`
Text must not overflow or cover the stick man's face. Fix the script (shorter `screen`/`pop` text) and rebuild if needed.

## 4. Publish
1. Copy `work/script.json` to `log/YYYY-MM-DD-script.json`. Append to `log/topics.md`: `- YYYY-MM-DD | <topic> | <keyword> | <source urls>`.
2. Commit and push to `main`.
3. Video URL: `https://raw.githubusercontent.com/feliximmman05-creator/shorts-media/main/videos/<file>.mp4` (check it returns HTTP 200).
4. Metricool `createScheduledPost`: blogId `7796937`, ~10 minutes ahead, timezone `Asia/Calcutta`, provider `youtube`, autoPublish true. `youtubeData`: type `short`, privacy `public`, madeForKids false, isAiGeneratedContent false, category to fit (`ENTERTAINMENT`, `SCIENCE_TECHNOLOGY`, `COMEDY`, `GAMING`, `SPORTS`), 6-8 tags including the keyword. Title under 70 characters with the keyword near the start, ending `#shorts`. Description: one curiosity line with the keyword, then "Did you spot the hidden item? Comment what it was 👀", then 4-5 hashtags.

## 5. Confirm and email
1. **Post at peak time, don't wait.** Call Metricool `getBestTimeToPostByNetwork` (brandId `7796937`, network `youtube`, timezone `Asia/Calcutta`, today 00:00 to 23:59). Morning run: schedule for the best hour between 14:00 and 18:00 IST. Evening run: schedule for the best hour between 19:30 and 23:30 IST. If that hour is less than 15 minutes away, schedule 10 minutes ahead. Do NOT sleep or wait for the publish (the 2026-11-12 run errored after 98 minutes, much of it spent waiting).
2. Call `getScheduledPosts` once to confirm the post exists with status PENDING (or PUBLISHED). The next run back-fills the YouTube URL.
3. Append the row in `log/posts.csv`: `date,title,youtube_url,topic,keyword,duration_s,hook_score,file` (duration from `ffprobe`; `youtube_url` = `PENDING` until back-filled; put the structure a/b/c in the topic field, e.g. `(a) Concord shutdown`). Commit and push.
4. Send the email with Gmail `send_message` to `feliximmman05@gmail.com`, `htmlBody`, subject `✅ New Short scheduled: <title>` (or `⚠️ Short failed: <reason>`). Contents:
   - Title, scheduled publish time (IST), status, plus the YouTube links back-filled this run
   - Trend picked and why it's trending (1-2 lines + source links)
   - What today's research found (top 3 videos from other channels with views) and which pattern this Short borrowed
   - Hook: on-screen text, spoken line, hook score
   - Keyword, length, hidden item
   - Description and tags used
   - Metricool planner link
   Keep it short and clean: one heading, a small table, no images.
