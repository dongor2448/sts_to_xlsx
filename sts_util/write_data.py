from pandas import DataFrame
import re, ast

shrine_event_lst = ["Bonfire Elementals", "Fountain of Cleansing", "Designer", "Duplicator", "FaceTrader",
                    "Golden Shrine", "The Joust", "Knowing Skull", "Lab", "Match and Keep!", "N'loth",
                    "Forge", "Purifier", "Transmorgrifier", "Shrine", "WeMeetAgain", "Wheel of Change",
                    "The Woman in Blue"]


def write(df, char):
    report = {}
    if char in df['character_chosen'].values:
        df = df[df["character_chosen"] == char]
        # df = df.head(50)  # test if too much data
        relics_lib = relic_obtain(df["relics"])
        report["relic get"] = dict(sorted(relics_lib.items(), key=lambda item: item[1], reverse=True))
        report["avg damage_taken"] = damage_taken(df["damage_taken"])
        report["act 1 boss relic pick rate (%)"] = act1_boss_relic_pick(df)
        report["act 2 boss relic pick rate (%)"] = act2_boss_relic_pick(df)
        report["card pick rate act1 (exclude shop/boss/starting)"] = card_pick(df, 1)
        report["card pick rate act2 onwards (exclude shop/boss1/boss2)"] = card_pick(df, 2)
        report["act 1 boss relic win rate (%)"] = act1_boss_relic_win(df[["victory", "boss_relics"]])
        report["act 2 boss relic win rate (%)"] = act2_boss_relic_win(df[["victory", "boss_relics"]])
        report["relic win rate(%)"] = relic_winrate(df)
        report["card removed"] = card_removed(df)
        report["card win rate (exclude duplicate)"] = most_win_card(df)
        report["card count (exclude duplicate)"] = card_count(df)
        # report["shrine event"] = shrine_event(df)
        report["max_damage_taken"] = max_damage_taken(df)
        # shrine_count(df)
        report["event distribution"] = event_count(df)
        # event_data(df)
        # event_count(df)
    return report


# def event_data(df):
#     df = df["event_choices"]
#     player_choice_dict = {}
#     event_list = []
#     for i in range(df.shape[0]):
#         event = df.iloc[i]
#         game_event = ast.literal_eval(event)
#         for floor in game_event:
#             if floor["event_name"] == 'The Mausoleum':
#                 print(floor)
    #             if floor["player_choice"] not in player_choice_dict:
    #                 player_choice_dict[floor["player_choice"]] = 1
    #             else:
    #                 player_choice_dict[floor["player_choice"]] += 1
    # print(player_choice_dict)


def event_count(df):
    df = df["event_choices"]
    event_list = {}
    for i in range(df.shape[0]):
        event = df.iloc[i]
        game_event = ast.literal_eval(event)
        temp = ""
        for floor in game_event:
            if temp != floor["floor"]:
                if floor["event_name"] not in event_list:
                    event_list[floor["event_name"]] = 1
                else:
                    event_list[floor["event_name"]] += 1
            temp = floor["floor"]
    return event_list


def max_damage_taken(df):
    dt_lst = df["damage_taken"].to_list()
    dt_lib = []
    for run in dt_lst:
        run = ast.literal_eval(run)
        for i,floor in enumerate(run):
                dt_lib.append([floor["enemies"], floor["damage"]])
    sorted_dict = sorted(dt_lib, key=lambda x: int(x[1]), reverse=True)
    new_lst = []
    for i,v in enumerate(sorted_dict):
        if i <= 100:
            new_lst.append(v)
    return new_lst


def floor_reached(df):
    df = df["floor_reached"]
    floor_dic = {}
    for i in range(df.shape[0]):
        if df.iloc[i] != 57:
            if df.iloc[i] in floor_dic:
                floor_dic[df.iloc[i]] += 1
            else:
                floor_dic[df.iloc[i]] = 1
    for i in range(57):
        if i not in floor_dic:
            floor_dic[i] = 0
    return dict(sorted(floor_dic.items()))


def find_last_in_list(lst):
    return lst[-1]


