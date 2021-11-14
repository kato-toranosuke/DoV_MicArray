#!/usr/bin/env python3
# coding: utf-8

import pyaudio
import numpy as np
import time
import usb.core
import usb.util
import sys
from typing import List
from mylib.usb_4_mic_array.tuning import Tuning
from mylib.load_constants import Rec_Consts
from mylib import record_audio

def main():
    #############
    ### Setup ###
    #############
    p = pyaudio.PyAudio()
    consts = Rec_Consts()
    # streamのopen
    stream = p.open(
        format=p.get_format_from_width(consts.RESPEAKER_WIDTH),
        channels=consts.RESPEAKER_CHANNELS,
        rate=consts.RESPEAKER_RATE,
        input=True,
        output=False,  # 追加
        input_device_index=consts.RESPEAKER_INDEX)
    # USB-Device
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

    #################
    ### Recording ###
    #################
    if dev:
        Mic_tuning = Tuning(dev)
        try:
            print("Start Recording....\n")
            while True:
                # 音声が検出
                if Mic_tuning.is_voice():
                    print("* recording")
                    # 音声データを格納する二次元配列
                    frames = [[] for _ in range(consts.RESPEAKER_CHANNELS)]
                    for i in range(0, int(consts.RESPEAKER_RATE / consts.CHUNK * consts.RECORD_SECONDS)):
                        data = stream.read(consts.CHUNK)
                        # channelごとの音声データの取得
                        for j in range(consts.RESPEAKER_CHANNELS):
                            ch_data = np.frombuffer(data, dtype=np.int16)[
                                j::consts.RESPEAKER_CHANNELS]
                            frames[j].append(ch_data.tobytes())
                    print("* done recording")

                    # wavファイルに出力
                    record_audio.outputWaveFiles(consts, frames, p)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStop Recording.")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()  # PyAudioのインスタンスを破棄する
    else:
        print("Device not found.", file=sys.stderr)

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
