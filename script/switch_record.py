#!/usr/bin/env python3
# coding: utf-8

import pyaudio
import numpy as np
import time
import usb.core
import usb.util
import sys
import keyboard
import argparse
from mylib.usb_4_mic_array.tuning import Tuning
from mylib.load_constants import Rec_Consts
from mylib import output_wav
from mylib import rec_audio

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
                    # 一定時間の録音
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
                    output_wav.outputWaveFiles(consts, frames, p)

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
                    output_wav.outputWaveFiles(consts, frames, p)

                    time.sleep(0.01)

        except KeyboardInterrupt:
            print("\nStop execution.")
        finally:
            p.terminate()  # PyAudioのインスタンスを破棄する
    else:
        print("Device not found.", file=sys.stderr)

class Recording():
    def __init__(self, consts: Rec_Consts) -> None:
        self.consts = consts
        self.p = pyaudio.PyAudio()
        # self.frames = [[] for _ in range(self.consts.RESPEAKER_CHANNELS)]
        self.frame_len = int(self.consts.RESPEAKER_RATE /
                             self.consts.CHUNK * self.consts.RECORD_SECONDS)
        # USB-Device
        self.dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
        # USB-Deviceが見つからなかった場合
        if self.dev is None:
            print("Device not found.", file=sys.stderr)
            return

    def startRecording(self):
        print("\n### start recording ###")
        self.frames = [[] for _ in range(self.consts.RESPEAKER_CHANNELS)]
        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.consts.RESPEAKER_WIDTH),
            channels=self.consts.RESPEAKER_CHANNELS,
            rate=self.consts.RESPEAKER_RATE,
            input=True,
            output=False,
            input_device_index=self.consts.RESPEAKER_INDEX,
            frames_per_buffer=self.consts.CHUNK)
        # 終了コマンドが押されるまでframeを読み込み続ける
        while self.stream.is_active():
            self.readFrame()

    def readFrame(self):
        '''
        1chunk分の全チャンネルのデータを読み込み、frames配列に追加する。
        '''
        data = self.stream.read(self.consts.CHUNK)
        # channelごとの音声データの取得
        for ch in range(self.consts.RESPEAKER_CHANNELS):
            ch_data = np.frombuffer(data, dtype=np.int16)[
                ch::self.consts.RESPEAKER_CHANNELS]
            self.frames[ch].append(ch_data.tobytes())

    def endRecording(self):
        self.stream.stop_stream()
        self.stream.close()
        # wavファイルに出力
        output_wav.outputWaveFiles(self.consts, self.frames, self.p)
        print("### stop recording ###")

    def on_press(self, key):
        self.startRecording()

    def on_release(self, key):
        self.endRecording()

    # def main(self):
    #     with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
    #         listener.join()


if __name__ == '__main__':
    # 引数の設定
    parser = argparse.ArgumentParser()
    parser.add_argument('--participant', default='s11', nargs='?')
    parser.add_argument('--utterance')
    parser.add_argument('--session', default=None, nargs='?')
    parser.add_argument('--room', default='upstairs',
                        choices=['upstairs', 'downstairs', 'onshinlab', 'gym'], nargs='?')
    parser.add_argument('--device_placement', default='wall',
                        choices=['wall', 'nowall'], nargs='?')
    # choices コンテナーに含まれているかどうかのチェックは、type による型変換が実行された後であることに注意してください。
    # このため、choices に格納するオブジェクトの型は指定された type にマッチしている必要があります
    parser.add_argument('--distance', choices=[1, 3, 5], type=int)
    parser.add_argument('--polar_angle', choices=[0, 45, 90], type=int)
    parser.add_argument(
        '--dov_angle', choices=[0, 45, 90, 135, 180, 225, 270, 315], type=int)

    # 定数の設定
    # consts = Rec_Consts(
    #     index=0, output_path="../out/recording/mac", record_sec=1.5, rate=48000)
    
    # "OSError: [Errno -9981] Input overflowed"によって録音できなかった→chunkを大きくすることで対応
    consts = Rec_Consts(
        index=0, output_path="../out/recording/raspi", record_sec=2.0, rate=48000, chunk=2048)
    # 引数がある場合
    if len(sys.argv) > 1:
        args = parser.parse_args()
        part_of_output_file_path = output_wav.setupOutputEnv(consts, args.participant, args.utterance, args.session,
                                                             args.room, args.device_placement, args.distance, args.polar_angle, args.dov_angle)
        rec_audio.recording(consts, part_of_output_file_path)
