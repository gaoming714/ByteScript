import time
import re
from pathlib import Path
import pendulum
import random

from playwright.sync_api import sync_playwright
import ipdb
from tenacity import retry, stop_after_attempt
import requests

import tomlkit
import kimiDB

from util import (
    logConfig,
    logger,
    lumos,
    check_folder,
    show_local,
    create_hash,
    check_hash,
    check_intact,
)

logConfig("logs/default.log", rotation="10 MB", level="DEBUG", lite=True)


Pooh = {}


COOKIE = Path() / "cookies" / "xiaohongshu_huihui.json"
# COOKIE = Path() / "cookies" / "cookie_Bellamy_177.json"


def launch():
    global Pooh
    kimiDB.boot(Pooh.get("MOONSHOT_API_KEY", None))
    Pooh["icons"] = [
        "*",
        "☁",
        "↑",
        "↓",
        "→",
        "←",
        "↗",
        "↘",
        "↙",
        "⇧",
        "⇩",
        "⌜",
        "⌝",
        "⌞",
        "⌟",
        "∩",
        "",
        "⊂",
        "⊃",
        "⊕",
        "⊗",
        "⊞",
        "⊠",
        "⊡",
        "∅",
        "∆",
        "∇",
        "≈",
        "≠",
        "≤",
        "≥",
        "≡",
        "≪",
        "≫",
        "≦",
        "≧",
        "∫",
        "∬",
        "∞",
        "☤",
        "◐",
        "✚",
        "✉",
        "¿",
        "ℵ",
        "℘",
        "℻",
        "℗",
        "℠",
        "™",
        "℡",
    ]
    print(Pooh)
    if not COOKIE.exists():
        store_cookie()
    alley()


def store_cookie():
    # current store all cookies
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        # browser = p.chromium.launch(headless=False, executable_path="./chromium-1124/chrome-win/chrome.exe" )
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({"width": 1880, "height": 720})
        # page.set_viewport_size({"width": 1280, "height": 720})
        page.goto("https://customer.xiaohongshu.com/login?service=https://ark.xiaohongshu.com/ark/home")
        # page.wait_for_selector("#svg_icon_avatar")

        logger.info("Please Login~")
        logger.info("Input 'continue' if finish.")

        ipdb.set_trace()
        logger.info("login end")

        if not COOKIE.exists():
            storage = context.storage_state(path=COOKIE)
            logger.success("Login success. Save to {}".format(COOKIE))
        else:
            logger.warning("Login fail. Use anonymous mode.")
        browser.close()


def alley():
    global Pooh
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        # browser.set_viewport_size({"width": 2000, "height": 720})
        # browser = p.chromium.launch(headless=False, executable_path="./chromium-1124/chrome-win/chrome.exe" )
        # iphone_13 = playwright.devices['iPhone 13']
        # https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/deviceDescriptorsSource.json
        context = browser.new_context(storage_state=COOKIE)
        page = context.new_page()
        page.set_viewport_size({"width": 1880, "height": 900})
        time.sleep(1)
        # if login_shop(page, "Bellamy") == 0:
        #     logger.info("Login success")
        # else:
        #     logger.error("Login UNsuccess")
        #     raise

        time.sleep(1)

        # test page
        for _ in range(600):
            logger.success("{}".format(_))
            page_upload(page, "66cc671ee6fff40001091111", "title", "desc")
        raise
            # ipdb.set_trace()

        # return
        # Pooh["mid_list"] = ['3695916325777047800', '3619451608343124460', '3695912685876150683', '3533524046341884755', '3690844572944040000', '3681847258573308139', '3689208164659626249', '3695378280258601010', '3695377266805702911', '3695377631710150955', '3695378351142338968', '3619456184706328443', '3567631938917413976', '3678952450733244420', '3689069203081527591', '3519245874033210149', '3686966092963643516', '3619462133319900163', '3679975995076640841']
        # tmp_page(page) # remove attention
        on_shop(page)

        for num in range(0, 60):
            base_folder = Path("./data/0006")
            pic_main = base_folder / "1-1"
            pic_43 = base_folder / "4-3"
            pic1_path = pic_main / "{}.png".format(num)
            pic2_path = pic_43 / "{}.png".format(num)
            base_id = "3679979403040915753"
            pname = "云逸柜机"
            price1 = 6569
            price2 = 5569
            if pic1_path.exists() and pic2_path.exists():
                logger.debug("find pic {}".format(num))
                on_product(
                    page, base_id, pic1_path, pic2_path, pname, Pooh["icons"][num]
                )
            else:
                logger.error("not find pic {}".format(num))
                continue

            time.sleep(20)
            new_id = on_shop(page)
            if new_id == None:
                time.sleep(10)
                new_id = on_shop(page)
            if new_id == None:
                logger.error("first step fail on {}".format(num))
                raise
            record_id(base_folder / "record.txt", new_id)
            logger.debug(new_id)
            # shot_time(page, new_id, price1, price2) # 限时限量购
            # qianchuan(page, new_id, pname) # 全域投流
            logger.success("Done {}".format(new_id))
            time.sleep(1)
        browser.close()


