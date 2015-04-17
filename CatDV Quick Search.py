import sys
import Tkinter as tk
import ttk 
import tkMessageBox
import requests
import json
import logging

sys.path.insert(0, '../py-catdv') # IV local
sys.path.insert(0, '../Py-CatDV')
from pycatdv import Catdvlib

logging.basicConfig(filename='CDVQsErr.log', level=logging.ERROR,
	format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)



cdv = Catdvlib()

#external access
#cdv.url = "http://mam.intervideo.co.uk:8080/api/4"

def c_login():
	try:
		usr = usernm.get()
		pwd = passwrd.get()
		logger.info('Start access to CatDV API')
		auth = cdv.set_auth(str(usr), str(pwd))
		key = cdv.get_session_key()
		if key:
			result.insert(END, "Login successful")
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
	entry = str(term.get())
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
						result.insert(END, i['userFields']['U7'] + '    ' + 
							i['name'])       
					else:
						count += 1
						result.insert(END, i['name'])
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
	result.insert(END, "Attempting login...")
	c_login()
	return

def clear_text():
	result.delete(0, END)

def delete_session():
	"""HTTP delete call to the API"""
	clear_text()
	logout = cdv.delete_session()
	if logout.status_code == 200:
		result.insert(END, "You have logged out.")
	else:
		result.insert(END, "There was an error logging out.")
	return # requests.delete(cdv.url + '/session')

def about():
	tkMessageBox.showinfo("CatDV QuickSearch 1.0b",
		"\nCatDV QuickSearch\n"
		"\nCreated by E.Cudjoe"
		"\nVersion 1.0b")
		#"\nCopyright " + "\u00A9" + " 2014-2015 E.cudjoe"
		#"\nhttps://github.com/edsondudjoe")


class QS(tk.Frame):
	def __init__(self, master):
		tk.Frame.__init__(self, master)
		self.login_frame = tk.Frame(master)
		self.search_frame = tk.Frame(master)
		self.result_frame = tk.Frame(master)
		self.bottom_frame = tk.Frame(master)
		
		self.login_frame.grid(sticky=W, padx=5, pady=5)
		self.search_frame.grid(sticky=W, padx=5, pady=5)
		self.result_frame.grid(sticky=W, padx=5, pady=5)
		self.bottom_frame.grid(sticky=S+E, padx=5, pady=5)		

		self.create_menubar()
		self.create_variables()
		self.create_widgets()
		self.grid_widgets()

	######## MENU BAR #########
	def create_menubar():

		self.menubar = tk.Menu(self.master)
		self.filemenu = tk.Menu(self.menubar, tearoff=0,)
		root.config(menu=self.menubar)

		# File
		self.menubar.add_cascade(label="File", menu=self.filemenu)
		self.filemenu.add_command(label="Login", command=c_login)
		self.filemenu.add_command(label="Search", command=query)
		# File > Export
		self.exportmenu = tk.Menu(self.filemenu, tearoff=0)
		self.filemenu.add_cascade(label="Export", menu=self.exportmenu,
			state="disabled")
		self.exportmenu.add_command(label="as Spreadsheet")
		self.exportmenu.add_command(label="as Text")
		# File
		self.filemenu.add_command(label="Print", state="disabled")
		self.filemenu.add_command(label="Clear", command=clear_text)
		self.filemenu.add_command(label="Logout", command=delete_session)
		self.filemenu.add_command(label="Quit", command=login.quit)

		# Edit
		self.editmenu = tk.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="Edit", menu=self.editmenu)
		self.editmenu.add_command(label="Select All", state="disabled")
		self.editmenu.add_command(label="Copy", state="disabled")

		# Help
		self.helpmenu = tk.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="Help", menu=self.helpmenu)
		self.helpmenu.add_command(label="About", command=about)

	def create_variables():
		self.username = StringVar() 
		self.password = StringVar()
		self.term = StringVar() 

	def create_widgets():
		self.usrname_label = ttk.Label(login_frame, text="Username: ")
		self.usrname_entry = ttk.Entry(login_frame, textvariable=self.username)
		self.password_label = ttk.Label(login_frame, text="Password: ")
		self.password_entry = ttk.Entry(
			login_frame, textvariable=self.password,show="*")
		self.password_entry.bind("<Return>", enter_login)
		self.login_btn = ttk.Button(login_frame, text="LOGIN", command=c_login)
		self.logout_btn = ttk.Button(login_frame, text="LOG OUT",
			command=delete_session)

		self.clip = ttk.Entry(search_frame, width="90", textvariable=self.term)
		self.clip.bind("<Return>", enter_query)
		self.search_btn = ttk.Button(search_frame, text="SEARCH", command=query)
		self.scrollbar = ttk.Scrollbar(result_frame)
		self.scrollbar.config(command=self.result.yview)
		self.result = Listbox(result_frame, bg='grey', width=100, height=30)
		self.result.config(yscrollcommand=self.scrollbar.set)
		self.clr_btn = ttk.Button(bottom_frame, text="Clear", command=clear_text)
		self.quit_button = ttk.Button(bottom_frame, text="QUIT", command=login.quit)

	def grid_widgets():
		self.usrname_label.grid(row=0, column=0)
		self.usrname_entry.grid(row=0, column=1, padx=2)
		self.password_label.grid(row=0, column=2, padx=2)
		self.password_entry.grid(row=0, column=3, padx=2)
		self.login_btn.grid(row=0, column=4, padx=2)
		self.logout_btn.grid(row=0, column=5, padx=2)
		self.clip.grid(row=0, column=0, sticky=E, padx=2)
		self.search_btn.grid(row=0, column=1, sticky=E, padx=2)
		self.scrollbar.grid(column=1, sticky=N+S+W)
		self.result.grid(row=0, column=0)
		self.clr_btn.grid(row=1, column=0, sticky=E, pady=2, padx=2)
		self.quit_button.grid(row=1, column=1, sticky=E, pady=2, padx=2)




root = tk.Tk()
app = QS(master=root)
root.title('CatDV QuickSearch')
root.geometry('500x500+200+100')


app.mainloop()
#root.destroy()
