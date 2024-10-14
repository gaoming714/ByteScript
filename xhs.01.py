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

COOKIE = Path() / "cookies" / "xhs.01.json"

def store_cookie():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({"width": 1880, "height": 720})
        page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")

        ipdb.set_trace()
        logger.info("login end")

        if not COOKIE.exists():
            storage = context.storage_state(path=COOKIE)
            logger.success("Login success. Save to {}".format(COOKIE))
        else:
            logger.warning("Login fail. Use anonymous mode.")
        browser.close()


def launch():
    global Pooh
    if not COOKIE.exists():
        store_cookie()
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context(storage_state=COOKIE)
        page = context.new_page()
        page.set_viewport_size({"width": 1880, "height": 900})
        page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
        time.sleep(1)

        upload_file(page, 0, Path() / "movie.mp4")
        magic_text(page, "title", "article", ["shenzhen", "rack"])
        pub_clock(page, "2024-10-15 21:10")
        page.get_by_role("button", name="发布")

def upload_file(page, mode, file_path):
    if mode == 0:
        page.get_by_text('上传视频').click()
        page.locator(".upload-wrapper").get_by_role("textbox").set_input_files(file_path)
        while "修改封面" not in page.locator(".operator").nth(0).inner_text():
            time.sleep(2)
    elif mode == 1:
        page.get_by_text('上传图文').click()
        page.locator(".upload-wrapper").get_by_role("textbox").set_input_files(file_path)
        time.sleep(3)

def magic_text(page, title, article, keyword_list):
    page.locator(".titleInput").locator("input").fill("title")
    if page.locator(".titleInput").locator(".c-input_max").count():
        page.locator(".titleInput").locator("input").press("Backspace")
    page.locator("#post-textarea").fill(article)
    # keyword
    for item in keyword_list:
        page.locator("#post-textarea").type("#")
        page.locator("#post-textarea").type(item)
        time.sleep(0.5)
        page.keyboard.press("Tab")
    time.sleep(0.5)

def pub_clock(page, pub_dt):
    if type(pub_dt) != type(""):
        pub_str = str(pub_dt)
    else:
        pub_str = pub_dt
    pub_tuple = pub_str[:10], pub_str[11:16]
    page.locator(".el-radio").get_by_text("定时发送").click()
    time.sleep(0.5)
    page.get_by_placeholder('选择日期和时间').click()
    time.sleep(0.5)
    page.locator(".el-popper").get_by_placeholder('选择日期').fill(pub_tuple[0])
    time.sleep(0.5)
    page.locator(".el-popper").get_by_placeholder('选择时间').fill(pub_tuple[1])
    time.sleep(0.5)
    page.locator(".el-picker-panel__footer").get_by_role("button", name="确定")
    time.sleep(0.5)


def click_sugar(locator):
    if locator.count():
        logger.debug(locator)
        if locator.count() != 1:
            logger.warning("Count : {}".format(locator.count()))
        locator.first.click()
        return True
    else:
        return False


def boot():
    global Pooh
    with open("config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    Pooh = config
    kimiDB.boot(Pooh.get("MOONSHOT_API_KEY", None))



if __name__ == "__main__":
    boot()
    # print(Pooh)
    # raise
    launch()
