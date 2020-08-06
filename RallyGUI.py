import os
import re
import sys
from configparser import ConfigParser
from functools import partial
from tkinter import *
from tkinter import messagebox, ttk

from pyral import Rally, rallyWorkset

import pandas as pd
from frames.ConfigFrame import ConfigFrame
from frames.ExportFrame import ExportFrame
from frames.QuickReportsFrame import QuickReportsFrame
from frames.ReportFrame import ReportFrame
from RallyExportTool import RallyExportTool
from RallyReportTool import RallyReportTool


class BackgroundFrame(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Rally Reporting Tool v1.0")
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.pack(pady=10, padx=10)
       
        self.RALLY = None
        self.frames = {}
        self._frame = None
        self.config_object = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})

        path = os.path.dirname(sys.argv[0]) + "/config.ini"
        try:
            # print(os.path.dirname(os.path.abspath(__file__)) + "/config.ini")
            path = os.path.dirname(os.path.abspath(__file__)) + "/config.ini"
        except NameError:
            path = os.path.dirname(os.path.abspath(sys.argv[0])) + "/config.ini"
        self.config_object.read(path)
            
        # print(self.config_object.__dict__)
        self.RALLY_REPORTER = RallyReportTool(self.config_object)

        for x in [LoginFrame, MainFrame]:
            self.frames[x.__name__] = x(container, self)
            self.frames[x.__name__].grid(row=0, column=0, sticky="nsew")
        
        self._frame = self.frames["LoginFrame"]
        self._frame.tkraise()

    def show_frame(self, frame):
        if self._frame is not None:
            self._frame.destroy()
        self._frame = self.frames[frame]
        self.frames[frame].tkraise()

    def set_rally(self, rallyObject):
        self.RALLY = rallyObject
        if (self.config_object["CREDENTIALS"]["API_KEY"]):
            self.RALLY.set_api_key(self.config_object["CREDENTIALS"]["API_KEY"])

    #todo: if api key is set, go straight to main screen. otherwise, try credentials
    def init_rally(self, username, password):
        return self.RALLY.validate_login(username, password)
        

class LoginFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.label_username = Label(self, text="Username: ")
        self.label_password = Label(self, text="Password: ")

        self.entry_username = Entry(self)
        self.entry_password = Entry(self, show="*")

        self.label_username.grid(row=0, sticky=E)
        self.label_password.grid(row=1, sticky=E)
        self.entry_username.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)

        self.logbtn = Button(self, text="Login",
                             command=self._login_btn_clicked)
        self.logbtn.grid(columnspan=2)
        self.controller = controller
        self.pack()

    def check_api_auth(self):
        if (self.controller.config_object['CREDENTIALS']["API_KEY"]):
            print("Found API key: Initializing Rally API")
            self.controller.init_rally("", "")
            print("Logged in successfully")
            self.controller.show_frame("MainFrame")
            self.controller.frames["MainFrame"].load_data()

    def _login_btn_clicked(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        success = self.controller.init_rally(username, password)
        if success:
            print("Logged in successfully")
            self.controller.show_frame("MainFrame")
            self.controller.frames["MainFrame"].load_data()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

class MainFrame(ttk.Notebook):
    def __init__(self, master, controller):
        ttk.Notebook.__init__(self, master)
        self.export_frame = ExportFrame(self, controller, controller.config_object)
        self.report_frame = ReportFrame(self, controller, controller.config_object)
        self.config_frame = ConfigFrame(self, controller, controller.config_object)
        self.quickreports_frame = QuickReportsFrame(self, controller, controller.config_object)
        self.add(self.config_frame, text='Settings')
        self.add(self.export_frame, text='Import Custom Data')
        self.add(self.quickreports_frame, text='Quick Reports')
        self.add(self.report_frame, text='Generate Reports')
        self.grid(sticky='nsew')

    def load_data(self):
        self.export_frame.load_data()
        self.report_frame.load_data()
        self.quickreports_frame.load_data()

def main():

    proxy = "http://zproxy.newyorklife.com:9480"
    cert = "ZScalerRootCertificate-2048-SHA256.crt"

    os.environ['HTTPS_PROXY'] = proxy
    os.environ['https_proxy'] = proxy
    os.environ['HTTP_PROXY'] = proxy
    os.environ["NODE_EXTRA_CA_CERTS"] = cert

    

    root = BackgroundFrame()
    rally = RallyExportTool(root.config_object)
    root.set_rally(rally)

    windowWidth = root.winfo_reqwidth()

    windowHeight = root.winfo_reqheight()
    print("Width", windowWidth, "Height", windowHeight)

    # Gets both half the screen width/height and window width/height
    positionRight = int(root.winfo_screenwidth()/3 - windowWidth/2)
    positionDown = int(root.winfo_screenheight()/3 - windowHeight/2)

    # Positions the window in the center of the page.
    root.geometry("+{}+{}".format(positionRight, positionDown))

    root._frame.check_api_auth()
    root.mainloop()

if __name__ == "__main__":
    main()
