# V45 live replay investigation

Submission56278443, public score2703.1 at query. Snapshot has81 completed games:
60 external wins,20 external losses,1 self-play loss. The self-play is not an
external defeat. Top10 cutoff in the downloaded leaderboard:3017.9; leader3179.0.
Scores are time-specific snapshots, not converged-rating claims.

Downloaded all81 available own games plus15 additional unique games, representing
two recent matches per top10 team. Total96 unique replays. Cash reconstruction
verified138048 player-turn transitions without mismatches. All20 external losses
end with zero crop yield left on tiles. This does not measure historical harvest
misses or animal yield, but rejects leftover terminal crops as the common cause.

## Loss families

14/20 losses meet the near-clone screen: >=97% identical worker-command turns and
equal sold quantities for milk,wool,tomato,carrot,melon,egg. This screen excludes
wheat arbitrage, fertilizer and strawberry quantities; it is not a proof of
identical farms. Fifteen losses have margins below500coins. Six residual cases
need separate production/opening analysis, rather than being called all-timing.

| Opponent / episode | Margin | Measured evidence |
|---|---:|---|
|Rasmus Hulthe109717409|-2813|By day12: rival8cow/4sheep/5geese vs8/6/3. Sold153eggs vs82 and128carrots vs94. Egg receipts+3760 and carrot receipts+1988 for rival; these are gross components, not net counterfactual gains.|
|Justin Yang109727079|-1388|Worker agreement98.7%; strawberry sales251vs249, milk222each. Strawberry receipt gap1250, milk1024. Production and timing both matter.|
|Roxy109726067|-1211|Own11melons at day1 vs12; final melon sales66vs72, receipts1258lower. Opening BUY29/SELL29 differs from our70/70.|
|yang zhang109729255|-780|100% worker-command agreement, identical sold quantities for every product; strawberry receipts908lower.|
|KongKongDe109724919|-511|Own11melons at day1 vs12; final66vs72melons,1258receipt deficit. Opponent opening BUY43/SELL38.|

No inference that gross receipt gaps can simply be added to our score: changing
production changes labor, feed, capital, market prices and the opponent's receipts.

## Top10 comparison

Two replays per player are a small descriptive sample, not recovered policies.
Leader Majkel1337 has day18 herds5cow/9sheep/4geese in one game and13/4/0 in the
other, alongside different crop mixes. Rank2 has4/6/13 with6 tomato plants in one
game,11/2/5 with28 tomato plants in the other. These observations show substantially
different allocations across worlds. They do not establish the exact algorithm
or prove that copying those configurations would improve our results.

## Recommended next experiments

1. Opening resource contract: reproduce the Roxy/KongKongDe seed deficit and find
   a fully funded twelve-melon schedule that preserves day1 hiring and feed.
   Test against70/70 mirrors AND29/29,43/38,5/5 and split-buy openings. Changing
   the first order is a pre-observation decision; do not assume we know it in advance.
2. Adaptive production within V45: evaluate a complete five-geese/four-sheep
   schedule plus late-carrot work where demand supports it. Optimize service,
   feeding, harvesting and sales together; swapping animal purchases alone is unsafe.
   Rasmus is the concrete target case, not proof that its mix is globally better.
3. Market quote controller: use actual stock and inferred public rival selling
   to address the many small near-clone losses. Evaluate per-product timing and
   price, not another unconditional horizon increase. Keep current reservation
   and pickup protections.

Acceptance: baseline reward reproduction, targeted mechanism improvement, fresh
paired seeds, preserved winning controls, distinct-family panel. Do not claim
top10 readiness from beating our own ancestor. No new model or submission in this
investigation. Counterfactual original-V45 controls are saved separately under
analysis/v45_loss_controls_20260916; fixed recordings cannot react to our changes.

## Original-V45 control check completed

Forty games: submitted and original on each of20 original loss seeds/seats.
All20 submitted reward pairs exactly reproduce the replay. Original wins two:
KongKongDe109724919 (+109 versus submitted-511), Hai Dang109728165 (+755 versus
submitted-324). Original loses the other18. Proactive improves margins in15,
worsens3 and leaves2 unchanged. Therefore two counterfactual lost wins are a
concrete selective-sale-rule target. This is a loss-selected dataset, not a fair
overall comparison of the policies; the60 winning controls must be protected.
It does not warrant a blind rollback or establish how live rivals would react.
