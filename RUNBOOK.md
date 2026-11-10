# Daily Short runbook (Into the Dark Web, @ShadowMan0011)

One Short per day. Animated stick man explainer on whatever is trending **right now**, 30-45 seconds, built to loop.

## 0. Research what's working (every run, before picking a topic)
Learn patterns from other channels and our own stats. Never copy another channel's script, title wording, characters or footage. Copy the pattern (topic type, hook style, length, structure), not the content.

1. **Our own Shorts** (Metricool, brandId `7796937`, last 14 days, connector "all videos"): `YTVV17` title, `YTVV01` date, `YTVV06` views, `YTVV08` avg view duration, `YTVV09` likes, `YTVV11` comments, `YTVV12` shares. Join with `log/posts.csv` (duration, hook score, topic). Note what our best ones have in common. Stats lag 1-2 days.
2. **Competitors** (Metricool, connector "competitor videos", last 7 days, one connector per call): `YTCV03` channel, `YTCV06` title, `YTCV04` url, `YTCV01` date, `YTCV07` views, `YTCV08` comments, `YTCV09` likes. Rank by views. If it returns nothing, no competitors are tracked yet: skip it.
3. **vidIQ, max ONE call per day** (free plan: 150 credits/month, 5 per call). First call `vidiq_balance` (free). If total credits ≥ 5, call `vidiq_trending_videos` with videoFormat `short`, sortBy `vph`, videoPublishedAfter = 3 days ago, videoTitleLanguage `en`, limit 25. Otherwise skip.
4. **Web**: 2-3 searches for Shorts/TikTok formats and topics going viral this week.
5. Write `log/research/YYYY-MM-DD.md` (max 40 lines): top 10 videos found (channel, title, views, views/hour if known, length if known), the patterns behind them (topic type, hook phrasing, format), and what we'll borrow today.
6. Add any channel that appears repeatedly with fast-growing Shorts in a similar style (animated, explainer, trending topics, faceless) to `log/competitors.md` with its @handle and why.
7. Update `log/playbook.md`: keep it as max 15 bullets of proven patterns ("question hooks on tech trends", "under 35s", "number in the first line"), each with the evidence and date. Merge, don't just append.

Use today's research to choose the topic and shape the script. The post email must say which pattern(s) today's Short borrowed and from where.

## 1. Find today's trend
Search the web for what is blowing up in the last 24-72 hours. Run several searches in one go, for example:
- `Google Trends trending now` / `trending searches today`
- `trending on YouTube today` / `viral TikTok trend this week`
- `Know Your Meme trending` / `viral video this week`
- `biggest tech news today`, `new movie / game / gadget everyone is talking about`
Use today's real date in queries.

Pick ONE topic that:
- has clearly rising interest right now (several sources mention it), and broad appeal (tech, AI, gadgets, games, movies, internet culture, viral moments, weird science, money/business, sports moments);
- can be explained in 30-45 seconds with a "wait, what?" angle;
- is NOT in `log/topics.md` in the last 30 days.

Also read `log/learnings.md` (Sunday report) and `log/playbook.md` (daily research) and apply them to topic choice and script. If research shows a trending topic already getting big views on similar channels, prefer it.

Never pick: tragedies, deaths, crimes, disasters, war, elections or party politics, medical or health claims, financial "buy this" advice, real private individuals, anything involving minors, or rumors you can't confirm. Use real people only for public, factual, neutral things they did.

Verify every fact with at least one reliable source. Hedge anything unconfirmed ("reportedly"). Keep the source URLs for the log.

## 2. Write `work/script.json`