@retry(stop=stop_after_attempt(3))
def page_upload(page, pid=None, title = None, desc=None):
    page.goto("https://ark.xiaohongshu.com/app-note/publish") # product list
    time.sleep(5)
        # kimi
    user_content = (
        "给我1个贝拉米奶粉的种草标题. 20个汉字,禁止用广告极限词."
    )
    res_dict = kimiDB.ask(user_content)
    kimi_title = res_dict["data"]
    user_content = (
        "给我1个贝拉米奶粉的种草文章需要有emoji表情，要很多.小红书风格 300 个汉字,禁止用广告极限词."
    )
    res_dict = kimiDB.ask(user_content)
    kimi_word = res_dict["data"]
    # user_content = (
    #     "给我10个贝拉米奶粉的种草话题. 每个话题5个字以内,禁止用广告极限词."
    # )
    # res_dict = kimiDB.ask(user_content)
    # kimi_topic = res_dict["data"]
    # ipdb.set_trace()
    # ipdb.set_trace()
    # for _ in range(10):
    #     page.locator(".main-item-list-wrap").hover()
    #     page.mouse.wheel(0, 1024)
    #     time.sleep(0.5)
    page.locator(".cell-note-item").locator(".item-title")
    page.locator(".cell-note-item").locator(".item-desc") # 5 商品：id
    page.locator(".d-text.d-link") #link
    p_count = page.locator(".cell-note-item").locator(".item-desc").count()
    box_dict = {}
    # for num in range(p_count):
    #     p_str = page.locator(".cell-note-item").locator(".item-desc").nth(num).inner_text()
    #     p_id = p_str.split('：')[1]
    #     p_name = page.locator(".cell-note-item").locator(".item-title")
    #     p_link = page.locator(".d-text.d-link").nth(num)
    #     box_dict[p_id] = {"name": p_name, "pid": p_id, "link": p_link}
    # print(box_dict)
    page.get_by_placeholder("请输入商品ID/商品名称查询").fill("66cc671ee6fff40001091111")
    time.sleep(1)
    page.keyboard.press("Enter")
    time.sleep(1)
    page.get_by_text("去发笔记", exact=True).click()
    time.sleep(1)
    # ipdb.set_trace()
    # click_sugar(box_dict[pid]["link"])
    # time.sleep(1)
    click_sugar(page.get_by_role("button", name="跳过"))
    time.sleep(1)
    page.get_by_text('手动创作').click()
    time.sleep(1)
    click_sugar(page.get_by_role("button", name="确定"))
    time.sleep(1)

    click_sugar(page.locator(".container").locator(".header").get_by_text("上传图文"))
    # page.locator(".upload-wrapper")
    # ipdb.set_trace()
    # main_path = Path("./data/xiao/")
    # a_list = list(main_path.glob("*"))
    # page.locator(".upload-wrapper").get_by_role("textbox").set_input_files(a_list)
    file_list = ["./data/xiao/1.png","./data/xiao/2.jpg","./data/xiao/3.jpg","./data/xiao/4.jpg","./data/xiao/5.jpg","./data/xiao/6.png","./data/xiao/7.jpg","./data/xiao/10.png"]
    random.shuffle(file_list)
    page.locator(".upload-wrapper").get_by_role("textbox").set_input_files(file_list)

    title_el = page.get_by_placeholder("填写标题，可能会有更多赞哦～").first
    # title_els = page.locator(".c-input_inner")
    title_el.fill(kimi_title)

    desc_el = page.locator("#post-textarea").first
    desc_el.fill(kimi_word)
    # for index in range(8):
    #     desc_el.fill(desc)
    #     page.keyboard.type(kimi_topic[index], delay=100)
    #     time.sleep(1)
    #     page.keyboard.press("Enter")
    time.sleep(5)
    # ipdb.set_trace()
    click_sugar(page.get_by_role("button", name="发布"))
    time.sleep(5)








