from Tkinter import *
import ttk as tk
import tkMessageBox
import requests
import json
from CatDVlib import Cdvlib

root = Tk()
root.title('CatDV QuickSearch')
cdv = Cdvlib()
#cdv.url = "http://mam.intervideo.co.uk:8080/api/4"

def c_login():
	try:
		usr = usernm.get()
		pwd = passwrd.get()
		auth = cdv.url + "/session?usr=" + str(usr) + "&pwd=" + str(pwd)
		response = requests.get(auth, timeout=5)
		data = json.loads(response.text)
		cdv.key = data['data']['jsessionid']
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
	entry = term.get()
	res = requests.get(cdv.url + "/clips;jsessionid=" + cdv.key + "?filter=and"
		"((clip.name)like({}))&include=userFields".format(str(entry)))
	data = json.loads(res.text)
	for i in data['data']['items']:
		try:
			if i['userFields']['U7']:
				count += 1
				result.insert(END, i['userFields']['U7'] + '  ' + i['name'])        
			else:
				count += 1
				result.insert(END, i['name'])
		except KeyError:
			pass
	else:
		if count == 0:
			tkMessageBox.showwarning("", "No files found.")

def clear_text():
	result.delete(0, END)

def deleteSession():
	"""HTTP delete call to the API"""
	clear_text()
	result.insert(END, "You have logged out.")
	return requests.delete(cdv.url + '/session')


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

######## USER LOGIN #######
usrn = tk.Label(login, text="username: ")
usrn.grid(row=0, column=0)

usernm = StringVar() 
usr_ent = tk.Entry(login, textvariable=usernm)
usr_ent.grid(row=0, column=1)

pwd = tk.Label(login, text="password: ")
pwd.grid(row=0, column=2)

passwrd = StringVar()
pwd_ent = tk.Entry(login, textvariable=passwrd, show="*")
pwd_ent.grid(row=0, column=3)

login_btn = tk.Button(login, text="LOGIN", command=c_login)
login_btn.grid(row=0, column=4)

logout_btn = tk.Button(login, text="LOG OUT", command=deleteSession)
logout_btn.grid(row=0, column=5)

######## USER SEARCH ENTRY ######
term = StringVar() 
clip = tk.Entry(usr_search, width="90", textvariable=term)
clip.grid(row=0, column=0, sticky=E)

search_btn = tk.Button(usr_search, text="SEARCH", command=query)
search_btn.grid(row=0, column=1, sticky=E)

####### RESULTS ###########
scrollbar = tk.Scrollbar(res_list)
scrollbar.grid(column=1, sticky=N+S+W)

result = Listbox(res_list, bg='grey', width=100, height=30)
result.grid(row=0, column=0)

scrollbar.config(command=result.yview)
result.config(yscrollcommand=scrollbar.set)

clr_btn = tk.Button(util_btns, text="Clear", command=clear_text)
clr_btn.grid(row=1, column=0, sticky=E)

button = tk.Button(util_btns, text="QUIT", command=login.quit)
button.grid(row=1, column=1, sticky=E)


#fileMenu = Menu(root, tearoff=0)
#fileMenu.add_command(label="Exit")
#root.add_cascade(label="File", menu=fileMenu)

root.mainloop()
root.destroy()