def card_count(df):
    card_tot = {}
    df = df["end game deck"]
    for x in range(df.shape[0]):
        temp_tot_card = {}
        tot_card_lst = ast.literal_eval(df.iloc[x].replace("+1", ""))
        for card in tot_card_lst:
            if card not in temp_tot_card:
                temp_tot_card[card] = 1
        for k in temp_tot_card:
            if k not in card_tot:
                card_tot[k] = temp_tot_card[k]
            else:
                card_tot[k] += 1
    return dict(sorted(card_tot.items(), key=lambda item: item[1], reverse=True))


def most_win_card(df):
    card_deck = {}
    card_tot = {}
    win_deck = {}
    df = df[["end game deck", "victory"]]
    victory = (df[df["victory"] == True]["victory"].shape[0])
    df_win = (df[df["victory"] == True]["end game deck"])
    for i in range(victory):
        temp_card = {}
        card_lst = ast.literal_eval(df_win.iloc[i].replace("+1", ""))
        for card in card_lst:
            if card not in temp_card:
                temp_card[card] = 1
        for k in temp_card:
            if k not in card_deck:
                card_deck[k] = temp_card[k]
            else:
                card_deck[k] += 1
    df = df["end game deck"]
    for x in range(df.shape[0]):
        temp_tot_card = {}
        tot_card_lst = ast.literal_eval(df.iloc[x].replace("+1", ""))
        for card in tot_card_lst:
            if card not in temp_tot_card:
                temp_tot_card[card] = 1
        for k in temp_tot_card:
            if k not in card_tot:
                card_tot[k] = temp_tot_card[k]
            else:
                card_tot[k] += 1
    for k in card_tot:
        if k in card_deck:
            win_deck[k] = round(card_deck[k] / card_tot[k]*100, 2)
        else:
            win_deck[k] = 0
    return dict(sorted(win_deck.items(), key=lambda item: item[1], reverse=True))


def card_removed(df):
    remove_lst = {}
    df = df["items_purged"]
    item_lst = df.tolist()
    for run in item_lst:
        run = ast.literal_eval(run)
        if run != []:
            for cards in run:
                if cards != "":
                    if cards not in remove_lst:
                        remove_lst[cards] = 1
                    else:
                        remove_lst[cards] += 1
    return dict(sorted(remove_lst.items(), key=lambda item: item[1], reverse=True))


def act2_boss_relic_pick(df):
    brp_lst = df["boss_relics"].to_list()
    brp_tol = {}
    brp_pick = {}
    brp_result = {}
    for run in brp_lst:
        run = ast.literal_eval(run)
        if run != []:
            if len(run) == 2:
                run = run[1]   # select act 1
                skip_item = run["not_picked"]
                for skip_relic in skip_item:
                    if skip_relic not in brp_tol:
                        brp_tol[skip_relic] = 1
                    else:
                        brp_tol[skip_relic] += 1
                try:
                    pick_relic = run["picked"]
                    if pick_relic not in brp_tol:
                        brp_tol[pick_relic] = 1
                    else:
                        brp_tol[pick_relic] += 1
                    if pick_relic not in brp_pick:
                        brp_pick[pick_relic] = 1
                    else:
                        brp_pick[pick_relic] += 1
                except:
                    continue  # exclude skipped case
    for k,v in brp_tol.items():
        if k in brp_pick:
            brp_result[k] = round(brp_pick[k]/brp_tol[k]*100, 2)
        else:
            brp_result[k] = 0
    return dict(sorted(brp_result.items(), key=lambda item: item[1], reverse=True))


