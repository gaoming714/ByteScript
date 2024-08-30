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

from util import (
    logConfig,
    logger,
    lumos,
    Nox,
)

logConfig("logs/default.log", rotation="10 MB", level="DEBUG", lite=True)


Pooh = {}

COOKIE = Path() / "cookies" / "Bellamy_171.json"


BEAN = [0, 0, 0, 0]


def launch():
    global Pooh

    if not COOKIE.exists():
        store_cookie()
        # test for recommend
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False)
            # browser = p.firefox.launch(headless=True)
            # browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=COOKIE)
            page = context.new_page()
            page.set_viewport_size({"width": 1920, "height": 900})
            # login_shop
            if login_shop(page, "Bellamy"):
                logger.info("Login success")
            else:
                logger.error("Login fail")
                raise
            time.sleep(1)
            with context.expect_page() as new_page_info:
                page.locator("#fxg-pc-header").get_by_text("精选联盟").click()
            new_page = new_page_info.value
            new_page.close()
            ns = daren_recommend(page)
            browser.close()

    with sync_playwright() as p:
        # browser = p.firefox.launch(headless=False)
        browser = p.firefox.launch(headless=True)
        # browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=COOKIE)
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 900})
        # login_shop
        if login_shop(page, "Bellamy"):
            logger.info("Login success")
        else:
            logger.error("Login fail")
            raise
        time.sleep(1)
        with context.expect_page() as new_page_info:
            page.locator("#fxg-pc-header").get_by_text("精选联盟").click()
        new_page = new_page_info.value
        # get count - total - left
        level_dash = dashboard(new_page)
        level_list = []
        if level_dash[0]["left"] > 0:
           level_list.append("LV0")
           level_list.append("LV1")
        if level_dash[1]["left"] > 0:
           level_list.append("LV2")
           level_list.append("LV3")
        if level_dash[2]["left"] > 0:
           level_list.append("LV4")
           level_list.append("LV5")
        if level_dash[3]["left"] > 0:
           level_list.append("LV6")
           level_list.append("LV7")
        new_page.close()

        time.sleep(1)
        logger.info(level_list)
        tab_list = ["全部达人", "直播达人", "视频达人"]

        daren_square(page, random.choice(level_list), random.choice(tab_list))

        browser.close()


def dashboard(page):
    page.goto("https://buyin.jinritemai.com/dashboard/author/construct-equity")
    time.sleep(5)
    # remove firefox note
    gear_sugar(
        page.locator(".browser-blocker-plugin-modal").get_by_text("知道了"),
        timeout=5,
    )
    cell_els = page.get_by_role("cell")
    cell_count = cell_els.count()

    my_shop_index = None
    for index in range(cell_count):
        if "我的店铺" in cell_els.nth(index).inner_text():
            my_shop_index = index
    level_0 = cell_els.nth(my_shop_index + 2)
    level_2 = cell_els.nth(my_shop_index + 3)
    level_4 = cell_els.nth(my_shop_index + 4)
    level_6 = cell_els.nth(my_shop_index + 5)

    level_list = []

    for cell_el in [level_0, level_2, level_4, level_6]:
        cell_str = cell_el.inner_text()
        if "/\n" in cell_str:
            cell_count, cell_total = [int(x) for x in cell_str.split("/\n")]
            cell_left = cell_total - cell_count
        else:
            cell_count = 0
            cell_total = 0
            cell_left = 0
        level_list.append({"count": cell_count, "total": cell_total, "left": cell_left})
    logger.debug(level_list)
    for index, item in enumerate(level_list):
        if cell_total == 0:
            continue
        v_c = item["count"]
        v_t = item["total"]
        v_l = item["left"]
        v_p = v_c / v_t * 100
        if v_l == 0:
            logger.success("Level {} & {}  => {} left (Finish {:.2f}%).".format(index*2, index*2+1, v_l, v_p))
        elif v_c >= v_l:
            logger.warning("Level {} & {}  => {} left (Finish {:.2f}%).".format(index*2, index*2+1, v_l, v_p))
        else:
            logger.error("Level {} & {}  => {} left (Finish {:.2f}%).".format(index*2, index*2+1, v_l, v_p))

    return level_list




