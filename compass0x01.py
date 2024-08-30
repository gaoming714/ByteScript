import time
import re
from pathlib import Path
import pendulum
import random
import sqlite3
from playwright.sync_api import sync_playwright
import ipdb

import requests
import tomlkit
import kimiDB
import pandas as pd
import numpy as np

import sqliteDB
from util import logConfig, logger, lumos, Nox
logConfig("logs/default.log", rotation="10 MB", level="DEBUG", lite=True)

Pooh = {}

BEAN = [
    0,
    0,
    0,
    0,
]

COOKIE = Path() / "cookies" / "GeLi_haiyang.json"
# COOKIE = Path() / "cookies" / "cookie_Bellamy_177.json"


## python pure BOX(dict) ##
# conn = BOX
# mainDB = sqliteDB

## DB json ##
# conn = Path("db.json")
# mainDB = sqliteDB

## sqlite ##
conn = sqlite3.connect("db.sqlite3")
mainDB = sqliteDB



BOX = []


race_df = None
anchor_list = []
slot_df = None
plan_df = None



def launch():
    global Pooh
    global race_df
    global anchor_list

    create_order_table(Path()/"compass"/"2024-08-27.csv")
    create_category_table(Path()/"compass"/"compass.toml")


    order_df = load_order(start_dt="2024-08-01 00:00:00", end_dt="2024-08-30 00:00:00", checkout="pay_dt") #"submit_dt", "pay_dt", "achieve_dt"
    category_df = load_category()

    merged_df = pd.merge(order_df, category_df, on='pid', how='left')

    # removing < $ 1000
    logger.info("成交金额   {:>12.2f} ".format(merged_df["sales"].sum()))
    logger.info("确收金额   {:>12.2f} ".format(merged_df[(merged_df['order_status'] == "已完成") & (merged_df["order_service"] != "退款成功")]["sales"].sum()))
    logger.info("退款金额   {:>12.2f} ".format(merged_df[(merged_df['order_status'] == "已关闭") | (merged_df["order_service"] == "退款成功")]["sales"].sum()))
    logger.info("1金额   {:>12.2f} ".format(merged_df[(merged_df['order_status'] == "已完成") & (merged_df["order_service"] != "退款成功")]["sales"].sum()))
    logger.info("2金额   {:>12.2f} ".format(merged_df[(merged_df['order_status'] == "已完成") & (merged_df["order_service"] == "退款成功")]["sales"].sum()))
    logger.info("3金额   {:>12.2f} ".format(merged_df[(merged_df['order_status'] == "已关闭") & (merged_df["order_service"] != "退款成功")]["sales"].sum()))
    logger.info("4金额   {:>12.2f} ".format(merged_df[(merged_df['order_status'] == "已关闭") & (merged_df["order_service"] == "退款成功")]["sales"].sum()))
    logger.warning("其他金额 {:>12.2f} ".format(merged_df[(merged_df['sales'] < 1000) & (merged_df['uid'].isna())]["sales"].sum()))
    merged_df.loc[(merged_df['sales'] < 1000) & merged_df['uid'].isna(), 'uid'] = 'aa'

    # find_missing(merged_df)

    # analyse_by_level(merged_df)
    a_list = (("2024-08-01 10:00:00","2024-08-01 14:11:00"),
              ("2024-08-02 6:00:00","2024-08-02 10:00:00"),
              ("2024-08-03 6:00:00","2024-08-03 10:02:00"),
              ("2024-08-04 22:02:00","2024-08-05 02:00:00"),
              ("2024-08-05 21:01:00","2024-08-06 01:00:00"),
              ("2024-08-06 21:00:00","2024-08-07 01:00:00"),
            ("2024-08-07 17:17:00","2024-08-07 21:00:00"),
              ("2024-08-08 17:00:00","2024-08-08 21:02:00"),
              ("2024-08-09 20:00:00","2024-08-10 0:10:00"),
              ("2024-08-10 16:00:00","2024-08-10 20:00:00"),
                ("2024-08-11 17:04:00","2024-08-11 21:00:00"),
              ("2024-08-12 13:00:00","2024-08-12 17:00:00"),
              ("2024-08-13 14:00:00","2024-08-13 18:00:00"),
              ("2024-08-14 16:05:00","2024-08-14 20:16:00"),
                ("2024-08-15 19:00:00","2024-08-15 23:05:00"),
              ("2024-08-16 19:03:00","2024-08-16 23:00:00"),
              ("2024-08-21 10:00:00","2024-08-21 14:00:00"),
              ("2024-08-22 6:00:00","2024-08-22 10:00:00"),
                ("2024-08-23 6:00:00","2024-08-23 10:08:00"),
              ("2024-08-24 12:09:00","2024-08-24 16:00:00"),
              ("2024-08-25 10:00:00","2024-08-25 14:00:00"),
              ("2024-08-26 10:08:00","2024-08-26 14:01:00"),
               ("2024-08-27 10:00:00","2024-08-27 14:00:00"),
               ("2024-08-28 11:00:00","2024-08-28 15:00:00"),
              
              
              
              )
    for item in a_list:
        analyse_by_anchor(merged_df, uid=item[0], start_dt=item[0], end_dt=item[1])
    raise

    # test
    # analyse_order(order_df, "2024-05-01 00:00:00","2024-08-16 0:00:00")



