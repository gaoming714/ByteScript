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

logConfig("logs/default.log", rotation="10 MB", level="DEBUG", lite=True)


Pooh = {}

BEAN = [
    0,
    0,
    0,
    0,
]

COOKIE = Path() / "cookies" / "GeLi_Tao.json"
# COOKIE = Path() / "cookies" / "cookie_Bellamy_177.json"


def launch():
    global Pooh
    kimiDB.boot(Pooh.get("MOONSHOT_API_KEY", None))
    Pooh["icons"] = "*☁↑→←↗⇧⌜⌝⌞" "⌟∩⊂⊃⊕⊗⊞⊠⊡∅" "∆∇≈≠≤≥≡≪≫≦≧" "∫∬∞☤◐✚✉¿ℵ℘℻" "℗℠™℡"

    if not COOKIE.exists():
        store_cookie()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=COOKIE)
        page = context.new_page()
        page.set_viewport_size({"width": 1880, "height": 900})
        time.sleep(1)
        if login_shop(page, "格力"):
            logger.info("Login success")
        else:
            logger.error("Login UNsuccess")
            raise

        time.sleep(1)

        pname = "云锦II代柜机"
        limit_id = "7395178912315343141"  # "云锦II代柜机"
        sale_list = [{"origin": 14359, "price": 7299}, {"origin": 13059, "price": 6299}]


        ns = limitsales(page, limit_id, sale_list, None)  # 改价 限时限量购

        # ns = limitsales(page, limit_id, None, None)  # 不改价 只寻找ID 限时限量购


        if ns:
            pid_list = ns.payload
        print(pid_list)
        for pid in pid_list:
            qianchuan(page, pid, pname)

        time.sleep(3)

        browser.close()


def store_cookie():
    # current store all cookies
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        # browser = p.chromium.launch(headless=False, executable_path="./chromium-1124/chrome-win/chrome.exe" )
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({"width": 1880, "height": 720})
        # page.set_viewport_size({"width": 1280, "height": 720})
        page.goto("https://fxg.jinritemai.com/login/common")
        # page.wait_for_selector("#svg_icon_avatar")

        logger.info("Please Login~")
        logger.info("Input 'continue' if finish.")

        ipdb.set_trace()

        page.goto("https://business.oceanengine.com/login")
        ipdb.set_trace()

        logger.info("login end")

        if not COOKIE.exists():
            storage = context.storage_state(path=COOKIE)
            logger.success("Login success. Save to {}".format(COOKIE))
        else:
            logger.warning("Login fail. Use anonymous mode.")
        browser.close()


def qianchuan(page, mid, pname):
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
    page.get_by_placeholder("请输入商品名称/ID搜索").fill(mid)
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
    page.get_by_role("textbox", name="请输入目标").fill("45")
    time.sleep(0.5)
    page.get_by_placeholder("请输入金额").fill("99999")
    time.sleep(0.5)
    page.locator(".oc-collapse__button > iconpark-icon > svg").click()
    time.sleep(0.5)
    page.locator(".ovui-input__after > .ovui-icon > svg").click()
    time.sleep(0.5)
    page.locator("label").filter(has_text="全选").click()
    time.sleep(0.5)
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
        page.locator(".ovui-image__img").nth(num).scroll_into_view_if_needed()
        time.sleep(1)
        box_dict = page.locator(".ovui-image__img").nth(num).bounding_box()
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
    # title
    page.get_by_role("button", name="添加标题").click()
    time.sleep(0.5)
    page.get_by_placeholder("请输入标题或使用系统推荐标题").fill(res_dict["data"])
    time.sleep(0.5)

    tick = pendulum.now()
    base_info = "{} {}".format(pname, tick.to_atom_string()[:-6])
    page.locator("#baseInfo").get_by_role("textbox").fill(base_info)
    time.sleep(1)

    # Final Check
    # ipdb.set_trace()
    click_sugar(page.get_by_role("button", name="发布计划"))
    time.sleep(1.5)
    click_sugar(page.get_by_role("button", name="确认发布"))
    time.sleep(2)


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
    time.sleep(3)
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
    ipdb.set_trace()
    # stop!!!!!!!!!!!!!!!!!
    raise
    if not sale_list:
        return Nox(0, pid_list)
    page.get_by_role("button", name="提交").click()
    time.sleep(10)
    click_sugar(page.get_by_role("button", name="仍要创建"))
    logger.debug("finish shot {}".format(pid_target))
    # page.pause()
    time.sleep(2)
    return Nox(0, pid_list)


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


