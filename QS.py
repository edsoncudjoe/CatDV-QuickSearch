import Tkinter as tk
import ttk

class QS(tk.Frame):
	def __init__(self, master):
		tk.Frame.__init__(self, master, bd=3, bg='RED')
		self.top_frame = tk.Frame(master)
		self.middle_frame = tk.Frame(master)
		self.bottom_frame = tk.Frame(master)
		
		self.top_frame.grid(row=0)
		self.middle_frame.grid(row=1)
		self.bottom_frame.grid(row=2)		

		self.create_menubar()
		self.create_variables()
		self.create_widgets()
		self.grid_widgets()

	def create_menubar(self):
		self.menubar = tk.Menu(self.master)
		self.filemenu = tk.Menu(self.menubar, tearoff=0)
		root.config(menu=self.menubar)


		self.menubar.add_cascade(label="File", menu=self.filemenu)
		self.filemenu.add_command(label="Login")
		self.filemenu.add_command(label="Search")

	def create_variables(self):
		pass

	def create_widgets(self):
		self.hello_label = ttk.Label(self.bottom_frame, text='Hello World!')

	def grid_widgets(self):
		self.hello_label.grid(row=0, column=0)

if __name__ == '__main__':
	#QS.main()

	root = tk.Tk()
	app = QS(master=root)
	#root.iconbitmap('icon.ico')
	root.title('Quick Search')
	root.geometry('200x200+100+300')
	app.mainloop()