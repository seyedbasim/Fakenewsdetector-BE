import logging
import http.client, urllib.request, urllib.parse, urllib.error, base64
from difflib import SequenceMatcher
import json
import requests
import azure.functions as func
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Please Insert Fake News with a paragraph')

    name = req.params.get('paragraph')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('paragraph')

    if name:      
        client = authenticate_client()

        documents = [name]
        response1 = client.extract_key_phrases(documents = documents)[0]
    
        subscriptionKey = "385b8a6ce15441c9ab4b3e49748d10fc"
        customConfigId = "8ade1031-2513-44e3-a57c-7aae377ae501"
        stre = name
        url = 'https://api.bing.microsoft.com/v7.0/search?' + 'q=' + stre + '&' + 'customconfig=' + customConfigId
        r = requests.get(url, headers={'Ocp-Apim-Subscription-Key': subscriptionKey})

        try:
            y = r.json()["webPages"]
        except:
            y = "noresults"

        if y == "noresults":
            body = {
                "url": "Fake News",
                "language": "",
                "ratio": "",
                "Key_phrase": str(response1.key_phrases)
            }
            z = json.dumps(body)
            return func.HttpResponse(z)
        else:
            searchresult = r.json()["webPages"]["value"][0]["snippet"]
            searchurl = r.json()["webPages"]["value"][0]["url"]
            #searchurl = r.json()["news"]["value"][0]["url"]
            searchlang = r.json()["webPages"]["value"][0]["language"]

            ratio = SequenceMatcher(None, name, searchresult).ratio()
            ratiostr = str(ratio)
            body = {
                "url": searchurl,
                "language": searchlang,
                "ratio": ratiostr,
                "Key_phrase": str(response1.key_phrases)
            }

            z = json.dumps(body)

            return func.HttpResponse(z)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

def authenticate_client():
    api_key1 = "18739397ba2c4f80863ff7afbfd0a5c6"
    endpoint1 = "https://textanalyticsforfndv1.cognitiveservices.azure.com/"
    ta_credential = AzureKeyCredential(api_key1)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint1, 
            credential=ta_credential)
    return text_analytics_client