def create_order_table(path):
    order_df = pd.DataFrame()
    order_raw = pd.read_csv(path)
    order_df["order_id"] = order_raw["主订单编号"].astype(str)
    order_df["order_sub_id"] = order_raw["子订单编号"].astype(str)
    order_df["pname"] = order_raw["选购商品"].str.strip().astype(str)
    order_df["sub_name"] = order_raw["商品规格"].str.strip().astype(str)
    order_df["quantity"] = order_raw["商品数量"].astype(int)
    order_df["pid"] = order_raw["商品ID"].astype(str)
    order_df["price"] = order_raw["商品单价"].str.replace(',', '').astype(float)
    order_df["sales"] = order_raw["订单应付金额"].str.replace(',', '').astype(float)
    order_df["order_status"] = order_raw["订单状态"].astype(str)
    order_df["order_service"] = order_raw["售后状态"].astype(str)
    order_df["expert"] = order_raw["达人昵称"].astype(str)
    order_df["channel"] = order_raw["流量体裁"].astype(str)
    order_df["submit_dt"] = order_raw["订单提交时间"].apply(lambda x: pd.to_datetime(x))
    order_df["pay_dt"] = order_raw["支付完成时间"].apply(lambda x: pd.to_datetime(x))
    order_df["achieve_dt"] = order_raw["订单完成时间"].apply(lambda x: pd.to_datetime(x))

    order_df.to_sql("orderTable", conn, if_exists="replace")

