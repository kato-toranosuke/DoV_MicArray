#!/usr/bin/env python3
# coding: utf-8

import pyaudio
import wave
import numpy as np

RESPEAKER_RATE = 48000
RESPEAKER_CHANNELS = 6 # change base on firmwares, default_firmware.bin as 1 or 6_firmware.bin as 6
RESPEAKER_WIDTH = 2
# run getDeviceInfo.py to get index
RESPEAKER_INDEX = 0  # refer to input device id
CHUNK = 1024
RECORD_SECONDS = 3

OUTPUT_PATH = "../out/"
# WAVE_OUTPUT_FILENAME = f"output_{RESPEAKER_CHANNELS}.wav"

p = pyaudio.PyAudio()

stream = p.open(
            rate=RESPEAKER_RATE,
            format=p.get_format_from_width(RESPEAKER_WIDTH),
            channels=RESPEAKER_CHANNELS,
            input=True,
            input_device_index=RESPEAKER_INDEX,)

print("* recording")

# 音声データを格納する二次元配列
frames = [[] for i in range(RESPEAKER_CHANNELS)]

for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)

    # channelごとの音声データの取得
    for j in range(RESPEAKER_CHANNELS):
        ch_data = np.frombuffer(data, dtype=np.int16)[j::RESPEAKER_CHANNELS]
        frames[j].append(ch_data.tobytes())

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

# 音声ファイルに出力
for i in range(RESPEAKER_CHANNELS):
    WAVE_OUTPUT_FILENAME = f"output_{i}.wav"
    WAVE_OUTPUT_FILEPATH = OUTPUT_PATH + WAVE_OUTPUT_FILENAME
    wf = wave.open(WAVE_OUTPUT_FILEPATH, 'wb')
    # wf.setnchannels(RESPEAKER_CHANNELS)
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
    wf.setframerate(RESPEAKER_RATE)
    wf.writeframes(b''.join(frames[i]))
    wf.close()
