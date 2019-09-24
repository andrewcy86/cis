from services import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from collections import Counter
import mimetypes

class Base(tk.Frame):
	
	dict = {
	'104-008-02_1035_d' : "Short-term environmental program and project records",
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
        'Encrypted' : None,
        '304-107_1021_a' : "Historically significant planning and resource allocation records",
        '108-205-03_1035_c' : "Routine environmental program and project records",
        '108-025-08_1044_d' : "Short-term compliance and enforcement records",
        '301-091_1016_c' : "Routine controls and oversight records",
        '301-093_1006_b' : "Other administrative management records",
        '306-114_1023_c' : "Nonfinal rulemakings and state standards records",
        '317-260_1025_b' : "Other legal services records"
        }

	def __init__(self, master):
		super().__init__(master)
		self.master = master
		self.master.title('CIS Application')
		self.master.resizable(0,0) 	
		#self.master.geometry('480x300') #width-height
		
		self.filename = ''
		self.schedule_list = ['','','']
		self.summary = ''
		self.keywords = ''
		self.information = '' 
		self.fin = bin
		self.files = {}
		self.recordlabel = ''

		#main containers
		self.top_box = tk.Frame(self.master, bd=1)
		self.summary_box = tk.LabelFrame(self.master, text='Summary', padx=5, pady=5)
		self.keywords_box = tk.LabelFrame(self.master, text='Keywords', padx=5, pady=5)
		self.info_box = tk.LabelFrame(self.master, text='Information', padx=5, pady=5)
		
		
		self.top_box.grid(row=0, sticky="nsew")
		self.summary_box.grid(row=3, sticky='nsew')
		self.keywords_box.grid(row=2, sticky='nsew')
		self.info_box.grid(row=1, sticky='nsew')
		
		
		# widgets for the top_box
		self.top_box.grid_rowconfigure(1, weight=1)
		self.top_box.grid_columnconfigure(2, weight=1)

		self.upload_button = tk.Button(self.top_box, text="Upload")
		self.upload_button.grid(row=0, column=0)
		
		self.boxlabel = tk.Label(self.top_box, text='Recommended Schedules')
		self.boxlabel.grid(row=0, column=1)	
		self.schedule_box = ttk.Combobox(self.top_box, values=self.schedule_list, state='readonly')
		self.schedule_box.current(0)
		self.schedule_box.grid(row=1, column=1)

		self.validate_button = tk.Button(self.top_box, text="Validate")
		self.validate_button.grid(row=0, column=2)

		#text display for summary, keywords, info
		self.summary_message = tk.Label(self.summary_box, text=self.summary, anchor='w', justify='left')
		self.keywords_message = tk.Label(self.keywords_box, text=self.keywords, anchor='w', justify='left')
		self.info_message = tk.Label(self.info_box, text=self.information, anchor='w', justify='left')

		self.summary_message.pack(fill='both')
		self.keywords_message.pack(fill='both')
		self.info_message.pack(fill='both')
		
		#bind function to click
		self.upload_button.bind('<Button-1>', self.update_text)
		
		#bind resizing, might not need
		self.master.bind('<Configure>', self.update_mess)
		#self.info_box.bind('<Button-1>', self.speak)
		
	def update_text(self, event):
		self.filename =  filedialog.askopenfilename(parent=root,initialdir="/home/liet/Desktop",title='Please select a file to scan')
		
		#run voice command here
		self.fin = open(self.filename, 'rb')
		self.files = {'files':self.fin}

		self.mimetype = mimetypes.MimeTypes().guess_type(self.filename)[0]
		self.summary_message.config(text=self.mimetype)

	
		e0,t0 = tika(self.files)
		
		# or (mimetype == 'application/vnd.ms-excel') or (mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		
		eseconds = abs(round(t0,2))
		self.information = 'Text Extraction Took ' + str(eseconds) + ' seconds' + '\n'
		
		if len(e0.text.strip()) == 0 and self.mimetype =='application/pdf':
			self.fin.seek(0)
			self.files = {'files':self.fin}
			e0,t0 = xtika(self.files)
			eseconds = abs(round(t0,2))
			self.information = 'Text Extraction with OCR Took ' + str(eseconds) + ' seconds' + '\n'

		#run voice command here 
		#if len(r.text.strip())==0: quit()

		e1,t1 = nlpbuddy(e0.text)
		#test function self.summary_message.config(text='')
		
		#tested up to here ----------------------------------
		#run voice command here
    		e2,t2 = klassify(e1.json()['summary'])
		
		#run voice command here
		d = Counter(e2.json()['scores'])
		self.schedule_list.clear()
		
		for k,v in d.most_common(3):
        		for label, desc in dict.items():
				#can be replaced with API Query builder TODO 
            			if label == k:
					self.schedule_list.append(label + ',' + desc + ', ' + 'score ' +v)
				else:
			    		self.schedule_list.append(k + ', ' + v)
		size = self.fin.seek(0,2)
		self.fin.close()
		
		sseconds = abs(round(t1,2))
		cseconds = abs(round(t2,2))

		self.information += 'Document Summarization Took ' + str(cseconds) + ' seconds' + '\n'
		self.information += 'Classification Took ' + str(cseconds) + ' seconds' + '\n'
		self.information += 'Total Time took to process of ' + str(size) + ' bits: ' + str(abs(round(t0+t1+t2,2))) + ' seconds'
		#run voice command here

		self.summary = e1.json()['summary']
		self.keywords = e1.json()['Keywords']


		self.summary_message.config(text=self.summary)
		self.keywords_message.config(text=self.keywords)
		self.info_message.config(text=self.information)



	#update the message box sizze
	def update_mess(self,event):
		self.info_message.config(width=self.master.winfo_width())
		self.summary_message.config(width=self.master.winfo_width())
		self.keywords_message.config(width=self.master.winfo_width())
		#self.master.update()

		

if __name__ == "__main__":

	
	#start the voice service first
	root = tk.Tk()
	Base(master=root)
	root.mainloop()


