import time
import re
import json
from pathlib import Path
import pendulum
import random

import sqlite3
from playwright.sync_api import sync_playwright
from tenacity import retry, stop_after_attempt
import ipdb

import requests

import tomlkit
import kimiDB
import sqliteDB

from util import logConfig, logger, lumos, Nox

logConfig("logs/rebuild0x01.log", rotation="10 MB", level="DEBUG", lite=True)

conn = sqlite3.connect("db.sqlite3")

Pooh = {}


COOKIE = Path() / "cookies" / "Bellamy_hai.json"
# COOKIE = Path() / "cookies" / "cookie_Bellamy_177.json"

main_path = Path() / "data" / "32-1"
########################################################################################


def launch():
    global Pooh
    kimiDB.boot(Pooh.get("MOONSHOT_API_KEY", None))

    Pooh.update({"first_flag": True})

    # Arrange data
    logger.info("Load config & PNG ")
    with open(main_path / "config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    logger.info(config)
    uid = config["uid"]
    uname = config["uname"]
    base_id = config["base_id"]
    # limit_id = config["limit_id"]
    figure_config = config["figure"]
    # sale_list = config["sale"]

    # figure_list :  [{'a0': WindowsPath('data/10015/1-1/1.png'), 'b0': WindowsPath('data/10015/4-3/1.png')},
    figure_list = []
    position_list = [item["name"] for item in figure_config]
    symbol_list = [list(main_path.glob(item["symbol"])) for item in figure_config]
    symbol_count = len(symbol_list[0])
    for i in range(symbol_count):
        current_dict = {}
        for position_, symbols_ in zip(position_list, symbol_list):
            current_dict[position_] = symbols_[i]
        figure_list.append(current_dict)
    logger.debug(figure_list)

    # check rule
    if not uid in str(main_path):
        logger.error("UID error")
        raise
    if not are_lengths_equal(symbol_list):
        logger.error("PNG length not same")
        raise
    logger.success("Load Complate")

    logger.info("Login Shop")
    # Act
    if not COOKIE.exists():
        store_cookie()
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=False)
        # browser = p.firefox.launch(headless=False)
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(storage_state=COOKIE)
        page = context.new_page()
        page.set_viewport_size({"width": 1480, "height": 900})
        time.sleep(1)
        if login_shop(page, "Bellamy"):
            logger.success("Login success")
        else:
            logger.error("Login Fail")
            raise

        time.sleep(1)

        ########## Login success
        # traffic_uni(page, "3705716058318045239", "大罐米粉")
        # raise

        # test
        # now = pendulum.now("Asia/Shanghai")
        # print(fetch_pid(page, "贝拉米宝宝婴儿营养米粉婴幼儿细腻原味有机高铁吸收冲泡米糊", pendulum.parse("2024-09-06 14:36:04.416008+08:00")))
        # raise
        # print(fetch_pid(page, "Bellamy’s/贝拉米婴幼儿配方白金版1-2岁白金A23段有机奶粉800g", pendulum.parse("2024/08/25 00:40:20",tz="Asia/Shanghai"),))
        # rebuild_product(
        #             page, "3699390584943935717", None, "no"
        #         )
        # kucun(page, "3703133520093380781")  # 全域推广
        # traffic_uni(page, "3699390584943935717", "ACN")  # 全域推广
        # limitsales(page, "7395136078669463849", [{"origin": 7899},{"origin": 6899}])
        # 测试搜索限时限量购返回ID
        # limitsales(page, "7395136078669463849", None,None)
        # 测试批量改价格
        # limitsales(page, "7395136078669463849", [{"origin": 7899,"price":7299},{"origin": 6899, "price": 6399}], pid_target=None)
        # 测试更新单体限时限量购
        # limitsales(page, "7395136078669463849", [{"origin": 7899,"price":7299},{"origin": 6899, "price": 6399}], "3640428409366182930")

        # qianchuan(page, "3604058235763602348", "云锦2代挂机" )
        # fetch_pid(page, "【夏日健康风】格力↘空调云轩大1匹1.5匹1级能效时尚挂机大风力")
        # rebuild_product(
        #             page, "3699390584943935717", None, "no"
        #         )
        # ipdb.set_trace()
        # limitsales(page, limit_id,  sale_list, pid)
        tmp_count = load_tmp_count()
        if tmp_count == symbol_count:
            logger.success("Finish all {}.".format(tmp_count))
            time.sleep(6000)
        for index in range(
            tmp_count, symbol_count
        ):  # symbol_count  如果这里不能跑了，从哪个开始，把 0 改成对应的值
            figure_dict = figure_list[index]
            if any(not item.exists() for item in figure_dict.values()):
                logger.error("not find pic {}".format(index))
                continue
            logger.success("On Job: {}".format(index))
            now = pendulum.now("Asia/Shanghai")
            now_str = str(now)[:19]
            ns = rebuild_product(page, base_id, figure_dict, uname)
            new_title = ns.payload
            if not ns:
                raise
                ipdb.set_trace()
            time.sleep(1)
            # drop fetch new pid
            # for retry_times in range(500):
            #     pid = fetch_pid(page, new_title)
            #     if pid:
            #         break
            #     else:
            #         logger.debug("New id retry {} times".format(retry_times + 1))
            #     if retry_times == 400:
            #         logger.error("First step fail on {}".format(index))
            #         raise
            #     time.sleep(4)
            # continue
            pid, checkpoint = fetch_pid(page, new_title, now)
            record_id(main_path / "record.txt", pid)

            sqliteDB.rebuild_insert(conn, "core", {"uid":uid, "uname":uname, "pid":pid, "pname":new_title, "status": 1, "checkpoint": checkpoint})
            logger.info(pid)

            # ADD kucun
            # ns = kucun(page, pid, 2)  # 库存
            # if not ns:
            #     ipdb.set_trace()
            # sqliteDB.rebuild_update_by_pid(conn, "core", pid, {"status":2})

            # limitsales(page, limit_id, sale_list, pid)  # 限时限量购
            # traffic_standard(page, pid, uname)  # 标准推广
            ns = traffic_uni(page, pid, uname)  # 全域推广
            if not ns:
                raise
                ipdb.set_trace()
            sqliteDB.rebuild_update_by_pid(conn, "core", pid, {"status":0})
            logger.success("Done {}".format(pid))
            logger.success("Finish index: ================ {}".format(index))
            time.sleep(3)
            save_tmp_count(index+1)
        logger.success("Finish all {}.".format(index + 1))
        browser.close()


