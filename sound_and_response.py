# coding:utf8
"""
取得した音声ファイルをテキスト化して、Dialogflowにテキストを渡すプログラムに渡す。
"""
import base64

from googleapiclient import discovery
import httplib2

from dialogflow_api import access_to_dialogflow

# 音声からテキストにするプログラム
# APIキーを設定
KEY = "AIzaSyCYdoExbu90ejput_e6mzyudQ7XgweQJos"

# 音声認識に使うファイル名
speech_file = "weather.wav"

# URL情報
DISCOVERY_URL = "https://speech.googleapis.com/$discovery/rest"


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
    録音した音声をテキスト化して、Dialogflowにテキストを渡すプログラムに渡す。
    """
    # 音声ファイルを開く
    with open(speech_file, 'rb') as speech:
        speech_content = base64.b64encode(speech.read())

    # APIの情報を取得して、音声認識を行う
    service = get_speech_service()
    service_request = service.speech().recognize(
        body={
            'config': {
                'encoding': 'LINEAR16',
                'sampleRateHertz': 48000,
                'languageCode': 'ja-JP',   # 日本語に設定
                'enableWordTimeOffsets': 'false',
            },
            'audio': {
                'content': speech_content.decode('utf-8')
                }
            })

    response = service_request.execute()  # SpeechAPIによる認識結果を保存
    # わかりやすいようにコンソールに認識された音声を出力
    print(response['results'][0]["alternatives"][0]["transcript"])

    # テキストをDialogflowに渡してレスポンスを受け取る
    access_to_dialogflow(response["results"][0]["alternatives"][0]["transcript"])


if __name__ == '__main__':
    send_text_to_dialogflow()
