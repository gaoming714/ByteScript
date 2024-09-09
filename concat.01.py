import time
import re
from pathlib import Path
import pendulum

from playwright.sync_api import sync_playwright

import cv2
import numpy as np
from PIL import Image

import tomlkit

from util import (
    logConfig,
    logger,
    lumos,
)

logConfig("logs/default.log", rotation="10 MB", level="DEBUG", lite=True)

DUCK = {}


def launch():
    with open("convert/config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    layer_mixin = []
    pid = "32"
    main_path = Path('./convert/input')
    output_path = Path()/config["output"] #Path('./convert/1-1')
    # 检查路径是否存在以及是否为文件夹
    if output_path.exists():
        if output_path.is_dir():
            print(f"文件夹 '{output_path}' 已存在。")
        else:
            # 路径存在，但不是文件夹
            print(f"存在同名的文件 '{output_path}'，而不是文件夹。")
    else:
        # 路径不存在，创建文件夹
        try:
            output_path.mkdir()  # 只创建当前文件夹，不创建父文件夹
            print(f"文件夹 '{output_path}' 已创建。")
        except OSError as error:
            print(f"创建文件夹 '{output_path}' 时出错: {error}")
    logger.debug(main_path)
    # get from toml & files
    for layer in config["layer"]:
        symbol = layer["symbol"]
        pinx = layer['x']
        piny = layer['y']
        if "*" in symbol:
            comfyui_list = main_path.glob("ComfyUI*.png")
            comfyui_layer = [{"symbol": file, 'x': pinx, 'y': piny} for file in comfyui_list]
            layer_mixin.append(comfyui_layer)
        else:
            ui_layer = {"symbol": main_path / symbol, 'x': pinx, 'y': piny}
            layer_mixin.append(ui_layer)
    logger.debug(layer_mixin)
    layer_matrix = flatten_layer(layer_mixin)
    logger.debug(layer_matrix)

    for layer_list in zip(*layer_matrix):
        result_img = None
        for layer in layer_list:
            layer_img = Image.open(layer['symbol'])
            pinx = layer['x']
            piny = layer['y']
            result_img = blend_images_offset(result_img, layer_img, pinx, piny)
        # result_img.show()
        now = pendulum.now("Asia/Shanghai")
        pid = config['pid']
        fid = config['figure']
        tid = str(now)[:22].replace(' ', '.').replace(':', '')
        output_name = "{}.{}.{}.png".format(pid, fid, tid) # pid. tid
        result_img.save(output_path / output_name)

def launch2():
    with open("convert/config2.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    layer_mixin = []
    pid = "32"
    main_path = Path('./convert/input')
    output_path = Path()/config["output"] #Path('./convert/1-1')
    # 检查路径是否存在以及是否为文件夹
    if output_path.exists():
        if output_path.is_dir():
            print(f"文件夹 '{output_path}' 已存在。")
        else:
            # 路径存在，但不是文件夹
            print(f"存在同名的文件 '{output_path}'，而不是文件夹。")
    else:
        # 路径不存在，创建文件夹
        try:
            output_path.mkdir()  # 只创建当前文件夹，不创建父文件夹
            print(f"文件夹 '{output_path}' 已创建。")
        except OSError as error:
            print(f"创建文件夹 '{output_path}' 时出错: {error}")
    logger.debug(main_path)
    # get from toml & files
    for layer in config["layer"]:
        symbol = layer["symbol"]
        pinx = layer['x']
        piny = layer['y']
        if "*" in symbol:
            comfyui_list = main_path.glob("ComfyUI*.png")
            comfyui_layer = [{"symbol": file, 'x': pinx, 'y': piny} for file in comfyui_list]
            layer_mixin.append(comfyui_layer)
        else:
            ui_layer = {"symbol": main_path / symbol, 'x': pinx, 'y': piny}
            layer_mixin.append(ui_layer)
    logger.debug(layer_mixin)
    layer_matrix = flatten_layer(layer_mixin)
    logger.debug(layer_matrix)

    for layer_list in zip(*layer_matrix):
        result_img = None
        for layer in layer_list:
            layer_img = Image.open(layer['symbol'])
            pinx = layer['x']
            piny = layer['y']
            result_img = blend_images_offset(result_img, layer_img, pinx, piny)
        # result_img.show()
        now = pendulum.now("Asia/Shanghai")
        pid = config['pid']
        fid = config['figure']
        tid = str(now)[:22].replace(' ', '.').replace(':', '')
        output_name = "{}.{}.{}.png".format(pid, fid, tid) # pid. tid
        result_img.save(output_path / output_name)

def flatten_layer(layer_mixin):
    # 将列表中的所有列表元素存储在一个列表中
    lists = [item for item in layer_mixin if isinstance(item, list)]

    # 检查所有列表长度是否一致
    if len(set(map(len, lists))) != 1:
        raise ValueError("Not all lists have the same length")

    horizon = len(lists[0])
    matrix = []
    for item in layer_mixin:
        if isinstance(item, list):
            # 如果元素是列表，直接添加到矩阵中（假设长度符合要求）
            matrix.append(item)
        else:
            # 如果元素不是列表，尝试将其转换为所需长度的列表
            matrix.append([item] * horizon)  
    return matrix


def blend_images_offset(bottom_layer, top_layer, x=0, y=0):
    """
    Blend two image objects with alpha transparency, applying an offset to the top layer.
    If the images are not in 'RGBA' mode, they will be converted.
    If the top layer is not the same size as the bottom layer, it will be resized.

    Parameters:
    - bottom_layer: PIL.Image object for the bottom layer.
    - top_layer: PIL.Image object for the top layer.
    - x_offset: Integer, the horizontal offset for the top layer.
    - y_offset: Integer, the vertical offset for the top layer.

    Returns:
    - A new PIL.Image object that is the result of blending the two layers
      with the top layer offset.
    """
    if bottom_layer == None:
        return top_layer
    # 确保下层图像是RGBA模式
    if bottom_layer.mode != "RGBA":
        bottom_layer = bottom_layer.convert("RGBA")

    # 确保上层图像是RGBA模式
    if top_layer.mode != "RGBA":
        top_layer = top_layer.convert("RGBA")

    # 如果上层图像和下层图像尺寸不一致，缩放上层图像, 拉伸改变了比例
    # if top_layer.size != bottom_layer.size:
        # top_layer.thumbnail(bottom_layer.size)
        # top_layer = top_layer.resize(bottom_layer.size, Image.LANCZOS)
    if top_layer.size != bottom_layer.size:
        scale_ratio = bottom_layer.height / top_layer.height  

        # 缩放上层图像的高度以匹配下层图像，同时保持宽高比
        new_width = int(top_layer.width * scale_ratio)
        top_layer = top_layer.resize((new_width, bottom_layer.height), Image.LANCZOS)

    # 创建一个空白的RGBA图像，尺寸与RGBA图片相同
    fusion_layer = Image.new("RGBA", bottom_layer.size, (0, 0, 0, 0))
    # 将缩放后的RGB图片粘贴到空白图像的(0, 100)位置
    fusion_layer.paste(top_layer, (x, y))

    # 使用alpha_composite混合图像
    blended_image = Image.alpha_composite(bottom_layer, fusion_layer)

    # result_img = blended_image
    # result_img.save('result_overlay.png')
    # result_img.show()
    return blended_image


def boot():
    global DUCK
    with open("config.toml", "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    DUCK["layers"] = config.get("layers", None)
    DUCK["main_path"] = config.get("main_path", None)


if __name__ == "__main__":
    # boot()
    # get_png_filenames()
    # print(DUCK)
    # raise
    launch()
    launch2()


##   现在的问题是上下层还很奇怪，到时是0在上还是0在下呢