def store_cookie():
    # current store all cookies
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        # browser = p.chromium.launch(headless=False, executable_path="./chromium-1124/chrome-win/chrome.exe" )
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({"width": 1480, "height": 900})
        # page.set_viewport_size({"width": 1280, "height": 720})
        page.goto("https://fxg.jinritemai.com/login/common")
        # page.wait_for_selector("#svg_icon_avatar")

        logger.info("Please Login~")
        logger.info("Input 'continue' if finish.")
        logger.info("https://business.oceanengine.com/login")
        logger.info("https://fxg.jinritemai.com/login/common")

        ipdb.set_trace()
        logger.info("login end")

        if not COOKIE.exists():
            storage = context.storage_state(path=COOKIE)
            logger.success("Login success. Save to {}".format(COOKIE))
        else:
            logger.warning("Login fail. Use anonymous mode.")
        browser.close()


@retry(stop=stop_after_attempt(20))
def fetch_pid(page, target_title, init_dt, must_flag=True):
    # goto list
    page.goto("https://fxg.jinritemai.com/ffa/g/list")
    # ready
    time.sleep(5)
    if not page.locator(".ecom-g-table-row").count():
        time.sleep(5)

    # select pid
    row_elem = page.locator(".ecom-g-table-row")
    row_count = row_elem.count()
    logger.debug("Search title {}".format(target_title))
    logger.debug("Search checkpoint {}".format(init_dt))
    # ipdb.set_trace()
    for index in range(row_count):
        pid = row_elem.nth(index).get_attribute("data-row-key")
        title = row_elem.nth(index).locator(".style_productNameNew__3eWnv").inner_text()
        # sub_title = row_elem.nth(index).locator(".style_productNameNew__3eWnv").inner_text()[10:]
        time_str = page.locator(".ecom-g-table-row").nth(index).locator(".style_timeSortTitle__mXOD6").inner_text()
        checkpoint = pendulum.parse(time_str.split()[0] + " " + time_str.split()[1], tz="Asia/Shanghai")
        checkpoint_str  =str(checkpoint)[:19]
        if title == target_title and init_dt <= checkpoint:
            print(title)
            print(init_dt)
            print(checkpoint)
            logger.info("Find New ID {}".format(pid))
            return pid, checkpoint_str
    if must_flag == True:
        logger.debug("Not found - Retry")
        time.sleep(5)
        raise
    else:
        return

