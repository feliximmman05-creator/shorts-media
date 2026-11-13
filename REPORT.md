# Sunday weekly report

Runs every Sunday evening. Emails `feliximmman05@gmail.com` a summary of the week's Shorts and an honest analysis of the channel.

## 1. Gather data
- `log/posts.csv`: every Short posted (this week = last 7 days, plus all-time).
- `log/topics.md`, `log/*-script.json`: topics, hooks, keywords, beats.
- `log/research/*.md`, `log/playbook.md`, `log/competitors.md`: what other channels did this week.
- Metricool `getAnalyticsDataByMetrics`, brandId `7796937`. **Call each connector separately** (mixing connectors returns only one):
  - Channel trend, this week and the week before: `YTEV01` subscribers, `YTEV05` gained, `YTEV06` lost, `YTEV02` views, `YTEV13` views on videos published in range, `YTEV19` shares.
  - Per video, all time: `YTVV17` title, `YTVV05` url, `YTVV01` date, `YTVV06` views, `YTVV08` avg view duration (seconds), `YTVV09` likes, `YTVV11` comments, `YTVV12` shares.
  - `YTTS01`+`YTTS02` traffic sources; `YTDP01`+`YTDP02` countries.
- Metricool per-video stats lag 1-2 days. If a video has no stats yet, say "stats pending", don't guess.

## 2. Analyze
Compute for each video and for the week:
- **APV estimate** = avg view duration ÷ video length (`duration_s` in posts.csv). Target 85%+. Over 100% means people rewatch (the loop is working).
- Like rate (likes ÷ views), comment rate, share rate, subscribers gained per 1,000 views.
- Week-over-week change in views, subscribers, avg APV.
- Best and worst video, and **why**: compare their topic type, hook text, hook score, length, keyword, posting day.
- Patterns across all videos once there are 5+ (e.g. tech trends beat movie trends, shorter beats longer, which hook styles work).
- **Us vs competitors:** our median views vs tracked competitors' median Shorts views; which of their patterns we used and whether they worked for us.
- Progress toward YouTube Partner Program: 1,000 subscribers and 10 million Shorts views in 90 days (or 4,000 watch hours on long videos). Show current numbers and the pace needed.

Be honest. Small numbers early on are normal; say what is and isn't meaningful yet. Never invent figures.

## 3. Improvements
Give 3-5 concrete, specific changes ranked by expected impact (e.g. "hooks phrased as a question got 2x APV, so use question hooks", "cut to 30s", "avoid celebrity topics"). Then:
- Clean up `log/playbook.md`: drop patterns that didn't work for us after 3+ tries, keep the proven ones.
- Overwrite `log/learnings.md` with the current top lessons (max 8 bullets, each with the evidence). The daily run reads this file.
- Do NOT change the pipeline code yourself. If a code change is needed (voice, animation, timing), list it in the email under "Changes that need your OK".
- Commit and push.

## 4. Email
Gmail `send_message` to `feliximmman05@gmail.com`, `htmlBody`, subject `📊 Weekly channel report: <start date> – <end date>`.
Sections:
1. **Headline numbers** (small table): views, subscribers (+gained / -lost), avg APV, shares, comments, vs last week with ↑/↓.
2. **This week's Shorts**: table with date, title (linked), views, APV, likes, comments, shares.
3. **Best and worst** and why.
4. **What's working / what isn't**.
5. **Improvements** (ranked), plus "Changes that need your OK" if any.
6. **Competitors**: what worked for them this week; channels in `log/competitors.md` not yet tracked in Metricool, listed so the owner can add them (Metricool → Analytics → YouTube → Competitors).
7. **Monetization progress** with pace needed.
8. **Next week's plan** in 2-3 lines.
Clean HTML, inline CSS only, no images, mobile friendly.

## Strategy checkpoints (added 2026-11-12)
Read "Channel strategy" at the top of RUNBOOK.md. Every report must: (1) grade the current checkpoint (day 14 / 30 / 60) with real numbers; (2) show engaged views ÷ views and average viewed per Short, split by structure (a/b/c) where known; (3) say which structure and hook style is winning and tell the daily runs to lean into it via log/learnings.md; (4) if a checkpoint is missed, propose one concrete change under "Changes that need your OK". Channel is Peak Dumb (@peakdumbtv); its lane changed to "What If" on 2026-11-12, so compare What If Shorts against the earlier ones.

## Two-per-day switch and scene format (added 2026-11-13)
- Shorts dated 2026-11-13 evening or later use the new scene renderer (full-screen drawn scenes, cold open, no title bar, watermark or hidden item). Compare them against the older character-and-emoji Shorts as two groups and say plainly whether engaged views ÷ views and average viewed improved.
- The first line of `log/learnings.md` must always be either `two_per_day: no` or `two_per_day: yes`. Write `yes` only when engaged views ÷ views for the week's new-format Shorts is 65% or higher (or, if engaged views are unavailable, APV estimate 85% or higher on at least 3 Shorts). Otherwise `no`. The evening run reads this line.
- For the best and worst Short, look at `log/<date>-script.json` and name the hook shot (what frame 0 showed) as part of the "why".
