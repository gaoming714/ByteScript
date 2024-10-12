import time
from pathlib import Path
import pygame
import pendulum

last_dt = pendulum.now("Asia/Shanghai")

def play_audio(audio_path):
    """
    不断监控指定文件夹，播放MP3或WAV文件。

    Args:
        audio_folder: 需要监控的音频文件夹路径。
    """

    pygame.mixer.init()  # 初始化pygame的mixer模块
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)  # 等待音频播放完成

def monitor_audio_folder(audio_folder):
    global last_dt
    while True:
        for file in audio_folder.glob('*.mp3') or audio_folder.glob('*.wav'):
            create_time = file.stat().st_ctime
            create_time_pendulum = pendulum.from_timestamp(create_time)
            if create_time_pendulum > last_dt:
                print("play {}".format(file))
                play_audio(file)
                last_dt = create_time_pendulum
        time.sleep(5)

if __name__ == "__main__":
    audio_folder = Path("audio")  # 替换为你的音频文件夹路径
    monitor_audio_folder(audio_folder)