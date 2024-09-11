import time
import re
from pathlib import Path
import pendulum

from playwright.sync_api import sync_playwright

import cv2
import numpy as np
from PIL import Image

import tomlkit
import os
import shutil

from util import (
    logConfig,
    logger,
    lumos,
)

logConfig("logs/default.log", rotation="10 MB", level="DEBUG", lite=True)

DUCK = {}




def organize_images(source_folder, target_folder_prefix, max_files_per_folder=200):
    """
    将源文件夹中的图片按指定数量分到多个目标文件夹中。

    Args:
        source_folder: 源文件夹路径。
        target_folder_prefix: 目标文件夹前缀。
        max_files_per_folder: 每个目标文件夹最多包含的图片数量。
    """

    source_path = os.path.join(os.getcwd(), source_folder)
    file_list = [f for f in os.listdir(source_path) if f.endswith('.png')]
    file_list.sort()  # 按文件名排序

    if not os.path.exists(source_path):
        print(f"源文件夹 {source_path} 不存在。")
        return

    count = 0
    current_folder_index = 1
    for file in file_list:
        source_file = os.path.join(source_path, file)
        target_folder = os.path.join(source_path, f"{target_folder_prefix}{current_folder_index}")
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        target_file = os.path.join(target_folder, file)
        shutil.copy2(source_file, target_file)
        count += 1

        if count % max_files_per_folder == 0:
            current_folder_index += 1




def boot():
    global DUCK
    with open("config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    DUCK["layers"] = config.get("layers", None)
    DUCK["main_path"] = config.get("main_path", None)


if __name__ == "__main__":

    # 示例用法：
    source_folder = Path()/"convert"/"3-4"  # 替换为你的源文件夹名
    target_folder_prefix = "batch_"
    max_files_per_folder = 400
    organize_images(source_folder, target_folder_prefix, max_files_per_folder)
##   现在的问题是上下层还很奇怪，到时是0在上还是0在下呢


