import sys
import Tkinter as tk
import ttk 
import tkMessageBox
import requests
import json
import logging
import tkFont

sys.path.insert(0, '../py-catdv') # IV local
sys.path.insert(0, '../Py-CatDV')
from pycatdv import Catdvlib

logging.basicConfig(filename='CDVQsErr.log', level=logging.ERROR,
	format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)



cdv = Catdvlib()

#external access
cdv.url = "http://mam.intervideo.co.uk:8080/api/4"

def c_login():
	try:
		usr = app.username.get()
		pwd = app.password.get()
		logger.info('Start access to CatDV API')
		auth = cdv.set_auth(str(usr), str(pwd))
		key = cdv.get_session_key()
		if key:
			app.result.insert(END, "Login successful")
			logger.info('Login successful')
	except TypeError:
		tkMessageBox.showwarning("Login Error", "You provided incorrect login"
		" details.\nPlease check and try again.")
		logger.error('Incorrect user login', exc_info=True)
	except requests.exceptions.ConnectTimeout as e:
		tkMessageBox.showwarning("Server Error", "The server connection"
			" timed-out.")
		logger.error('Server timed-out', exc_info=True)
	except requests.exceptions.ConnectionError as e:
		tkMessageBox.showwarning("Connection Error",'\nCan\'t access the API.'
			' Please check the if CatDV server is working.')
		logger.error('Server possibly not connected.', exc_info=True)
	except Exception, e:
		tkMessageBox.showwarning("","There was an error accessing the CatDV"
		" Server.")
		logger.error('Server error', exc_info=True)


def query():
	count = 0
	entry = str(app.term.get())
	if entry:
		try:
			res = requests.get(cdv.url + "/clips;jsessionid=" + cdv.key + 
				"?filter=and((clip.name)like({}))&include=userFields".format(
					entry))
			data = json.loads(res.text)
			clear_text()
			for i in data['data']['items']:
				try:
					if i['userFields']['U7']:
						count += 1
						app.result.insert(END, i['userFields']['U7'] + ' '*5 + 
							i['name'] + ' '*7 + '*' + i['notes'])       
					else:
						count += 1
						app.result.insert(END, i['name'])
				except TypeError, e: 
					print("File not on LTO: {}".format(i['name']))
				except KeyError:
					pass
			else:
				if count == 0:
					raise ValueError
		except ValueError: 
			tkMessageBox.showwarning("", "No files found.")
	else:
		tkMessageBox.showwarning("", "Enter name of the title in the search" 
			" bar")

def enter_query(event):
	query()
	return 

def enter_login(event):
	print "logging in..."
	app.result.insert(END, "Attempting login...")
	c_login()
	return

def clear_text():
	app.result.delete(0, END)

def delete_session():
	"""HTTP delete call to the API"""
	clear_text()
	logout = cdv.delete_session()
	if logout.status_code == 200:
		app.result.insert(END, "You have logged out.")
	else:
		app.result.insert(END, "There was an error logging out.")
	return # requests.delete(cdv.url + '/session')

def about():
	tkMessageBox.showinfo("CatDV QuickSearch 1.0b",
		"\nCatDV QuickSearch\n"
		"\nCreated by E.Cudjoe"
		"\nVersion 1.0.1b"
		#"\nCopyright " + "\u00A9" + " 2014-2015 E.cudjoe"
		"\nhttps://github.com/edsondudjoe")

# Tkinter grid maanagement and listbox commands.
N = tk.N
S = tk.S
E = tk.E
W = tk.W
END = tk.END



