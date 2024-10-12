#!/usr/bin/env python3
"""
Name: zh-CN-XiaoxiaoNeural
Gender: Female

Name: zh-CN-XiaoyiNeural
Gender: Female

Name: zh-CN-YunjianNeural
Gender: Male

Name: zh-CN-YunxiNeural
Gender: Male

Name: zh-CN-YunxiaNeural
Gender: Male

Name: zh-CN-YunyangNeural
Gender: Male

Name: zh-CN-liaoning-XiaobeiNeural
Gender: Female

Name: zh-CN-shaanxi-XiaoniNeural
Gender: Female

Name: zh-HK-HiuGaaiNeural
Gender: Female

Name: zh-HK-HiuMaanNeural
Gender: Female

Name: zh-HK-WanLungNeural
Gender: Male

Name: zh-TW-HsiaoChenNeural
Gender: Female

Name: zh-TW-HsiaoYuNeural
Gender: Female

Name: zh-TW-YunJheNeural
Gender: Male

"""

"""
Basic audio streaming example for sync interface

"""

import edge_tts

TEXT = "我们不难发现，做一张完美的照片级作品，就是要添加很多【瑕疵】在场景中，Blitter的作品引起我们对于【完美】与【真实】的重新思考。加上UE5今年将会发布完整版，离我们体验超写实的VR日子，也许不远了。 作者：CG模型网 https://www.bilibili.com/read/cv15389517/ 出处：bilibili"
VOICE = "zh-CN-XiaoyiNeural"
OUTPUT_FILE = "test.mp3"


def main() -> None:
    """Main function to process audio and metadata synchronously."""
    communicate = edge_tts.Communicate(TEXT, VOICE)
    with open(OUTPUT_FILE, "wb") as file:
        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                print(f"WordBoundary: {chunk}")


if __name__ == "__main__":
    main()