def act2_boss_relic_win(df):
    brw_lst = df["boss_relics"].to_list()
    brw_pick = {}
    brw_win = {}
    brw_result = {}
    for run in brw_lst:
        run = ast.literal_eval(run)
        if run != [] and len(run) == 2:
            run = run[1]    # choosing act 2
            try:
                pick_relic = run["picked"]
                if pick_relic not in brw_pick:
                    brw_pick[pick_relic] = 1
                else:
                    brw_pick[pick_relic] += 1
            except:     # skip relic case
                continue
    df = df[df["victory"] == True]
    bp_lst_win = df["boss_relics"].to_list()
    for run in bp_lst_win:
        run = ast.literal_eval(run)
        if run != [] and len(run) == 2:
            run = run[1]
            try:
                pick_relic_win = run["picked"]
                if pick_relic_win not in brw_win:
                    brw_win[pick_relic_win] = 1
                else:
                    brw_win[pick_relic_win] += 1
            except:     # skip relic case
                continue

    for k,v in brw_pick.items():
        if k in brw_win:
            brw_result[k] = round(brw_win[k]/brw_pick[k]*100, 2)
        else:
            brw_result[k] = 0
    return dict(sorted(brw_result.items(), key=lambda item: item[1], reverse=True))


def shrine_event(df):
    df = df[["path_per_floor", "path_taken", "event_choices"]]
    merge_path = []
    count_fail = 0
    shrine_garbage_count = 0
    fk_path_lst = []
    result = {}
    question_node = 0
    treature_count = 0
    for i in range(df.shape[0]):
        rl_path = df.iloc[i]["path_per_floor"]
        rl_path = rl_path.replace(", None", "")
        rl_path = ast.literal_eval(rl_path)
        fk_path = df.iloc[i]["path_taken"]
        fk_path = fk_path.replace(", 'BOSS'", ", 'B'")
        fk_path = ast.literal_eval(fk_path)
        rl_event = df.iloc[i]["event_choices"]
        rl_event = ast.literal_eval(rl_event)
        temp = []
        collect_eve = []
        for eve in rl_event:
            if eve["floor"] not in temp:
                collect_eve.append(eve["event_name"])
                temp.append(eve["floor"])
            else:
                temp.remove(eve["floor"])
                temp.append(eve["floor"])
        count = 0
        for path in rl_path:
            for node in path:
                if node == "?":
                    count += 1
        if count != len(collect_eve):
            count_fail += 1
        else:
            merge_path.append(event_merge(fk_path, rl_path, collect_eve))
        fk_path_lst.append(fk_path)
    for run in fk_path_lst:
        for node in run:
            if node == "?":
                question_node += 1
    temp_event = ""
    for run in merge_path:
        for node in run:
            if node in shrine_event_lst:
                temp_event = node
            if node == "B":
                temp_event = ""
            if node == "?/M":
                if temp_event in shrine_event_lst:
                    shrine_garbage_count += 1
            if node == "?/T":
                treature_count += 1

    result["shrine garbage"] = shrine_garbage_count
    result["fail count"] = count_fail
    result["total ? run into"] = question_node
    return result


def relic_winrate(df):
    df_total = df["relics"]
    relic_total = {}
    relic_total_win = {}
    relic_result = {}
    relic_list = df_total.tolist()
    for run in relic_list:
        run = ast.literal_eval(run)
        if len(run) != 0:
            for relic in run:
                if relic not in relic_total:
                    relic_total[relic] = 1
                else:
                    relic_total[relic] += 1

    df_win = df[df["victory"] == True]["relics"]
    relic_list_win = df_win.tolist()
    for run in relic_list_win:
        run = ast.literal_eval(run)
        if len(run) != 0:
            for relic in run:
                if relic not in relic_total_win:
                    relic_total_win[relic] = 1
                else:
                    relic_total_win[relic] += 1

    for k,v in relic_total.items():
        if k in relic_total_win:
            relic_result[k] = round(relic_total_win[k]/relic_total[k]*100, 2)
        else:
            relic_result[k] = 0
    return dict(sorted(relic_result.items(), key=lambda item: item[1], reverse=True))



def relic_win_count(df):
    rwc_dic = {}
    df = df["relics"][df["victory"] == True]
    rlc_win = df.tolist()
    for run in rlc_win:
        run = ast.literal_eval(run)
        for item in run:
            if item not in rwc_dic:
                rwc_dic[item] = 1
            else:
                rwc_dic[item] += 1
    return rwc_dic


