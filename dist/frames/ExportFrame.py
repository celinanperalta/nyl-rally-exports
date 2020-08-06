import sys, os
import pandas as pd
from pyral import Rally, rallyWorkset
import re
import tkinter as tk
from tkinter import *
from functools import partial
from .ReorderableListbox import ReorderableListbox

class ExportFrame(Frame):
    def __init__(self, master, controller, config):
        tk.Frame.__init__(self, master)

        self.controller = controller
        self.master = master
        self.workspace = None
        self.project = None
        self.export_option = StringVar()
        self.query_list = None
        self.row_limit = 200
        self.desc = False
        self.config_object = config
        self.OPTION_MAP = self.config_object.getlist("FIELDS", "OPTION_MAP")
        self.qd_1 = None

        self.filter_by = StringVar()
        self.filter_by_attr = StringVar()

        self.to_excel = IntVar()


    def load_data(self):

        #   ---------------------------------
        #      Load Workspaces + Projects
        #   ---------------------------------

        workspaces = self.controller.RALLY.get_workspaces()
        projects = self.controller.RALLY.get_projects()

        self.workspace = StringVar()
        

        workspace_label = Label(self, text="Workspace: ")
        workspace_label.grid(row=0, column=0, sticky=W)

        workspace_dd = OptionMenu(self, self.workspace, *workspaces)
        workspace_dd.grid(row=0, column=1, sticky=NW)

        self.project = StringVar()


        project_label = Label(self, text="Project: ")
        project_label.grid(row=1, column=0, sticky=W)

        project_dd = OptionMenu(self, self.project, *projects)
        project_dd.grid(row=1, column=1, sticky=NW)

        def set_proj_wksp(*args):
            self.controller.RALLY.set_workspace(self.workspace.get())
            self.controller.RALLY.set_project(self.project.get())

        self.workspace.trace('w', set_proj_wksp)
        self.project.trace('w', set_proj_wksp)
        self.workspace.set(workspaces[0])
        self.project.set(projects[0])

        #   ---------------------------------
        #      Set Export Type + Row Limit
        #   ---------------------------------

        # self.pack()
        self.export_option.set(self.OPTION_MAP[0])

        export_label = Label(self, text="Select Export Type: ")
        export_label.grid(row=2, column=0, sticky=W)

        export_dd = OptionMenu(self, self.export_option, *self.OPTION_MAP)
        export_dd.grid(row=2, column=1, sticky='w')

        self.row_limit = IntVar()
        self.row_limit.set(100)

        row_label = Label(self, text="Row Limit: ")
        row_label.grid(row=4, column=0, sticky=W)

        row_entry = Entry(self, textvariable=self.row_limit)
        row_entry.grid(row=4, column=1, sticky=W)

        #   ---------------------------------
        #           Order By
        #   ---------------------------------

        self.order_by = StringVar()
        order_by_options = self.config_object.getlist('DEFAULT_FIELDS', self.export_option.get())

        order_label = Label(self, text="Order By: ")
        order_label.grid(row=5, column=0, sticky=W)

        self.order_dd = OptionMenu(
            self, self.order_by, *order_by_options)
        self.order_dd.grid(row=5, column=1, sticky=NW)

        def set_export_option(*args):
            self.order_by.set('')
            self.order_dd['menu'].delete(0, 'end')
            self.qd_1['menu'].delete(0, 'end')
            order_by_options = self.config_object.getlist(
                'DEFAULT_FIELDS', self.export_option.get())
            for x in order_by_options:
                self.order_dd['menu'].add_command(label=x, command=tk._setit(self.order_by, x))
                self.qd_1['menu'].add_command(
                    label=x, command=tk._setit(self.filter_by, x))
            self.order_by.set(order_by_options[0])
            self.filter_by.set(order_by_options[0])

        self.export_option.trace('w', set_export_option)
        self.order_by.set(order_by_options[0])

        #   ---------------------------------
        #         Order by descending
        #   ---------------------------------

        self.desc = IntVar()
        self.desc.set(0)

        desc_check = tk.Checkbutton(self, text="Descending", variable=self.desc,
                                    onvalue=1, offvalue=0)
        desc_check.grid(row=5, column=2, sticky=W)

        Label(self, text="Generate Excel Table: ").grid(
            row=6, column=0, sticky=W)

        to_excel_check = Checkbutton(
            self, variable=self.to_excel, onvalue=1, offvalue=0)
        to_excel_check.grid(row=6, column=1, sticky=W)

        #   ---------------------------------
        #           Query Builder
        #   ---------------------------------

        query_label = Label(self, text="Query Builder")
        query_label.grid(row=7, column=0, sticky=W)

        # Two dropdowns, then a textbox or dropdown depending on field
        # Dropdown 1: Options list
        # Dropdown 2: Operators
        # Textbox/Dropdown: Allowed attributes for query

        operator = StringVar()
        filter_value = StringVar()

        query_frame = Frame(self)

        operator_options = ["=", "!=", ">", ">=", "<", "<=", "in",
                            "contains", "!contains", "containsall", "containsany"]

        attr_options = [""]

        self.qd_1 = OptionMenu(query_frame, self.filter_by, *order_by_options)
        self.qd_1.grid(row=0, column=0, sticky='nsew')

        self.qd_1_2 = OptionMenu(query_frame, self.filter_by_attr, *attr_options)
        # self.qd_1_2.grid(row=0, column=1, sticky='nsew')

        def handle_change_filter(*args):
            fil = self.filter_by.get().replace(" ", "")
            self.qd_1_2["menu"].delete(0, 'end')
            try:
                attr_options = self.controller.RALLY.typedef(fil)
            except Exception as e:
                print(e)
                attr_options = [""]
            for x in attr_options:
                self.qd_1_2['menu'].add_command(
                    label=x, command=tk._setit(self.filter_by_attr, x))

        self.filter_by.trace('w', handle_change_filter)
        self.filter_by.set(order_by_options[0])

        qd_2 = OptionMenu(query_frame, operator, *operator_options)
        operator.set(operator_options[0])
        qd_2.grid(row=0, column=2, sticky='nsew')

        qd_3 = Entry(query_frame, textvariable=filter_value)
        qd_3.grid(row=0, column=3, sticky='nsew')

        query_frame.grid(row=8, column=0, sticky='nsew')

        query_frame_2 = Frame(self)

        self.query_list = ReorderableListbox(query_frame_2)
        self.query_list.grid(row=0, column=0, columnspan=2, sticky='nsew')

        def handle_query_list_add():
            query_string = ""
            if self.filter_by_attr.get() != "":
                query_string = ".".join([self.filter_by.get().replace(" ", ""), self.filter_by_attr.get()]) + " " + operator.get() + " " + filter_value.get()
            else:
                query_string = self.filter_by.get().replace(" ", "") + " " + operator.get() + " " + filter_value.get()

            self.query_list.insert(1, query_string)

        def handle_query_list_delete():
            i = self.query_list.curselection()
            self.query_list.delete(i)

        query_add_button = Button(query_frame_2, text="Add Query",
                                  command=handle_query_list_add)
        query_add_button.grid(row=1, column=0, sticky='nsew')
        query_delete_button = Button(
            query_frame_2, text="Delete Query", command=handle_query_list_delete)
        query_delete_button.grid(row=1, column=1, sticky='nsew')

        query_frame_2.grid(row=9, column=0, columnspan=2, sticky='nsew')

        #   ---------------------------------
        #           Submit Fields
        #   ---------------------------------

        submit_button = Button(self, text="Submit",
                               command=self.handle_submit)

        submit_button.grid(row=11, columnspan=1)

    def handle_submit(self):
        query = self.query_list.get(0, 'end')
    
        path = self.controller.RALLY.get_exports(self.export_option.get(), query, self.row_limit.get(), self.order_by.get().replace(" ", "") + (" desc" if self.desc.get() == 1 else ""))

        if self.to_excel.get() == 1 and path is not None:
            self.controller.RALLY_REPORTER.csv_to_excel(path)

        # Update files in Report Frame after export
        self.controller.frames["MainFrame"].report_frame.update_files()
