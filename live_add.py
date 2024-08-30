import time
import re
from pathlib import Path
import pendulum
import random

from playwright.sync_api import sync_playwright
import ipdb

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

        pop_user(page)

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


def pop_user(page):
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
            user_timestamp = pendulum.parse(user["timestamp"])
            if  user_timestamp > now:
                logger.debug("Enter {}".format(user["uname"]))
                send_to(page, user["sec_uid"])
                now = user_timestamp
                star_id = user["id"]

def send_to(page, secuid):
    page.goto("https://www.douyin.com/user/{}".format(secuid))
    time.sleep(5)
    user_str = page.locator(".j5WZzJdp").first.inner_text()
    logger.info("User Name: {}".format(user_str))
    follow_el = page.get_by_role("button", name="关注", exact=True)
    follow_el.click()
    time.sleep(0.5)
    target_el = page.locator(".popShadowAnimation")
    button_el = page.get_by_role("button", name="私信", exact=True)
    retry_count = 0
    while target_el.count() == 0:
        logger.debug("target_el retry: {}".format(retry_count))
        if retry_count > 20:
            return "Not found popShadowAnimation"
        click_sugar(button_el)
        time.sleep(1)
        retry_count = retry_count + 1
    if target_el.count():
        logger.debug("Found popShadowAnimation")
    else:
        logger.warning("Not found popShadowAnimation")
    if page.locator(".public-DraftStyleDefault-block").count():
        logger.debug("found input space")
        time.sleep(0.5)
        # ipdb.set_trace()
        msg_str = ( "新规有效粉步骤\n"
                    "1.点第一条作品完播\n"
                    "2.点赞/评论\n"
                    "3.关注\n"
                    "4.连续互发私信3天，超过5字，发表情无效。\n"
                    "5.第三天聊天框出现“小火花🔥”互发一张图片，出现紫色🔥火花，就是有效粉了。\n"
                    "我会以同样方式回你\n"
                    "让我们互动起来一起做有效吧！（懒得打字麻烦复制一下转发我就行）\n"
                    )
        page.locator(".public-DraftStyleDefault-block").fill(msg_str)
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(0.5)


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
            user_timestamp = pendulum.parse(user["timestamp"])
            if  user_timestamp > now:
                logger.debug("Enter {}".format(user["uname"]))
                if user["act"] == "enter":
                    send_front_msg(page, user["uname"], act="Enter")
                now = user_timestamp
                star_id = user["id"]


def send_front_msg(page, uname=None, act=None):
    uname_mark = uname[:3] + "**"
    msg_str = "欢迎 {} 进入直播间 ^_^".format(uname_mark)
    page.locator("#chat-textarea").fill(msg_str)
    time.sleep(0.2)
    page.keyboard.press("Enter")
    time.sleep(0.2)


def send_back_msg(context, page, el):
    logger.debug("send_back_msg_func")
    if not click_sugar(el):
        logger.error("name button is down")
        user_page.close()
        return
    time.sleep(2)
    with context.expect_page() as user_page_info:
        if not click_sugar(page.locator("#user_popup").get_by_role("button", name="主页")):
            logger.error("主页 is down")
            user_page.close()
            return
    time.sleep(2)
    user_page = user_page_info.value
    if user_page.get_by_text("是否保存登录信息?", exact=True).count:
        logger.debug("Found 保存")
        time.sleep(6)
    time.sleep(5)
    click_sugar(user_page.get_by_role("button", name="私信", exact=True))
    time.sleep(6)
    user_page.keyboard.type("Hello")
    time.sleep(2)
    user_page.keyboard.press("Enter")
    time.sleep(2)
    user_page.close()




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