def store_cookie():
    # current store all cookies
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 900})
        page.goto("https://fxg.jinritemai.com/login/common")
        # Scan RQ Manual
        logger.info("Please Login~")
        logger.warning(
            "手动登录，点击上方的精选联盟，然后等待页面加载出来精选联盟，大约5分钟。然后输入continue"
        )
        logger.info("Input 'continue' if finish.")

        ipdb.set_trace()
        logger.info("Continue")

        if not COOKIE.exists():
            storage = context.storage_state(path=COOKIE)
            logger.success("Login success. Save to state.json.")
        else:
            logger.warning("Login fail. Use anonymous mode.")
        browser.close()


def daren_recommend(page):

    # 导航到页面
    page.goto("https://buyin.jinritemai.com/dashboard/servicehall/daren-recommend")
    time.sleep(10)
    # remove firefox note
    gear_sugar(
        page.locator(".browser-blocker-plugin-modal").get_by_text("知道了"),
        timeout=5,
    )
    point_num = 0
    finish_count = 0

    logger.debug("mouse.wheel")
    for wheel in range(5):
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 1024 * 1024)
        time.sleep(0.2)
    time.sleep(2)
    # check & act
    target_els = page.locator(".auxo-table-row").get_by_role(
        "button", name="邀约带货"
    )
    target_count = target_els.count()

    logger.debug("target_count {}".format(target_count))
    # find first point is enabled, if no found wheel
    while point_num < target_count:
        logger.debug("here point_num {}".format(point_num))
        point_el = target_els.nth(point_num)
        if point_el.is_visible() and point_el.is_enabled():
            logger.debug("find target_els_count {}".format(target_count))
            logger.debug("find point_el_count {}".format(point_num))
            point_el = target_els.nth(point_num)
            logger.debug(point_el)
            point_el.scroll_into_view_if_needed()
            time.sleep(0.2)
            try:
                point_el.click()
            except:
                point_num = point_num + 1
                continue
            time.sleep(1.4)
            click_sugar(
                page.locator(".auxo-drawer-content-wrapper").get_by_role(
                    "button", name="确定发送"
                )
            )
            time.sleep(1.4)
            close_el = (
                page.locator(".auxo-drawer-content-wrapper")
                .locator(".auxo-drawer-header")
                .get_by_label("Close", exact=True)
            )
            if close_el.count():
                gear_sugar(close_el, timeout=2, interval=0.5)
            finish_count = finish_count + 1
            logger.success("Finish count {}".format(finish_count))
            continue
        else:
            point_num = point_num + 1
            logger.debug("Round End {}".format(point_num))
    exit()