@retry(stop=stop_after_attempt(3))
def rebuild_product(page, copyid, figure, uname=None):
    page.goto("https://fxg.jinritemai.com/ffa/g/create?copyid={}".format(copyid))
    time.sleep(2)
    full_name_elem = page.get_by_placeholder("请输入15-60个字符（8-30个汉字）")
    short_name_elem = page.get_by_placeholder(
        "建议填写简明准确的标题内容，避免重复表达"
    )
    # kimi full_name
    user_content = (
        "{}\n"
        "处理上一句变换顺序,不改变原意，去掉标点符号,去掉空格\n"
        "{} 是一个词组,\n"
        "\n".format(full_name_elem.first.input_value(), uname)
    )
    res_dict = kimiDB.ask(user_content)
    full_name_str = res_dict["data"].replace(" ", "")
    # kimi short_name
    user_content = (
        "{}\n"
        "处理上一句变换顺序,不改变原意，去掉标点符号,去掉空格\n"
        "{} 是一个词组,\n"
        "\n".format(short_name_elem.first.input_value(), uname)
    )
    res_dict = kimiDB.ask(user_content)
    # short_name_str = res_dict["data"]
    short_name_str = short_name_elem.first.input_value()
    # remove 商品信息质量分提示
    if Pooh["first_flag"]:
        poll_sugar(
            page.locator(".ecom-guide-normal-step-button").get_by_role(
                "button", name="知道了"
            ),
            timeout=15,
        )
        Pooh["first_flag"] = False
    time.sleep(1)
    click_sugar(page.get_by_role("tooltip").get_by_role("button", name="知道了"))
    # remove kefu
    click_sugar(page.locator("#DOUXIAOER_WRAPPER").locator(".index_union__1bLD3"))
    time.sleep(0.5)
    # ipdb.set_trace()
    # ready
    # 基础信息  page.locator("#goodsEditScrollContainer-基础信息")
    # 基础信息 2 page.locator(".goods-publish-highlight-group")
    # page.locator("#goodsEditScrollContainer-图文信息")
    # page.locator("#goodsEditScrollContainer-权益")
    # page.locator("#goodsEditScrollContainer-价格库存")
    # #goodsEditScrollContainer-尺码信息
    # #goodsEditScrollContainer-服务与履约
    # #goodsEditScrollContainer-商品资质
    # #goodsEditScrollContainer-质检信息
    # #goodsEditScrollContainer-达人带货

    full_name_elem.first.fill(full_name_str)
    while page.get_by_text("最长不能超过30个汉字").count():
        page.keyboard.press("Backspace")
        time.sleep(0.1)
    short_name_elem.first.fill(short_name_str)

    # change 型号 for 格力
    # page.locator('div[attr-field-id="型号"]').click()
    # time.sleep(1)
    # page.get_by_text("+新建型号").click()
    # time.sleep(1)
    # page.get_by_placeholder("请输入自定义属性").fill(uname)
    # time.sleep(1)
    # page.get_by_role("img", name="确认").click()
    # time.sleep(1)
    # page.locator("#rc_select_1").fill(uname)
    # # ipdb.set_trace()
    # # page.keyboard.type(uname)
    # time.sleep(1)
    # page.keyboard.press("Enter")
    # poll_sugar(page.get_by_role("button", name="重新编辑商品信息"), timeout=5)
    # time.sleep(0.2)

    # figure
    click_sugar(page.locator(".ecom-g-tabs").get_by_text("图文信息"))
    time.sleep(1)

    # 1:1
    image_elem = page.locator(".styles_mainImg__Gl6ii").locator("ul").locator("img")
    image_count = image_elem.count()
    if image_count:
        blank_elem = (
            page.locator(".styles_mainImg__Gl6ii")
            .locator("ul")
            .locator(".upload_button__17N5e")
        )
        box_list = []  # image box position
        for num in range(image_count):
            if image_elem.nth(num).is_visible():
                box_list.append(image_elem.nth(num).bounding_box())

        for num in range(5 - image_count):
            if blank_elem.nth(num).is_visible():
                box_list.append(blank_elem.nth(num).bounding_box())
        # delete
        image_elem.nth(0).hover()
        page.mouse.move(box_list[0]["x"] + 76, box_list[0]["y"] + 90)
        page.mouse.click(box_list[0]["x"] + 76, box_list[0]["y"] + 90)
        time.sleep(1)
        if (
            page.locator(".styles_mainImg__Gl6ii").locator("ul").locator("img").count()
            != image_count - 1
        ):
            logger.error("image not count correct")
        blank_elem = (
            page.locator(".styles_mainImg__Gl6ii")
            .locator("ul")
            .locator(".upload_button__17N5e")
        )
        blank_elem.first.hover()
        page.get_by_role("tooltip", name="本地上传 图库选择 智能做图").locator(
            "label"
        ).set_input_files(figure["a0"])
        time.sleep(4)
        if (
            page.locator(".styles_mainImg__Gl6ii").locator("ul").locator("img").count()
            != image_count
        ):
            logger.error("image not count correct after upload")
            raise
        act_move(page, box_list, image_count - 1, 0)
    else:
        logger.info("Skip 1:1")

    # 3:4
    image_elem = page.locator(".styles_mainImg__3Kags").locator("ul").locator("img")
    image_count = image_elem.count()
    if image_count:
        blank_elem = (
            page.locator(".styles_mainImg__3Kags")
            .locator("ul")
            .locator(".upload_button__17N5e")
        )
        box_list = []  # image box position
        for num in range(image_count):
            if image_elem.nth(num).is_visible():
                box_list.append(image_elem.nth(num).bounding_box())

        for num in range(5 - image_count):
            if blank_elem.nth(num).is_visible():
                box_list.append(blank_elem.nth(num).bounding_box())
        # delete
        image_elem.nth(0).hover()
        page.mouse.move(box_list[0]["x"] + 76, box_list[0]["y"] + 118)
        page.mouse.click(box_list[0]["x"] + 76, box_list[0]["y"] + 118)
        time.sleep(1)
        if (
            page.locator(".styles_mainImg__3Kags").locator("ul").locator("img").count()
            != image_count - 1
        ):
            logger.error("image not count correct")
        blank_elem = (
            page.locator(".styles_mainImg__3Kags")
            .locator("ul")
            .locator(".upload_button__17N5e")
        )
        blank_elem.first.hover()
        page.get_by_role("tooltip", name="本地上传 图库选择 智能做图").locator(
            "label"
        ).set_input_files(figure["b0"])
        time.sleep(4)
        if (
            page.locator(".styles_mainImg__3Kags").locator("ul").locator("img").count()
            != image_count
        ):
            logger.error("image not count correct after upload")
            raise
        act_move(page, box_list, image_count - 1, 0)
    else:
        logger.info("Skip 3:4")


    # 物流信息
    # click_sugar(page.locator(".ecom-g-tabs").get_by_text("物流信息"))
    # time.sleep(1)
    # page.locator("#rc_select_9").click()
    # time.sleep(0.5)
    # page.locator("#rc_select_9").fill("澳大利亚")
    # time.sleep(0.3)
    # page.locator("#rc_select_9").press("Enter")
    # time.sleep(0.3)
    # page.locator("#rc_select_10").click()
    # time.sleep(0.5)
    # page.locator("#rc_select_10").fill("澳大利亚")
    # time.sleep(0.3)
    # page.locator("#rc_select_10").press("Enter")
    # time.sleep(0.3)
    # page.locator("#rc_select_11").click()
    # time.sleep(0.5)
    # page.locator("#rc_select_11").fill("澳大利亚")
    # time.sleep(0.3)
    # page.locator("#rc_select_11").press("Enter")
    # time.sleep(0.3)

    # 含有品牌名
    # full_name_final = (
    #     page.locator(".ecom-g-input-group-addon").inner_text()
    #     + page.get_by_placeholder("请输入15-60个字符（8-30个汉字）").first.input_value()
    # )
    #不含品牌名
    full_name_final = (
        page.get_by_placeholder("请输入15-60个字符（8-30个汉字）").first.input_value()
    )
    # check error
    if page.locator(".has-error").count() or page.locator(".sp-tag-error").count():
        logger.debug("modify then press continue")
        raise
        ipdb.set_trace()
    # Final check !!!
    # ipdb.set_trace()
    time.sleep(0.5)
    page.get_by_role("button", name="发布商品").click()
    time.sleep(5)

    logger.debug("End rebuild_product")
    return Nox(0, full_name_final)


