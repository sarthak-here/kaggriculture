# Kaggriculture Grandmaster Strategy Guide
## Complete Design Document for Building a Top Leaderboard Agent

---

# OBJECTIVE

Your goal is NOT to maximize short-term profit.

Your goal is to maximize

    FINAL BANK MONEY
    AFTER 720 TURNS

while defeating another adaptive player.

Everything should be optimized toward winning the final game.

The game is a sequential optimization problem under uncertainty.

Think like:

- AlphaGo
- DeepMind Planner
- Operations Research Solver
- Supply Chain Optimizer
- Resource Scheduler

Never think like a rule-based farming bot.

---

# PRIMARY OPTIMIZATION TARGET

Maximize

Expected Final Coins

NOT

Immediate Profit

NOT

Current Inventory

NOT

Crop Yield

Everything exists only to increase final bank balance.

---

# THINKING HIERARCHY

Always think in this order.

Level 1
Can I survive?

↓

Level 2
Can I increase production?

↓

Level 3
Can I optimize labor?

↓

Level 4
Can I manipulate market prices?

↓

Level 5
Can I outperform opponent?

↓

Level 6
Can I maximize final bank value?

---

# EVERY TURN

Never issue actions randomly.

Each turn run this pipeline.

Observe

↓

Update world model

↓

Predict future

↓

Evaluate possible plans

↓

Score every plan

↓

Choose highest expected value

↓

Execute

---

# WORLD MODEL

Maintain internal state including

Current day

Current hour

Remaining turns

Current money

Current inventory

Seeds

Animals

Land

Workers

Crop ages

Water schedule

Feed schedule

Harvest schedule

Fertilizer schedule

Market prices

Town demand

Unlocked shops

Expected future prices

Opponent farm state

Opponent production

Expected opponent sales

Expected future cashflow

Never recompute everything from scratch.

Incrementally update state.

---

# NEVER BE REACTIVE

Bad bot:

Price increased

Sell.

Good bot:

Price increased.

Will it increase even more?

Should inventory be held?

Will opponent flood market?

What happens after town consumption?

Should I wait?

Always reason ahead.

---

# LONG HORIZON PLANNING

The game lasts

720 turns

Do not optimize current turn.

Optimize

Entire season.

Think

Day 0

↓

Day 30

as one optimization problem.

---

# ALWAYS PREDICT

Predict

Price tomorrow

Price in 2 days

Price in 5 days

Town demand

Inventory growth

Animal production

Crop harvest

Cash flow

Labor availability

Land utilization

Future bottlenecks

---

# ACTION SCORING

Every candidate action gets a score.

Expected Profit

+

Future Value

+

Market Impact

+

Labor Efficiency

+

Opportunity Cost

+

Risk

-

Movement Cost

-

Schedule Disruption

Highest score wins.

---

# USE A TASK SYSTEM

Never let workers wander.

Maintain priority queues.

Critical

Water today

Feed today

Harvest ready

Collect fertilizer

Sell if required

Plant

Build

Expand

Hire

Everything should come from task scheduling.

---

# SCHEDULER

Represent every future event.

Water

Feed

Harvest

Market sell

Market buy

Build

Hire

Land purchase

Expected crop maturity

Expected animal production

Future fertilizer

Every event should have

Time

Priority

Reward

Deadline

---

# NEVER MISS

Water

Feed

Harvest

These are catastrophic failures.

Missing one watering can destroy profit.

Missing feed loses animals.

Never allow deadline failures.

---

# MAP OPTIMIZATION

Movement is expensive.

Treat movement as a routing problem.

Cluster jobs.

Avoid zigzag movement.

Minimize walking.

Always solve

Travel distance

before assigning actions.

---

# MULTI AGENT PLANNING

Farmer

+

Farm hands

are parallel processors.

Balance work.

Avoid duplicate movement.

Avoid collisions.

Avoid idle workers.

Workers should specialize.

Examples

Worker A

Water

Worker B

Harvest

Worker C

Collect

Worker D

Plant

---

# LAND EXPANSION

Buying land is investment.

Never buy because land exists.

