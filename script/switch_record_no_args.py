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
from pynput.keyboard import Key, Listener

def start_with_key(consts: Rec_Consts) -> None:
    '''
    Sキーを押す時に録音を開始する。
    '''
    #############
    ### Setup ###
    #############
    p = pyaudio.PyAudio()
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

def start_end_with_key(consts: Rec_Consts, block_sec: float = 0.1) -> None:
    '''
    Sキーを押す時に録音を開始し、Eキーを押す時に終了する。

    Parameter
    '''

    #############
    ### Setup ###
    #############
    p = pyaudio.PyAudio()
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

                    # start recording
                    print("\n### recording ###")

                    # 音声データを格納する二次元配列
                    frames = [[] for _ in range(consts.RESPEAKER_CHANNELS)]
                    while True:
                        for _ in range(0, int(consts.RESPEAKER_RATE / consts.CHUNK * consts.RECORD_SECONDS)):
                            data = stream.read(consts.CHUNK)
                            # channelごとの音声データの取得
                            for j in range(consts.RESPEAKER_CHANNELS):
                                ch_data = np.frombuffer(data, dtype=np.int16)[
                                    j::consts.RESPEAKER_CHANNELS]
                                frames[j].append(ch_data.tobytes())

                        # 終了キー判定
                        if keyboard.is_pressed("e"):
                            break

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


if __name__ == '__main__':
    consts = Rec_Consts(index=0)
    # start_with_key(consts)
    start_end_with_key(consts)