def act_move(page, box_list, from_idx, to_idx):
    page.mouse.move(box_list[from_idx]["x"] + 50, box_list[from_idx]["y"] + 50)
    page.mouse.down()
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.up()

@retry(stop=stop_after_attempt(3))
def kucun(page, pid, quantity = 2):
    logger.debug("on kucun")
    page.goto("https://fxg.jinritemai.com/ffa/supply-chain-inventory/goods-inventory")
    time.sleep(4)
    page.get_by_placeholder("请输入商品ID").fill(pid)
    time.sleep(0.3)
    page.get_by_role("button", name="查询").click()
    time.sleep(1.5)
    icon_els = page.locator(".auxo-table-row").locator(".icon")
    if icon_els.count() == 1:
        icon_els.click()
        time.sleep(0.5)
    else:
        logger.debug("Waiting multi icon")
        raise
        ipdb.set_trace()
    now_quantity = get_kuncun_quantity(page.locator('.auxo-table-expanded-row-fixed').inner_text())
    if now_quantity < quantity:
        need_quantity = quantity - now_quantity
        logger.debug("need add {}".format(need_quantity))
    else:
        return
    page.get_by_role("cell", name="可售库存", exact=False).locator("svg").last.click()
    time.sleep(0.5)
    # page.locator("[id=\"\\34 PLZWYBBC01_4PLZWYBBC01\"]").fill("{}".format(quantity)) # 宁波仓
    page.locator("[id=\"\\34 PLZYBBC01_4PLZYBBC01\"]").fill("{}".format(quantity)) # 广州仓
    time.sleep(0.5)
    # final check
    # ipdb.set_trace()
    page.get_by_role("button", name="确定").click()
    time.sleep(4)

    #check
    now_quantity = get_kuncun_quantity(page.locator('.auxo-table-expanded-row-fixed').inner_text())
    if now_quantity == quantity:
        logger.info("check quantity is {}".format(now_quantity))
        return Nox(0)
    else:
        logger.error("check quantity is {} != {}".format(now_quantity, quantity))
        raise
        ipdb.set_trace()
        return Nox(0)


def get_kuncun_quantity(row_str):
    row_list = row_str.split()
    for index, value in enumerate(row_list):
        if value == "可售库存":
            break
    quantity = int(row_list[index+1])
    return quantity