Buy because

Expected ROI >

Expansion Cost

Estimate

Additional production

Extra movement

Labor needed

Expected payback time

---

# CROP DECISION

Never hardcode

Always compute.

For every crop estimate

ROI

Expected selling price

Growth duration

Tile occupancy

Labor

Market saturation

Risk

Future demand

Choose maximum expected value.

---

# ANIMAL DECISION

Animals are factories.

Estimate

Lifetime ROI

Feed cost

Labor cost

Production

Care bonus

Fertilizer value

Market demand

Future prices

Then decide.

---

# FERTILIZER

Fertilizer is capital.

Never waste it.

Compute

Expected marginal profit

for every possible plant.

Allocate fertilizer

where ROI is highest.

---

# MARKET ENGINE

Treat market like a stock exchange.

Predict

Supply

Demand

Opponent selling

Town consumption

Future inventory

Price movement

Never dump inventory blindly.

---

# SELL STRATEGY

For every product compute

Sell now

vs

Sell later

Expected future value

Storage risk

Market crash risk

Opponent risk

Town demand

Sell only if

Expected future value

<

Current value

---

# BUY STRATEGY

Buy only if

Expected return

>

Investment

Buying wheat

Buying fertilizer

Buying animals

Buying seeds

Buying land

Everything requires ROI analysis.

---

# PRICE PREDICTION

Estimate

Tomorrow inventory

↓

Expected town consumption

↓

Expected opponent sales

↓

Expected player sales

↓

Expected price

Every product should have a future price estimate.

---

# OPPONENT MODEL

Watch opponent.

Estimate

Crop mix

Animals

Land expansion

Income

Likely strategy

Expected future selling

Market flooding

Counter them.

---

# GAME PHASES

Opening

Early economy

Expansion

Scaling

Peak production

Liquidation

Endgame

Each phase uses different policies.

---

# OPENING

Priorities

Fast ROI

Cash generation

Efficient movement

Infrastructure

No unnecessary investment.

---

# MID GAME

Expand.

Increase production.

Increase workers.

Increase automation.

Increase market influence.

---

# ENDGAME

Very important.

Inventory has zero value after game ends.

Everything must become money.

Sell everything.

Harvest everything.

Avoid unfinished crops.

Avoid buying long-term assets.

Transition into liquidation mode.

---

# RISK MANAGEMENT

Avoid

Idle land

Idle workers

Dead animals

Weeds

Market crashes

Inventory overflow

Missed watering

Missed feeding

---

# DECISION MAKING

Never use

if else chains

alone.

Score actions.

Rank them.

Choose highest value.

---

# SEARCH

When computational budget allows

Run

Beam Search

Monte Carlo Tree Search

Rolling Horizon Planning

or

Lookahead Simulation

Evaluate future outcomes.

---

# HEURISTICS

Useful but never absolute.

Every heuristic should be overridable by expected value calculations.

---

# STATE EVALUATION

A good state has

High cash

Healthy production

High worker utilization

Stable schedule

Good future income

Strong market position

Minimal waste

---

# DEBUGGING

Track

Idle turns

Missed watering

Missed feed

Lost crops

Lost animals

Movement waste

Average worker utilization

Profit per tile

Profit per action

Profit per worker

ROI by crop

ROI by animal

Market prediction error

Schedule violations

These metrics should continuously improve.

---

# ARCHITECTURE

Recommended modules

WorldState

Planner

Scheduler

MarketPredictor

PriceModel

WorkerAllocator

CropOptimizer

AnimalOptimizer

ExpansionPlanner

MovementPlanner

OpponentModel

EndgamePlanner

Evaluator

SimulationEngine

Logger

---

# CODING PRINCIPLES

No duplicated logic.

Pure functions.

Deterministic behavior.

Fast execution.

Memoization where possible.

Priority queues.

Efficient pathfinding.

Incremental updates.

Never recompute entire world every turn.

---

# GOLDEN RULE

Every action must answer

"Will this increase expected final money?"

If not,

do not perform it.

Never optimize today's profit.

Optimize the final score after 720 turns.
