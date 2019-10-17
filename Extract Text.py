import requests
import os

#default path to save records
default = 'C:/Users/ECMS_Test04/Desktop/extract'

fpl = []
filterout = ['openxml','excel','xls', 'spreadsheet']
fail = []
failtype = []

#get fileplan name from path /fileplan/folder/file    
def getFileplan(path):
    t = path.replace('\\','/')
    l = t.split('/')
    n = len(l)
    return l[n-3], l[-1]

#create containing folder, write the result text to the folder
def writefile(text,path):
    foldern, filen = getFileplan(path) 
    d1 = os.path.join(default,foldern)

    #create the folder if not already exist
    if foldern not in fpl:
        fpl.append(foldern)
        try:
            if not os.path.exists(d1):
                os.makedirs(d1)
        except OSError:
            pass

    #write the text to file
    d2 = os.path.join(d1, filen + '.txt')
    f = open(d2,'w')
    f.write(text)
    f.close()

#cleanup
def cleantext(text):
    p = re.compile(r'<.*?>')
    text = p.sub('', text)
    
    
#build file queue             
def buildq(rootdir, genfile = 'no'):
    qq = []
    for (root, dirs, files) in os.walk(rootdir, topdown=False):
        if len(files) > 0:
            for file in files:
                qq.append(os.path.join(root,file))

    if genfile.lower() == 'yes':
        with open('folderQ.txt', 'wt') as folderq:
            for i in qq:
                folderq.write(i)

        folderq.close()

    return qq

#detect mimetype using tika
def detect(files):
    
    url = 'https://ecms-cis-tika.edap-cluster.com/detect/stream'
    headers = {'Cache-Control': 'no-cache', 'Content-Type': "false"}
    r = requests.put(url, files=files, headers = headers)
    return r.text

#extract text with tika
#def tika(files, ftype=''):
    url = 'https://ecms-cis-tika.edap-cluster.com/tika'
    if len(ftype) == 0:
            headers = {'Cache-Control': 'no-cache'}
    else:
            headers = {'Cache-Control': 'no-cache', 'Content-Type': ftype}

    r = requests.put(url, files=files, headers = headers)
    return r

def tika(files):
    url = 'https://ecms-cis-tika.edap-cluster.com/tika/form'
    headers = {'Cache-Control': 'no-cache'}
    r = requests.post(url, files=files, headers = headers)
    return r

#extract text with ocrtika
def xtika(files):
    url = 'https://ecms-cis-tika.edap-cluster.com/tika'
    headers = {'Content-Type' : 'application/pdf', 'X-Tika-PDFOcrStrategy': 'ocr_only', 'Cache-Control': 'no-cache'}
    r = requests.put(url, files=files, headers = headers) 
    return r

def checkvalid(mime):
    for i in filterout:
        if i in mime:
            return 0

    return 1

#OCR PDF
def cleanse(data):
    return re.sub('[^0-9a-zA-Z]+', ' ', data)

#html and xml
from bs4 import BeautifulSoup

def striphtml(data):
    p = re.compile(r'<.*?>')    
    return p.sub('', data)

def cleanMe(html):
    soup = BeautifulSoup(html) # create a new bs4 object from the html data loaded
    for script in soup(["script", "style"]): # remove all javascript and stylesheet code
        script.extract()
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    for ch in ['\\a','\\b', '\\t', '\\n', '\\v', '\\f', '\\r', '\\xe2', '\\x80', '\\xc2', '\\xb7', '\\x9c', '\\x9d', '\\x93']:
        if ch in text:
            text=text.replace(ch,"")
    text = re.sub(r'(.*)/USEPA/US@EPA',r'', text)
    text = re.sub(r'[^\x00-\x7f]',r'', text)
    bad_chars = [';', ',', '*', '\'', '\"', '\\', '/']
    rx = '[' + re.escape(''.join(bad_chars)) + ']'
    text = re.sub(rx, '', striphtml(text))

    return text

#xml only
def xmlclean(text):
    try:
        p = text.find('EPA Official Record') + 19
        return text[p:-1]
    except:
        return text
    

def make(path):
    fin = open(path, 'rb')
    return {'files':fin}, fin

def writefail(l):
    f = open('failed.txt','a')
    for i in l:
        f.write(i[0] + ', ' + i[1] +'\n')
    f.close()
    
if __name__ == "__main__":

    from tkinter import filedialog
    from tkinter import *
    root = Tk()
    root.dirname = filedialog.askdirectory(parent=root,initialdir="C:/Users/ECMS_Test04/Documents/Records File",title='Please select a directory to scan')
    TheQ = buildq(root.dirname)
    print('TheQ Contains Your File Queue')
    root.destroy()

    def process(q):
        for i in q:
            fin = open(i,'rb')
            files = {'files':fin}
            mime = detect(files)
            fin.seek(0)
            
            print(mime)
            
            #filters excel
            if checkvalid(mime) == 0:
                print('invalid')
                fin.close()
                continue

            else:
                resp = tika(files)
                content = resp.text
                c=content
                #print('waiting respond')
                
                if resp.status_code == 200 and 'pdf' in mime:
                    fin.seek(0)
                    if len(resp.text.strip()) == 0:
                        print('ocring')
                        resp = xtika(files)
                        a = resp
                        writefile(cleanse(resp.text),i)
                        fin.close()
                        continue

                if 'xml' in mime:
                    content = xmlclean(content)
                    b=content
                    
                if resp.status_code != 200:
                    print('not supported')
                    fail.append([i,mime])
                    fin.close()
                    continue
                if 'LDF' in i:
                    print('not supported ldf')
                    fail.append([i,mime])
                    fin.close()
                    continue

                writefile(cleanMe(content),i)
                fin.close()
                
    #f = open(TheQ[104],'rb')
    #files = {'files':f}
    #r = tika2(files)
    #make changes here
    #process(TheQ[0:2000])
    #writefail(fail)
    #process(TheQ[2000:4000])
    #writefail(fail)
    process(TheQ[5069:8000])
    writefail(fail)
