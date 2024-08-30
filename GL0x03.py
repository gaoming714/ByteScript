import time
import re
from pathlib import Path
import pendulum
import random

from playwright.sync_api import sync_playwright
import ipdb

import requests

import tomlkit
import kimiDB

from util import logConfig, logger, lumos, Nox

logConfig("logs/GL0x03.log", rotation="10 MB", level="DEBUG", lite=True)


Pooh = {}

BEAN = [
    0,
    0,
    0,
    0,
]

COOKIE = Path() / "cookies" / "GeLi_haiyang.json"
# COOKIE = Path() / "cookies" / "cookie_Bellamy_177.json"


def launch():
    global Pooh
    kimiDB.boot(Pooh.get("MOONSHOT_API_KEY", None))
    Pooh["icons"] = (
        "*☁↑→←↗⇧⌜⌝⌞⌟∩⊂⊃⊕⊗⊞⊠⊡∅∆∇≈≠≤≥≡≪≫≦≧∫∬∞☤◐✚✉¿ℵ℘℻℗℠™℡"
        "*☁↑→←↗⇧⌜⌝⌞⌟∩⊂⊃⊕⊗⊞⊠⊡∅∆∇≈≠≤≥≡≪≫≦≧∫∬∞☤◐✚✉¿ℵ℘℻℗℠™℡"
        "*☁↑→←↗⇧⌜⌝⌞⌟∩⊂⊃⊕⊗⊞⊠⊡∅∆∇≈≠≤≥≡≪≫≦≧∫∬∞☤◐✚✉¿ℵ℘℻℗℠™℡"
        "*☁↑→←↗⇧⌜⌝⌞⌟∩⊂⊃⊕⊗⊞⊠⊡∅∆∇≈≠≤≥≡≪≫≦≧∫∬∞☤◐✚✉¿ℵ℘℻℗℠™℡"
        "*☁↑→←↗⇧⌜⌝⌞⌟∩⊂⊃⊕⊗⊞⊠⊡∅∆∇≈≠≤≥≡≪≫≦≧∫∬∞☤◐✚✉¿ℵ℘℻℗℠™℡"
    )
    Pooh["first_flag"] = True
    # Pooh["main_path"] = "./data/0015"
    # main_path = Path(Pooh["main_path"])
    main_path = Path() / "data" / "0007"

    # Arrange data
    logger.info("Load config & PNG ")
    with open(main_path / "config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    logger.info(config)
    uid = config["uid"]
    uname = config["uname"]
    base_id = config["base_id"]
    limit_id = config["limit_id"]
    figure_config = config["figure"]
    sale_list = config["sale"]

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
        browser = p.firefox.launch(headless=False)
        context = browser.new_context(storage_state=COOKIE)
        page = context.new_page()
        page.set_viewport_size({"width": 1480, "height": 900})
        time.sleep(1)
        if login_shop(page, "格力"):
            logger.success("Login success")
        else:
            logger.error("Login UNsuccess")
            raise

        time.sleep(1)

        ########## Login success

        # test
        # traffic_uni(page, "3653340621122454321", "ACN")  # 全域推广
        # limitsales(page, "7395136078669463849", [{"origin": 7899},{"origin": 6899}])
        # 测试搜索限时限量购返回ID
        # limitsales(page, "7395136078669463849", None,None)
        # 测试批量改价格
        # limitsales(page, "7395136078669463849", [{"origin": 7899,"price":7299},{"origin": 6899, "price": 6399}], pid_target=None)
        # 测试更新单体限时限量购
        # limitsales(page, "7395136078669463849", [{"origin": 7899,"price":7299},{"origin": 6899, "price": 6399}], "3640428409366182930")

        # qianchuan(page, "3604058235763602348", "云锦2代挂机" )
        # fetch_new_id(page, "【夏日健康风】格力↘空调云轩大1匹1.5匹1级能效时尚挂机大风力")
        # rebuild_product(
        #             page, "3679979403040915753", None, None, "no", Pooh["icons"][1]
        #         )
        # ipdb.set_trace()
        # limitsales(page, limit_id,  sale_list, new_id)

        for index in range(0, symbol_count):  # symbol_count  如果这里不能跑了，从哪个开始，把 0 改成对应的值
            figure_dict = figure_list[index]
            if any(not item.exists() for item in figure_dict.values()):
                logger.error("not find pic {}".format(index))
                continue
            logger.success("On Job: {}".format(index))
            ns = rebuild_product(
                page, base_id, figure_dict, uname, Pooh["icons"][index]
            )

            if not ns:
                raise

            time.sleep(5)
            for retry_times in range(15):
                new_id = fetch_new_id(page, ns.payload)
                if new_id:
                    break
                else:
                    logger.debug("New id retry {} times".format(retry_times + 1))
                if retry_times == 14:
                    logger.error("First step fail on {}".format(index))
                    raise
                time.sleep(3)
            record_id(main_path / "record.txt", new_id)
            logger.debug(new_id)
            # limitsales(page, limit_id, sale_list, new_id)  # 限时限量购
            traffic_uni(page, new_id, uname)  # 全域推广
            logger.success("Done {}".format(new_id))
            logger.success("Finish index: ================ {}".format(index))
            time.sleep(3)
        logger.success("Finish all {}.".format(index+1))
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


def fetch_new_id(page, target_title):
    global Pooh
    # goto list
    page.goto("https://fxg.jinritemai.com/ffa/g/list")

    # ready
    time.sleep(0.6)
    if not page.locator(".ecom-g-table-row").count():
        time.sleep(1)

    # select pid
    row_elem = page.locator(".ecom-g-table-row")
    row_count = row_elem.count()
    logger.debug("Search title {}".format(target_title))
    for index in range(row_count):
        pid = row_elem.nth(index).get_attribute("data-row-key")
        title = row_elem.nth(index).locator(".style_productNameNew__3eWnv").inner_text()
        if title == target_title:
            logger.info("Find New ID {}".format(pid))
            return pid
    return


def rebuild_product(page, copyid, figure, uname=None, icon=None):
    page.goto("https://fxg.jinritemai.com/ffa/g/create?copyid={}".format(copyid))
    time.sleep(2)
    full_name_elem = page.get_by_placeholder("请输入15-60个字符（8-30个汉字）")
    short_name_elem = page.get_by_placeholder(
        "建议填写简明准确的标题内容，避免重复表达"
    )

    # kimi full_name
    user_content = (
        "{}\n"
        ".上一句变换顺序,不改变原意，去掉标点符号,中间随机一个位置插入一次{},\n"
        ".{} 是一个固定词组,\n"
        ".输出至多 56 个字符 \n"
        ".输出json格式,key='data'".format(
            full_name_elem.first.input_value(), icon, uname
        )
    )
    res_dict = kimiDB.ask(user_content)
    full_name_str = res_dict["data"].replace(" ", "")
    # kimi short_name
    user_content = (
        "{}\n"
        "变换顺序,不改变原意，不要标点符号,中间随机一个位置插入一次{},\n"
        # "{} 是一个固定词组,\n"
        "输出至多 24 个字符）\n"
        "输出json格式,key='data'".format(
            short_name_elem.first.input_value(), icon, uname
        )
    )
    res_dict = kimiDB.ask(user_content)
    # short_name_str = res_dict["data"]
    short_name_str = short_name_elem.first.input_value() + icon
    # remove 商品信息质量分提示
    if Pooh["first_flag"]:
        poll_sugar(
            page.locator(".ecom-guide-normal-step-button").get_by_role(
                "button", name="知道了"
            ),
            timeout=10,
        )
        Pooh["first_flag"] = False
    time.sleep(1)
    click_sugar(page.get_by_role("tooltip").get_by_role("button", name="知道了"))
    # remove kefu
    click_sugar(page.locator("#DOUXIAOER_WRAPPER").locator(".index_union__1bLD3"))
    time.sleep(0.5)

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

    # change 型号
    page.locator('div[attr-field-id="型号"]').click()
    time.sleep(1)
    page.get_by_text("+新建型号").click()
    time.sleep(1)
    page.get_by_placeholder("请输入自定义属性").fill(uname)
    time.sleep(1)
    page.get_by_role("img", name="确认").click()
    time.sleep(1)
    page.locator("#rc_select_1").fill(uname)
    # ipdb.set_trace()
    # page.keyboard.type(uname)
    time.sleep(1)
    page.keyboard.press("Enter")
    poll_sugar(page.get_by_role("button", name="重新编辑商品信息"), timeout=5)
    time.sleep(0.2)

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

    full_name_final = page.get_by_placeholder(
        "请输入15-60个字符（8-30个汉字）"
    ).first.input_value()
    # check error
    if page.locator(".has-error").count() or page.locator(".sp-tag-error").count():
        logger.debug("modify then press continue")
        ipdb.set_trace()
    # Final check !!!
    # ipdb.set_trace()
    time.sleep(0.5)
    page.get_by_role("button", name="发布商品").click()

    logger.debug("End rebuild_product")
    return Nox(0, full_name_final)


def act_move(page, box_list, from_idx, to_idx):
    page.mouse.move(box_list[from_idx]["x"] + 50, box_list[from_idx]["y"] + 50)
    page.mouse.down()
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.up()


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


def traffic_uni(page, pid_target, pname):
    """全域推广"""
    page.goto(
        "https://qianchuan.jinritemai.com/creation/uni-prom-product?aavid=1703862409356302"
    )
    # kimi
    user_content = (
        "我需要一条格力空调的种草创意标题,\n"
        "至多 100 个字符 \n"
        "至少 80 个字符 \n"
        "输出json格式, key='data'"
    )
    res_dict = kimiDB.ask(user_content)

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
    page.get_by_role("textbox", name="请输入目标").fill("35")
    time.sleep(0.5)
    page.get_by_placeholder("请输入金额").fill("99999")
    time.sleep(0.5)
    page.locator(".oc-collapse__button > iconpark-icon > svg").click()
    time.sleep(0.5)
    page.locator(".ovui-input__after > .ovui-icon > svg").click()
    time.sleep(0.5)
    page.locator("label").filter(has_text="全选").click()
    time.sleep(0.5)

    # add AD. video
    page.get_by_role("button", name="添加视频").click()
    time.sleep(3)
    # for num in random.sample(list(range(0, 12)), 3):
    #     box_dict = page.locator(".ovui-image__img").nth(num).bounding_box()
    #     pixel_x = box_dict["x"] + box_dict["width"] / 2
    #     pixel_y = box_dict["y"] + box_dict["height"] / 2
    #     page.mouse.move(pixel_x, pixel_y)
    #     page.mouse.move(pixel_x, pixel_y)
    #     time.sleep(1)
    #     page.mouse.click(pixel_x, pixel_y)
    #     time.sleep(0.5)
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
        ipdb.set_trace()
    for num in random.sample(list(range(0, box_count - 1)), 2):
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
    page.get_by_role("button", name="添加标题").click()
    time.sleep(0.5)
    page.get_by_placeholder("请输入标题或使用系统推荐标题").fill(res_dict["data"])
    time.sleep(0.5)

    tick = pendulum.now()
    base_info = "{} {}".format(pname, tick.to_iso8601_string()[:-5])
    page.locator("#baseInfo").get_by_role("textbox").fill(base_info)
    time.sleep(1)

    # Final Check
    # ipdb.set_trace()
    click_sugar(page.get_by_role("button", name="发布计划"))
    time.sleep(1.5)
    click_sugar(page.get_by_role("button", name="确认发布"))
    time.sleep(2)


def login_shop(page, name=None):
    page.goto("https://fxg.jinritemai.com/login/common")
    time.sleep(10)
    logger.debug("Check login status")
    # 这里需要处理一个账号多个店铺的情况，暂时不用
    if not page.locator(".headerShopName").count():
        logger.debug("select one shop")
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
    poll_sugar(page.get_by_role("dialog").get_by_role("button", name="知道了"),
        timeout=5,
    )
    # remove auxo-modal "重要消息"
    logger.debug("remove auxo modal & wrappers")
    poll_sugar(
        page.locator(".auxo-modal").get_by_label("Close", exact=True),
        # page.locator(".auxo-modal").locator(".auxo-modal-close"),
        timeout=5,
    )
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

    time.sleep(1)
    # remove white wrapper
    click_sugar(
        page.locator(".ecom-guide-normal-content-wrapper").get_by_role(
            "button", name="知道了"
        )
    )
    time.sleep(0.2)
    # firefox note 2
    click_sugar(page.locator(".browser-blocker-plugin-modal").get_by_text("知道了"))
    time.sleep(1)
    # remove blue wrapper
    click_sugar(page.locator(".auxo-tooltip").get_by_role("button", name="知道了"))
    time.sleep(1)
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
    Pooh = config


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


if __name__ == "__main__":
    boot()
    # print(Pooh)
    # raise
    launch()