def qianchuan(page, mid, pname):
    page.goto(
        "https://qianchuan.jinritemai.com/creation/uni-prom-product?aavid=1703862409356302"
    )
    # ipdb.set_trace()
    page.get_by_role("button", name="添加商品", exact=True).click()
    page.get_by_placeholder("请输入商品名称/ID搜索").fill(mid)
    time.sleep(0.5)
    page.get_by_placeholder("请输入商品名称/ID搜索").press("Enter")
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
    time.sleep(0.5)
    page.get_by_role("textbox", name="请输入目标").fill("45")
    time.sleep(0.5)
    page.get_by_placeholder("请输入金额").fill("99999")
    time.sleep(0.5)
    page.locator(".oc-collapse__button > iconpark-icon > svg").click()
    time.sleep(0.5)
    page.locator(".ovui-input__after > .ovui-icon > svg").click()
    time.sleep(0.5)
    page.locator("label").filter(has_text="全选").locator("div").nth(1).click()
    time.sleep(0.5)
    page.get_by_role("button", name="添加视频").click()
    time.sleep(3)
    for num in random.sample(list(range(0, 11)), 3):
        box_dict = page.locator(".ovui-image__img").nth(num).bounding_box()
        pixel_x = box_dict["x"] + box_dict["width"] / 2
        pixel_y = box_dict["y"] + box_dict["height"] / 2
        page.mouse.move(pixel_x, pixel_y)
        time.sleep(0.5)
        page.mouse.click(pixel_x, pixel_y)
        time.sleep(0.5)
    page.get_by_role("button", name="确定").click()
    time.sleep(0.5)
    # title
    page.get_by_role("button", name="添加标题").click()
    time.sleep(0.5)
    page.get_by_placeholder("请输入标题或使用系统推荐标题").click()
    time.sleep(0.5)
    page.get_by_text("从标题库选").click()
    time.sleep(3)
    title_els = page.locator(".ovui-modal__body").locator("label")
    ran_num = random.randint(0, title_els.count())
    page.locator(".ovui-modal__body").locator("label").nth(ran_num).click()
    page.locator(".ovui-modal__body").locator("label").nth(ran_num).click()
    time.sleep(0.5)
    page.get_by_role("button", name="确定").click()
    time.sleep(0.5)
    if len(page.get_by_placeholder("请输入标题或使用系统推荐标题").input_value()) >= 50:
        page.get_by_placeholder("请输入标题或使用系统推荐标题").click()
        title_str = page.get_by_placeholder(
            "请输入标题或使用系统推荐标题"
        ).input_value()[:50]
        title_str = title_str.replace("618", "")
        page.get_by_placeholder("请输入标题或使用系统推荐标题").fill(title_str)

    tick = pendulum.now()
    base_info = pname + tick.strftime("%Y%m%dT%H%M%S")
    page.locator("#baseInfo").get_by_role("textbox").fill(base_info)
    time.sleep(1)

    # finalcheck
    # ipdb.set_trace()
    page.get_by_role("button", name="发布计划").click()
    time.sleep(1)
    button_els = page.get_by_role("button", name="确认发布")
    if button_els.is_visible():
        button_els.click()
    time.sleep(2)


