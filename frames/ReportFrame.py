import sys
import pandas as pd
from pyral import Rally, rallyWorkset
import re
import tkinter as tk
import numpy as np
from tkinter import *
from tkinter import ttk
from functools import partial
from PIL import ImageTk, Image
import glob
from .ListBuilderComponent import ListBuilderComponent
from pathlib import Path

class ReportFrame(Frame):
    def __init__(self, master, controller, config):
        tk.Frame.__init__(self, master)

        self.controller = controller
        self.master = master
        self.workspace = None
        self.project = None
        self.export_option = 1
        self.query_list = None
        self.row_limit = 200
        self.desc = False
        self.OPTION_MAP = {
            1: "UserStory",
            2: "Defect"
        }
        self.REPORTS = self.controller.RALLY_REPORTER
        self.REPORTS.set_export_paths()
        self.headers = [""]
        self.export_file = StringVar()

        self.fields = None
        self.curr_field = StringVar()

        self.indices = ListBuilderComponent(self, self.curr_field)
        self.values = ListBuilderComponent(self, self.curr_field)
        self.columns = ListBuilderComponent(self, self.curr_field)

        self.agg_func_options = {
            "Count": len,
            "Sum": np.sum,
            "Mean": np.mean,
            "None":None}

        self.aggfunc = StringVar()

        self.files = [""]

        self.image = None
        self.canvas = Canvas(self, width=800, height=600, bg='grey')

        self.file_dd = OptionMenu(self, self.export_file, *self.files)

        self.config_object = config
    
    def update_fields(self, headers):
        self.fields['menu'].delete(0, 'end')
        for x in headers:
                self.fields['menu'].add_command(
                    label=x, command=tk._setit(self.curr_field, x))

        self.curr_field.set(headers[0])

    def get_selected_fields(self):
        data = []
        for x in [self.indices, self.values, self.columns]:
            data.append(x.get_selected())
        return data

    def update_files(self):
        print(str(self.REPORTS.__dict__))
        print(self.REPORTS.export_path)
        self.files = glob.glob(str(self.REPORTS.export_path / "*.csv"))
        self.files = list(map(lambda x: x.replace(str(self.REPORTS.export_path) + "\\", ""), self.files))
        self.file_dd['menu'].delete(0, 'end')
        for x in self.files:
                self.file_dd['menu'].add_command(
                    label=x, command=tk._setit(self.export_file, x))

    def generate_title(self, data):
        data[2].append("")
        data[1].append("")
        print(data[2])
        print(data[1])
        if len(data[2]) >= 2:
            return "".join(data[2]) + " by " + "".join(data[0])
        else:
            return "".join(data[1]) + " by " + "".join(data[0])

    def render_output(self, img_path):
        path = img_path

        #Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
        self.image = Image.open(path).copy()
        self.image2 = ImageTk.PhotoImage(self.image)
        width = self.image2.width()
        height = self.image2.height()

        ratio = 800.0 / width
        new_height = height * ratio

        self.image = self.image.resize((800, int(new_height)), Image.ANTIALIAS)

        self.image = ImageTk.PhotoImage(master=self, image=self.image)

        self.canvas.create_image(0, 0, image=self.image, anchor=NW)
    
    def render_table(self, table_path):
        #TODO: Render xlsx pivot table in pandastable
        return -1

    def generate_pivot_table(self):
        data = self.get_selected_fields()
        fp = self.REPORTS.export_path / self.export_file.get()
        self.REPORTS.set_df(str(fp))
        table = self.REPORTS.create_pivot(index_list=data[0], value_list=data[1], columns=data[2], aggfunc=self.agg_func_options[self.aggfunc.get()])
        # table = self.REPORTS.create_grouped_df(index_list=data[0], value_list=data[1], aggfunc=len)
        print(table)
        self.REPORTS.generate_excel_table(table, self.generate_title(data))
    
    def generate_chart(self):
        data = self.get_selected_fields()
        print("data: " + str(data))
        table = self.REPORTS.create_pivot(
            index_list=data[0], value_list=data[1], columns=data[2], aggfunc=self.agg_func_options[self.aggfunc.get()])

        path = self.REPORTS.generate_bar_chart_from_pt(table, self.generate_title(data))
        self.render_output(path)
                
    def load_data(self):

        field_label = Label(self, text="Fields: ")
        field_label.grid(row=1, column=0, sticky='e')

        self.fields = OptionMenu(self, self.curr_field, *self.headers)
        self.fields.grid(row=1, column=1, sticky='w')

        def handle_file_update(*args):
            fp = self.REPORTS.export_path / self.export_file.get()
            self.REPORTS.set_df(str(fp))

            for x in [self.indices, self.values, self.columns]:
                x.clear_list()
            self.headers = self.REPORTS.get_columns()

            self.update_fields(self.headers)
            
        self.update_files()
        self.export_file.trace('w', handle_file_update)

        file_label = Label(self, text="Available Data: ")
        file_label.grid(row=0, sticky="e")
        self.file_dd.grid(row=0, column=1, sticky="w")


        Label(self, text="Indices").grid(row=3, column=0, sticky='nsew')
        Label(self, text="Values").grid(row=3, column=1, sticky='nsew')
        Label(self, text="Columns").grid(row=3, column=2, sticky='nsew')

        self.indices.grid(row=4, column=0, rowspan=3)
        self.values.grid(row=4, column=1, rowspan=3)
        self.columns.grid(row=4, column=2, rowspan=3)
        
        aggfunc_label = Label(self, text="Agg Function: ")
        aggfunc_label.grid(row=2, column=0, sticky='e')

        self.aggfunc.set("Count")

        aggfunc_dd = OptionMenu(self, self.aggfunc, *self.agg_func_options.keys())
        aggfunc_dd.grid(row=2,column=1,sticky='w')

        table_button = Button(self, text="Generate Table", command=self.generate_pivot_table)
        table_button.grid(row=8, column=0, sticky='w')

        #TODO: Add select stacked or not, select chart type
        # chart_button = Button(self, text="Generate Chart",
                            #   command=self.generate_chart)
        # chart_button.grid(row=8, column=2, sticky='e')

        self.canvas.grid(row=9, column=0, columnspan=3, sticky='nsew')

        