def act1_boss_relic_win(df):
    brw_lst = df["boss_relics"].to_list()
    brw_pick = {}
    brw_win = {}
    brw_result = {}
    for run in brw_lst:
        run = ast.literal_eval(run)
        if run != []:
            run = run[0]    # choosing act 1
            try:
                pick_relic = run["picked"]
                if pick_relic not in brw_pick:
                    brw_pick[pick_relic] = 1
                else:
                    brw_pick[pick_relic] += 1
            except:     # skip relic case
                continue
    df = df[df["victory"] == True]
    bp_lst_win = df["boss_relics"].to_list()
    for run in bp_lst_win:
        run = ast.literal_eval(run)
        if run != []:
            run = run[0]
            try:
                pick_relic_win = run["picked"]
                if pick_relic_win not in brw_win:
                    brw_win[pick_relic_win] = 1
                else:
                    brw_win[pick_relic_win] += 1
            except:     # skip relic case
                continue

    for k,v in brw_pick.items():
        if k in brw_win:
            brw_result[k] = round(brw_win[k]/brw_pick[k]*100, 2)
        else:
            brw_result[k] = 0
    return dict(sorted(brw_result.items(), key=lambda item: item[1], reverse=True))



def find_sm_re(string, key_word):
    smith = re.compile(key_word)
    sm = len(re.findall(smith, string))
    return sm


def relic_obtain(df):
    relic_lib = {}
    for i in range(df.shape[0]):
        relic_lst = ast.literal_eval(df.iloc[i])
        for i, v in enumerate(relic_lst):
            if v in relic_lib:
                relic_lib[v] += 1
            else:
                relic_lib[v] = 1
    return relic_lib


def damage_taken(df):
    dt_lst = df.to_list()
    dt_lib = {}
    dt_time = {}
    dt_result = {}
    for run in dt_lst:
        run = ast.literal_eval(run)
        for floor in run:
            if floor["enemies"] not in dt_lib:
                dt_lib[floor["enemies"]] = floor["damage"]
                dt_time[floor["enemies"]] = 1
            else:
                dt_lib[floor["enemies"]] = dt_lib[floor["enemies"]] + floor["damage"]
                dt_time[floor["enemies"]] += 1

    for key in dt_lib:
        dt_result[key] = round(dt_lib[key] / dt_time[key], 2)
    return dict(sorted(dt_result.items(), key=lambda item: item[1], reverse=True))


def act1_boss_relic_pick(df):
    brp_lst = df["boss_relics"].to_list()
    brp_tol = {}
    brp_pick = {}
    brp_result = {}
    for run in brp_lst:
        run = ast.literal_eval(run)
        if run != []:
            run = run[0]   # select act 1
            skip_item = run["not_picked"]
            for skip_relic in skip_item:
                if skip_relic not in brp_tol:
                    brp_tol[skip_relic] = 1
                else:
                    brp_tol[skip_relic] += 1
            try:
                pick_relic = run["picked"]
                if pick_relic not in brp_tol:
                    brp_tol[pick_relic] = 1
                else:
                    brp_tol[pick_relic] += 1
                if pick_relic not in brp_pick:
                    brp_pick[pick_relic] = 1
                else:
                    brp_pick[pick_relic] += 1
            except:
                continue  # exclude skipped case
    for k,v in brp_tol.items():
        if k in brp_pick:
            brp_result[k] = round(brp_pick[k]/brp_tol[k]*100, 2)
        else:
            brp_result[k] = 0
    return dict(sorted(brp_result.items(), key=lambda item: item[1], reverse=True))