def shot_time(page, mid, price1=None, price2=None):
    # mid = "3695378905142788199"
    # price1 = 4000
    # price2 = 3000

    page.goto(
        "https://fxg.jinritemai.com/ffa/marketing/tools/limitsales/detail?refer=edit&id=7392949199031419188"
    )
    # page.goto('https://fxg.jinritemai.com/ffa/marketing/tools/limitsales/detail?refer=edit&id=7392165657150030116')
    # 7月柜机
    # page.goto('https://fxg.jinritemai.com/ffa/marketing/tools/limitsales/detail?refer=edit&id=7386328354288615730')
    # 7月挂机
    # page.goto('https://fxg.jinritemai.com/ffa/marketing/tools/limitsales/detail?refer=edit&id=7386327774992580916')
    time.sleep(3)
    button = page.query_selector("div.ecom-guide-normal-step-button")
    # 检查元素是否存在并点击
    if button:
        logger.debug("find 知道了")
        button.click()
    else:
        pass
        # print("Element not found")
    print(page.get_by_role("button", name="添加商品").first.bounding_box())
    js_down = "window.scrollTo(0,{})".format(
        page.get_by_role("button", name="添加商品").first.bounding_box()["y"] - 120
    )
    page.evaluate(js_down)

    time.sleep(1)
    page.get_by_role("button", name="添加商品").click()
    page.get_by_role("button", name="添加商品")
    time.sleep(1)
    page.locator("form").get_by_role("textbox", name="请输入商品ID").fill(mid)
    time.sleep(1)
    page.locator("form").get_by_role("button", name="search").click()
    time.sleep(1)
    page.get_by_role("row", name="商品信息 商品原价 商品库存").get_by_label("").check()
    time.sleep(1)
    page.get_by_role("button", name="选择").click()
    time.sleep(1)
    page.get_by_placeholder("请输入商品ID").fill(mid)
    time.sleep(1)
    page.get_by_role("button", name="search").click()
    time.sleep(1)
    page.get_by_title("1", exact=True).first.click()
    time.sleep(1)
    page.get_by_title("5", exact=True).locator("div").click()
    time.sleep(1)
    page.get_by_role("switch").click()
    time.sleep(0.5)
    js_down = "window.scrollTo(0,1000000)"
    page.evaluate(js_down)
    time.sleep(1)
    page.locator("td:nth-child(3) > div:nth-child(2)").locator("input").fill(
        str(price1)
    )
    page.locator("td:nth-child(3) > div:nth-child(3)").locator("input").fill(
        str(price2)
    )
    time.sleep(0.5)

    page.get_by_role("button", name="提交").click()
    time.sleep(10)
    try:
        page.get_by_role("button", name="仍要创建").click()
    except:
        pass
    logger.debug("finish shot {}".format(mid))
    # page.pause()
    time.sleep(2)


def on_shop(page):
    global Pooh
    # goto list
    page.goto("https://fxg.jinritemai.com/ffa/g/list")
    time.sleep(2)

    mid_els = page.query_selector_all("div.style_productId__10lIK")
    mid_list = []

    for el in mid_els:
        raw = el.inner_text()
        if raw.startswith("ID:"):
            cleaned_id = raw[3:].strip()
            mid_list.append(cleaned_id)
    logger.debug(mid_list)
    # page.pause()
    if not "mid_list" in Pooh:
        Pooh["mid_list"] = mid_list
        return
    else:
        diff_set = set(mid_list) - set(Pooh["mid_list"])
        if len(diff_set) == 0:
            logger.debug("no new")
            return None
        elif len(diff_set) == 1:
            new_id = diff_set.pop()
            logger.debug(new_id)
            Pooh["mid_list"].append(new_id)
            return new_id
        else:
            logger.debug(diff_set)
            raise


def tmp_page(page):
    time.sleep(10)
    try:
        if page.get_by_text("重要消息"):
            page.get_by_label("Close", exact=True).click()
        time.sleep(5)
        if page.locator("#DOUXIAOER_WRAPPER"):
            page.get_by_role("button", name="知道了").click()
    except:
        pass


