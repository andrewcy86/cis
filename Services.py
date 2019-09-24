import requests
import time

def tika(files):
    url = 'https://ecms-cis-tika.edap-cluster.com/tika/form'
    h = {'Cache-Control': 'no-cache'}
    s = time.time()
    r = requests.post(url, files=files, headers = headers)
    f = time.time()
    return(r, f-s)

def xtika(files):
    url = 'https://ecms-cis-tika.edap-cluster.com/tika/form'
    h = {'Content-Type' : 'application/pdf', 'X-Tika-PDFOcrStrategy': 'ocr_only', 'Cache-Control': 'no-cache'}
    s = time.time()
    r = requests.post(url, files=files, headers = headers1)
    f = time.time()
    return(r, f-s)

def nlpbuddy(text):
    url = 'https://ecms-cis-nlpbuddy.edap-cluster.com/api/analyze'
    h = {'Content-Type' : 'application/json'}
    data = {'text': text}
    s = time.time()
    r = requests.post(url, json=data)
    f = time.time()
    return(r, f-s)

def klassify(text):
    url = 'https://ecms-cis-klassify.edap-cluster.com/classify'
    data = {'text': text}
    s = time.time()
    r = requests.post(url, json=data)
    f = time.time()
    return(r, f-s)
