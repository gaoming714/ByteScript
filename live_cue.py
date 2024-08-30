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
import sqlite3
import sqliteDB
import kimiDB

from util import logConfig, logger, lumos, Nox

logConfig("logs/live_cue.log", rotation="10 MB", level="DEBUG", lite=True)

conn = sqlite3.connect("db.sqlite3")

live_id = None

Pooh = {}

COOKIE = Path() / "cookies" / "Live_171.json"


def launch():
    global Pooh
    if not COOKIE.exists():
        store_cookie()

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        # browser = p.firefox.launch(headless=True)
        # browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=COOKIE)
        page = context.new_page()
        page.set_viewport_size({"width": 1480, "height": 900})

        liveroom(context, page)


        browser.close()



def store_cookie():
    # current store all cookies
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({"width": 1480, "height": 720})
        page.goto("https://live.douyin.com/")
        # Scan RQ Manual
        logger.info("Please Login~")
        logger.info("Input 'continue' if finish.")

        ipdb.set_trace()
        logger.info("Continue")

        if not COOKIE.exists():
            storage = context.storage_state(path=COOKIE)
            logger.success("Login success. Save to state.json.")
        else:
            logger.warning("Login fail. Use anonymous mode.")
        browser.close()

def liveroom(context, page):
    page.goto("https://live.douyin.com/{}".format(live_id))
    time.sleep(10)
    star_id = None
    now = pendulum.now()
    while True:
        if star_id:
            user_list = sqliteDB.fetch_mq_all(conn, star_id = star_id, table="liveQueue")
        else:
            user_list = sqliteDB.fetch_mq_all(conn, table="liveQueue")
        if star_id == None:
            logger.debug("Launch first user")
            logger.debug("Wait for new user 5s")
            time.sleep(5)
        if user_list == []:
            time.sleep(10)
            logger.debug("No new user")
            # continue
        for user in user_list:
            user_timestamp = pendulum.parse(user["timestamp"], tz="Asia/Shanghai")
            if  user_timestamp > now:
                logger.debug("For {}".format(user["uname"]))
                if user["act"] == "enter":
                    try:
                        send_front_msg(page, user["uname"], act="chat")
                        # send_back_msg(context, user["sec_uid"])
                    except:
                        logger.error("send msg fail")
                        pass
                now = user_timestamp
                star_id = user["id"]

@retry(stop=stop_after_attempt(3))
def send_front_msg(page, uname=None, act=None):
    logger.info("front msg")
    uname_mask = uname[:3] + "**"
    # msg_str = "欢迎 {} 进入直播间 ^_^".format(uname_mark)
    msg_str = "欢迎 {} 进入直播间，4.4元新人特惠价，了解一下贝拉米吧。点关注不错过好物分享。".format(uname_mask)
    page.locator("#chat-textarea").fill(msg_str)
    time.sleep(0.2)
    page.keyboard.press("Enter")
    time.sleep(0.2)
    logger.success("send front done!")

@retry(stop=stop_after_attempt(3))
def send_back_msg(context, sec_uid):
    logger.info("end msg")
    page = context.new_page()
    page.goto("https://www.douyin.com/user/{}".format(sec_uid))
    time.sleep(5)
    user_el = page.locator(".cx3p4vL2")
    if user_el.count():
        user_str = user_el.first.inner_text()
    else:
        page.close()
        return
    logger.info("User Name: {}".format(user_str))
    # follow_el = page.get_by_role("button", name="关注", exact=True)
    # if follow_el.count():
    #     follow_el.click()
    # else:
    #     return
    time.sleep(0.5)
    target_el = page.locator(".popShadowAnimation")
    button_el = page.get_by_role("button", name="私信", exact=True)
    retry_count = 0
    while target_el.count() == 0:
        logger.debug("target_el retry: {}".format(retry_count))
        if retry_count > 20:
            raise
        button_el.click()
        time.sleep(1)
        retry_count = retry_count + 1
        logger.debug("end target_el retry: {}".format(retry_count))
    if target_el.count():
        logger.debug("Found popShadowAnimation")
    else:
        logger.warning("Not found popShadowAnimation")
    if page.locator(".public-DraftStyleDefault-block").count():
        logger.debug("found input space")
        time.sleep(0.5)
        msg_str = ( "关注我，买贝拉米奶粉，现在直播间购买2件，私信店铺，享受哈利波特北京门票。DDDD"
                    )
        page.locator(".public-DraftStyleDefault-block").fill(msg_str)
        # figure
        # page.locator(".file_input_f6852").set_input_files("./data/ad.png")
        # time.sleep(1)
        page.locator(".CoTAoLdJ").count()
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(1)
        # figure
        # page.locator(".file_input_f6852").set_input_files("./data/5.png")
        # page.locator(".CoTAoLdJ").count()
    logger.success("send back done!")
    page.close()


def click_sugar(locator):
    if locator.count():
        logger.debug(locator)
        if locator.count() != 1:
            logger.warning("Count : {}".format(locator.count()))
        locator.first.click()
        return True
    else:
        return False

def poll_sugar(locator, timeout = 3, interval = 1, retry = False):
    if interval == 0:
        interval == 0.1
    count = timeout / interval
    found_flag = False
    while count > 0:
        logger.debug("poll left {}".format(count))
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

def fetch_sugar(locator, target = True, timeout = 3, interval = 0.2, index = 0):
    global BEAN
    if interval == 0:
        interval == 0.1
    timer = 0
    logger.debug(locator)
    while timer <= timeout:
        if target and locator.count():
            BEAN[index] = max(BEAN[index], timer)
            logger.warning("Index {}, Max Seconds {:.4f} Found.".format(index, BEAN[index]))
            return True
        elif not target and not locator.count():
            BEAN[index] = max(BEAN[index], timer)
            logger.warning("Index {}, Max Seconds {:.4f} Missing.".format(index, BEAN[index]))
            return True

        else:
            time.sleep(interval)
            timer = timer + interval
    return False


def boot():
    global live_id
    with open("config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    live_id = config["live_id"]

if __name__ == "__main__":
    boot()
    # get_png_filenames()
    # print(Pooh)
    # raise
    launch()