@retry(stop=stop_after_attempt(3))
def limitsales(page, limit_id, sale_list=None, pid_target=None):
    """
    sale_list = [{"origin": , "price": }]
    sale_list == None pid_target = None 表示只搜索页面ID
    sale_list != None pid_target = None 表示改价
    sale_list != None pid_target = ID 表示添加新限时限量购
    sale_list == None pid_target = ID 单一改价 （未测试）
    # origin 只要在sale_list 中就会检查原价 (目前不能查询时候不检查)
    """
    page.goto(
        "https://fxg.jinritemai.com/ffa/marketing/tools/limitsales/detail?refer=edit&id={}".format(
            limit_id
        )
    )
    time.sleep(2)
    # ready
    if pid_target:
        page.get_by_role("button", name="添加商品").scroll_into_view_if_needed()
        time.sleep(1)
        page.get_by_role("button", name="添加商品").click()
        time.sleep(1)
        page.locator("form").get_by_role("textbox", name="请输入商品ID").fill(
            pid_target
        )
        time.sleep(0.5)
        page.locator("form").get_by_role("button", name="search").click()
        time.sleep(1)
        page.get_by_role("row", name="商品信息 商品原价 商品库存").get_by_label(
            ""
        ).check()
        time.sleep(1)
        page.get_by_role("button", name="选择").click()
        time.sleep(1)
        page.get_by_placeholder("请输入商品ID").fill(pid_target)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        # page.get_by_role("button", name="search").click()
        time.sleep(1)
        page.locator(".ecom-mcenter-table-row").get_by_text("1", exact=True).click()
        # page.locator(".ecom-mcenter-table-row").first.locator("td:nth-child(6) > div:nth-child(1)").locator(".ecom-mcenter-select-selector").click()
        time.sleep(0.5)
        page.locator(".rc-virtual-list-holder-inner").get_by_title(
            "5", exact=True
        ).locator("div").click()
        time.sleep(0.5)
        page.get_by_role("switch").click()
        time.sleep(0.5)
        page.mouse.wheel(0, 1024)
        time.sleep(0.5)
    else:
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 1024 * 1024)
        time.sleep(0.5)
        page.locator("span").filter(has_text="条/页").click()
        time.sleep(0.5)
        page.get_by_title("100 条/页").scroll_into_view_if_needed()
        time.sleep(0.5)
        page.get_by_title("100 条/页").click()
        time.sleep(0.5)
        page.get_by_role("switch").scroll_into_view_if_needed()
        time.sleep(0.5)
        page.get_by_role("switch").click()
        time.sleep(0.5)

    row_elems = page.locator(".ecom-mcenter-table-row")
    row_count = row_elems.count()
    logger.debug("Found ID count: {}".format(row_count))
    if pid_target and row_count != 1:
        raise
        ipdb.set_trace()

    # act
    pid_list = []
    for line_index in range(row_count):
        row_elem = row_elems.nth(line_index)
        pid = (
            row_elem.locator("td:nth-child(1) > div:nth-child(1)")
            .get_by_text("ID：")
            .inner_text()[3:]
        )  # ID
        logger.debug("Focus ID: {}".format(pid))
        if pid_target and pid != pid_target:
            logger.debug("pid != pid_target")
            raise
            ipdb.set_trace()
        if not sale_list:
            pid_list.append(pid)
            continue
        for index in range(len(sale_list)):
            origin_input = sale_list[index].get("origin", None)
            price_input = sale_list[index].get("price", None)
            # 原价
            if origin_input:
                raw_ = (
                    row_elem.locator(
                        "td:nth-child(2) > div:nth-child({})".format(index + 2)
                    )
                    .get_by_text("¥")
                    .inner_text()
                )
                origin_online = float(raw_.split("¥")[-1].replace(",", ""))
                if origin_online == origin_input:
                    pid_list.append(pid)
                else:
                    logger.warning("Attention ID: {}".format(pid))
                    logger.warning(
                        "origin_online: {} != origin_input: {}".format(
                            origin_online, origin_input
                        )
                    )
                    raise
                    ipdb.set_trace()
                    continue
            # input
            if price_input:
                logger.debug(
                    "Update price origin {} to {}".format(origin_input, price_input)
                )
                row_elem.locator(
                    "td:nth-child(3) > div:nth-child({})".format(index + 2)
                ).locator("input").fill(str(price_input))
            else:
                continue

    # Final Check
    # ipdb.set_trace()
    if not sale_list:
        return Nox(0, pid_list)
    page.get_by_role("button", name="提交").click()
    time.sleep(10)
    click_sugar(page.get_by_role("button", name="仍要创建"))
    logger.debug("finish shot {}".format(pid_target))
    # page.pause()
    time.sleep(2)
    return Nox(0, pid_list)

