import re
import json
import tomlkit

from openai import OpenAI

Pooh = {}


def ask(user_content = None, system_content = None, temp = 0.618):
    if not system_content:
        system_content = (
        "你是 Kimi。由 Moonshot AI 提供的人工智能助手，你更擅长种草文案的撰写，你不可以写广告极限词，不可以写任何功效有关的文案。"
        "你不使用中文符号，如果需要使用符号都是用英文符号,请输出json格式，key='data'"
        "你可以正确处理汉字和英文的长度，一个汉字算两个字符，其他算一个字符"
        "不可以出现下面这几个词语：0添加，无添加，首选，肠胃"
    )
    client = OpenAI(
        api_key = Pooh["MOONSHOT_API_KEY"],
        base_url = "https://api.moonshot.cn/v1",
    )
    # print(system_content)
    print(user_content)
    completion = client.chat.completions.create(
        model = "moonshot-v1-8k",
        messages = [
            {"role": "system", "content": system_content },
            {"role": "user", "content": user_content }
        ],
        # temperature = 0.3,
        temperature = temp, # 0.618
        # temperature = 0.7,
        response_format={"type": "json_object"},
    )

    content = completion.choices[0].message.content
    if "data" in content:
        print(content)
        return json.loads(content)
    else:
        raise
    # drop pause
    # print(content)
    # payload_dict = kimi_parse(content)
    # if "data" in payload_dict:
    #     return payload_dict
    # else:
    #     print("Output error")
    #     print(payload_dict.keys())
    #     return

def fetch(user_content = None, system_content = None, temp = 0.618):
    if not system_content:
        system_content = (
        "你是 Kimi。不可以写任何功效有关的文案。"
        # "你正在没得事贝拉米奶粉和贝拉米米粉，没有其他品牌，没有其他品类，直播带货中"
        # "你的回复大约在100个字以内，不要太长，推荐用户买贝拉米的奶粉或者贝拉米的米粉。"
        "你擅长推荐一些家庭使用的小商品，希望用户购买，经济实惠。优惠力度大。"
        "你知道我每次提问提出的客户名字，可以针对不同的客户名字进行不同的上下文记录"
        "你不使用中文符号，如果需要使用符号都是用英文符号,请输出json格式，key='data'"
        "你可以正确处理汉字和英文的长度，一个汉字算两个字符，其他算一个字符"
    )
    client = OpenAI(
        api_key = Pooh["MOONSHOT_API_KEY"],
        base_url = "https://api.moonshot.cn/v1",
    )
    # print(system_content)
    # print(user_content)
    completion = client.chat.completions.create(
        model = "moonshot-v1-8k",
        messages = [
            {"role": "system", "content": system_content },
            {"role": "user", "content": user_content }
        ],
        # temperature = 0.3,
        temperature = temp, # 0.618
        # temperature = 0.7,
        response_format={"type": "json_object"},
    )

    content = completion.choices[0].message.content
    if "data" in content:
        print(json.loads(content)["data"])
        return json.loads(content)
    else:
        raise

def launch():
    client = OpenAI(
        api_key = Pooh["MOONSHOT_API_KEY"],
        base_url = "https://api.moonshot.cn/v1",
    )

    completion = client.chat.completions.create(
        model = "moonshot-v1-8k",
        messages = [
            {"role": "system", "content": "你是 Kimi，是一个擅长写母婴类产品种草文案的母亲，你会为用户提供安全，有帮助，准确的回答。"},
            {"role": "user", "content": "请给我30条关于格力空调的种草标题，要求字数在50-58汉字，请输出标准的json格式，key='data'"}
        ],
        # temperature = 0.3,
        temperature = 0.618,
        # temperature = 0.7,
    )

    content = completion.choices[0].message.content
    print(content)
    payload_dict = kimi_parse(content)
    if "datax" in payload_dict:
        return payload_dict
    else:
        print("Output error")
        print(payload_dict.keys())
        return


def kimi_parse(kimi_text):
    # 定义正则表达式模式以匹配 JSON 字符串
    json_pattern = r'```json\s*(.*?)```'
    # 使用正则表达式搜索文本中的 JSON 字符串
    json_match = re.search(json_pattern, kimi_text, re.DOTALL)

    if json_match:
        # 提取并清理 JSON 字符串
        json_str = json_match.group(1).strip()
        try:
            # 尝试将字符串解析为 JSON 对象
            content_dict = json.loads(json_str)
            print("JSON 数据解析成功：")
            print(content_dict)
            return content_dict
        except json.JSONDecodeError as e:
            # 如果解析失败，打印错误信息
            print(f"JSON 解析失败：{e}")
            return
    else:
        try:
            # 尝试将字符串解析为 JSON 对象
            content_dict = json.loads(kimi_text)
            print("JSON 数据解析成功：")
            print(content_dict)
            return content_dict
        except json.JSONDecodeError as e:
            # 如果解析失败，打印错误信息
            print(f"JSON 解析失败：{e}")
            return

def boot(api_key = None):
    global Pooh
    if not api_key:
        print("MOONSHOT_API_KEY is essential!!")
    Pooh["MOONSHOT_API_KEY"] = api_key


if __name__ == "__main__":
    boot()
    launch()