def create_category_table(path):
    category_df = pd.DataFrame()
    with open(path, "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    data = []
    for item in config["category"]:
        # 将列表转换为列
        for i, pid in enumerate(item['pid_list']):
            data.append({
                'uid': item['uid'],
                'uname': item['uname'],
                'pid': pid
            })
    # 创建DataFrame
    category_df = pd.DataFrame(data)
    category_df.to_sql("category", conn, if_exists="replace")


def load_order(start_dt=None, end_dt=None, checkout=None):
    sql_str = "SELECT * FROM {}".format("orderTable")
    df = pd.read_sql(sql_str, conn, index_col="index", parse_dates=["submit_dt", "pay_dt", "achieve_dt"])
    if start_dt and type(start_dt) == type(""):
        start_dt = pd.to_datetime(start_dt)
    if end_dt and type(end_dt) == type(""):
        end_dt = pd.to_datetime(end_dt)
    if checkout == None:
        checkout = "pay_dt"
    order_df = df[(df[checkout] >= start_dt) & (df[checkout] < end_dt)]
    return order_df

def load_category():
    sql_str = "SELECT * FROM {}".format("category")
    category_df = pd.read_sql(sql_str, conn, index_col="index")
    return category_df

def find_missing(df):
    filtered_df = df[(df['uid'].isna()) & (df['sales'] > 1000)]
    selected_df = filtered_df[['sales', 'pid', 'pname', "uid"]]
    sorted_filtered_df = selected_df.sort_values(by='sales', ascending=False)
    unique_df = sorted_filtered_df.drop_duplicates(subset='pid')

    if len(unique_df) > 0:
        print(unique_df)
        logger.warning("add sth. not matched items")
        ipdb.set_trace()
    else:
        logger.info("message cover all items. > $1000")
    return

def analyse_by_anchor(df, uid=None, start_dt=None, end_dt=None, confirm_delivery = True):

    df = df[df['expert']=="格力官方旗舰店"] # 只要官旗
    #tmp
    if start_dt and type(start_dt) == type(""):
        start_dt = pd.to_datetime(start_dt)
    if end_dt and type(end_dt) == type(""):
        end_dt = pd.to_datetime(end_dt)
    df = df[(df["pay_dt"] >= start_dt) & (df["pay_dt"] < end_dt)]

    if confirm_delivery: # 只留下确认收货
        lite_df = df[(df['order_status'] == "已完成") & (df["order_service"] != "退款成功")]
    logger.debug("{} {} {}".format(uid, df["sales"].sum(), lite_df["sales"].sum()))
    # ipdb.set_trace()

def analyse_by_level(df, start_dt=None, end_dt=None, confirm_delivery = True):
    if confirm_delivery: # 只留下确认收货
        df = df[(df['order_status'] == "已完成") & (df["order_service"] != "退款成功")]
    if start_dt and type(start_dt) == type(""):
        start_dt = pd.to_datetime(start_dt)
    if end_dt and type(end_dt) == type(""):
        end_dt = pd.to_datetime(end_dt)

    lite_df = df[~(df['uid'].isna())] # remove NaN 只要空调
    sales_list = []
    quantity_list = []

    level_df =lite_df[lite_df['uid'].str.startswith('9')]
    group_df = level_df.groupby('uid')[['uname', 'sales', 'quantity']].agg({'uname': 'first', 'sales': 'sum', 'quantity': 'sum'})
    sort_df = group_df.sort_values('sales', ascending=False)
    # mixin= group_df[["sales", "quantity"]].sum().to_list()
    sales_sub = group_df["sales"].sum()
    quantity_sub = group_df["quantity"].sum()
    sales_list.append(sales_sub)
    quantity_list.append(quantity_sub)
    logger.debug("组合 => 销售额 {:>12.2f}   销售数量 {:6.0f}".format(sales_sub, quantity_sub))
    print(sort_df)

    level_df =lite_df[lite_df['uid'].str.startswith('7')]
    group_df = level_df.groupby('uid')[['uname', 'sales', 'quantity']].agg({'uname': 'first', 'sales': 'sum', 'quantity': 'sum'})
    sort_df = group_df.sort_values('sales', ascending=False)
    sales_sub = group_df["sales"].sum()
    quantity_sub = group_df["quantity"].sum()
    sales_list.append(sales_sub)
    quantity_list.append(quantity_sub)
    logger.debug("高端 => 销售额 {:>12.2f}   销售数量 {:6.0f}".format(sales_sub, quantity_sub))
    print(sort_df)

    level_df =lite_df[lite_df['uid'].str.startswith('5')]
    group_df = level_df.groupby('uid')[['uname', 'sales', 'quantity']].agg({'uname': 'first', 'sales': 'sum', 'quantity': 'sum'})
    sort_df = group_df.sort_values('sales', ascending=False)
    sales_sub = group_df["sales"].sum()
    quantity_sub = group_df["quantity"].sum()
    sales_list.append(sales_sub)
    quantity_list.append(quantity_sub)
    logger.debug("中端 => 销售额 {:>12.2f}   销售数量 {:6.0f}".format(sales_sub, quantity_sub))
    print(sort_df)

    level_df =lite_df[lite_df['uid'].str.startswith('3')]
    group_df = level_df.groupby('uid')[['uname', 'sales', 'quantity']].agg({'uname': 'first', 'sales': 'sum', 'quantity': 'sum'})
    sort_df = group_df.sort_values('sales', ascending=False)
    sales_sub = group_df["sales"].sum()
    quantity_sub = group_df["quantity"].sum()
    sales_list.append(sales_sub)
    quantity_list.append(quantity_sub)
    logger.debug("低端 => 销售额 {:>12.2f}   销售数量 {:6.0f}".format(sales_sub, quantity_sub))
    print(sort_df)

    logger.success("合计 => 销售额 {:>12.2f}   销售数量 {:6.0f}".format(sum(sales_list), sum(quantity_list)))


    ipdb.set_trace()



def analyse_order(order_df, start_time, end_time):
    total_sales = 0
    cfm_sales = 0
    cancel_sales = 0
    tbd_sales = 0
    tbd_detail = []

    total_df = order_df[(order_df['checkpoint'] >= start_time) & (order_df['checkpoint'] < end_time)]
    # total_df = total_df[total_df["expert"] == "格力官方旗舰店"]
    total_sales = total_df["sales"].sum()
    logger.success(total_df["p_count"].sum())


    cfm_df = total_df[total_df["order_status"] == "已完成"]
    cfm_df = cfm_df[cfm_df["order_service"] != "退款成功"]
    cfm_sales = cfm_df["sales"].sum()

    cancel_df = total_df[(total_df["order_status"] == "已关闭") | (total_df["order_service"] == "退款成功")]
    cancel_sales = cancel_df["sales"].sum()

    tbd_df = total_df.drop(cfm_df.index).drop(cancel_df.index)
    tbd_sales = tbd_df["sales"].sum()
    if tbd_sales != 0:
        for item in tbd_df["order_id"]:
            tbd_detail.append(item)
    # print(cfm_sales)
    return {"total_sales":total_sales, "cfm_sales": cfm_sales, "cancel_sales": cancel_sales,"tbd_sales": tbd_sales, "tbd_detail":tbd_detail}



def analyse_anchor():
    global anchor_list
    for anchor in anchor_list:
        logger.info(anchor)
        sub_df = race_df[race_df["uuid"] == anchor["uuid"]]
        dawn_list = []
        point_list = []
        for index in sub_df.index:
            if point_list == []:
                point_list.append(index)
            elif index - point_list[-1] < pd.Timedelta(hours=1):
                point_list.append(index)
            else:
                dawn_list.append([point_list[0],point_list[-1]])
                point_list = []
        if point_list != []:
            dawn_list.append([point_list[0],point_list[-1]])
        logger.warning(dawn_list)

        # logger.debug("M1")
        for dawn in dawn_list:
            score_list = analyse_anchor_cal(sub_df.loc[dawn[0] : dawn[1] - pd.Timedelta(seconds=1)])
            # score_list = analyse_anchor_cal(sub_df.loc[dawn[0] + pd.Timedelta(seconds=1) : dawn[1]])
            # update anchor_list
            if anchor["scores"][0] == 0:
                anchor["scores"] = score_list
            else:
                anchor["scores"] =  [(x + y * 2) / 3 for x, y in zip(anchor["scores"], score_list)]
            # logger.info(anchor["uuid"])
            # logger.info(anchor["scores"])


        # logger.debug("M2") # 平均方式
        # if anchor["scores"] == [0,0,0,0]:
        #     mean_scores = []
        # else:
        #     mean_scores = anchor["scores"]
        # for dawn in dawn_list:
        #     score_list = analyse_anchor_cal(sub_df.loc[dawn : dawn + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)])
        #     if score_list == None:
        #         continue
        #     # update anchor_list
        #     mean_scores.append(score_list)
        #     logger.warning(mean_scores)
        # logger.info(mean_scores)
        # if mean_scores != []:
        #     if type(mean_scores[0]) == type([]):
        #         anchor["scores"] = [sum(values) / len(values) for values in zip(*mean_scores)]
        #     else:
        #         anchor["scores"] = mean_scores
        # logger.debug(anchor["uuid"])
        # logger.debug(anchor["scores"])
    logger.success(anchor_list)

def analyse_anchor_cal(sub_race_df, observatory = 4):
    # logger.debug("analyse_anchor_cal")
    # logger.debug(sub_race_df)
    if len(sub_race_df) == 0:
        logger.error("check double")
        return None
    numeric_columns = sub_race_df.select_dtypes(include=['int64', 'float64']).columns 
    re_df = sub_race_df[numeric_columns].resample("60Min").mean()
    score_list = list((re_df["roi"] / 100) ** 2   + (re_df["sales"] / 5000) ** 2)
    # 补齐 4位
    score_list = score_list + [0] * (observatory - len(score_list))
    return score_list

def launch_old():
    global Pooh
    global anchor_df
    global anchor_list
    for anchor in anchor_list:
        logger.info(anchor)
        # 筛选出来最近的duty  目前是pandas 未来应该是list
        sub_df = anchor_df[anchor_df["uuid"] == anchor["uuid"]]
        # 这里的方式是  (x + y * 2) / 3 增大新一次权重
        logger.debug("M1")
        for index, row in sub_df.iterrows():
            score_list = analyse_anchor_cal_old(start_time = row["start_time"], end_time = row["end_time"])
            if score_list == None:
                continue
            # update anchor_list
            if anchor["scores"][0] == 0:
                anchor["scores"] = score_list
            else:
                anchor["scores"] =  [(x + y * 2) / 3 for x, y in zip(anchor["scores"], score_list)]
            logger.debug(anchor["uuid"])
            logger.debug(anchor["scores"])
        # logger.debug("M2") # 平均方式
        # if anchor["scores"] == [0,0,0,0]:
        #     mean_scores = []
        # else:
        #     mean_scores = anchor["scores"]
        # for index, row in sub_df.iterrows():
        #     score_list = analyse_anchor_cal_old(start_time = row["start_time"], end_time = row["end_time"])
        #     if score_list == None:
        #         continue
        #     # update anchor_list
        #     mean_scores.append(score_list)
        #     logger.warning(mean_scores)
        # logger.info(mean_scores)
        # if mean_scores != []:
        #     if type(mean_scores[0]) == type([]):
        #         anchor["scores"] = [sum(values) / len(values) for values in zip(*mean_scores)]
        #     else:
        #         anchor["scores"] = mean_scores
        # logger.debug(anchor["uuid"])
        # logger.debug(anchor["scores"])
    logger.success(anchor_list)
    # 上面完成给人的打分
    # 下面完成给slot打分



def analyse_slot():
    global race_df
    global slot_df

    re_df = race_df.resample("60Min").agg({"status":"first","uuid":"first","consume":"mean","roi":"mean","sales":"mean","refunds":"mean"})
    slot_series = (re_df["roi"] / 100) ** 2   + (re_df["sales"] / 5000) ** 2
    for slot_t,slot_v  in slot_series.items():
        if pd.isna(slot_v):
            continue
        day_of_week = slot_t.day_of_week
        hour_of_day = slot_t.hour
        before_value = slot_df.iloc[hour_of_day, day_of_week]
        if before_value == 0:
            slot_df.iloc[hour_of_day, day_of_week] = slot_v
        else:
            slot_df.iloc[hour_of_day, day_of_week] =  [(x + y * 2) / 3 for x, y in zip(before_value, slot_v)]
    logger.success(slot_df)

def plan_ancher():
    global slot_df
    global plan_df
    global anchor_list

    day_name  = pendulum.now().start_of('day').day_of_week.name

    best_score = 0
    best_list = []
    best_uuid_list = []
    best_name_list = []
    for i in range(10000):
        mixin_list = []
        uuid_list = []
        name_list = []
        dp_dash = []

        random_list = random.sample(anchor_list, len(anchor_list))
        for ancher_item in random_list:
            score_list = list(ancher_item["scores"])
            score_count = len(score_list)
            score_rand = random.randint(0, score_count)
            mixin_list.extend(score_list[0:score_rand])
            ancher_item["duration"] = score_rand
            dp_dash.append(ancher_item)
        uuid_list = fix_end(slot_df[day_name], dp_dash, mixin_list)
        name_list = [find_name(item) for item in uuid_list]
        if len(uuid_list)> 24:
            uuid_list = uuid_list[:24]
            name_list = name_list[:24]
        if len(uuid_list)< 24:
            uuid_list += [0] * (len(slot_df[day_name]) - len(uuid_list))
            name_list += [0] * (len(slot_df[day_name]) - len(name_list))
        res_score = calc(slot_df[day_name], mixin_list)
        if res_score > best_score:
            best_score = res_score
            best_list = dp_dash
            best_uuid_list = uuid_list
            best_name_list = name_list
            logger.debug("Update Best: {}".format(best_score))
            logger.success(best_list)
            logger.debug(mixin_list)
            logger.debug(best_uuid_list)
            logger.debug(best_name_list)
            plan_df[day_name] = name_list



    logger.info("Best: {}".format(best_score))
    logger.success(plan_df)




def analyse_anchor_cal_old(start_time=None, end_time=None, duration=None, observatory=4):
    global race_df

    # sub_df = race_df[(race_df["time"] >= start_time) & ( race_df["time"] < end_time)].set_index("time")
    print("Strat {}".format(start_time))
    end_time = end_time - pd.Timedelta(seconds=1)
    sub_df = race_df.loc[start_time: end_time]
    logger.debug(sub_df)
    if len(sub_df) == 0:
        return None
    re_df = sub_df.resample("60Min").mean()
    logger.debug(re_df)
    score_list = list((re_df["roi"] / 100) ** 2   + (re_df["sales"] / 5000) ** 2)
    # 补齐 4位
    score_list = score_list + [0] * (observatory - len(score_list))
    logger.debug(score_list)
    return score_list


def load_anchor():
    global anchor_list
    with open(Path() / "plan"/ "config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    anchor_list = list(config["anchor"])

def load():
    global race_df
    global anchor_df

    race_raw = pd.read_excel(Path()/"plan"/"traffic.xlsx")
    race_df = pd.DataFrame()
    race_df["time"] = race_raw['时段'].apply(lambda x: pd.to_datetime("2024-" + x.split("~")[0]))
    race_df["cost"] = race_raw['总投放消耗']
    race_df["roi"] = race_raw['全场ROI']
    race_df["sales"] = race_raw['总销售额']
    race_df.set_index("time", inplace=True)
    # anchor not use anymore
    anchor_raw = pd.read_excel(Path()/"plan"/"anchor.xlsx")
    anchor_df = pd.DataFrame()
    anchor_df["name"] = anchor_raw['主播']
    anchor_df["uuid"] = anchor_raw['主播'].apply(lambda x: find_uuid(x))
    anchor_df["start_time"] = pd.to_datetime(anchor_raw['上播时间'])
    anchor_df["end_time"] = pd.to_datetime(anchor_raw['下播时间'])
    anchor_df["duration"] = anchor_raw['直播时长（小时）']
    anchor_df["sales"] = anchor_raw['销售额']
    logger.debug(race_df)
    logger.debug(anchor_df)




def find_uuid(name):
    for item in anchor_list:
        if item["name"] == name:
            return item["uuid"]
    return -1

def find_name(uuid):
    for item in anchor_list:
        if item["uuid"] == uuid:
            return item["name"]
    return -1

def create_slot_df():
    global slot_df
    global plan_df
    base_day = pendulum.now().end_of('week')
    weekname_list = []
    for num in range(7):
        on_day = base_day.add(days=num)
        weekname_list.append(on_day.day_of_week.name)
    logger.debug(weekname_list)

    slot_df = pd.DataFrame(0.0,index=[f"{hour:02d}:00" for hour in range(24)],columns=weekname_list)
    plan_df = pd.DataFrame(0.0,index=[f"{hour:02d}:00" for hour in range(24)],columns=weekname_list)

    print(slot_df)
    print(plan_df)



def pretty_traffic():
    global traffic_list
    for item in traffic_list:
        raw = "2024-" + item["time"].split("~")[0]
        item["time"] = pendulum.parse(raw,tz="Asia/Shanghai").to_iso8601_string()
    logger.debug(traffic_list)



def test():
    # 假设有24个小时的时间分
    # slot_list = [1,1,2,2,3,4,4,5,6,7,    7,8,8,8,8,8,8,8,8,8,   8,8,10,10]
    slot_list = [1,1,2,2,3,4,3,2]
    people_list = [{
                        "uuid": "0001",
                        "name": "GeLi_Gaoming",
                        "scores":[5,4,4,3,3,2],
                    },
         {
            "uuid": "0002",
            "name": "GeLi_Gaoming2",
            "scores":[2,2,2,2],
        },
                 {
            "uuid": "0003",
            "name": "GeLi_Gaoming3",
            "scores":[6,5,2,1],
        },
                         {
            "uuid": "000a",
            "name": "GeLi_Gaoming--",
            "scores":[0,0,0,0],
        }
        ]

    best_score = 0
    best_dict = {}

    while True:
        mixin_list = []
        dp_dash = []

        random_list = random.sample(people_list, len(people_list))
        for ancher_item in random_list:
            score_count = len(ancher_item["scores"])
            score_rand = random.randint(1, score_count)
            mixin_list.extend(ancher_item["scores"][0:score_rand])
            ancher_item["duration"] = score_rand
            dp_dash.append(ancher_item)
        fix_end(slot_list, dp_dash, mixin_list)
        res_score = calc(slot_list, mixin_list)
        if res_score > best_score:
            best_score = res_score
            best_dict = dp_dash
            logger.success("Best: {}".format(best_score))
            logger.success(best_dict)
            logger.debug(mixin_list)
            # logger.debug("Current: {}".format(res_score))
            # logger.debug(mixin_list)
            # logger.debug(dp_dash)

        # logger.info("Best: {}".format(best_score))
        # logger.info(best_dict)


def calc(slot_list, people_list):
    output = 0
    ex_list = people_list + [0] * (len(slot_list) - len(people_list))
    for index in range(len(slot_list)):
        output += slot_list[index] * ex_list[index]
    return output

def fix_end(slot_list, dp_list, mixin_list):
    # dp_list = [[{'uuid': '0006', 'name': '好好', 'scores': [7.8909953781481486, 6.254293933649073, 4.775636138333333, 11.730393876666668], 'duration': 1},
    # mixin_list = [1,2,3,4,5,6,]
    count = 0
    uuid_list = []
    for item in dp_list:
        count += item["duration"]
        diff = count - len(slot_list)
        if diff > 0:
            item["duration"] = max(0, item["duration"]-diff)
        uuid_list.extend([item["uuid"]] * item["duration"])
    mixin_list[:] = mixin_list[:len(slot_list)]
    return uuid_list

def test_dftime():
    # pltime is pendulum time
    # pdtime is pandas time
    pandastime = pd.to_datetime('2023-04-01 12:00:00')
    pendulumtime = pendulum.parse(pandastime.isoformat(), tz="Asia/Shanghai")
    pendulumtime.to_iso8601_string()
    pandastime.isoformat()
    pandastime.tz_convert("Asia/Shanghai")
    race_df["iso"] = race_df.index.tz_localize("Asia/Shanghai")

    raw_df = pd.read_sql_query("SELECT * FROM race", conn)
    race_df.to_sql("race", conn, if_exists="append")


def convert_from_csv_to_sqlite():
    global race_df
    race_raw = pd.read_excel(Path()/"plan"/"traffic.xlsx")
    race_df = pd.DataFrame()
    race_df["checkpoint"] = race_raw['时段'].apply(lambda x: pd.to_datetime("2024-" + x.split("~")[0]))
    race_df["consume"] = race_raw['总投放消耗']
    race_df["roi"] = race_raw['全场ROI']
    race_df["sales"] = race_raw['总销售额']
    race_df.set_index("checkpoint", inplace=True)
    race_df.sort_index()

    anchor_raw = pd.read_excel(Path()/"plan"/"anchor.xlsx")
    anchor_df = pd.DataFrame()
    anchor_df["name"] = anchor_raw['主播']
    anchor_df["uuid"] = anchor_raw['主播'].apply(lambda x: find_uuid(x))
    anchor_df["start_time"] = pd.to_datetime(anchor_raw['上播时间'])
    anchor_df["end_time"] = pd.to_datetime(anchor_raw['下播时间'])
    anchor_df["duration"] = anchor_raw['直播时长（小时）']
    anchor_df["sales"] = anchor_raw['销售额']


    for _, row in anchor_df.iterrows():
        race_df.loc[row["start_time"]: row["end_time"], "uuid"] = row["uuid"]
        race_df.loc[row["start_time"]: row["end_time"], "status"] = 1

    race_df.to_sql("race", conn, if_exists="append")





if __name__ == "__main__":
    # boot()
    # logger.debug(Pooh)
    # raise
    # launch()
    # sqliteDB.init_db_anchor(conn)
    # load_anchor()
    

    # create_slot_df()
    # # load()
    # sqliteDB.init_db_race(conn)
    # convert_from_csv_to_sqlite()

    launch()
    # analyse_slot()
    # plan_ancher()
    # pretty_traffic()
    # test()
