import kimiDB
import tomlkit


def launch():
    system_content = "你是 Kimi，由 Moonshot AI 提供的人工智能助手，请输出json格式，key='data'"
    user_content = "请给我30条关于格力空调的种草标题，要求字数在50-58汉字，"
    res_dict = kimiDB.ask(user_content)
    print(res_dict)
    pass


if __name__ == "__main__":
    with open("config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    kimiDB.boot(config["MOONSHOT_API_KEY"])
    launch()