def on_product(page, copyid, pic1=None, pic2=None, pname=None, icon=None):
    page.goto("https://fxg.jinritemai.com/ffa/g/create?copyid={}".format(copyid))
    time.sleep(2)
    full_name_elem = page.get_by_placeholder("请输入15-60个字符（8-30个汉字）")
    short_name_elem = page.get_by_placeholder(
        "建议填写简明准确的标题内容，避免重复表达"
    )

    # kimi full_name
    user_content = (
        "{}\n"
        "变换词组顺序,不改变原意，不要标点符号,中间插入{},不要空格,\n"
        "{} 是一个固定词组,\n"
        "至多 60 个字符 \n"
        "输出json格式,key='data'".format(
            full_name_elem.first.input_value(), icon, pname
        )
    )
    res_dict = kimiDB.ask(user_content)
    full_name_str = res_dict["data"]
    # kimi short_name
    user_content = (
        "{}\n"
        "变换词组顺序,不改变原意，不要标点符号,中间插入{},不要空格,\n"
        # "{} 是一个固定词组,\n"
        "至多 24 个字符）\n"
        "输出json格式,key='data'".format(
            short_name_elem.first.input_value(), icon, pname
        )
    )
    res_dict = kimiDB.ask(user_content)
    # short_name_str = res_dict["data"]
    short_name_str = short_name_elem.first.input_value() + icon
    # remove 商品信息质量分提示
    poll_sugar(
        page.locator(".ecom-guide-normal-step-button").get_by_role(
            "button", name="知道了"
        ),
        timeout=5,
    )
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
    short_name_elem.first.fill(short_name_str)

    # change 型号
    page.locator('div[attr-field-id="型号"]').click()
    time.sleep(1)
    page.get_by_text("+新建型号").click()
    time.sleep(1)
    page.get_by_placeholder("请输入自定义属性").fill(pname)
    time.sleep(1)
    page.get_by_role("img", name="确认").click()
    time.sleep(1)
    page.keyboard.type(pname)
    page.keyboard.press("Enter")
    poll_sugar(page.get_by_role("button", name="重新编辑商品信息"), timeout=5)
    time.sleep(0.5)

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
        time.sleep(0.5)
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
        ).set_input_files(pic1)
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
        ).set_input_files(pic2)
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

    # check error
    if page.locator(".has-error").count():
        ipdb.set_trace()
    # Final check !!!
    # ipdb.set_trace()
    time.sleep(0.5)
    page.get_by_role("button", name="发布商品").click()

    logger.debug("End on_product")
    return Nox(0, full_name_str)


def act_move(page, box_list, from_idx, to_idx):
    page.mouse.move(box_list[from_idx]["x"] + 50, box_list[from_idx]["y"] + 50)
    page.mouse.down()
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.up()


def login_shop(page, name=None):
    page.goto("https://fxg.jinritemai.com/login/common")
    time.sleep(15)
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

    # remove auxo-modal
    logger.debug("remove auxo modal & wrappers")
    while page.locator(".auxo-modal").count():
        logger.debug("Try to remove auxo-modal use mathed A")
        if not click_sugar(
            page.locator(".auxo-modal").get_by_label("Close", exact=True)
        ):
            click_sugar(page.locator(".auxo-modal").locator(".auxo-modal-close"))
        time.sleep(1)
    time.sleep(2)
    while page.locator(".auxo-modal").count():
        logger.debug("Try to remove auxo-modal use mathed B")
        if not click_sugar(
            page.locator(".auxo-modal").get_by_label("Close", exact=True)
        ):
            click_sugar(page.locator(".auxo-modal").locator(".auxo-modal-close"))
        time.sleep(3)

    time.sleep(0.5)
    # remove white wrapper
    click_sugar(
        page.locator(".ecom-guide-normal-content-wrapper").get_by_role(
            "button", name="知道了"
        )
    )
    time.sleep(1)
    # blue
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


def record_id(file_path, mid):
    with open(file_path, "a", encoding="utf-8") as file:
        file.write('"{}",\n'.format(mid))


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


if __name__ == "__main__":
    boot()
    # print(Pooh)
    # raise
    launch()
