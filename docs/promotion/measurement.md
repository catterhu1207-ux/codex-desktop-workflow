# Measurement plan

Review the following public signals every week and at day 30.

## Primary funnel

| Stage | Source | Day 7 target | Day 14 target | Day 30 target |
|---|---|---|---|---|
| Repository visits | GitHub Traffic | 100 uniques | 250 uniques | 600 uniques |
| Release bundle downloads | GitHub Releases | 3 | 8 | 20 |
| Completed installs reported | Discussions / Issues | 1 | 4 | 10 |
| Useful feedback items | Discussions / Issues | 1 | 3 | 5 |
| Stars | GitHub | 5 | 12 | 25 |

The install target is a report of a completed `inspect/build/verify` run or uninstall-free use, not a download count alone.

## Referrers to watch

- V2EX
- Zhihu
- Bilibili
- Xiaohongshu
- news.ycombinator.com
- reddit.com
- x.com
- dev.to
- GitHub search and topic pages

## Decision rules

- High views, low bundle downloads: rewrite the first screen, demo, and install command.
- High downloads, low feedback: test the installer and first-run experience.
- Low views across all channels: increase Chinese short-video and community distribution.
- Repeated install failures: pause promotion and fix the failing prerequisite or package version.

## Day 30 report

Include:

- the funnel table with actual numbers;
- the top referrer and the weakest conversion step;
- five concrete user questions or objections;
- the three features users asked for most;
- a v0.3 decision: adapt a new version, improve first-run setup, or fix installer friction.
