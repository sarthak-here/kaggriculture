"""Final v35 architecture: one robust tape plus three sparse feedback experts.

Route selection is intentionally absent.  Current Top-10 walk-forward results
showed that the former public-layout router consistently selected the weaker
continuation.  The policy remains closed-loop where observation has measured
value: legality/weed recovery, SELL ordering and near-clone preemption, and a
capital-reserved WHEAT round trip.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass

from v23.planner import build_sparse_planner
from v24.market_maker import MarketMakerConfig, wrap_market_maker
from v32.preemption import LatchedPreemptionConfig, wrap_latched_sell_preemption


@dataclass(frozen=True)
class V35FixedHybridConfig:
    clone_horizon: int = 1
    clone_detection_start: int = 48
    clone_active_stop: int = 679
    clone_distance_threshold: float = 2.0
    clone_streak_required: int = 24
    maximum_sell_batch: int = 100
    maximum_market_orders: int = 10
    market_item: str = "WHEAT"
    market_quantity: int = 10
    market_reserve: float = 500.0
    market_start: int = 72
    market_stop: int = 716
    feed_days_reserve: float = 2.0
    investment_horizon: int = 2
    shed_headroom: int = 10


def build_v35_fixed_hybrid(
    actions: list[dict],
    config: V35FixedHybridConfig = V35FixedHybridConfig(),
):
    """Compile a 719-action route into the sparse v35 feedback policy."""

    if not isinstance(actions, list) or len(actions) != 719:
        raise ValueError("v35 backbone must contain exactly 719 actions")
    route = copy.deepcopy(actions)
    policy = build_sparse_planner(copy.deepcopy(route))
    policy = wrap_latched_sell_preemption(
        policy,
        route,
        LatchedPreemptionConfig(
            horizon=max(1, int(config.clone_horizon)),
            detection_start=max(0, int(config.clone_detection_start)),
            active_stop=max(0, int(config.clone_active_stop)),
            clone_distance_threshold=max(
                0.0, float(config.clone_distance_threshold)
            ),
            clone_streak_required=max(1, int(config.clone_streak_required)),
            maximum_batch=max(0, int(config.maximum_sell_batch)),
            maximum_orders=max(1, int(config.maximum_market_orders)),
        ),
    )
    policy = wrap_market_maker(
        policy,
        route,
        MarketMakerConfig(
            item=str(config.market_item),
            start_step=max(0, int(config.market_start)),
            stop_entry_step=max(0, int(config.market_stop)),
            max_batch=max(0, int(config.market_quantity)),
            minimum_expected_profit=1.0,
            mirror_minimum_expected_profit=1.0,
            minimum_cash_reserve=max(0.0, float(config.market_reserve)),
            feed_days_reserve=max(0.0, float(config.feed_days_reserve)),
            investment_horizon=max(0, int(config.investment_horizon)),
            shed_headroom=max(0, int(config.shed_headroom)),
        ),
    )
    policy.v35_config = config
    policy.open_loop_routes = 1
    policy.route_switching = False
    return policy

