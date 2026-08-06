# Kaggriculture

Agent for Kaggle's [Kaggriculture](https://www.kaggle.com/competitions/kaggriculture) simulation
competition — a turn-based farming/economy game (720 turns, 30 in-game days), head-to-head against
another agent, ranked by a skill-rating ladder. Entry deadline 2026-09-23, final submission
2026-09-30.

## Status

Just getting started. See `STRATEGY.md` for the design philosophy driving the agent (long-horizon
expected-value optimization over hand-written reactive rules — world model, scheduler, lookahead
search, ROI-scored decisions for crops/animals/land/market, endgame liquidation).

Plan:
1. Get a correct, never-misses-water/feed/harvest baseline running locally against the built-in
   `random` and `starter` agents.
2. Layer in ROI-scored decisions for crop/animal choice, land expansion, hiring.
3. Add lookahead (reuse the real engine — `kaggle_environments.envs.kaggriculture.kaggriculture` —
   as the forward simulator rather than reimplementing the rules) to score candidate plans a few
   turns out.
4. Endgame liquidation logic for the final days.
5. Submit, iterate based on ladder results (5 submissions/day, only latest 2 scored).

## Local setup

```
python -m venv .venv
./.venv/Scripts/pip install -U kaggle-environments   # Windows; use .venv/bin/pip elsewhere
```

## Submitting

Requires a Kaggle API token at `~/.kaggle/access_token` (not committed — see `.gitignore`).

```
kaggle competitions submit kaggriculture -f main.py -m "message"
```