def on_product(
    page, copyid, pic1="./input.png", pic2="./input.png", pname=None, icon=None
):
    page.goto("https://fxg.jinritemai.com/ffa/g/create?copyid={}".format(copyid))
    time.sleep(1)
    # remove 商品信息质量分提示
    for check_num in range(25):
        if click_sugar(
            page.locator(".ecom-guide-normal-step-button").get_by_role(
                "button", name="知道了"
            )
        ):
            logger.debug("商品信息质量分提示 Times: {} (s)".format(check_num))
            break
        time.sleep(1)
    # remove 知道了
    while page.get_by_role("tooltip").get_by_role("button", name="知道了").count():
        logger.debug("Try to remove tooltip use mathed A")
        click_sugar(page.get_by_role("tooltip").get_by_role("button", name="知道了"))
        time.sleep(1)
    # remove kefu
    # click_sugar(page.locator("#DOUXIAOER_WRAPPER").locator(".index_union__1bLD3"))

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
    # 

    full_name_els = page.get_by_placeholder("请输入15-60个字符（8-30个汉字）")
    if full_name_els.count():
        full_name_str = full_name_els.first.input_value()
        system_content = (
            "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你可以准确的输出json格式，"
            "尤其是处理双引号的时候用的是英文的双引号"
        )
        template_content = (
            "，请不改变原意情况下将这一句只变换顺序，不要加标点符号，字数控制在60以内，"
            "并在其中加入一个特殊符号{}。"
            "输出json格式，key='data'".format(icon)
        )
        user_content = "{}{}".format(full_name_str, template_content)
        res_dict = kimiDB.ask(user_content, system_content)
        if len(res_dict["data"]) <= 60:
            full_name_els.first.fill(res_dict["data"])
        else:
            full_name_els.first.fill(res_dict["data"][:60])

    short_name_els = page.get_by_placeholder("建议填写简明准确的标题内容，避免重复表达")
    if short_name_els.count():
        short_name_str = short_name_els.first.input_value()
        system_content = (
            "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你可以准确的输出json格式，"
            "尤其是处理双引号的时候用的是英文的双引号"
        )
        template_content = (
            "，请不改变原意情况下将这一句只变换顺序，不要加标点符号，字数控制在24以内，"
            "并在其中加入一个特殊符号{}。"
            "输出json格式，key='data'".format(icon)
        )
        user_content = "{}{}".format(short_name_str, template_content)
        res_dict = kimiDB.ask(user_content, system_content)
        if len(res_dict["data"]) <= 24:
            short_name_els.first.fill(res_dict["data"])
        else:
            short_name_els.first.fill(res_dict["data"][:24])

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
    time.sleep(5)
    if page.get_by_role("button", name="重新编辑商品信息").count():
        page.get_by_role("button", name="重新编辑商品信息").first.click()
    time.sleep(0.5)

    # figure
    if page.locator(".ecom-g-tabs").get_by_text("图文信息").count():
        page.locator(".ecom-g-tabs").get_by_text("图文信息").first.click()
        time.sleep(1)
    # 1:1
    image_els = page.locator(".styles_mainImg__Gl6ii").locator("ul").locator("img")
    image_count = image_els.count()
    blank_els = (
        page.locator(".styles_mainImg__Gl6ii")
        .locator("ul")
        .locator(".upload_button__17N5e")
    )
    box_list = []  # image box position
    for num in range(image_count):
        if image_els.nth(num).is_visible():
            box_list.append(image_els.nth(num).bounding_box())

    for num in range(5 - image_count):
        if blank_els.nth(num).is_visible():
            box_list.append(blank_els.nth(num).bounding_box())
    logger.debug(box_list)
    # delete
    image_els.nth(0).hover()
    page.mouse.click(box_list[0]["x"] + 76, box_list[0]["y"] + 90)
    time.sleep(0.5)
    if (
        page.locator(".styles_mainImg__Gl6ii").locator("ul").locator("img").count()
        != image_count - 1
    ):
        logger.error("image not count correct")
    blank_els = (
        page.locator(".styles_mainImg__Gl6ii")
        .locator("ul")
        .locator(".upload_button__17N5e")
    )
    blank_els.first.hover()
    page.get_by_role("tooltip", name="本地上传 图库选择 智能做图").locator(
        "label"
    ).set_input_files(pic1)
    time.sleep(5)
    if (
        page.locator(".styles_mainImg__Gl6ii").locator("ul").locator("img").count()
        != image_count
    ):
        logger.error("image not count correct after upload")
    # move
    # act_move(page, box_list, image_count-1, 0)
    page.mouse.move(
        box_list[image_count - 1]["x"] + 50, box_list[image_count - 1]["y"] + 50
    )
    page.mouse.down()
    page.mouse.move(box_list[0]["x"] + 50, box_list[0]["y"] + 50)
    page.mouse.move(box_list[0]["x"] + 50, box_list[0]["y"] + 50)
    page.mouse.move(box_list[0]["x"] + 50, box_list[0]["y"] + 50)
    page.mouse.up()

    # 3:4
    if page.get_by_role("button", name="图文信息").is_visible():
        page.get_by_role("button", name="图文信息").click()

    image_els = page.locator(".styles_mainImg__3Kags").locator("ul").locator("img")
    image_count = image_els.count()
    blank_els = (
        page.locator(".styles_mainImg__3Kags")
        .locator("ul")
        .locator(".upload_button__17N5e")
    )
    box_list = []  # image box position
    for num in range(image_count):
        if image_els.nth(num).is_visible():
            box_list.append(image_els.nth(num).bounding_box())

    for num in range(5 - image_count):
        if blank_els.nth(num).is_visible():
            box_list.append(blank_els.nth(num).bounding_box())
    logger.debug(box_list)
    # delete
    image_els.nth(0).hover()
    page.mouse.move(box_list[0]["x"] + 76, box_list[0]["y"] + 118)
    page.mouse.move(box_list[0]["x"] + 76, box_list[0]["y"] + 118)
    page.mouse.click(box_list[0]["x"] + 76, box_list[0]["y"] + 118)
    if (
        page.locator(".styles_mainImg__3Kags").locator("ul").locator("img").count()
        != image_count - 1
    ):
        logger.error("image not count correct")
    blank_els = (
        page.locator(".styles_mainImg__3Kags")
        .locator("ul")
        .locator(".upload_button__17N5e")
    )
    blank_els.first.hover()
    page.get_by_role("tooltip", name="本地上传 图库选择 智能做图").locator(
        "label"
    ).set_input_files(pic2)
    time.sleep(5)
    if (
        page.locator(".styles_mainImg__3Kags").locator("ul").locator("img").count()
        != image_count
    ):
        logger.error("image not count correct after upload")
    # move
    # act_move(page, box_list, image_count-1, 0)
    page.mouse.move(
        box_list[image_count - 1]["x"] + 50, box_list[image_count - 1]["y"] + 50
    )
    page.mouse.down()
    page.mouse.move(box_list[0]["x"] + 50, box_list[0]["y"] + 50)
    page.mouse.move(box_list[0]["x"] + 50, box_list[0]["y"] + 50)
    page.mouse.move(box_list[0]["x"] + 50, box_list[0]["y"] + 50)
    page.mouse.up()

    # Final check !!!
    # page.pause()
    time.sleep(0.5)
    page.get_by_role("button", name="发布商品").click()

    logger.success("create new mid, current no mid")


