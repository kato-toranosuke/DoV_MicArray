#!/usr/bin/env python3
# coding: utf-8

import pyaudio
import numpy as np
import time
import usb.core
import usb.util
import sys
from typing import List
import keyboard
from mylib.usb_4_mic_array.tuning import Tuning
from mylib.load_constants import Rec_Consts
from mylib import record_audio

def start_with_key(consts: Rec_Consts):
    #############
    ### Setup ###
    #############
    p = pyaudio.PyAudio()
    # consts = Rec_Consts()
    # USB-Device
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

    #################
    ### Recording ###
    #################
    print("Start execution....")
    if dev:
        try:
            while True:
                if keyboard.is_pressed("s"):
                    # streamのopen
                    stream = p.open(
                        format=p.get_format_from_width(consts.RESPEAKER_WIDTH),
                        channels=consts.RESPEAKER_CHANNELS,
                        rate=consts.RESPEAKER_RATE,
                        input=True,
                        output=False,  # 追加
                        input_device_index=consts.RESPEAKER_INDEX)

                    # recording
                    print("\n### recording ###")
                    # 音声データを格納する二次元配列
                    frames = [[] for _ in range(consts.RESPEAKER_CHANNELS)]
                    for _ in range(0, int(consts.RESPEAKER_RATE / consts.CHUNK * consts.RECORD_SECONDS)):
                        data = stream.read(consts.CHUNK)
                        # channelごとの音声データの取得
                        for j in range(consts.RESPEAKER_CHANNELS):
                            ch_data = np.frombuffer(data, dtype=np.int16)[
                                j::consts.RESPEAKER_CHANNELS]
                            frames[j].append(ch_data.tobytes())
                    print("### done recording ###")
                    stream.stop_stream()
                    stream.close()

                    # wavファイルに出力
                    record_audio.outputWaveFiles(consts, frames, p)

                    time.sleep(0.01)

        except KeyboardInterrupt:
            print("\nStop execution.")
        finally:
            p.terminate()  # PyAudioのインスタンスを破棄する
    else:
        print("Device not found.", file=sys.stderr)

def start_end_with_key():
    #############
    ### Setup ###
    #############
    p = pyaudio.PyAudio()
    consts = Rec_Consts()
    # USB-Device
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

    #################
    ### Recording ###
    #################
    if dev:
        try:
            print("Start execution....\n")
            # streamのopen
            stream = p.open(
                format=p.get_format_from_width(consts.RESPEAKER_WIDTH),
                channels=consts.RESPEAKER_CHANNELS,
                rate=consts.RESPEAKER_RATE,
                input=True,
                output=False,  # 追加
                input_device_index=consts.RESPEAKER_INDEX)
            print("### recording ###")
            # 音声データを格納する二次元配列
            frames = [[] for _ in range(consts.RESPEAKER_CHANNELS)]
            for i in range(0, int(consts.RESPEAKER_RATE / consts.CHUNK * consts.RECORD_SECONDS)):
                data = stream.read(consts.CHUNK)
                # channelごとの音声データの取得
                for j in range(consts.RESPEAKER_CHANNELS):
                    ch_data = np.frombuffer(data, dtype=np.int16)[
                        j::consts.RESPEAKER_CHANNELS]
                    frames[j].append(ch_data.tobytes())
            print("### done recording ###")

        except KeyboardInterrupt:
            print("\nStop execution.")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()  # PyAudioのインスタンスを破棄する

        # wavファイルに出力
        record_audio.outputWaveFiles(consts, frames, p)
    else:
        print("Device not found.", file=sys.stderr)


if __name__ == '__main__':
    consts = Rec_Consts(index=0)
    start_with_key(consts)
