#!/usr/bin/env python3
# coding: utf-8

import pyaudio
import wave
import numpy as np
import time
from mylib.usb_4_mic_array.tuning import Tuning
import usb.core
import usb.util
from typing import List

RESPEAKER_RATE = 48000
# change base on firmwares, default_firmware.bin as 1 or 6_firmware.bin as 6
RESPEAKER_CHANNELS = 6
RESPEAKER_WIDTH = 2
# run getDeviceInfo.py to get index
RESPEAKER_INDEX = 0  # refer to input device id
CHUNK = 1024
RECORD_SECONDS = 3
OUTPUT_PATH = "../out/"


def outputWaveFiles(nch: int, output_path: str, frames: List):
    '''
    チャンネル毎にwavファイルを出力する。

    Parameters
    ----------
    nch: int, default 6
                    チャンネル数
    '''
    for i in range(nch):
        wave_output_filename = f"output_{i}.wav"
        wave_output_filepath = output_path + wave_output_filename
        wf = wave.open(wave_output_filepath, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(
            p.get_format_from_width(RESPEAKER_WIDTH)))
        wf.setframerate(RESPEAKER_RATE)
        wf.writeframes(b''.join(frames[i]))
        wf.close()


def outputWaveFile(file_path: str, frame: List, pyaudio: pyaudio.PyAudio):
    '''
    音声データをwavファイルを出力する。

    Parameters
    ----------
    file_path: str
            ファイルパス
    frame: array-like
            音声データが格納された配列
    pyaudio: pyaudio.PyAudio
            pyaudio
    '''
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.get_sample_size(
        pyaudio.get_format_from_width(RESPEAKER_WIDTH)))
    wf.setframerate(RESPEAKER_RATE)
    wf.writeframes(b''.join(frame))
    wf.close()


def main():
    #############
    ### Setup ###
    #############
    p = pyaudio.PyAudio()
    # streamのopen
    stream = p.open(
        rate=RESPEAKER_RATE,
        format=p.get_format_from_width(RESPEAKER_WIDTH),
        channels=RESPEAKER_CHANNELS,
        input=True,
        input_device_index=RESPEAKER_INDEX,)
    # USB-Device
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

    ##################
    ### Processing ###
    ##################
    if dev:
        Mic_tuning = Tuning(dev)
        try:
            print("Start Recording....\n")
            while True:
                # 音声が検出
                if Mic_tuning.is_voice():
                    print("* recording")
                    # 音声データを格納する二次元配列
                    frames = [[] for _ in range(RESPEAKER_CHANNELS)]
                    for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
                        data = stream.read(CHUNK)
                        # channelごとの音声データの取得
                        for j in range(RESPEAKER_CHANNELS):
                            ch_data = np.frombuffer(data, dtype=np.int16)[
                                j::RESPEAKER_CHANNELS]
                            frames[j].append(ch_data.tobytes())
                    print("* done recording")
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStop Recording.")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

# print("* recording")

# # 音声データを格納する二次元配列
# frames = [[] for i in range(RESPEAKER_CHANNELS)]

# for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
#     data = stream.read(CHUNK)

#     # channelごとの音声データの取得
#     for j in range(RESPEAKER_CHANNELS):
#         ch_data = np.frombuffer(data, dtype=np.int16)[j::RESPEAKER_CHANNELS]
#         frames[j].append(ch_data.tobytes())

# print("* done recording")

# stream.stop_stream()
# stream.close()
# p.terminate()

# # 音声ファイルに出力
# for i in range(RESPEAKER_CHANNELS):
#     WAVE_OUTPUT_FILENAME = f"output_{i}.wav"
#     WAVE_OUTPUT_FILEPATH = OUTPUT_PATH + WAVE_OUTPUT_FILENAME
#     wf = wave.open(WAVE_OUTPUT_FILEPATH, 'wb')
#     # wf.setnchannels(RESPEAKER_CHANNELS)
#     wf.setnchannels(1)
#     wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
#     wf.setframerate(RESPEAKER_RATE)
#     wf.writeframes(b''.join(frames[i]))
#     wf.close()


if __name__ == '__main__':
    main()
