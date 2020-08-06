import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from configparser import ConfigParser
from .ListBuilderComponent import ListBuilderComponent


class ConfigFrame(Frame):

    def __init__(self, master, controller, config):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.master = master
        self.config_object = config

        self.config_object.read("config.ini")

        Label(self, text="API Key:").grid(row=0, column=0, sticky='e')
        api_key = StringVar(
            self, value=self.config_object['CREDENTIALS']['API_KEY'])
        api_key_text = Entry(self, textvariable=api_key, show="*")
        api_key_text.grid(row=0, column=1, sticky='w')
        
        Label(self, text="Export Directory").grid(row=1, column=0, sticky='e')

        export_dir = StringVar(
            self, value=self.config_object['CREDENTIALS']['EXPORT_DIRECTORY'])

        def update_directory():
            name = fd.askdirectory()
            export_dir.set(name)
            self.config_object['CREDENTIALS']['EXPORT_DIRECTORY'] = export_dir.get()
            with open('config.ini', 'w') as conf:
                self.config_object.write(conf)
            self.controller.RALLY_REPORTER.set_export_paths()
            self.config_object.read("config.ini")

        export_dir_text = Entry(self, textvariable=export_dir)
        export_dir_text.grid(row=1, column=1, sticky='w')
        export_dir_update = Button(self, text="Set Directory", command=update_directory)
        export_dir_update.grid(row=1, column=2, sticky='w')

        #Get default headers for given artifact
        Label(self, text="Artifact: ").grid(row=2,column=0, sticky='e')
        artifact = StringVar()
        artifact_list = ["UserStory", "Defect", "TestCase", "Feature"]
        artifact_dd = OptionMenu(self, artifact, *artifact_list)
        artifact_dd.grid(row=2, column=1, sticky='w')
        artifact.set(artifact_list[0])

        us_default = self.config_object.getlist(
            "DEFAULT_FIELDS", artifact.get())
        us_headers = self.config_object.getlist("FIELDS", artifact.get())

        curr_field = StringVar()
        curr_field.set(us_default[0])

        field_label = Label(self, text="Fields: ")
        field_label.grid(row=4, column=0, sticky='e')

        fields = OptionMenu(self, curr_field, *us_headers)
        fields.grid(row=4, column=1, sticky='w')

        us_pane = ListBuilderComponent(self, curr_field)
        us_pane.grid(row=5, column=1, sticky='nsew')

        def handle_field_update(*args):
            self.config_object["DEFAULT_FIELDS"][artifact.get()
                                                 ] = ",".join(us_pane.get_selected())
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            
            self.config_object.read("config.ini")
        
        def handle_artifact_update(*args):
            us_pane.clear_list()

            self.config_object.read("config.ini")

            us_default = self.config_object.getlist("DEFAULT_FIELDS", artifact.get())
            us_headers = self.config_object.getlist("FIELDS", artifact.get())

            for i in range(len(us_headers)):
                if (us_headers[i] in us_default):
                    us_pane.add_element(us_headers[i])

        artifact.trace('w', handle_artifact_update)
        artifact.set(artifact_list[0])
        

        field_button = Button(self, text="Set Default Fields", command=handle_field_update)
        field_button.grid(row = 5, column=2, sticky='w')


