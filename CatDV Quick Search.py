import ConfigParser
import sys
import Tkinter as tk
import ttk
import tkMessageBox
import requests
import json
import logging
import threading
import tkFont
import tkFileDialog


sys.path.insert(0, '../py-catdv')  # IV local
sys.path.insert(0, '../Py-CatDV')
from pycatdv import Catdvlib

logging.basicConfig(filename='CDVQsErr.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)

Settings = ConfigParser.ConfigParser()
parse = ConfigParser.SafeConfigParser()

s_results = []
API_VERS = '4'

config = './QuickSearchConf.ini'
try:
    parse.readfp(open(config))
except IOError:
    pass

try:
    server_url = parse.get('url', 'url_address')
    print('Server URL: {}'.format(server_url))
    cdv = Catdvlib(server_url=server_url, api_vers=API_VERS)
    cdv.url = server_url
except ConfigParser.NoSectionError:
    pass


def c_login():
    """Login access to the CatDV database"""
    try:
        usr = app.username.get()
        pwd = app.password.get()
        logger.info('Start access to CatDV API')
        auth = cdv.set_auth(str(usr), str(pwd))
        key = cdv.get_session_key()
        if key:
            app.status.set("Login successful")
            logger.info('Login successful: KEY: {}'.format(cdv.key))
        else:
            raise TypeError
    except TypeError:
        tkMessageBox.showwarning("Login Error", "You provided incorrect login"
                                                " details.\nPlease check and "
                                                "try again.")
        logger.error('Incorrect user login', exc_info=True)
    except requests.exceptions.ConnectTimeout as e:
        tkMessageBox.showwarning("Server Error", "The server connection"
                                                 " timed-out.")
        logger.error('Server timed-out', exc_info=True)
    except requests.exceptions.ConnectionError as e:
        tkMessageBox.showwarning("Connection Error", '\nCan\'t access the API.'
                                                     '\nPlease check if you '
                                                     'have the right server '
                                                     'address and if the '
                                                     'CatDV server is working')
        logger.error('Server possibly not connected.', exc_info=True)
    except Exception, e:
        tkMessageBox.showwarning("", "There was an error accessing the CatDV"
                                     " Server.")
        logger.error('Server error', exc_info=True)


def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def query():
    count = 0
    entry = str(app.term.get())
    if entry:
        try:
            res = requests.get(
                'http://192.168.0.101:8080/api/4/clips;jsessionid=' + cdv.key +
                '?filter=or((clip.name)like({0}))or'
                '((clip.userFields[U7])like({0}))or'
                '((clip.clipref)like({0}))&include=userFields'.format(entry))
            data = json.loads(res.text)
            clear_text()
            for i in data['data']['items']:
                try:
                    if i['userFields']['U7']:
                        count += 1
                        if i['notes']:
                            size = sizeof_fmt(i['media']['fileSize'])
                            s_results.append((i['clipref'],
                                              i['name'],
                                              i['userFields']['U7'],
                                              size, i['notes']))
                            app.tree.insert("", count, text=str(count),
                                            values=(i['clipref'],
                                                    i['name'],
                                                    i['userFields']['U7'],
                                                    size,
                                                    i['notes']),)
                        else:
                            size = sizeof_fmt(i['media']['fileSize'])
                            s_results.append((i['clipref'],
                                              i['name'],
                                              i['userFields']['U7'],
                                              size))
                            app.tree.insert("", count, text=str(count),
                                            values=(i['clipref'],
                                                    i['name'],
                                                    i['userFields']['U7'],
                                                    size),)
                    else:
                        count += 1
                        app.result.insert(END, i['name'])
                except TypeError, e:
                    logger.error('Search error', exc_info=True)
                    print(e)
                except KeyError:
                    pass
            else:
                if count == 0:
                    raise ValueError
        except ValueError:
            tkMessageBox.showwarning("", "No files found")
        except AttributeError:
            tkMessageBox.showwarning("", "Log in to CatDV first")
    else:
        tkMessageBox.showwarning("", "Enter name of the title in the "
                                     "search bar")


def enter_query(event):
    q = threading.Thread(name="search_query", target=query)
    q.start()


def enter_login(event):
    app.status.set("Attempting login...")
    c_login()
    return


def export_text():
    """
    Once the user has defined a filename. This function will export
    their search results to a text file.
    """
    save_as = tkFileDialog.asksaveasfilename()
    save_as = save_as + '.txt'
    with open(save_as, 'w') as user_results:
        for r in s_results:
            for l in range(len(r)):
                user_results.write((r[l] + '\t' + '\n'))
        user_results.write('\n')
    app.status.set("File has been saved to : {}".format(save_as))


def clear_text():
    for i in app.tree.get_children():
        app.tree.delete(i)


def delete_session():
    """HTTP delete call to the API"""
    clear_text()
    logout = cdv.delete_session()
    if logout.status_code == 200:
        app.status.set("You have logged out.")
    else:
        app.status.set("There was an error logging out.")


def about():
    tkMessageBox.showinfo("CatDV QuickSearch 1.0b",
                          "\nCatDV QuickSearch\n"
                          "\nCreated by E.Cudjoe"
                          "\nVersion 1.5.7"
                          "\nhttps://github.com/edsoncudjoe")


def select_all(event):
    tree_items = app.tree.identify_row(event.y)
    print app.tree.item(item)


def search_btn_return(event):
    query()


def login_btn_handlr():
    c_login()
    app.login.destroy()


def login_return(event):
    c_login()
    app.login.destroy()

# Tkinter grid management and listbox commands.
N = tk.N
S = tk.S
E = tk.E
W = tk.W
END = tk.END


class QS(tk.Frame):
    """
    GUI that connects to the CatDV server api and returns clip
    results based on user entry
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.create_variables()
        self.login_window()

        self.parent.columnconfigure(0, weight=4)
        self.parent.rowconfigure(2, weight=4)
        self.parent.config(bg='#595959')

        self.login_frame = tk.LabelFrame(parent, bg='#595959',
                                         fg='#f5f5f5', text="Login",
                                         pady=3, padx=3, relief=tk.FLAT)
        self.search_frame = tk.LabelFrame(parent, bg='#595959',
                                          fg='#f5f5f5', text="Search",
                                          relief=tk.FLAT)
        self.result_frame = tk.LabelFrame(parent, bg='#595959',
                                          fg='#f5f5f5', text="Results",
                                          padx=1, relief=tk.FLAT)
        self.bottom_frame = tk.Frame(parent, bg='#595959')

        self.search_frame.grid(row=1, sticky=W + E, padx=2, pady=2)
        self.result_frame.grid(row=2, sticky=N + S + W + E, padx=5, pady=2)
        self.bottom_frame.grid(row=3, sticky=S + E, padx=5, pady=2)

        self.login_frame.columnconfigure(6, weight=1)
        self.result_frame.rowconfigure(0, weight=4)
        self.result_frame.columnconfigure(0, weight=4)

        self.create_menubar()
        self.create_widgets()
        self.grid_widgets()
        try:
            self.set_theme_colour(parse.get('theme', 'colour'))
        except:
            logger.warning('Unable to set colour for main window. check '
                           'config file')
            pass
        self.s = ttk.Style()
        self.s.theme_use('default')

    ######## MENU BAR #########
    def create_menubar(self):

        self.menubar = tk.Menu(self.parent)
        self.filemenu = tk.Menu(self.menubar, tearoff=0, )
        root.config(menu=self.menubar)

        # File
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Login", command=self.login_window)
        self.filemenu.add_command(label="Search", command=query)

        # File > Export
        self.exportmenu = tk.Menu(self.filemenu, tearoff=0)
        self.filemenu.add_cascade(label="Export results", menu=self.exportmenu)
        self.exportmenu.add_command(label="as Text", command=export_text)

        # File
        self.filemenu.add_command(label="Clear", command=clear_text)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Settings",
                                  command=self.settings_window)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Logout", command=delete_session)
        self.filemenu.add_command(label="Quit", command=self.on_exit)

        # Help
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.helpmenu.add_command(label="About", command=about)

    def create_variables(self):
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.term = tk.StringVar()
        self.cdv_server = tk.StringVar()
        self.status = tk.StringVar()


    def login_window(self):
        self.login = tk.Toplevel(self, width=250, height=250, padx=5,
                                 pady=5, bg='#595959')
        self.login.lift()
        self.login.title("CatDV QuickSearch Login")
        self.login.config(bg='#595959')
        self.login_fr = tk.Frame(self.login, padx=5, pady=5, bg='#595959')

        self.user_label = ttk.Label(self.login_fr, text="Username: ",
                                    justify=tk.LEFT, background='#595959',
                                    foreground='#ffffff')
        self.user_entry = ttk.Entry(self.login_fr, textvariable=self.username)
        self.pwd_label = ttk.Label(self.login_fr, text="Password: ",
                                   background='#595959', foreground='#f5f5f5')
        self.pwd_entry = ttk.Entry(
            self.login_fr, textvariable=self.password, show="*",
            justify=tk.LEFT)
        self.pwd_entry.bind("<Return>", login_return)
        self.cancel_login_btn = ttk.Button(self.login_fr, text='cancel',
                                           command=self.login.destroy)
        self.u_login_btn = ttk.Button(self.login_fr, text="login",
                                      command=login_btn_handlr)

        self.login_fr.grid()
        self.user_label.grid(row=0, column=0)
        self.user_entry.grid(row=0, column=1)
        self.pwd_label.grid(row=1, column=0)
        self.pwd_entry.grid(row=1, column=1, pady=2)
        self.cancel_login_btn.grid(row=2, column=0, sticky=E, pady=2)
        self.u_login_btn.grid(row=2, column=1, pady=2)


    def create_widgets(self):
        self.usrname_label = ttk.Label(self.login_frame, text="Username: ",
                                       background='#666666',
                                       foreground='#ffffff')
        self.usrname_entry = ttk.Entry(self.login_frame,
                                       textvariable=self.username)
        self.password_label = ttk.Label(self.login_frame, text="Password: ",
                                       background='#666666',
                                       foreground='#ffffff')
        self.password_entry = ttk.Entry(
            self.login_frame, textvariable=self.password, show="*")
        self.password_entry.bind("<Return>", enter_login)
        self.login_btn = ttk.Button(self.login_frame, text="LOGIN",
                                    command=c_login)
        self.login_btn.bind("<Return>", enter_login)
        self.logout_btn = ttk.Button(self.login_frame, text="LOG OUT",
                                     command=delete_session)

        self.clip = ttk.Entry(self.search_frame, width="150",
                              textvariable=self.term)
        self.clip.bind("<Return>", enter_query)
        self.search_btn = ttk.Button(self.search_frame, text="SEARCH",
                                     command=query)
        self.search_btn.bind("<Return>", search_btn_return)

        m_font = tkFont.Font(root=self.result_frame, size=14)
        self.result = tk.Listbox(self.login_frame, bg='grey', width=50,
                                 height=2)
        self.result.config(font=m_font)

        self.status_bar = tk.Label(self.parent, bg='#595959', fg='#f5f5f5',
                                   textvariable=self.status, relief=tk.SUNKEN,
                                   anchor=W, justify=tk.LEFT)

        # Treeview
        self.columns = ('Clip ID', 'Filename', 'IV Number', 'Size', 'Notes')
        self.tree = ttk.Treeview(self.result_frame, columns=self.columns,
                                 height=15, selectmode="browse")
        for col in self.columns:
            self.tree.heading(col, text=col)

        self.tree.column("#0", width=50)
        self.tree.column("Clip ID", width=120)
        self.tree.column("Filename", width=800)
        self.tree.column("IV Number", width=140)
        self.tree.column("Size", width=100)
        self.tree.column("Notes", width=250)

        self.tree.heading("Clip ID")
        self.tree.heading("Filename", command=lambda: self.treeview_sort(
            self.tree, "Filename", False))
        self.tree.heading("IV Number", command=lambda: self.treeview_sort(
            self.tree, "IV Number", False))
        self.tree.heading("Size", command=lambda: self.treeview_sort(
            self.tree, "Size", False))
        self.tree.heading("Notes", command=lambda: self.treeview_sort(
            self.tree, "Notes", False))

        self.tree_scrollbar = ttk.Scrollbar(self.result_frame,
                                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        self.clr_btn = ttk.Button(self.bottom_frame, text="Clear",
                                  command=clear_text)
        self.quit_button = ttk.Button(self.bottom_frame, text="QUIT",
                                      command=self.on_exit)

    def grid_widgets(self):
        self.usrname_label.grid(row=0, column=0)
        self.usrname_entry.grid(row=0, column=1, padx=2)
        self.password_label.grid(row=0, column=2, padx=2)
        self.password_entry.grid(row=0, column=3, padx=2)
        self.login_btn.grid(row=0, column=4, padx=2)
        self.logout_btn.grid(row=0, column=5, padx=2)

        self.clip.grid(row=0, column=0, columnspan=4, sticky=E, padx=2)
        self.search_btn.grid(row=0, column=5, sticky=E, padx=2)

        self.tree.grid(row=0, column=0)
        self.tree_scrollbar.grid(row=0, column=1, sticky=N + S)

        self.clr_btn.grid(row=0, column=0, sticky=E, padx=2)
        self.quit_button.grid(row=0, column=1, sticky=E, padx=2)

        self.status_bar.grid(row=4, column=0, ipady=4, ipadx=10, sticky=E+W+S)

    def treeview_sort(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: \
            self.treeview_sort(tv, col, not reverse))

    def settings_window(self):
        """
        Users can change location address of the CatDV server
        """
        self.s = tk.Toplevel(self, width=120, height=50, bg='#595959', padx=10,
                             pady=10)

        self.settings_entry_frame = tk.Frame(self.s, bg='#595959', pady=1,
                                             padx=1)
        self.theme_change_frame = tk.Frame(self.s, bg='#595959',
                                           pady=10, padx=10)
        self.settings_btns_frame = tk.Frame(self.s, bg='#595959', pady=3,
                                            padx=3)
        self.settings_entry_frame.grid(row=0)
        self.theme_change_frame.grid(row=2)
        self.settings_btns_frame.grid(row=3)

        self.s.wm_title("Settings")
        self.theme_values = ['firebrick1', 'sea green', 'DodgerBlue4',
                             'DarkGoldenrod1', 'gray83',
                             'hot pink', 'magenta4', 'DeepSkyBlue4', 'green4']
        self.server_address = ttk.Label(self.settings_entry_frame,
                                        text="Enter the full CatDV server "
                                             "Address including protocol"
                                             " and port number.\n\nExample:"
                                             " \'http://"
                                             "<ExampleDomainAddress>:8080\'\n",
                                        width=100,
                                        background='#595959',
                                        foreground='#f5f5f5')
        self.s_address_entry = ttk.Entry(self.settings_entry_frame,
                                         textvariable=self.cdv_server,
                                         width=100)
        self.sep = ttk.Separator(self.s, orient='horizontal')
        self.theme_lbl = tk.Label(self.theme_change_frame, text='Change '
                                                                'theme '
                                                                'colour:',
                                  background='#595959', foreground='#f5f5f5')
        self.choose_theme = tk.Spinbox(self.theme_change_frame,
                                       values=self.theme_values)
        self.apply_theme = ttk.Button(self.settings_btns_frame, text='Apply',
                                     command=lambda: self.theme_colour_handle(
                                         self.choose_theme.get()))
        self.cancel_settings = ttk.Button(self.settings_btns_frame,
                                          text="Cancel",
                                          command=self.s.destroy)
        self.confirm_setting = ttk.Button(self.settings_btns_frame,
                                          text="OK",
                                          command=self.save_settings)

        self.server_address.grid()
        self.s_address_entry.grid()
        self.sep.grid(row=1, pady=20, sticky=E+W)
        self.theme_lbl.grid(row=0, column=0)
        self.choose_theme.grid(row=0, column=1)
        self.apply_theme.grid(row=0, column=1)
        self.cancel_settings.grid(row=0, column=0)
        self.confirm_setting.grid(row=0, column=2)

        self.s_address_entry.bind('<Return>', self.save_settings_handle)
        try:
            self.set_settings_theme_colour(parse.get('theme', 'colour'))
        except:
            logger.warning('Unable to set colour for settings window. check '
                           'config file')
            pass

    def set_server_address(self):
        address = self.cdv_server.get()
        if address != '':
            if address.startswith('http://') or address.startswith('https://'):
                cdv.url = address
            else:
                tkMessageBox.showwarning("", "Server address should start with"
                                         " \'http://\' or \'https://\'")
            logger.info("Server url changed to {}".format(cdv.url))
        else:
            pass

        self.status.set("Server address set to: {}".format(cdv.url))
        self.s.destroy()

    def set_theme_colour(self, theme):
        self.theme_color = theme
        # Main window
        try:
            self.parent.config(bg='{}'.format(self.theme_color))
            self.search_frame.config(bg='{}'.format(self.theme_color))
            self.result_frame.config(bg='{}'.format(self.theme_color))
            self.bottom_frame.config(bg='{}'.format(self.theme_color))
            self.result.config(bg='{}'.format(self.theme_color))
            self.status_bar.config(bg='{}'.format(self.theme_color))

            # Login window
            self.login.config(bg='{}'.format(self.theme_color))
            self.login_fr.config(bg='{}'.format(self.theme_color))
            self.user_label.config(background='{}'.format(self.theme_color))
            self.pwd_label.config(background='{}'.format(self.theme_color))
            if self.theme_color == 'gray83':
                self.user_label.config(foreground='black')
                self.pwd_label.config(foreground='black')
                # self.usrname_label.config(foreground='black')
                # self.password_label.config(foreground='black')
                # self.login_frame.config(foreground='black')
                self.search_frame.config(foreground='black')
                self.result_frame.config(foreground='black')
                self.bottom_frame.config(foreground='black')
                self.status_bar.configure(fg='black')
        except Exception as e:
            logger.warning(e)

    def set_settings_theme_colour(self, theme):
        """Set colour for the settings window"""
        self.settings_theme_color = theme
        self.s.config(bg='{}'.format(self.settings_theme_color))
        self.settings_entry_frame.config(bg='{}'.format(
            self.settings_theme_color))
        self.theme_change_frame.config(bg='{}'.format(
            self.settings_theme_color))
        self.settings_btns_frame.config(bg='{}'.format(
            self.settings_theme_color))
        self.server_address.config(background='{}'.format(
            self.settings_theme_color))
        self.theme_lbl.config(background='{}'.format(
            self.settings_theme_color))
        if self.settings_theme_color == 'gray83':
            self.server_address.config(foreground='black')
            self.theme_lbl.config(foreground='black')

    def theme_colour_handle(self, theme):
        self.set_theme_colour(theme)
        self.set_settings_theme_colour(theme)

    def save_settings_handle(self, event):
        self.set_server_address()
        self.save_settings()

    def save_settings(self):
        self.set_server_address()
        self.conf = open('./QuickSearchConf.ini', 'w')
        Settings.add_section('theme')
        Settings.set('theme', 'colour', self.theme_color)
        Settings.add_section('url')
        Settings.set('url', 'url_address', cdv.url)
        Settings.write(self.conf)
        self.conf.close()
        self.s.destroy()

    def on_exit(self):
        if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
            try:
                delete_session()
                root.quit()
            except:
                root.quit()


root = tk.Tk()
root.title('CatDV QuickSearch')
root.update()
root.minsize(root.winfo_width(), root.winfo_height())

app = QS(root)

root.mainloop()