@retry(stop=stop_after_attempt(3))
def traffic_standard(page, pid_target, uname):
    """标准推广"""
    # page.goto(
    #     "https://qianchuan.jinritemai.com/promotion-v2/standard?aavid=1712324674292736"
    # )
    page.goto(
        "https://qianchuan.jinritemai.com/creation/feed-video-standard?type=create&aavid=1712324674292736"
    )
    time.sleep(1)
    # ipdb.set_trace()
    # kimi title_list
    user_content = (
        "给我10个贝拉米奶粉的种草标题.每个标题 30 至 50个汉字,禁止用广告极限词."
        ".输出 30 至 50 个字符 \n"
        ".输出json格式,key='data'"
    )
    res_dict = kimiDB.ask(user_content)
    kimi_title_list = res_dict["data"]
    # kimi label_list
    user_content = (
        "给我10个贝拉米奶粉的种草标签.禁止用广告极限词."
        "用空格分割，写在一个字符串当中. \n"
        ".输出json格式,key='data'"
    )
    res_dict = kimiDB.ask(user_content)
    kimi_label = res_dict["data"]

    # ipdb.set_trace()
    page.locator("#deliveryTarget").get_by_text("添加商品").click()
    time.sleep(1)
    # product mask
    if not page.locator(".oc-drawer-close").is_visible():
        time.sleep(0.5)
    page.get_by_placeholder("请输入商品名称/ID搜索").fill(pid_target)
    time.sleep(1)
    page.keyboard.press("Enter")
    time.sleep(1)
    page.locator(".ovui-radio__inner").first.click()
    time.sleep(1)
    page.get_by_role("button", name="确定").click()
    time.sleep(1)
    page.get_by_text("商品支付ROI", exact=True).click()
    time.sleep(1)
    page.get_by_placeholder("请输入金额").fill("999")
    time.sleep(0.5)
    page.get_by_placeholder("请输入支付ROI目标").fill("4.0")
    time.sleep(1)
    page.get_by_text("已有定向包", exact=True).click()

    time.sleep(0.5)
    page.locator("#audience").get_by_placeholder("请选择").click()
    time.sleep(0.5)
    page.get_by_text("精致妈妈徕卡", exact=True).click()
    time.sleep(1)
    page.get_by_role("button", name="添加视频").click()
    time.sleep(1)
    page.get_by_text("来源：").click()
    time.sleep(0.5)
    page.get_by_text("本地上传").click()
    time.sleep(1)

    # focus
    box_dict = page.locator(".create-material-list-rolling-load-wrapper").bounding_box()
    pixel_x = box_dict["x"] + box_dict["width"] / 2
    pixel_y = box_dict["y"] + box_dict["height"] / 2
    page.mouse.move(pixel_x, pixel_y)
    # wheel
    # for _ in range(10):
    #     page.mouse.wheel(0, 1024 * 1024)
    #     time.sleep(0.5)
    #     page.mouse.wheel(0, 1024 * 1024)
    #     time.sleep(0.5)
    # random
    box_count = page.locator(".ovui-image__img").count()
    if not box_count:
        raise
        ipdb.set_trace()

    # for num in random.sample(list(range(0, box_count - 1)), 2):
    for num in random.sample(list(range(0, 22)), 7):
        video_elem = (
            page.locator("#creative-video-drawer").locator(".ovui-image__img").nth(num)
        )
        video_elem.scroll_into_view_if_needed()
        time.sleep(1)
        box_dict = video_elem.bounding_box()
        pixel_x = box_dict["x"] + box_dict["width"] / 2
        pixel_y = box_dict["y"] + box_dict["height"] / 2
        page.mouse.move(pixel_x, pixel_y)
        page.mouse.move(pixel_x, pixel_y)
        time.sleep(1)
        page.mouse.click(pixel_x, pixel_y)
        time.sleep(0.5)
    time.sleep(0.5)
    page.get_by_role("button", name="确定").click()
    time.sleep(0.5)
    time.sleep(1)
    title_els = page.get_by_placeholder("请输入标题或使用系统推荐标题")
    title_count = title_els.count()
    for index in range(title_count):
        title_els.nth(index).fill(kimi_title_list[index])
        time.sleep(0.5)

    page.locator("#creative").get_by_placeholder("请选择").click()
    time.sleep(0.5)
    if uname == "奶粉":
        page.get_by_text("母婴宠物").click()
        time.sleep(0.5)
        page.get_by_text("奶粉", exact=True).click()
        time.sleep(0.5)
        page.get_by_text("儿童奶粉", exact=True).click()
        time.sleep(0.5)
    elif uname == "牛奶粉3段":
        page.get_by_text("母婴宠物").click()
        time.sleep(0.5)
        page.get_by_text("奶粉", exact=True).click()
        time.sleep(0.5)
        page.get_by_text("婴幼儿牛奶粉（3段）", exact=True).click()
        time.sleep(0.5)
    else:
        raise

    page.get_by_placeholder("最多20个标签，每个1-10个字，可用空格分隔").click()
    page.get_by_placeholder("最多20个标签，每个1-10个字，可用空格分隔").fill(kimi_label)
    time.sleep(0.3)
    page.get_by_placeholder("最多20个标签，每个1-10个字，可用空格分隔").press("Enter")
    time.sleep(4)

    # ipdb.set_trace()
    click_sugar(page.get_by_role("button", name="发布计划"))
    time.sleep(2)