def card_pick(df, act=None):
    card_lst = df["card_choices_from_reward"].to_list()
    card_tol = {}
    card_added = {}
    card_result = {}
    for run in card_lst:
        run = run.replace("+1", "")
        run = ast.literal_eval(run)
        for item in run:
            if act == 1:
                if item["floor"] > 15:
                    continue
                elif item["floor"] < 1:
                    continue
                else:
                    for skip_card in item["not_picked"]:
                        if skip_card not in card_tol:
                            card_tol[skip_card] = 1
                        else:
                            card_tol[skip_card] += 1
                    if item["picked"] not in card_tol:
                        card_tol[item["picked"]] = 1
                    else:
                        card_tol[item["picked"]] += 1
                    if item["picked"] not in card_added:
                        card_added[item["picked"]] = 1
                    else:
                        card_added[item["picked"]] += 1

            if act == 2:
                if item["floor"] <= 16 and item["floor"] != 33:  # exclude boss reward
                    continue
                else:
                    for skip_card in item["not_picked"]:
                        if skip_card not in card_tol:
                            card_tol[skip_card] = 1
                        else:
                            card_tol[skip_card] += 1
                    if item["picked"] not in card_tol:
                        card_tol[item["picked"]] = 1
                    else:
                        card_tol[item["picked"]] += 1
                    if item["picked"] not in card_added:
                        card_added[item["picked"]] = 1
                    else:
                        card_added[item["picked"]] += 1
    for key in card_tol:
        if key == "Singing Bowl" or key == "SKIP":
            continue
        else:
            try:
                card_result[key] = round((card_added[key] / card_tol[key])*100 , 2)
            except:
                card_result[key] = 0
    return dict(sorted(card_result.items(), key=lambda item: item[1], reverse=True))


def event_merge(path_fk, path_rl, event_sub):
    for i, node in enumerate(path_rl):
        if path_rl[i] != path_fk[i]:
            path_rl[i] = path_fk[i] + "/" + path_rl[i]
    counter = 0
    for i, node in enumerate(path_rl):
        if node == "?":
            path_rl[i] = event_sub[counter]
            counter += 1
    return path_rl


def juze_excluder(string):
    key = re.compile(".*Juzu Bracelet.*")
    result_lst = re.findall(key, string)
    if len(result_lst) == 1:
        return True
    else:
        return False


def tiny_chest_excluder(string):
    key = re.compile(".*tiny chest.*")
    result_lst = re.findall(key, string)
    if len(result_lst) == 1:
        return True
    else:
        return False


def shrine_count(df):
    df = df[["path_per_floor", "path_taken", "event_choices", "relics"]]
    df_temp = df[df["relics"].apply(juze_excluder) == False]
    df_new = df_temp[df_temp["relics"].apply(tiny_chest_excluder) == False]
    merge_path = []
    count_fail = 0
    shrine_garbage_count = 0
    fk_path_lst = []
    result = {}
    question_node = 0
    treature_count = 0
    shop_count = 0
    for i in range(df_new.shape[0]):
        rl_path = df_new.iloc[i]["path_per_floor"]
        rl_path = rl_path.replace(", None", "")
        rl_path = ast.literal_eval(rl_path)
        fk_path = df_new.iloc[i]["path_taken"]
        fk_path = fk_path.replace(", 'BOSS'", ", 'B'")
        fk_path = ast.literal_eval(fk_path)
        rl_event = df_new.iloc[i]["event_choices"]
        rl_event = ast.literal_eval(rl_event)
        temp = []
        collect_eve = []
        for eve in rl_event:
            if eve["floor"] not in temp:
                collect_eve.append(eve["event_name"])
                temp.append(eve["floor"])
            else:
                temp.remove(eve["floor"])
                temp.append(eve["floor"])
        count = 0
        for path in rl_path:
            for node in path:
                if node == "?":
                    count += 1
        if count != len(collect_eve):
            count_fail += 1
        else:
            merge_path.append(event_merge(fk_path, rl_path, collect_eve))
        fk_path_lst.append(fk_path)
    for run in fk_path_lst:
        for node in run:
            if node == "?":
                question_node += 1
    for run in merge_path:
        temp_event = ""
        for node in run:
            if node == "B":
                temp_event = ""
            if node in shrine_event_lst:
                temp_event = node
            if node == "?/M":
                if temp_event in shrine_event_lst:
                    shrine_garbage_count += 1
                    temp_event = ""
            if node == "?/T":
                if temp_event in shrine_event_lst:
                    treature_count += 1
                    temp_event = ""
                    print(run)
            if node == "?/$":
                if temp_event in shrine_event_lst:
                    shop_count += 1
                    temp_event = ""