def act_move(page, box_list, from_idx, to_idx):
    page.mouse.move(box_list[from_idx]["x"] + 50, box_list[from_idx]["y"] + 50)
    page.mouse.down()
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.move(box_list[to_idx]["x"] + 50, box_list[to_idx]["y"] + 50)
    page.mouse.up()


def login_shop(page, name=None):
    page.goto("https://customer.xiaohongshu.com/login?service=https://ark.xiaohongshu.com/ark/home")
    time.sleep(5)
    logger.debug("Check login status")
    if not page.locator(".store-name").count():
        logger.debug("select one shop")
        ipdb.set_trace()

    # header to read shop_name
    if page.locator(".store-name").count():
        shop_name = page.locator(".store-name").first.inner_text()
        if name in shop_name:
            logger.info("Shop: {}".format(shop_name))
        else:
            logger.error("Shop wrong: {}".format(shop_name))
            logger.error("Not match : {}".format(name))
            raise
    else:
        logger.error("Login Fail")
        raise
    

    click_sugar(page.locator(".d-modal").locator(".d-modal-close"))



    # # remove auxo-modal
    # logger.debug("remove auxo modal & wrappers")
    # while page.locator(".auxo-modal").count():
    #     logger.debug("Try to remove auxo-modal use mathed A")
    #     if not click_sugar(
    #         page.locator(".auxo-modal").get_by_label("Close", exact=True)
    #     ):
    #         click_sugar(page.locator(".auxo-modal").locator(".auxo-modal-close"))
    #     time.sleep(1)
    # time.sleep(2)
    # while page.locator(".auxo-modal").count():
    #     logger.debug("Try to remove auxo-modal use mathed B")
    #     if not click_sugar(
    #         page.locator(".auxo-modal").get_by_label("Close", exact=True)
    #     ):
    #         click_sugar(page.locator(".auxo-modal").locator(".auxo-modal-close"))
    #     time.sleep(3)

    # time.sleep(0.5)
    # # remove white wrapper
    # click_sugar(
    #     page.locator(".ecom-guide-normal-content-wrapper").get_by_role(
    #         "button", name="知道了"
    #     )
    # )
    # time.sleep(1)
    # # blue
    # click_sugar(page.locator(".auxo-tooltip").get_by_role("button", name="知道了"))
    # time.sleep(1)
    # # kefu
    # click_sugar(page.locator("#DOUXIAOER_WRAPPER").locator(".index_union__1bLD3"))

    # if page.locator(".headerShopName").count():
    #     page.locator(".headerShopName").hover()
    #     time.sleep(1)
    #     logger.info(
    #         "Shop Detail: {}".format(
    #             page.locator(".headerShopName").first.text_content()
    #         )
    #     )
    return 0


def click_sugar(locator):
    if locator.count():
        logger.debug(locator)
        if locator.count() != 1:
            logger.warning("Count : {}".format(locator.count()))
        locator.first.click()
        return True
    else:
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
