import sys
from Tkinter import *
import ttk as tk
import tkMessageBox
import requests
import json
sys.path.insert(0, '../py-catdv') # IV local
#sys.path.insert(0, '../Py-CatDV')
from pycatdv import Catdvlib

root = Tk()
root.title('CatDV QuickSearch')
cdv = Catdvlib()

#external access
#cdv.url = "http://mam.intervideo.co.uk:8080/api/4"

def c_login():
	try:
		usr = usernm.get()
		pwd = passwrd.get()
		
		auth = cdv.set_auth(str(usr), str(pwd))
		key = cdv.get_session_key()
		if key:
			result.insert(END, "Login successful")
	except TypeError:
		tkMessageBox.showwarning("Login Error", "You provided incorrect login details.\n"
			"Please check and try again.")
	except requests.exceptions.ConnectTimeout as e:
		tkMessageBox.showwarning("Server Error", "The server connection timed-out.")
		print(e)
	except requests.exceptions.ConnectionError as e:
		tkMessageBox.showwarning("Connection Error",'\nCan\'t access the API.'
			' Please check you have the right domain address')
		print(e)
	except ValueError:
		tkMessageBox.showwarning("","There was an error accessing the CatDV Server.")

def query():
	count = 0
	entry = str(term.get())
	if entry:
		try:
			res = requests.get(cdv.url + "/clips;jsessionid=" + cdv.key + "?filter=and"
				"((clip.name)like({}))&include=userFields".format(entry))
			data = json.loads(res.text)
			clear_text()
			for i in data['data']['items']:
				try:
					if i['userFields']['U7']:
						count += 1
						result.insert(END, i['userFields']['U7'] + '    ' + i['name'])       
					else:
						count += 1
						result.insert(END, i['name'])
				except TypeError, e: # For files with no LTO number.
					print("File not on LTO: {}".format(i['name']))
				except KeyError:
					pass
			else:
				if count == 0:
					raise ValueError
				#tkMessageBox.showwarning("", "No files found.")
		except ValueError: # catches JSON errors where symbols have been entered.
			tkMessageBox.showwarning("", "No files found.")
	else:
		tkMessageBox.showwarning("", "Enter name of the title in the search bar")

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
	tkMessageBox.showinfo("Mortgage Monthly Payment Calculator",
		"\nCatDV QuickSearch beta\n\n"
		"\nCreated by E.Cudjoe"
		"\nVersion 1.0"
		"\nCopyright " + u"\u00A9" + " 2014-2015 E.cudjoe"
		"\nhttps://github.com/edsondudjoe")


main = tk.Frame(root)
main.grid()

login = tk.Frame(main)
login.grid(sticky=W, padx=5, pady=5)

usr_search = tk.Frame(main)
usr_search.grid(sticky=W, padx=5, pady=5)

res_list = tk.Frame(main)
res_list.grid(sticky=W, padx=5, pady=5)

util_btns = tk.Frame(main)
util_btns.grid(sticky=S+E, padx=5, pady=2)

######## MENU BAR #########
menubar = Menu(main)
filemenu = Menu(menubar, tearoff=0,)
root.config(menu=menubar)

# File
menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Login", command=c_login)
filemenu.add_command(label="Search", command=query)
# File > Export
exportmenu = Menu(filemenu, tearoff=0)
filemenu.add_cascade(label="Export", menu=exportmenu, state="disabled")
exportmenu.add_command(label="as Spreadsheet")
exportmenu.add_command(label="as Text")
# File
filemenu.add_command(label="Print", state="disabled")
filemenu.add_command(label="Clear", command=clear_text)
filemenu.add_command(label="Logout", command=delete_session)
filemenu.add_command(label="Quit", command=login.quit)

# Edit
editmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Edit", menu=editmenu)
editmenu.add_command(label="Select All", state="disabled")
editmenu.add_command(label="Copy", state="disabled")

# Help
helpmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About", command=about)


######## USER LOGIN #######
usrn = tk.Label(login, text="username: ")
usrn.grid(row=0, column=0)

usernm = StringVar() 
usr_ent = tk.Entry(login, textvariable=usernm)
usr_ent.grid(row=0, column=1, padx=2)

pwd = tk.Label(login, text="password: ")
pwd.grid(row=0, column=2, padx=2)

passwrd = StringVar()
pwd_ent = tk.Entry(login, textvariable=passwrd, show="*")
pwd_ent.bind("<Return>", enter_login)
pwd_ent.grid(row=0, column=3, padx=2)

login_btn = tk.Button(login, text="LOGIN", command=c_login)
login_btn.grid(row=0, column=4, padx=2)

logout_btn = tk.Button(login, text="LOG OUT", command=delete_session)
logout_btn.grid(row=0, column=5, padx=2)

######## USER SEARCH ENTRY ######
term = StringVar() 
clip = tk.Entry(usr_search, width="90", textvariable=term)
clip.bind("<Return>", enter_query)
clip.grid(row=0, column=0, sticky=E, padx=2)

search_btn = tk.Button(usr_search, text="SEARCH", command=query)
search_btn.grid(row=0, column=1, sticky=E, padx=2)

####### RESULTS ###########
scrollbar = tk.Scrollbar(res_list)
scrollbar.grid(column=1, sticky=N+S+W)

result = Listbox(res_list, bg='grey', width=100, height=30)
result.grid(row=0, column=0)

scrollbar.config(command=result.yview)
result.config(yscrollcommand=scrollbar.set)

clr_btn = tk.Button(util_btns, text="Clear", command=clear_text)
clr_btn.grid(row=1, column=0, sticky=E, pady=2, padx=2)

button = tk.Button(util_btns, text="QUIT", command=login.quit)
button.grid(row=1, column=1, sticky=E, pady=2, padx=2)

root.mainloop()
root.destroy()
