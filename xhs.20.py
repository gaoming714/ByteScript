import time
import pendulum
import hashlib

import uiautomator2 as u2
import tomlkit
import kimiDB
from tqdm.rich import trange, tqdm

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

d = u2.connect()

print(d.info)
add_list = []


def launch():
    add_new_user()
    alert_funs()


def add_new_user():
    """
    在全成员列表中，寻找没关注的人。
    """
    count = 0
    while True:
        for index in range(len(d.xpath('//android.widget.RelativeLayout').all())):
            user_elem = d.xpath('//android.widget.RelativeLayout[{}]'.format(index))
            if not user_elem.exists:
                # logger.debug("skip index {}".format(index))
                continue
            nickname_elem = user_elem.child('/androidx.appcompat.widget.LinearLayoutCompat[1]/android.widget.TextView[1]')
            if nickname_elem.exists:
                nickname_str = nickname_elem.text
                if nickname_str in add_list:
                    continue
                else:
                    add_list.append(nickname_str)
            else:
                continue
            label_elem = user_elem.child('androidx.appcompat.widget.LinearLayoutCompat[1]/androidx.appcompat.widget.LinearLayoutCompat[1]/android.widget.TextView[1]')
            if label_elem.exists:
                label_str = label_elem.text
            else:
                label_str = ""
            if label_str == "" or label_str == "你的粉丝":
                logger.debug("Try follow: {}".format(nickname_str))
                user_elem.click()
                follow_this()
                count = count + 1
            else:
                logger.debug("skip: {}".format(nickname_str))
        logger.info("Count: {}".format(count))
        logger.debug("scroll")
        d(scrollable=True).scroll()


def alert_funs():
    scroll_total = check_total()
    scroll_count = 0
    new_count = 0
    pbar = tqdm(total=scroll_total)
    while scroll_count < scroll_total:
        input_elem = d.xpath('//android.widget.EditText[@text="发消息…"]')
        # input_elem = d.xpath("//android.widget.FrameLayout").all()[-1]
        input_elem.click()
        d.send_keys("@")
        time.sleep(1)

        for _ in range(scroll_count):
            d(scrollable=True).scroll()
            # time.sleep(0.5)

        finish_elem = d(textMatches="完成 \\(\\d+\\)")
        while not (finish_elem.exists and "20" in finish_elem.get_text()):
            if find_end():
                break
            for index in range(len(d.xpath('//android.widget.RelativeLayout').all())):
                user_elem = d.xpath('//android.widget.RelativeLayout[{}]'.format(index))
                if not user_elem.exists:
                    continue
                nickname_elem = user_elem.child('/androidx.appcompat.widget.LinearLayoutCompat[1]/android.widget.TextView[1]')
                if nickname_elem.exists:
                    nickname_str = nickname_elem.text
                else:
                    continue
                label_elem = user_elem.child('/androidx.appcompat.widget.LinearLayoutCompat[1]/android.widget.LinearLayout[1]/android.widget.TextView[1]')
                if label_elem.exists:
                    label_str = label_elem.text
                else:
                    continue
                if label_str == "你关注了TA" and nickname_str not in add_list:
                    add_list.append(nickname_str)
                    new_count = new_count + 1
                    user_elem.click()
                if finish_elem.exists and "20" in finish_elem.get_text():
                    print("find 20")
                    break
            scroll_count = scroll_count + 1
            pbar.update(1)
            d(scrollable=True).scroll()
            # time.sleep(0.5)
        logger.debug("click finish new count: {}".format(new_count))
        finish_elem.click()


        time.sleep(1)
        now = pendulum.now("Asia/Shanghai")
        now_str = now.to_iso8601_string()
        now_hash = hashlib.sha1()
        now_hash.update(now_str.encode('utf-8'))

        d.send_keys(" 👋 已关注，感谢回关 {}".format(now_hash.hexdigest()[:5]))
        time.sleep(1)
        d(className="android.widget.RelativeLayout").child(text="发送").click()

    pbar.close()

def follow_this():
    button_elem = d.xpath('//android.widget.LinearLayout/android.widget.Button')
    while not button_elem.exists:
        time.sleep(1)
    if button_elem.exists:
        nickname_elem = d.xpath('//*[@resource-id="com.xingin.xhs:id/h4n"]')
    # logger.debug("on home: {}".format(nickname_elem.text))
    if button_elem.text in ["关注","回关"]:
        # logger.success("find it")
        logger.debug("5")

        button_elem.click()
        time.sleep(0.3)
    d.press("back")
    time.sleep(0.2)
    while button_elem.exists:
        d.press("back")
        time.sleep(1)


def find_end():
    end_elem = d.xpath('//android.widget.TextView[@text="- THE END -"]')
    return end_elem.exists

def check_total():
    check_scroll_count = 0
    input_elem = d.xpath('//android.widget.EditText[@text="发消息…"]')
    input_elem.click()
    d.send_keys("@")
    time.sleep(1)

    while not find_end():
        d(scrollable=True).scroll()
        check_scroll_count = check_scroll_count + 1
    d.press("back")
    time.sleep(0.3)
    d.press("del")
    logger.info("Scroll total: {}".format(check_scroll_count))
    return check_scroll_count



def boot():
    global Pooh
    with open("config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    Pooh = config
    kimiDB.boot(Pooh.get("MOONSHOT_API_KEY", None))



if __name__ == "__main__":
    boot()
    launch()
