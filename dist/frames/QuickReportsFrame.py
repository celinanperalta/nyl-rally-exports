import sys
import os
import pandas as pd
from pyral import Rally, rallyWorkset
import re
import tkinter as tk
from tkinter import *
from functools import partial
from .ReorderableListbox import ReorderableListbox
import QuickReports as qr
import Macros as macros


class QuickReportsFrame(Frame):
    def __init__(self, master, controller, config):
        tk.Frame.__init__(self, master)

        self.controller = controller
        self.master = master
        self.workspace = StringVar()
        self.project = StringVar()
        self.export_option = StringVar()
        self.query_list = None
        self.row_limit = IntVar()
        self.desc = False
        self.config_object = config
        self.OPTION_MAP = self.config_object.getlist("FIELDS", "OPTION_MAP")
        self.qd_1 = None

        self.filter_by = StringVar()
        self.filter_by_attr = StringVar()

        self.quick_report = StringVar()
        self.quick_report_options = [""]
        self.quick_reports_dd = OptionMenu(
            self, self.quick_report, *self.quick_report_options)
        
        self.custom_query_fields = {}
        self.cq_labels = []
        self.cq_entries = []

        self.to_excel = IntVar()

    def load_data(self):

        #   ---------------------------------
        #      Load Workspaces + Projects
        #   ---------------------------------

        workspaces = self.controller.RALLY.get_workspaces()
        projects = self.controller.RALLY.get_projects()

        workspace_label = Label(self, text="Workspace: ")
        workspace_label.grid(row=0, column=0, sticky=W)

        workspace_dd = OptionMenu(self, self.workspace, *workspaces)
        workspace_dd.grid(row=0, column=1, sticky=NW)


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

        self.row_limit.set(100)

        row_label = Label(self, text="Row Limit: ")
        row_label.grid(row=4, column=0, sticky=W)

        row_entry = Entry(self, textvariable=self.row_limit)
        row_entry.grid(row=4, column=1, sticky=W)

        #   ---------------------------------
        #           Order By
        #   ---------------------------------

        self.order_by = StringVar()
        order_by_options = self.config_object.getlist(
            'DEFAULT_FIELDS', self.export_option.get())

        order_label = Label(self, text="Order By: ")
        order_label.grid(row=5, column=0, sticky=W)

        self.order_dd = OptionMenu(
            self, self.order_by, *order_by_options)
        self.order_dd.grid(row=5, column=1, sticky=NW)

        def set_export_option(*args):
            self.order_by.set('')
            self.order_dd['menu'].delete(0, 'end')
            self.quick_reports_dd['menu'].delete(0, 'end')
            order_by_options = self.config_object.getlist(
                'DEFAULT_FIELDS', self.export_option.get())
            self.quick_report_options = list(
                qr.quick_reports[self.export_option.get()]["custom_reports"].keys())

            for x in order_by_options:
                self.order_dd['menu'].add_command(
                    label=x, command=tk._setit(self.order_by, x))

            for x in self.quick_report_options:
                self.quick_reports_dd['menu'].add_command(label=x, command=tk._setit(self.quick_report, x))

            self.order_by.set(order_by_options[0])
            self.filter_by.set(order_by_options[0])
            self.quick_report.set(self.quick_report_options[0])


        self.export_option.trace('w', set_export_option)
        self.export_option.set(self.OPTION_MAP[0])
        self.order_by.set(order_by_options[0])

        #   ---------------------------------
        #         Order by descending
        #   ---------------------------------

        self.desc = IntVar()
        self.desc.set(0)

        desc_check = tk.Checkbutton(self, text="Descending", variable=self.desc,
                                    onvalue=1, offvalue=0)
        desc_check.grid(row=5, column=2, sticky=W)

        #   ---------------------------------
        #           Show Quick Reports
        #   ---------------------------------

        Label(self, text="Select Report: ").grid(row=7,column=0, sticky=W)
        self.quick_reports_dd.grid(row=7, column=1, sticky=W)


        Label(self, text="Generate Excel Table: ").grid(row=8, column=0, sticky=W)

        to_excel_check = Checkbutton(self, variable=self.to_excel, onvalue=1, offvalue=0)
        to_excel_check.grid(row=8, column=1, sticky=W)

    
        #TODO: Show custom query fields

        Label(self, text="Custom Queries: ").grid(row=9, column=0, sticky=W)

        def handle_qr_update(*args):
            query_custom = qr.quick_reports[self.export_option.get()]["custom_reports"][self.quick_report.get()]["query_custom"]
            row = 10

            for i in range(len(self.cq_labels)):
                self.cq_labels[i].destroy()
                self.cq_entries[i].destroy()

            self.cq_entries = []
            self.cq_labels = []

            self.custom_query_fields.clear()

            for query in query_custom:
                self.custom_query_fields[query] = StringVar()
                label = Label(self, text=query)
                label.grid(row=row, column=0)
                self.cq_labels.append(label)

                entry = Entry(self, textvariable=self.custom_query_fields[query])
                entry.grid(row=row, column=1)
                self.cq_entries.append(entry)
                row += 1


        self.quick_report.trace('w', handle_qr_update)
        self.quick_report.set(self.quick_report_options[0])

        
        #   ---------------------------------
        #           Submit Fields
        #   ---------------------------------

        submit_button = Button(self, text="Submit",
                               command=self.handle_submit)

        submit_button.grid(row=20, columnspan=2)

    def handle_submit(self):
        artifact = qr.quick_reports[self.export_option.get()].copy()
        # query = artifact["custom_reports"][self.quick_report.get()]["query"].copy()
        query = []
        headers = artifact["custom_reports"][self.quick_report.get()]['headers'].copy()
        df_query = artifact["custom_reports"][self.quick_report.get()]['query']
        
        for key, val in self.custom_query_fields.items():
            if (val.get() == ""):
                pass
            else:
                x = key.replace('$', val.get())
                query.insert(0, x)

        print("Query: " + str(query))
        
        path = self.controller.RALLY.get_exports_custom_fetch(self.export_option.get(), headers, query, self.row_limit.get(), self.order_by.get().replace(" ", "") + (" desc" if self.desc.get() == 1 else ""), df_query)
        
        if self.to_excel.get() == 1 and path is not None:
            read_file, writer, workbook, worksheet = self.controller.RALLY_REPORTER.csv_to_excel(path)
            macros.highlight_missing(df=read_file, writer=writer, workbook=workbook, worksheet=worksheet)

        # Update files in Report Frame after export
        self.controller.frames["MainFrame"].report_frame.update_files()
