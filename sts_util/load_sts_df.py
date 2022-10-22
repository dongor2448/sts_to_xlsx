import datetime
import pandas as pd
import os, json, re, ast


def load_df(path_lst):
    if os.path.exists(f"./stsstat"):
        try:
            df = pd.read_csv(f"./stsstat/merge_data.csv")
            print(f"file: .\\stsstat\\merge_data.csv already exist.")
            return df
        except FileNotFoundError:
            print(f".\\stsstat\\merge_data.csv not found, try to del the stsstat folder")
    else:
        df = pd.DataFrame()
        percent = 0
        for file in path_lst:
            percent += 1 / len(path_lst) * 100
            with open(file, "r") as f:
                words = f.read()
                words = card_rename(words)
                data = json.loads(words)
                df = pd.concat([pd.DataFrame([data]), df])
            print("\b" * 80, flush=True, end="")
            print(f"{percent:.2f}%... loading {os.path.basename(file)}", flush=True, end="")
        print("")
        df.reset_index(inplace=True)
        if df.shape[0] != 0:
            df = clean_data(df)
            save_file(df)
            new_df = pd.read_csv(f"./stsstat/merge_data.csv")
            return new_df
        else:
            return df


def card_rename(words):
    replacement = [["Underhanded Strike", "Sneaky Strike"],
                   ["Night Terror", "Nightmare"],
                   ["Venomology", "Alchemis"],
                   ["Crippling Poison", "Crippling Cloud"],
                   ["Ghostly", "Apparition"],
                   ["Wraith Form v2", "Wraith Form"],
                   ["\+\d", ""],
                   ["WingedGreaves", "Wing Boots"]
                   ]
    for pair in replacement:
            words = re.sub(pair[0], pair[1], words)
    return words


def clean_data(df):
    drop_lst = ["special_seed", "potion_discard_per_floor", "player_experience",
                "build_version", "floor_exit_playtime", "win_rate", "chose_seed", "rewards_skipped",
                "potion_use_per_floor", "circlet_count", "shop_contents",
                "seed_source_timestamp", "score_breakdown", "play_id",
                "items_purged_floors", "local_time",
                "campfire_choices", "potions_floor_usage", "timestamp", "gold",
                "item_purchase_floors", "max_hp_per_floor",
                'no. of card removed', 'real path'
                ]
    #  drop installed mod data
    lst = df.filter(regex=("relic_stats.*")).columns
    if len(lst) != 0:
        for col in lst:
            df.drop(col, inplace=True, axis=1)

    lst = df.filter(regex=(".*_log.*")).columns
    if len(lst) != 0:
        for col in lst:
            df.drop(col, inplace=True, axis=1)

    #  drop special mode beside normal
    df = df.drop("is_ascension_mode", axis=1)
    mode_lst = df.filter(regex=("is_.*")).columns
    for mode in mode_lst:
        df = df.drop(df[df[mode]==True].index)
        df.drop(mode, inplace=True, axis=1)

    #  group useful data
    df["saved time"] = change_datetime(df)
    df["gold_total"] = df["gold_per_floor"].apply(lambda x: counting_gold(x))
    df["playtime"] = df["playtime"].apply(lambda x:round(x/60, 2))
    df.rename(columns={'purchased_purges': 'no. of card removed'}, inplace=True)
    df.rename(columns={'master_deck': 'end game deck'}, inplace=True)
    df.rename(columns={'card_choices': 'card_choices_from_reward'}, inplace=True)
    df.rename(columns={'path_per_floor': 'real path'}, inplace=True)
    df["max_hp"] = df["max_hp_per_floor"].apply(lambda x: x[-1])
    df["act 1 elite taken"] = df["path_taken"].apply(lambda x: elite_taken(x, 1))
    df["act 2 elite taken"] = df["path_taken"].apply(lambda x: elite_taken(x, 2))
    df["act 3 elite taken"] = df["path_taken"].apply(lambda x: elite_taken(x, 3))
    df["seed_played"] = df["seed_played"].apply(lambda x: convert_seed_to_string(int(x)))

    #  drop data not used
    for item in drop_lst:
        try:
            df.drop(item, inplace=True, axis=1)
        except:
            #  in case item not in data grabbed or someone type sth in txt file
            #  not droping data is not very important, and data not gonna to read anyways
            continue

    #  rearrage columns
    df = df[['index', 'character_chosen', "seed_played", 'saved time', 'playtime', 'ascension_level',
             'victory', 'score', 'floor_reached', 'path_taken', 'campfire_rested', 'campfire_upgraded',
             'max_hp', 'gold_total', 'gold_per_floor', 'neow_cost', 'neow_bonus', 'killed_by', 'damage_taken', 'event_choices',
             'card_choices_from_reward', 'end game deck', 'items_purchased', 'items_purged',
             'relics_obtained', "relics", 'current_hp_per_floor',
             "potions_floor_spawned", 'potions_obtained', "act 1 elite taken", "act 2 elite taken",
             "act 3 elite taken", 'boss_relics']]
    df = split_boss_relic(df)
    return df


