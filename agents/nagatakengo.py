import random


def get_market_price(obs, product):
    """現在価格を取得する。"""
    return obs["market"]["prices"][product]


def score(input):
    """
    max_depth=3 のDecisionTreeモデル。
    https://www.kaggle.com/code/nagatakengo/predict-future-melon-prices
    
    """

    if input[3] <= 10096.5:
        if input[0] <= 257.5:
            if input[2] <= 265.0:
                var0 = 262.30210213139543
            else:
                var0 = 269.14311998948614
        else:
            if input[2] <= 180.0:
                var0 = 169.52286374133948
            else:
                var0 = 192.71375464684016
    else:
        if input[0] <= 497.5:
            if input[3] <= 10127.5:
                var0 = 95.84500378501136
            else:
                var0 = 82.26066931619805
        else:
            if input[3] <= 10154.5:
                var0 = 19.437829958238122
            else:
                var0 = 6.73007806147341

    return var0


def should_sell_melon(
    melon_price,
    melon_stock,
    melon_in_shed,
    day,
    step,
):
    """MELONをSELLするかHOLDするか判断する。"""

    # 終盤は価格に関係なく売却
    if step >= 710:
        return True

    # 12ターン以内の最高価格を予測
    pred_price = score([
        step,
        melon_in_shed,
        melon_price,
        melon_stock,
        0,
        0,
        0,
    ])

    # 現在価格の方が予測最高価格以上なら売却
    if melon_price >= pred_price:
        return True

    return False


def get_harvest_age(crop_name):
    """現在の戦略で使う収穫開始日を返す。"""
    if crop_name == "MELON":
        return 10
    return 2


def get_tile_action(tile, day):
    """足元のタイルで今すぐ行う作業を返す。"""
    if not isinstance(tile, dict):
        return None

    if tile.get("kind") == "WEED":
        return ["DIG"]

    if tile.get("animal"):
        if not tile.get("fed_today", False):
            return ["FEED"]

        if not tile.get("cared_today", False):
            return ["CARE"]

        if tile.get("yield_units", 0) > 0:
            return ["HARVEST"]

        if tile.get("fertilizer_available", 0) > 0:
            return ["COLLECT_FERTILIZER"]

        return None

    if tile.get("kind") != "PLANT":
        return None

    crop_name = tile.get("crop", "WHEAT")
    crop_age = day - tile.get("planted_day", day)
    harvest_age = get_harvest_age(crop_name)

    if not tile.get("watered_today", True):
        return ["WATER"]

    if crop_age >= harvest_age:
        return ["HARVEST"]

    return None


def step_toward(fx, fy, tx, ty, tiles):
    """
    目的地に近づく方向へ1マス移動する。
    目的地へ直接進めない場合は、移動可能な方向を選ぶ。
    """
    max_y = len(tiles) - 1
    max_x = len(tiles[0]) - 1

    candidates = []

    if fx < tx and fx < max_x and tiles[fy][fx + 1] != "LOCKED":
        candidates.append("EAST")
    elif fx > tx and fx > 0 and tiles[fy][fx - 1] != "LOCKED":
        candidates.append("WEST")

    if fy < ty and fy < max_y and tiles[fy + 1][fx] != "LOCKED":
        candidates.append("SOUTH")
    elif fy > ty and fy > 0 and tiles[fy - 1][fx] != "LOCKED":
        candidates.append("NORTH")

    if candidates:
        return random.choice(candidates)

    valid_dirs = []

    if fy > 0 and tiles[fy - 1][fx] != "LOCKED":
        valid_dirs.append("NORTH")

    if fy < max_y and tiles[fy + 1][fx] != "LOCKED":
        valid_dirs.append("SOUTH")

    if fx < max_x and tiles[fy][fx + 1] != "LOCKED":
        valid_dirs.append("EAST")

    if fx > 0 and tiles[fy][fx - 1] != "LOCKED":
        valid_dirs.append("WEST")

    if valid_dirs:
        return random.choice(valid_dirs)

    return "PASS"

def find_empty_coop(
    tiles,
    fx,
    fy,
):
    """現在位置から最も近い空のcoopを返す"""

    best_target = None
    best_distance = 9999

    for y in range(len(tiles)):
        for x in range(len(tiles[0])):

            tile = tiles[y][x]

            if(
                isinstance(tile, dict)
                and tile.get("kind") == "COOP"
                and  not tile.get("animal")
            ):
                distance = (abs(x - fx) + abs(y - fy))

                if distance < best_distance:
                    best_distance = distance
                    best_target = (x, y)

    return best_target