@retry(stop=stop_after_attempt(3))
def traffic_uni(page, pid_target, uname):
    """全域推广"""
    page.goto(
        # "https://qianchuan.jinritemai.com/creation/uni-prom-product?aavid=1703862409356302" # 格力
        "https://qianchuan.jinritemai.com/creation/uni-prom-product?aavid=1712324674292736"  # 贝拉米
    )
    # kimi
    user_content = (
        "给我10个贝拉米 {} 的种草标题.每个标题 50个汉字,禁止用广告极限词.不可以出现下面这几个词语：0添加、无添加、首选、肠胃".format(uname)
    )
    res_dict = kimiDB.ask(user_content)
    kimi_title_list = res_dict["data"]

    # ready
    page.get_by_role("button", name="添加商品", exact=True).click()
    time.sleep(0.5)

    # product mask
    if not page.locator(".oc-drawer-close").is_visible():
        time.sleep(0.5)
    page.get_by_placeholder("请输入商品名称/ID搜索").fill(pid_target)
    time.sleep(1)
    page.keyboard.press("Enter")
    time.sleep(2)
    page.locator(
        ".radio > .oc-checkbox > .ovui-checkbox > .ovui-checkbox__wrapper > .ovui-checkbox__inner"
    ).first.click()
    time.sleep(0.5)
    # todo  retry
    if not page.locator(
        ".radio > .oc-checkbox > .ovui-checkbox > .ovui-checkbox__wrapper > .ovui-checkbox__inner"
    ).first.is_checked():
        raise
    page.get_by_role("button", name="确定").click()

    # ROI & else
    page.get_by_role("textbox", name="请输入目标").fill("3")
    time.sleep(0.5)
    page.get_by_placeholder("请输入金额").fill("9999")
    time.sleep(0.5)
    page.locator(".oc-collapse__button > iconpark-icon > svg").click()
    time.sleep(0.5)
    page.locator(".ovui-input__after > .ovui-icon > svg").click()
    time.sleep(0.5)
    page.locator("label").filter(has_text="全选").click()
    time.sleep(0.5)

    # 智能优惠券，选择不启用
    checked_els = page.get_by_text("智能优惠券 启用 不启用")
    if checked_els.locator(".ovui-radio-item--checked").inner_text() == "启用":
        checked_els.get_by_text("不启用").click()
        time.sleep(0.2)

    # add AD. video
    page.get_by_role("button", name="添加视频").click()
    time.sleep(3)
    page.locator(".ovui-select > .ovui-input__wrapper").first.click()
    time.sleep(0.5)
    page.get_by_text("本地上传").click()
    time.sleep(1)
    # focus
    box_dict = page.locator(".create-material-list-rolling-load-wrapper").bounding_box()
    pixel_x = box_dict["x"] + box_dict["width"] / 2
    pixel_y = box_dict["y"] + box_dict["height"] / 2
    page.mouse.move(pixel_x, pixel_y)
    # wheel
    for _ in range(10):
        page.mouse.wheel(0, 1024 * 1024)
        time.sleep(0.5)
        page.mouse.wheel(0, 1024 * 1024)
        time.sleep(0.5)
    # random
    box_count = page.locator(".ovui-image__img").count()
    if not box_count:
        raise
        ipdb.set_trace()
    for num in random.sample(
        list(range(0, box_count - 1)), 6
    ):  # random.sample or random.shuffle
        video_elem = (
            page.locator("#creative-video-drawer").locator(".ovui-image__img").nth(num)
        )
        video_elem.scroll_into_view_if_needed()
        time.sleep(0.5)
        box_dict = video_elem.bounding_box()
        pixel_x = box_dict["x"] + box_dict["width"] / 2
        pixel_y = box_dict["y"] + box_dict["height"] / 2
        page.mouse.move(pixel_x, pixel_y)
        page.mouse.move(pixel_x, pixel_y)
        time.sleep(0.5)
        page.mouse.click(pixel_x, pixel_y)
        time.sleep(0.5)
    time.sleep(0.5)
    page.get_by_role("button", name="确定").click()
    time.sleep(0.5)

    # add AD. picture range 0,5
    # page.get_by_role("button", name="添加商品图片").click()
    # time.sleep(3)

    # box_count = page.locator(".ovui-image__img").count()
    # for num in range(5):
    #     image_elem = (
    #         page.locator("#creative-image-drawer").locator(".ovui-image__img").nth(num)
    #     )
    #     image_elem.click()
    #     time.sleep(0.2)
    # time.sleep(0.5)
    # page.get_by_role("button", name="确定").click()
    # time.sleep(0.5)

    # title
    # page.get_by_role("button", name="添加标题").click()
    # time.sleep(0.5)
    # page.get_by_placeholder("请输入标题或使用系统推荐标题").fill(res_dict["data"])
    # time.sleep(0.5)
    for _ in range(5):
        page.get_by_role("button", name="添加标题").click()
        time.sleep(0.2)
    title_els = page.get_by_placeholder("请输入标题或使用系统推荐标题")
    title_count = title_els.count()
    for index in range(title_count):
        title_els.nth(index).fill(kimi_title_list[index])
        time.sleep(0.5)


    now = pendulum.now("Asia/Shanghai")
    now_str = str(now)[:19]
    base_info = "{} {} {}".format(uname, now_str, pid_target)
    page.locator("#baseInfo").get_by_role("textbox").fill(base_info)
    time.sleep(1)

    # Final Check
    # ipdb.set_trace()
    click_sugar(page.get_by_role("button", name="发布计划"))
    time.sleep(1.5)
    click_sugar(page.get_by_role("button", name="确认发布"))
    time.sleep(3)

    # traffic status check
    page.goto(
        "https://qianchuan.jinritemai.com/creation/uni-prom-product?aavid=1712324674292736"  # 贝拉米
    )
    time.sleep(1)
    # ready
    page.get_by_role("button", name="添加商品", exact=True).click()
    time.sleep(0.5)
    # product mask
    if not page.locator(".oc-drawer-close").is_visible():
        time.sleep(0.5)
    page.get_by_placeholder("请输入商品名称/ID搜索").fill(pid_target)
    time.sleep(1)
    page.keyboard.press("Enter")
    time.sleep(2)
    if page.locator(
        ".card-container > .card-disabled"
    ).count():
        return Nox(0)
    else:
        raise