def convert_seed_to_string(seed: int) -> str:
    """Converts numeric seed from run file to alphanumeric seed"""

    char_string = "0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
    # Convert to unsigned
    leftover = seed = seed + 2 ** 64 if seed < 0 else seed
    char_count = len(char_string)
    result = []
    while leftover != 0:
        remainder = leftover % char_count
        leftover = leftover // char_count
        index = int(remainder)
        c = char_string[index]
        result.insert(0, c)
    return ''.join(result)


def elite_taken(path_list, act):
    count = 0
    max_floor = len(path_list)
    if act == 1:
        if max_floor <= 16:
            for floor in range(max_floor):
                if path_list[floor] == "E":
                    count += 1
        else:
            for floor in range(16):
                if path_list[floor] == "E":
                    count += 1
    if act == 2:
        if max_floor <= 32:
            for floor in range(16, max_floor):
                if path_list[floor] == "E":
                    count += 1
        else:
            for floor in range(16, 32):
                if path_list[floor] == "E":
                    count += 1
    if act == 3:
        if max_floor <= 49:
            for floor in range(32, max_floor):
                if path_list[floor] == "E":
                    count += 1
        else:
            for floor in range(32, 49):
                if path_list[floor] == "E":
                    count += 1
    return count


def split_boss_relic(df):
    boss_lst_not_pick = []
    boss_lst_pick = []
    for i in range(df["boss_relics"].shape[0]):
        try:
            boss_lst_not_pick.append(df["boss_relics"].iloc[i][0]["not_picked"])
            try:
                boss_lst_pick.append(df["boss_relics"].iloc[i][0]["picked"])
            except:
                boss_lst_pick.append("NaN")
        except:
            boss_lst_not_pick.append("NaN")
            boss_lst_pick.append("NaN")
    df["act 1 not picked"] = boss_lst_not_pick
    df["act 1 picked"] = boss_lst_pick
    boss_lst_not_pick_2 = []
    boss_lst_pick_2 = []
    for i in range(df["boss_relics"].shape[0]):
        try:
            boss_lst_not_pick_2.append(df["boss_relics"].iloc[i][1]["not_picked"])
        except:
            boss_lst_not_pick_2.append("NaN")
        try:
            boss_lst_pick_2.append(df["boss_relics"].iloc[i][1]["picked"])
        except:
            boss_lst_pick_2.append("NaN")
    df["act 2 not picked"] = boss_lst_not_pick_2
    df["act 2 picked"] = boss_lst_pick_2
    df["index"] = 1
    return df


def counting_gold(lst):
    total = int(lst[0])
    for i, gold in enumerate(lst[1:]):
        gain = int(gold) - int(lst[i])
        if gain >= 0:
            total += gain
    return total


def change_datetime(df):
    return df["local_time"].apply(lambda x: datetime.datetime.strptime(x, "%Y%m%d%H%M%f").replace(
        microsecond=0))


def save_file(df):
    os.makedirs(f"./stsstat")
    df.to_csv(f"./stsstat/merge_data.csv", index=False)
    print(f"saving to...\\stsstat\\merge_data.csv")


#  need to figure out potion drop through fight/alchemize/event
# def potion_used(df):
#     df["potion_used"] = df["potions_floor_usage"].apply(lambda x:len(x))
#     return df["potion_used"]


# def potion_get(df):
#     df["potion_get"] = df["potions_floor_spawned"].apply(lambda x:len(x))
#     return df["potion_get"]