class QS(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent

		self.parent.columnconfigure(0, weight=4)
		self.parent.rowconfigure(2, weight=4)
		
		self.login_frame = tk.Frame(parent)
		self.search_frame = tk.Frame(parent)
		self.result_frame = tk.Frame(parent)
		self.bottom_frame = tk.Frame(parent)
		
		self.login_frame.grid(row=0, sticky=W+E, padx=5, pady=10)
		self.search_frame.grid(row=1, sticky=W+E, padx=5, pady=10)
		self.result_frame.grid(row=2, sticky=N+S+W+E, padx=5, pady=10)
		self.bottom_frame.grid(row=3, sticky=S+E, padx=5, pady=10)

		self.result_frame.rowconfigure(0, weight=4)
		self.result_frame.columnconfigure(0, weight=4)		

		self.create_menubar()
		self.create_variables()
		self.create_widgets()
		self.grid_widgets()

	######## MENU BAR #########
	def create_menubar(self):

		self.menubar = tk.Menu(self.master)
		self.filemenu = tk.Menu(self.menubar, tearoff=0,)
		root.config(menu=self.menubar)

		# File
		self.menubar.add_cascade(label="File", menu=self.filemenu)
		self.filemenu.add_command(label="Login", command=c_login)
		self.filemenu.add_command(label="Search", command=query)
		# File > Export
		#self.exportmenu = tk.Menu(self.filemenu, tearoff=0)
		#self.filemenu.add_cascade(label="Export", menu=self.exportmenu,
		#	state="disabled")
		#self.exportmenu.add_command(label="as Spreadsheet")
		#self.exportmenu.add_command(label="as Text")
		# File
		#self.filemenu.add_command(label="Print", state="disabled")
		self.filemenu.add_command(label="Clear", command=clear_text)
		self.filemenu.add_command(label="Logout", command=delete_session)
		self.filemenu.add_command(label="Quit", command=root.quit)

		# Edit
		#self.editmenu = tk.Menu(self.menubar, tearoff=0)
		#self.menubar.add_cascade(label="Edit", menu=self.editmenu)
		#self.editmenu.add_command(label="Select All", state="disabled")
		#self.editmenu.add_command(label="Copy", state="disabled")

		# Help
		self.helpmenu = tk.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="Help", menu=self.helpmenu)
		self.helpmenu.add_command(label="About", command=about)

	def create_variables(self):
		self.username = tk.StringVar() 
		self.password = tk.StringVar()
		self.term = tk.StringVar() 

	def create_widgets(self):
		self.usrname_label = ttk.Label(self.login_frame, text="Username: ")
		self.usrname_entry = ttk.Entry(self.login_frame, textvariable=self.username)
		self.password_label = ttk.Label(self.login_frame, text="Password: ")
		self.password_entry = ttk.Entry(
			self.login_frame, textvariable=self.password,show="*")
		self.password_entry.bind("<Return>", enter_login)
		self.login_btn = ttk.Button(self.login_frame, text="LOGIN", command=c_login)
		self.logout_btn = ttk.Button(self.login_frame, text="LOG OUT",
			command=delete_session)

		self.clip = ttk.Entry(self.search_frame, width="90", textvariable=self.term)
		self.clip.bind("<Return>", enter_query)
		self.search_btn = ttk.Button(self.search_frame, text="SEARCH", command=query)
		
		m_font = tkFont.Font(root=self.result_frame, size=14)
		self.scrollbar = ttk.Scrollbar(self.result_frame)
		self.u_scrollbar = ttk.Scrollbar(self.result_frame, orient='horizontal')
		self.result = tk.Listbox(self.result_frame, bg='grey', width=100, height=20)
		self.result.config(xscrollcommand = self.u_scrollbar.set,
			yscrollcommand=self.scrollbar.set, font=m_font)
		self.scrollbar.config(command=self.result.yview)
		self.u_scrollbar.config(command=self.result.xview)
		
		self.clr_btn = ttk.Button(self.bottom_frame, text="Clear", command=clear_text)
		self.quit_button = ttk.Button(self.bottom_frame, text="QUIT", command=root.quit)

	def grid_widgets(self):
		self.usrname_label.grid(row=0, column=0)
		self.usrname_entry.grid(row=0, column=1, padx=2)
		self.password_label.grid(row=0, column=2, padx=2)
		self.password_entry.grid(row=0, column=3, padx=2)
		self.login_btn.grid(row=0, column=4, padx=2)
		self.logout_btn.grid(row=0, column=5, padx=2)

		self.clip.grid(row=0, column=0, columnspan=4, sticky=E, padx=2) #colspan
		self.search_btn.grid(row=0, column=5, sticky=E, padx=2)
		self.scrollbar.grid(column=5, sticky=N+S+W)
		self.u_scrollbar.grid(row=1, sticky=E+W+S)
		self.result.grid(row=0, column=0, columnspan=4, sticky=N+S+E+W)
		
		self.clr_btn.grid(row=0, column=0, sticky=E, pady=2, padx=2)
		self.quit_button.grid(row=0, column=1, sticky=E, pady=2, padx=2)




root = tk.Tk()
root.title('CatDV QuickSearch')
#root.update()
root.minsize(root.winfo_width(), root.winfo_height())

app = QS(root)

root.mainloop()
#root.destroy()