```json
{
 "keyword": "emu war",
 "hook": {"screen": "Birds beat an army", "text": "The emu war is the only war humans ever lost to birds, and",
          "prop": "1f426", "pose": "point"},
 "beats": [
  {"text": "...", "poses": ["explain", "shock"], "prop": "1f33e", "pop": "20,000 EMUS"},
  {"text": "...", "poses": ["hold", "facepalm"], "prop": "1f52b", "pop": "MACHINE GUNS"},
  {"text": "...", "poses": ["run", "shock"], "prop": "1f4a8"},
  {"text": "... The emu war is real, and it proves", "poses": ["sad", "shrug"], "prop": "1f3f3"}
 ],
 "hidden": {"emoji": "1f95a", "beat": 1},
 "youtube": {"title": "...", "description": "...", "tags": ["..."], "category": "ENTERTAINMENT"}
}
```
A complete working example is in `log/example-script.json`.

### Triple hook (first 3 seconds; the renderer handles timing)
- **Visual (0-1s):** the stick man slams `hook.prop` (impact, shake, flash). Pick a prop that is the topic's object.
- **Written (0-1.5s):** `hook.screen` = 3-5 words, curiosity or a bold promise ("Stop doing this", "This changes everything", "Birds beat an army"). Big and centered.
- **Verbal (starts ~0.7s):** `hook.text` = one punchy line that confirms the topic and opens a curiosity gap. No greetings, no "hey guys". Write 3 options, score them with `python3 -I pipeline/hooks/hookscore.py hooks.txt`, and use the best (60+).

### Retention rules
- **Seamless loop:** `hook.text` starts mid-thought, and the LAST beat ends mid-sentence so its last words run straight into the hook's first words ("...and it proves" → "The emu war is the only war..."). Read last + first aloud together: it must sound like one sentence. No outro, no "follow for more", no "thanks for watching".
- **Micro-hooks:** 3-5 beats, each 5-7 seconds (about 14-22 words). Every beat after the first opens or ends with a curiosity line: "But that's where things went completely wrong", "And then it got worse", "Here's the part nobody talks about", "But wait, it gets weirder".
- **Keyword 5-7 times:** put the exact `keyword` phrase in the spoken text 5-7 times in total (hook + beats). It is highlighted green in the captions.
- **Comment bait:** set `hidden` to a small unrelated emoji shown for about 1 second during that beat. The video shows "Spot the hidden item? Comment what it was" at the end, and the description asks the same. Never add deliberate factual mistakes.
- Total spoken length 30-45 seconds. Write numbers as words. No em dashes.

### Visual fields
- `poses` (1-2 per beat, alternated about every 1.8s with camera cuts): `talk, explain, point, shock, shrug, facepalm, celebrate, think, sad, hold, run, idle`. Match the emotion of the words.
- `prop`: one Twemoji codepoint per beat (lowercase hex, e.g. `1f4f1` phone, `1f916` robot, `1f4b8` money, `1f3ae` game controller, `1f525` fire). Flags look like `1f1fa-1f1f8`.
- `pop` (optional, most beats): 1-3 word sticker label, e.g. a number or "BUT WAIT".

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
1. Schedule the post only ~5 minutes ahead. Then run `sleep 480` in the background (Bash `run_in_background`) and continue when it finishes.
2. Check Metricool `getScheduledPosts` (brandId `7796937`, today's date range, timezone `Asia/Calcutta`). When the YouTube provider status is `PUBLISHED`, take its `publicUrl`. If still pending, wait another 5 minutes, check again (max 3 checks). If it shows an error, say so in the email.
3. Append a row to `log/posts.csv`: `date,title,youtube_url,topic,keyword,duration_s,hook_score,file` (duration from `ffprobe`). Commit and push.
4. Send the email with Gmail `send_message` to `feliximmman05@gmail.com`, `htmlBody`, subject `✅ New Short posted: <title>` (or `⚠️ Short failed: <reason>`). Contents:
   - Title, YouTube link, publish time (IST), status
   - Trend picked and why it's trending (1-2 lines + source links)
   - What today's research found (top 3 videos from other channels with views) and which pattern this Short borrowed
   - Hook: on-screen text, spoken line, hook score
   - Keyword, length, hidden item
   - Description and tags used
   - Metricool planner link
   Keep it short and clean: one heading, a small table, no images.
