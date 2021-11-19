#!/usr/bin/env python3
# coding: utf-8

import pyaudio
import wave
from typing import List
import datetime
import os
import re
import sys
from .load_constants import Rec_Consts


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

def getOutputDirPath(participant, utterance, session, room, device_placement, distance, polar_angle, dov_angle) -> tuple[str, str, str, str, str]:
    # 第０階層（録音日）
    zero_dir_name = datetime.date.today().isoformat()
    # 第１階層
    first_dir_name = participant
    # 第２階層
    if session is None:
        second_dir_name = participant + '_' + room + '_' + device_placement + '_trial'
    else:
        second_dir_name = participant + '_' + room + \
            '_' + device_placement + '_' + session
    # 第３階層
    # get distance_id
    if distance == 1:
        distance_id = 'A'
    elif distance == 3:
        distance_id = 'B'
    elif distance == 5:
        distance_id = 'C'

    # get polar_angle_id
    if polar_angle == 0:
        polar_angle_id = 0
    elif polar_angle == 45:
        polar_angle_id = 1
    elif polar_angle == 90:
        polar_angle_id = 2

    polar_position_id = distance_id + str(polar_angle_id)
    third_dir_name = polar_position_id + '_' + \
        str(distance) + '_' + str(polar_angle)

    output_path = zero_dir_name + '/' + first_dir_name + \
        '/' + second_dir_name + '/' + third_dir_name
    return output_path, zero_dir_name, first_dir_name, second_dir_name, third_dir_name

def setupOutputEnv(consts: Rec_Consts, participant, utterance, session, room, device_placement, distance, polar_angle, dov_angle) -> str:
    output_path, zero_dir_name, first_dir_name, second_dir_name, third_dir_name = getOutputDirPath(
        participant, utterance, session, room, device_placement, distance, polar_angle, dov_angle)
    # sessionの設定（trialの設定）
    if session == None:
        # 探索対象のパスの設定
        search_for_1st_dir = consts.OUTPUT_PATH + '/' + \
            zero_dir_name + '/' + first_dir_name
        # パスが存在しないと、listdirがエラーになるので
        os.makedirs(search_for_1st_dir, exist_ok=True)
        dirs_list = os.listdir(search_for_1st_dir)

        # [second_dir] フォルダ内のtrialの最大値を取得
        regex = re.compile(re.escape(second_dir_name) + r'.*')
        current_max_trial = 0
        for dir_name in dirs_list:
            is_match = regex.match(dir_name)
            if is_match != None:
                current_max_trial += 1

        if current_max_trial > 0:
            # [third_dir] trial1から目標ディレクトリないか探索する
            file_name = utterance + '_' + str(dov_angle) + '_0.wav'
            for i in range(1, current_max_trial + 1):
                _second_dir_name = second_dir_name + str(i)
                search_for_wav_file = search_for_1st_dir + '/' + \
                    _second_dir_name + '/' + third_dir_name + '/' + file_name
                if os.path.isfile(search_for_wav_file):
                    if i == current_max_trial:
                        trial_no = current_max_trial + 1
                else:
                    trial_no = i
                    break
        else:
            # 1試行も行われていない場合、1に設定する
            trial_no = 1

        # sessionの設定
        new_second_dir_name = second_dir_name + str(trial_no)
        output_path = zero_dir_name + '/' + first_dir_name + \
            '/' + new_second_dir_name + '/' + third_dir_name

    # フルパス
    output_dir_path = consts.OUTPUT_PATH + '/' + output_path
    # exist_ok = Trueで既存ディレクトリを指定してもエラーにしない
    os.makedirs(output_dir_path, exist_ok=True)
    # output_file_nameの生成
    part_of_output_file_name = utterance + '_' + str(dov_angle) + '_'
    part_of_output_file_path = output_dir_path + '/' + part_of_output_file_name

    return part_of_output_file_path

def outputWaveFiles(consts: Rec_Consts, frames: List, p: pyaudio.PyAudio, part_of_output_file_path: str):
    '''
    同一ディレクトリにチャンネル毎のwavファイルを出力する。

    Parameters
    ----------
    nch: int
            チャンネル数
    output_path: str

    '''
    # # 音声ファイルを格納するディレクトリの名前を取得
    # dir_name = getDirname(consts.OUTPUT_PATH)
    # # ディレクトリを作成
    # output_dir_path = consts.OUTPUT_PATH + dir_name
    # os.mkdir(output_dir_path)

    for i in range(consts.RESPEAKER_CHANNELS):
        # filename = f"ch{i}.wav"
        output_file_path = part_of_output_file_path + str(i) + '.wav'
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
        print(f'Failed to write audio file.: {file_path}', file=sys.stderr)
    else:
        print(f'Success to write audio file.: {file_path}')
    finally:
        wf.close()