def find_target_tile(
    tiles,
    fx,
    fy,
    has_seeds,
    day,
    excluded_coords=None,
):
    """
    現在位置から各作業候補を評価し、
    最もスコアの高いタイルの座標を返す。
    """
    if excluded_coords is None:
        excluded_coords = set()

    best_target = None
    best_score = -9999

    for y in range(len(tiles)):
        for x in range(len(tiles[0])):
            if (x, y) in excluded_coords:
                continue

            tile = tiles[y][x]
            if tile == "LOCKED":
                continue

            base_score = None

            # 雑草
            if isinstance(tile, dict) and tile.get("kind") == "WEED":
                if day >= 27:
                    continue

                base_score = 0

            #動物
            elif isinstance(tile, dict) and tile.get("animal"):
                if not tile.get("fed_today", False):
                    base_score = 100

                elif not tile.get("cared_today", False):
                    base_score = 75

                elif tile.get("yield_units", 0) > 0:
                    base_score = 60

                elif tile.get("fertilizer_available", 0) > 0:
                    base_score = 55


            # 植物
            elif isinstance(tile, dict) and tile.get("kind") == "PLANT":
                crop_name = tile.get("crop", "WHEAT")
                crop_age = day - tile.get("planted_day", day)
                harvest_age = get_harvest_age(crop_name)

                if crop_age >= harvest_age:
                    if crop_name == "MELON":
                        base_score = 250
                    else:
                        base_score = 25

                elif not tile.get("watered_today", True):
                    base_score = 50

            # 空き地
            elif tile is None and has_seeds:
                if day >= 27:
                    continue

                base_score = 50

            if base_score is None:
                continue

            movement_cost = abs(x - fx) + abs(y - fy)
            task_score = base_score - movement_cost

            if task_score > best_score:
                best_score = task_score
                best_target = (x, y)

    return best_target


def build_market_actions(
    me,
    seeds,
    shed,
    day,
    step,
    melon_price,
    melon_stock,
    goose_count,
):
    """現在の市場売買・雇用・土地購入ルールから注文一覧を作る。"""

    market = []

    money = me.get("money", 0)
    current_hands = me.get("hands", [])
    unlocked_quads = me.get(
        "unlocked_quadrants",
        ["NW"],
    )

    wheat_seeds = seeds.get("WHEAT", 0)
    melon_seeds = seeds.get("MELON", 0)

    wheat_in_shed = shed.get("WHEAT", 0)
    melon_in_shed = shed.get("MELON", 0)

    # 種を購入
    if money >= 500:
        if melon_seeds == 0:
            market.append(
                ["BUY_SEED", "MELON", 10]
            )


    if wheat_seeds == 0 and money >= 10:
        market.append(
            ["BUY_SEED", "WHEAT", 3]
        )

    # WHEAT売却
    if wheat_in_shed > 0:
        market.append(
            ["SELL", "WHEAT", wheat_in_shed]
        )

    # MELON売却
    if melon_in_shed > 0:
        if should_sell_melon(
            melon_price,
            melon_stock,
            melon_in_shed,
            day,
            step,
        ):
            market.append(
                ["SELL", "MELON", melon_in_shed]
            )

    # 雇用
    total_people = 1 + len(current_hands)

    if total_people < 5 and money >= 200:
        market.append(
            ["HIRE"]
        )
    if total_people < 10 and money >= 5000:
        market.append(
            ["HIRE"]
        )

    # 土地購入
    if len(unlocked_quads) < 2 and money >= 5000:
        market.insert(
            0,
            ["BUY_LAND"],
        )

    #gooseを飼う
    goose_in_shed = shed.get("GOOSE", 0)

    if(
        len(unlocked_quads) >= 1
        and goose_count == 0
        and money >= 300
    ):
        market.append(
            ["BUY_ANIMAL", "GOOSE", 1]
        )

    return market


