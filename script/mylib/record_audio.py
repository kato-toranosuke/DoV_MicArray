#!/usr/bin/env python3
# coding: utf-8

import pyaudio
import wave
from typing import List
import datetime
import os
import re
import sys
from load_constants import Rec_Consts


def getDirname(output_path) -> str:
    # 現在日時
    d_today = datetime.date.today().isoformat()
    # 実行中のスクリプトの名前を取得
    # resultディレクトリに同一日時のディレクトリがいくつあるか
    dirs_list = os.listdir(output_path)
    no = 0
    regex = re.compile(r'.*' + re.escape(d_today) + r'.*')
    for dir_name in dirs_list:
        is_match = regex.match(dir_name)
        if is_match != None:
            no += 1

    dir_name = d_today + '_no' + str(no)
    return dir_name


def outputWaveFiles(consts: Rec_Consts, frames: List, p: pyaudio.PyAudio):
    '''
    同一ディレクトリにチャンネル毎のwavファイルを出力する。

    Parameters
    ----------
    nch: int
            チャンネル数
    output_path: str

    '''
    # 音声ファイルを格納するディレクトリの名前を取得
    dir_name = getDirname(consts.OUTPUT_PATH)
    # ディレクトリを作成
    output_dir_path = consts.OUTPUT_PATH + dir_name
    os.mkdir(output_dir_path)

    for i in range(consts.RESPEAKER_CHANNELS):
        filename = f"ch{i}.wav"
        output_file_path = output_dir_path + '/' + filename
        outputWaveFile(
            output_file_path, frames[i], p, consts.RESPEAKER_WIDTH, consts.RESPEAKER_RATE)


def outputWaveFile(file_path: str, frame: List, p: pyaudio.PyAudio, width: int, fs: int) -> None:
    '''
    音声データをwavファイルを出力する。

    Parameters
    ----------
    file_path: str
            ファイルパス
    frame: array-like
            音声データが格納された配列
    pa: pyaudio.PyAudio
            pyaudio
    '''
    try:
        wf = wave.open(file_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(p.get_format_from_width(width)))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frame))
    except:
        print(f'Failed to write audio file.: {file_path}\n', file=sys.stderr)
    else:
        print(f'Success to write audio file.: {file_path}\n')
    finally:
        wf.close()
