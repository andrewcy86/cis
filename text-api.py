import requests
import time
import mimetypes
import json
    
sttime = "global"
fttime = "global"
sotime = "global"
fotime = "global"
snltime = "global"
fnltime = "global"
sktime = "global"
fktime = "global"

mimetype = ""

def tika(files):
    global sttime
    global fttime
    url = 'https://ecms-cis-tika.edap-cluster.com/tika/form'
    headers = {'Cache-Control': 'no-cache'}
    sttime = time.time()
    r = requests.post(url, files=files, headers = headers)
    fttime = time.time()
    return r

#must provide filename as a hint using 'content-disposition' : 'attachment; filename = fullfilename'
def detect(files, filename):
    url = 'https://ecms-cis-tika.edap-cluster.com/detect/stream'
    getname = 'attachment; filename=' + filename
    headers = {
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Connection': "keep-alive",
    'cache-control': "no-cache",
    'Content-Disposition': getname,
    }
    r = requests.put(url, files=files, headers = headers)
    return r 

def xtika(files):
    global sotime
    global fotime
    url = 'https://ecms-cis-tika.edap-cluster.com/tika'
    headers1 = {'Content-Type' : 'application/pdf', 'X-Tika-PDFOcrStrategy': 'ocr_only', 'Cache-Control': 'no-cache'}
    sotime = time.time()
    r = requests.put(url, files=files, headers = headers1)
    fotime = time.time()
    return r

def nlpbuddy(text):
    global snltime
    global fnltime
    url = 'https://ecms-cis-nlpbuddy.edap-cluster.com/api/analyze'
    headers = {'Content-Type' : 'application/json'}
    data = {'text': text}
    snltime = time.time()
    r = requests.post(url, json=data)
    fnltime = time.time()
    return r

def klassify(text):
    global sktime
    global fktime
    url = 'https://ecms-cis-klassify.edap-cluster.com/classify'
    data = {"text": text}
    sktime = time.time()
    r = requests.post(url, json=data)
    fktime = time.time()
    return r

def getLabel(label):
    x = label[label.index('_')+1:label.index('_')+5]
    y = x.replace('_','')
    url = 'https://developer.epa.gov/api/index.php/records/api_records?filter=Record_Schedule_Number,cs,' + y
    r = requests.get(url)
    q = r.json()
    return q['records'][0]['Schedule_Title']

if __name__ == "__main__":     
    
    from tkinter import filedialog
    from tkinter import *
    #from tkinter import messagebox
    #messagebox.showinfo("Title", "a Tk MessageBox")

    root = Tk()
    #root.dirname = filedialog.askdirectory(parent=root,initialdir="/",title='Please select a directory to scan')
    root.filename = filedialog.askopenfilename(parent=root,initialdir="/",title='Please select a file to scan')
    
    #get filenam from path
    import ntpath
    def getname(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)
    
    
    fin = open(root.filename, 'rb')
    name = getname(root.filename)
    
    files = {'files':fin}

    print ('Parsing File: '+root.filename)

    #mimetype = mimetypes.MimeTypes().guess_type(root.filename)[0]
    #print (mimetype)
    
    mimetype = detect(files,name)
    
    r = tika(files)
    #print (r.content)
    #print(r.status_code) API STATUS
    
    
    #Determine if PDF needs OCRing
    if len(r.text.strip())==0 and ('pdf' in mimetype):
        fin.seek(0) # Move to the beginning of document
        r = xtika(files)
        print("--- Text Extraction with OCR Took {} seconds ---".format(abs(round(sttime - fttime,2))))
    else:
        print("--- Text Extraction Took {} seconds ---".format(abs(round(sttime - fttime,2))))
    #print(r.text)
    
    # or (mimetype == 'application/vnd.ms-excel') or (mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if len(r.text.strip())==0:
        quit()
        
    t = nlpbuddy(r.text)
    print("--- Text Summarization Took {} seconds ---".format(abs(round(snltime - fnltime,2))))
   
    a = t.json()    
    b = klassify(a['summary'])
    c = b.json()
    print("--- ML Text Classification Took {} seconds ---".format(abs(round(sktime - fktime,2))))
    print("Suggested Records Schedule: " + str(c['label']) + " - " + getLabel(str(c['label'])))
    
    #Display top 3 categories
    from collections import Counter
    d = Counter(c['scores'])
    print('Recommended Top 3 Record Schedules')
    for k,v in d.most_common(3):
        print('{} - {}: Score {}'.format(k,getLabel(k),v))
    
    size = fin.seek(0,2)
    fin.close()
    
    #print total processing time, and size of document
    print('Total Time Took to Process this Document of {} bit: {} Seconds'.format(size, abs(round(sttime - fktime,2))))
    
    #print summary
    print("Here's the summary: ")
    print(a['summary'][:400])

    #print keywords
    print("Here are some keywords: ")
    print(a['keywords'][:400])
