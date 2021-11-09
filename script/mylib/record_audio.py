#!/usr/bin/env python3
# coding: utf-8

import pyaudio
import wave
import time
import usb.core
import usb.util
from typing import List
import datetime
import os
import re


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


def outputWaveFiles(nch: int, output_path: str, frames: List):
    '''
    同一ディレクトリにチャンネル毎のwavファイルを出力する。

    Parameters
    ----------
    nch: int
            チャンネル数
    output_path: str

    '''
    dir_name = getDirname(output_path)
    for i in range(nch):
        filename = f"ch{i}.wav"
        wave_output_filepath = output_path + wave_output_filename
        wf = wave.open(wave_output_filepath, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(
            p.get_format_from_width(RESPEAKER_WIDTH)))
        wf.setframerate(RESPEAKER_RATE)
        wf.writeframes(b''.join(frames[i]))
        wf.close()


def outputWaveFile(file_path: str, frame: List, pa: pyaudio.PyAudio, width: int, fs: int) -> None:
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
        wf.setsampwidth(pa.get_sample_size(pa.get_format_from_width(width)))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frame))
    except:
        print(f'Failed to write audio file.: {file_path}')
    else:
        print(f'Success to write audio file.: {file_path}')
    finally:
        wf.close()
