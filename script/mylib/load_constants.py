#!/usr/bin/env python3
# coding: utf-8

class Rec_Consts():
    '''
    機械学習に用いる定数を定義するクラス
    '''

    def __init__(self, rate: int = 48000, channels: int = 6, width: int = 2, index: int = 2, chunk: int = 1024, record_sec: int = 3, output_path: str = "../out/recording"):
        self.RESPEAKER_RATE = rate
        # change base on firmwares, default_firmware.bin as 1 or 6_firmware.bin as 6
        self.RESPEAKER_CHANNELS = channels
        self.RESPEAKER_WIDTH = width
        # run getDeviceInfo.py to get index
        self.RESPEAKER_INDEX = index  # refer to input device id
        self.CHUNK = chunk
        self.RECORD_SECONDS = record_sec
        self.OUTPUT_PATH = output_path
