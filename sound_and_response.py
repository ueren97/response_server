# coding:utf8
"""
exchange posted audio file into text file 
-> export file which export it to dialogflow 
"""
import base64

from googleapiclient import discovery
import httplib2

from dialogflow_api import access_to_dialogflow

# Speech to Text
# set the api key
KEY = "**********"

# filename
speech_file = "**********"

# URL information
DISCOVERY_URL = "https://speech.googleapis.com/**********"


def get_speech_service():
    """
    return information of api
    """
    http = httplib2.Http()
    return discovery.build(
        'speech', 'v1', http=http,
        discoveryServiceUrl=DISCOVERY_URL, developerKey=KEY)


def send_text_to_dialogflow():
    """
    exchange recorded audio to text 
    -> export to function which export text to dialogflow 
    """
    # open audio file
    with open(speech_file, 'rb') as speech:
        speech_content = base64.b64encode(speech.read())

    # get api information -> speech to text
    service = get_speech_service()
    service_request = service.speech().recognize(
        body={
            'config': {
                'encoding': 'LINEAR16',
                'sampleRateHertz': 48000,
                'languageCode': 'ja-JP',   # set Japanese
                'enableWordTimeOffsets': 'false',
            },
            'audio': {
                'content': speech_content.decode('utf-8')
            }
        })

    response = service_request.execute()  # save response esult

    # check output result
    print(response['results'][0]["alternatives"][0]["transcript"])

    # export the text to dialogflow -> get result
    access_to_dialogflow(response["results"][0]
                         ["alternatives"][0]["transcript"])


if __name__ == '__main__':
    send_text_to_dialogflow()
