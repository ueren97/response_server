# coding:utf8
"""
音声を録音しテキスト化して、Dialogflowに渡すプログラムに渡す。
録音→音声認識→音声ファイル化→Dialogflow→レスポンスの実装
"""
import base64
from googleapiclient import discovery
import httplib2

import pyaudio  # 録音機能を使うためのライブラリ
import wave     # wavファイルを扱うためのライブラリ

from dialogflow_api import access_to_dialogflow

# APIキーを設定
KEY = "AIzaSyCYdoExbu90ejput_e6mzyudQ7XgweQJos"

# 音声を保存するファイル名
WAVE_OUTPUT_FILENAME = "record.wav"

# 録音に関する基本情報
RECORD_SECONDS = 5  # 録音する時間の長さ（秒）
DEVICE_INDEX = 0  # 録音デバイスのインデックス番号

# APIのURL情報
DISCOVERY_URL = "https://speech.googleapis.com/$discovery/rest"


def record():
    # 基本情報の設定
    FORMAT = pyaudio.paInt16  # 音声のフォーマット
    CHANNELS = 1              # モノラル
    RATE = 16000              # サンプルレート
    CHUNK = 2**11             # データ点数
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        input_device_index=DEVICE_INDEX,  # 録音デバイスのインデックス番号
                        frames_per_buffer=CHUNK)

    # --------------録音開始---------------

    print("話かけてください...")
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("録音が完了しました。")

    # --------------録音終了---------------

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()


def get_speech_service():
    """
    APIの情報を返す関数
    """
    http = httplib2.Http()
    return discovery.build(
        'speech', 'v1', http=http,
        discoveryServiceUrl=DISCOVERY_URL, developerKey=KEY)


def send_text_to_dialogflow():
    """
    録音した音声をテキスト化して、Dialogflowに渡すプログラムに渡す。
    """

    # responseのフォーマット
    response = {"results": [{
                    "alternatives": [{
                        "transcript": ""}
                           ]}
                ]}

    while response["results"][0]["alternatives"][0]["transcript"] != "終了":
        record()

        # 音声ファイルを開く
        with open(WAVE_OUTPUT_FILENAME, 'rb') as speech:
            speech_content = base64.b64encode(speech.read())

        # APIの情報を取得して、音声認識を行う
        service = get_speech_service()
        service_request = service.speech().recognize(
            body={
                'config': {
                    'encoding': 'LINEAR16',
                    'sampleRateHertz': 16000,
                    'languageCode': 'ja-JP',  # 日本語に設定
                    'enableWordTimeOffsets': 'false',
                },
                'audio': {
                    'content': speech_content.decode('utf-8')
                    }
                })

        try:
            response = service_request.execute() # SpeechAPIによる認識結果を保存
            # わかりやすいようにコンソール画面で出力
            print(response["results"][0]["alternatives"][0]["transcript"])
        except KeyError:
            print('音声が認識できませんでした。')
            break  # 入力されなかった時にループを抜ける

        # 入力音声が"終了"ではない限りDialogflowにアクセスする
        if response["results"][0]["alternatives"][0]["transcript"] != "終了":
            input_value = response["results"][0]["alternatives"][0]["transcript"]
            access_to_dialogflow(input_value)

if __name__ == '__main__':
    send_text_to_dialogflow()