def daren_square(page, level=None, tab=None):
    # ipdb.set_trace()
    page.goto("https://buyin.jinritemai.com/dashboard/servicehall/daren-square")
    time.sleep(6)
    # remove firefox note
    gear_sugar(
        page.locator(".browser-blocker-plugin-modal").get_by_text("知道了"),
        timeout=5,
    )
    logger.info("Level: {}, Tab: {}".format(level, tab))
    # remove kefu
    click_sugar(page.locator("#DOUXIAOER_WRAPPER").locator(".index_union__1bLD3"))
    time.sleep(0.5)
    for _ in range(10):
        if (
            page.locator(".message-center-popup")
            .locator(".message-center-popup__close-icon")
            .count()
            == 0
        ):
            break
        click_sugar(
            page.locator(".message-center-popup").locator(
                ".message-center-popup__close-icon"
            )
        )
        time.sleep(0.3)
    time.sleep(0.5)

    # body
    click_sugar(page.get_by_role("button", name="达人等级"))
    time.sleep(1)
    click_sugar(page.get_by_text(level, exact=True))
    time.sleep(2)
    click_sugar(page.get_by_role("tab", name=tab))
    time.sleep(3)
    if tab == "全部达人" :
        click_sugar(page.locator("thead").get_by_text("销售总额"))
    elif tab == "视频达人" :
        click_sugar(page.locator("thead").get_by_text("视频销售总额"))
    elif tab == "直播达人" :
        click_sugar(page.locator("thead").get_by_text("直播销售总额"))
    point_num = 0
    finish_count = 0
    for _ in range(30):
        # end condition
        if page.locator(".sp-infinit-end").get_by_text("没有更多了").count():
            logger.success("Level: {}, Tab: {} 没有更多了".format(level, tab))
            break
        # mouse wheel
        logger.debug("mouse.wheel")
        for wheel in range(5):
            page.mouse.move(500, 500)
            page.mouse.wheel(0, 1024 * 1024)
            time.sleep(0.2)
        time.sleep(2)
        # check & act
        target_els = page.locator(".auxo-table-row").get_by_role(
            "button", name="邀约带货"
        )
        target_count = target_els.count()
        if target_count == 0:
            continue
        logger.debug("target_count {}".format(target_count))
        # find first point is enabled, if no found wheel
        while point_num < target_count:
            logger.debug("here point_num {}".format(point_num))
            point_el = target_els.nth(point_num)
            if point_el.is_visible() and point_el.is_enabled():
                logger.debug("find target_els_count {}".format(target_count))
                logger.debug("find point_el_count {}".format(point_num))
                point_el = target_els.nth(point_num)
                logger.debug(point_el)
                point_el.scroll_into_view_if_needed()
                time.sleep(0.2)
                try:
                    point_el.click()
                except:
                    point_num = point_num + 1
                    continue
                time.sleep(1.4)
                click_sugar(
                    page.locator(".auxo-drawer-content-wrapper").get_by_role(
                        "button", name="确定发送"
                    )
                )
                # make speed show
                time.sleep(2)

                time.sleep(1.4)
                close_el = (
                    page.locator(".auxo-drawer-content-wrapper")
                    .locator(".auxo-drawer-header")
                    .get_by_label("Close", exact=True)
                )
                if close_el.count():
                    gear_sugar(close_el, timeout=2, interval=0.5)
                finish_count = finish_count + 1
                logger.success("Finish count {}".format(finish_count))
                if finish_count > 300:
                    logger.success("Finish count {} exit.".format(finish_count))
                    exit()
                continue
            else:
                point_num = point_num + 1
                logger.debug("Round End {}".format(point_num))
            # make speed show
            # time.sleep(2)


def peer_reference(page):
    page.goto("https://buyin.jinritemai.com/dashboard/servicehall/peer-reference")
    time.sleep(5)

    pass

@retry(stop=stop_after_attempt(3))
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
    gear_sugar(
        page.get_by_role("dialog").get_by_role("button", name="知道了"),
        timeout=5,
    )
    # remove auxo-modal "重要消息"
    logger.debug("remove auxo modal & wrappers")
    gear_sugar(
        page.locator(".auxo-modal").get_by_label("Close", exact=True),
        # page.locator(".auxo-modal").locator(".auxo-modal-close"),
        timeout=5,
    )

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


def gear_sugar(locator, timeout=3, interval=1, retry=False):
    if interval == 0:
        interval == 0.1
    count = timeout / interval
    found_flag = False
    while count > 0:
        logger.debug("gear left {}".format(count))
        if locator.count() > 1:
            logger.debug(locator)
            logger.warning("Count : {}".format(locator.count()))
            locator.first.click()
            if retry == False:
                return True
            else:
                found_flag = True
        elif locator.count() == 1:
            logger.debug(locator)
            logger.warning("Element 1 Found")
            locator.first.click()
            if retry == False:
                return True
            else:
                found_flag = True
        else:
            logger.debug(locator)
            logger.warning("Element Not Found")
        count = count - 1
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


def boot():
    global MAIN_PATH
    global USER
    global MANUAL
    with open("config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())


if __name__ == "__main__":
    # boot()
    # get_png_filenames()
    # print(Pooh)
    # raise
    launch()