def agent(obs, config):

    # 状態取得

    player = obs["player"]

    me = obs["farms"][player]
    private = obs["private"]

    tiles = me["tiles"]

    fx, fy = me["farmer"]
    farmer_tile = tiles[fy][fx]

    seeds = private.get("seeds", {})
    shed = private.get("shed", {})

    day = obs.get("day", 0)
    step = obs.get("step", 0)
    hour = obs.get("hour", 0)

    current_hands = me.get("hands", [])

    melon_price = get_market_price(obs, "MELON",)#メロン価格
    melon_stock = obs["market"]["inventory"]["MELON"]#メロン市場在庫

    wheat_seeds = seeds.get("WHEAT", 0)#小麦在庫
    melon_seeds = seeds.get("MELON", 0)#メロン在庫

    has_seeds = (wheat_seeds > 0 or melon_seeds > 0)

    inventories = private.get("inventories", [])

    famer_inventory = (
        inventories[0]
        if len(inventories) > 0
        else {}
    )
    farmer_goose = famer_inventory.get("GOOSE", 0)

    coop_count = 0

    for row in tiles:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "COOP":
                coop_count += 1

    goose_count = 0

    for row in tiles:
        for tile in row:
            if (
                isinstance(tile, dict) and tile.get("animal") == "GOOSE"
            ):
                goose_count += 1
    goose_count += shed.get("GOOSE", 0)
    goose_count += farmer_goose


    # 市場

    market = build_market_actions(
        me,
        seeds,
        shed,
        day,
        step,
        melon_price,
        melon_stock,
        goose_count,
    )

    # メイン農家

    farmer_action = None
    goose_in_shed = shed.get("GOOSE", 0)

    if farmer_goose > 0:
        if (
            isinstance(farmer_tile, dict)
            and farmer_tile.get("kind") == "COOP"
            and not farmer_tile.get("animal")
        ):
            farmer_action = [
                "PLACE",
                "GOOSE"
            ]
        else:
            coop_target = find_empty_coop(
                tiles,
                fx,
                fy
            )

            if coop_target is not None:
                move_dir = step_toward(
                    fx,
                    fy,
                    coop_target[0],
                    coop_target[1],
                    tiles,
                )

                farmer_action = [
                    move_dir
                ]

    elif(
        goose_in_shed > 0
        and coop_count > 0
        and hour == 0
    ):
        farmer_action = [
            "PICKUP",
            "GOOSE",
            1,
        ]

    elif farmer_tile is None:
        if goose_in_shed > 0 and coop_count < 1:
            farmer_action = [
                "BUILD_COOP",
            ]

        elif melon_seeds > 0:
            farmer_action = [
                "PLANT",
                "MELON",
            ]
        elif wheat_seeds > 0:
            farmer_action = [
                "PLANT",
                "WHEAT",
            ]


    else:
        farmer_action = get_tile_action(
            farmer_tile,
            day,
        )

    # メイン農家の移動

    claimed_targets = set()

    if farmer_action is None:
        target = find_target_tile(
            tiles,
            fx,
            fy,
            has_seeds,
            day,
            claimed_targets,
        )
        if target is not None:
            claimed_targets.add(target)
            move_dir = step_toward(
                fx,
                fy,
                target[0],
                target[1],
                tiles,
            )
            farmer_action = [move_dir]
        else:
            farmer_action = ["PASS"]
    else:
        claimed_targets.add(
            (fx, fy)
        )

    for y in range(len(tiles)):
        for x in range(len(tiles[0])):
            tile = tiles[y][x]

            if(
                isinstance(tile, dict)
                and tile.get("animal")
            ):
                claimed_targets.add(
                    (x, y)
                )

    # 作業員

    hands_actions = []

    for hand in current_hands:
        hx, hy = hand

        hand_tile = tiles[hy][hx]

        if(
            isinstance(hand_tile, dict)
            and hand_tile.get("animal")
        ):
            hand_action = None

        elif hand_tile is None:
            if melon_seeds > 0:
                hand_action = [
                    "PLANT",
                    "MELON",
                ]
            elif wheat_seeds > 0:
                hand_action = [
                    "PLANT",
                    "WHEAT",
                ]
            else:
                hand_action = None
        else:
            hand_action = get_tile_action(
                hand_tile,
                day,
            )
        if hand_action is None:
            target = find_target_tile(
                tiles,
                hx,
                hy,
                has_seeds,
                day,
                claimed_targets,
            )
            if target is not None:
                claimed_targets.add(target)
                move_dir = step_toward(
                    hx,
                    hy,
                    target[0],
                    target[1],
                    tiles,
                )
                hand_action = [move_dir]
            else:
                hand_action = ["PASS"]
        else:
            claimed_targets.add(
                (hx, hy)
            )
        hands_actions.append(
            hand_action
        )

    # 出力

    return {
        "farmer": farmer_action,
        "hands": hands_actions,
        "market": market,
    }