@retry(stop=stop_after_attempt(3))
def login_shop(page, name=None):
    page.goto("https://fxg.jinritemai.com/login/common")
    time.sleep(10)
    logger.debug("Check login status")
    # 这里需要处理一个账号多个店铺的情况，暂时不用
    if not page.locator(".headerShopName").count():
        logger.debug("select one shop")
        raise
        ipdb.set_trace()

    # header to read shop_name
    if page.locator(".headerShopName").count():
        shop_name = page.locator(".headerShopName").first.inner_text()
        if name in shop_name:
            logger.info("Shop: {}".format(shop_name))
        else:
            logger.error("Shop wrong: {}".format(shop_name))
            logger.error("Not match : {}".format(name))
            raise
    else:
        logger.error("Login Fail")
        raise
    # remove firefox note
    click_sugar(page.get_by_role("dialog").get_by_role("button", name="知道了"))
    time.sleep(0.2)
    # poll_sugar(
    #     page.get_by_role("dialog").get_by_role("button", name="知道了"),
    #     timeout=5,
    # )
    # remove auxo-modal "重要消息"
    # logger.debug("remove auxo modal & wrappers")
    # poll_sugar(
    #     page.locator(".auxo-modal").get_by_label("Close", exact=True),
    #     # page.locator(".auxo-modal").locator(".auxo-modal-close"),
    #     timeout=5,
    # )

    # poll_sugar(
    #     page.locator(".auxo-modal").locator(".auxo-modal-close"),
    #     timeout=5,
    # )
    # while page.locator(".auxo-modal").count():
    #     logger.debug("Try to remove auxo-modal use mathed A")
    #     if not click_sugar(
    #         page.locator(".auxo-modal").get_by_label("Close", exact=True)
    #     ):
    #         click_sugar()
    #     time.sleep(1)
    # time.sleep(2)
    # while page.locator(".auxo-modal").count():
    #     logger.debug("Try to remove auxo-modal use mathed B")
    #     if not click_sugar(
    #         page.locator(".auxo-modal").get_by_label("Close", exact=True)
    #     ):
    #         click_sugar(page.locator(".auxo-modal").locator(".auxo-modal-close"))
    #     time.sleep(3)

    # firefox note 2
    click_sugar(page.locator(".browser-blocker-plugin-modal").get_by_text("知道了"))
    time.sleep(1)
    # remove white wrapper
    # click_sugar(
    #     page.locator(".ecom-guide-normal-content-wrapper").get_by_role(
    #         "button", name="知道了"
    #     )
    # )
    time.sleep(0.5)
    # remove blue wrapper
    click_sugar(page.locator(".auxo-tooltip").get_by_role("button", name="知道了"))
    time.sleep(1)
    # remove white wrapper
    click_sugar(
        page.locator(".ecom-guide-normal-content-wrapper").get_by_role(
            "button", name="知道了"
        )
    )
    time.sleep(0.2)
    # kefu
    click_sugar(page.locator("#DOUXIAOER_WRAPPER").locator(".index_union__1bLD3"))

    if page.locator(".headerShopName").count():
        page.locator(".headerShopName").hover()
        time.sleep(1)
        logger.info(
            "Shop Detail: {}".format(
                page.locator(".headerShopName").first.text_content()
            )
        )
    return Nox(0)


def click_sugar(locator):
    if locator.count():
        logger.debug(locator)
        if locator.count() != 1:
            logger.warning("Count : {}".format(locator.count()))
        locator.first.click()
        return True
    else:
        return False


def poll_sugar(locator, timeout=10, interval=1, retry=False):
    if interval == 0:
        interval == 0.1
    timer = 0
    found_flag = False
    while timer <= timeout:
        logger.debug("Poll watching {} (s)".format(timer))
        if locator.count() > 1:
            logger.debug(locator)
            logger.warning("Elem multi : {}".format(locator.count()))
            locator.first.click()
            if retry == False:
                return True
            else:
                found_flag = True
        elif locator.count() == 1:
            logger.debug(locator)
            logger.info("Element 1 Found")
            locator.first.click()
            if retry == False:
                return True
            else:
                found_flag = True
        else:
            logger.debug(locator)
            logger.warning("Element Not Found")
        timer = timer + interval
        time.sleep(interval)

    return found_flag


def fetch_sugar(locator, target=True, timeout=3, interval=0.2, index=0):
    global BEAN
    if interval == 0:
        interval == 0.1
    timer = 0
    logger.debug(locator)
    while timer <= timeout:
        if target and locator.count():
            BEAN[index] = max(BEAN[index], timer)
            logger.warning(
                "Index {}, Max Seconds {:.4f} Found.".format(index, BEAN[index])
            )
            return True
        elif not target and not locator.count():
            BEAN[index] = max(BEAN[index], timer)
            logger.warning(
                "Index {}, Max Seconds {:.4f} Missing.".format(index, BEAN[index])
            )
            return True

        else:
            time.sleep(interval)
            timer = timer + interval
    return False


def record_id(file_path, pid):
    with open(file_path, "a", encoding="utf-8") as file:
        file.write('"{}",\n'.format(pid))


def boot():
    global Pooh
    with open("config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    Pooh.update(config)
    sqliteDB.rebuild_init(conn)


def get_png_filenames():
    global Pooh
    png_files = []
    folder_path = Path("./data/main")
    for file in folder_path.rglob("*.png"):  # rglob是递归的glob，会遍历所有子目录
        png_files.append(
            folder_path / file.name
        )  # 如果你想要完整路径，可以使用str(file)
    Pooh["main"] = png_files

    png_files = []
    folder43_path = Path("./data/main43")
    for file in folder43_path.rglob("*.png"):  # rglob是递归的glob，会遍历所有子目录
        png_files.append(
            folder43_path / file.name
        )  # 如果你想要完整路径，可以使用str(file)
    Pooh["43"] = png_files


def are_lengths_equal(lst):
    # 检查列表是否为空或第一个元素是否是可迭代的
    if not lst or not hasattr(lst[0], "__len__"):
        return False
    # 使用 all() 函数和列表推导式来验证所有元素的长度是否相同
    return all(len(item) == len(lst[0]) for item in lst)


def load_tmp_count():
    file_path = Path() / 'tmp_hai.json'
    if file_path.exists():
        with open(file_path, 'r') as file:
            # 加载 JSON 数据
            data = json.load(file)
            # 获取 count 字段的值
            count = data.get('count', 0)  # 如果没有 count 字段，返回 0
            print(f"load tmp count is: {count}")
            return count
    return 0

def save_tmp_count(count_value):
    file_path = Path() / 'tmp_hai.json'
    data = {'count': count_value}
    try:
        # 将字典转换为 JSON 格式并写入文件
        with open(file_path, 'w') as file:
            json.dump(data, file)
        print(f"The count has been saved to {file_path}.")
    except Exception as e:
        print(f"An error occurred while saving the count: {e}")

if __name__ == "__main__":
    boot()
    # print(Pooh)
    # raise
    launch()
