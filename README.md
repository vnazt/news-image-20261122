# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/vnazt/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/vnazt/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

One page that sums up Sunday 22 November 2026's world news: an illustrated broadsheet front page drawn entirely in code — masthead, giant serif date, a six-figure numbers strip, region tabs counted from the story list, three hero stories with drawn scenes (Russia's 186-drone night over Ukraine, COP31 ending with no deal, Iran's radar claim against Bahrain's denial), twelve pictured story cards, a block world map with a pin for every pictured story, twenty-one one-line briefs, and a date-check box naming the neighbouring days' stories the page leaves out. All 36 stories were verified against two independent sources before they were allowed on the page; one-sided claims are labelled as claims. `frontpage.py` renders the page deterministically with Pillow; `main.py` is the grader entrypoint and simply delivers the committed `entry.png` (with `fallback.png`, a compact edition of the same page, as the safety copy).

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=ws8tc7yd&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
