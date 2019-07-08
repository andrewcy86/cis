import requests
import time
import mimetypes

sttime = "global"
fttime = "global"
sotime = "global"
fotime = "global"
snltime = "global"
fnltime = "global"
sktime = "global"
fktime = "global"

mimetype = ""

dict = {'104-008-02_1035_d' : "Short-term environmental program and project records",
        '108-025_1036_a' : "Historically significant site-specific records (See Guidance for explanation.)",
        '108-025-01-01_1044_d' : "Short-term compliance and enforcement records",
        '108-025-08_1044_b' : "Long-term compliance and enforcement records",
        '108-028_1036_c' : "Long-term site-specific records",
        '204-079_1047_c' : "Routine permits",
        '205_1003_a' : "Waste water construction and state revolving fund grants",
        '205_1003_b' : "Other grants and program support agreements",
        '301-093_1016_c' : "Routine controls and oversight records",
        '301-093_1051_b' : "Routine senior officials records",
        '302-095_1008_c' : "Other security records",
        '304-104-02_1021_a' : "Historically significant planning and resource allocation records",
        '304-104-06_1035_c' : "Routine environmental program and project records",
        '305-109-02-04_1022_a' : "Historically significant public affairs records",
        '305-109-02-04_1051_a' : "Historically significant records of senior officials",
        '306-112_1023_c' : "Nonfinal rulemakings and state standards records",
        '317-261_1025_b' : "Other legal services records",
        '401_1006_b' : "Other administrative management records",
        '401-122_1010_a' : "Travel records",
        'Encrypted' : None}

def tika(files):
    global sttime
    global fttime
    url = 'https://ecms-cis-tika.edap-cluster.com/tika/form'
    headers = {'Cache-Control': 'no-cache'}
    sttime = time.time()
    r = requests.post(url, files=files, headers = headers)
    fttime = time.time()
    return r

def xtika(files):
    global sotime
    global fotime
    url = 'https://ecms-cis-tika.edap-cluster.com/tika/form'
    headers1 = {'Content-Type' : 'application/pdf', 'X-Tika-PDFOcrStrategy': 'ocr_only', 'Cache-Control': 'no-cache'}
    sotime = time.time()
    r = requests.post(url, files=files, headers = headers1)
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
    
if __name__ == "__main__":     
    
    from tkinter import filedialog
    from tkinter import *
    import json
    #from tkinter import messagebox
    #messagebox.showinfo("Title", "a Tk MessageBox")

    root = Tk()
    #root.dirname = filedialog.askdirectory(parent=root,initialdir="/",title='Please select a directory to scan')
    root.filename = filedialog.askopenfilename(parent=root,initialdir="/",title='Please select a file to scan')

    fin = open(root.filename, 'rb')
   
    files = {'files':fin}

    print ('Parsing File: '+root.filename)

    mimetype = mimetypes.MimeTypes().guess_type(root.filename)[0]
    #print (mimetype)
    r = tika(files)
    #print (r.content)
    #print(r.status_code) API STATUS
    #Determine if PDF needs OCRing
    if len(r.text.strip())==0 and (mimetype == 'application/pdf'):
        fin.seek(0) # Move to the beginning of document
        r = xtika(files)
        print("--- Text Extraction with OCR Took %s seconds ---" % abs(round(sttime - fttime,2)))
    else:
        print("--- Text Extraction Took %s seconds ---" % abs(round(sttime - fttime,2)))
    #print(r.text)
    
    # or (mimetype == 'application/vnd.ms-excel') or (mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if len(r.text.strip())==0:
        quit()
        
    t = nlpbuddy(r.text)
    print("--- Text Summarization Took %s seconds ---" % abs(round(snltime - fnltime,2)))
   
    a = t.json()    
    b = klassify(a['summary'])
    c = b.json()
    slabel = str(c['label'])
    print("--- ML Text Classification Took %s seconds ---" % abs(round(sktime - fktime,2)))
    for key, value in dict.items():
        if slabel == key:
            print("Suggested Records Schedule: " + slabel + " - " + value)  
            
    #pisplay top 3 categories
    from collections import Counter
    d = Counter(c['scores'])
    print('Recommended Top 3 Labels')
    for k,v in d.most_common(3):
        print('%s: Score %i' % (k,v))
    
    size = fin.seek(0,2)
    fin.close()
    
    #print total processing time, and size of document
    print('Total Time Took to Process this Document of %s bit: %i Seconds' % (size, abs(sttime - fktime)))
    
    #print summary
    print("Here's the summary: ")
    print(a['summary'][:400])

    #print keywords
    print("Here are some keywords: ")
    print(a['keywords'][:400])
