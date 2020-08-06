import os
import pandas as pd
import numpy as np
from tkinter import *
from tkinter.filedialog import askopenfilename
import csv
import pygal
# import cairosvg
import lxml
import datetime
from glob import glob
import xlsxwriter
from xlsxwriter import *
from xlsxwriter.workbook import Workbook
from pathlib import Path

class RallyReportTool:

    def __init__(self, config):

        # Change to export path config variable
        self.export_path = ""
        self.chart_path = ""
        self.table_path = ""
        self.df = None
        self.config_object = config

        self.set_export_paths()

    def set_export_paths(self):
        base_path = Path(self.config_object['CREDENTIALS']['export_directory']) / "rally-data"
        try:
            os.mkdir(base_path)
            print("Created directory " + base_path)
        except:
            pass
        self.export_path = base_path / "csv_files"
        self.chart_path = base_path / "charts"
        self.table_path = base_path / "xlsx_files"
        for x in [self.export_path, self.chart_path, self.table_path]:
            try:
                os.mkdir(x)
            except:
                print(x)
                pass

    def set_df(self, file):
        self.df = pd.read_csv(file)

    def get_columns(self):
        columns = list(self.df.columns.values)
        print(str(columns))
        return columns

    def create_pivot(self, index_list, value_list, columns, aggfunc=np.sum):
        """
        Create a pivot table from a raw DataFrame and return it as a DataFrame
        """
        table = pd.pivot_table(self.df, index=index_list, values=value_list, columns=columns,
                            aggfunc=aggfunc, fill_value=0)
        return table

    def create_grouped_df(self, index_list, value_list=[], aggfunc=None):
        """
        Create outline view from a raw DataFrame and return it as a DataFrame
        """
        if (aggfunc is None):
            table = self.df.groupby(index_list)[value_list]
        else:
            table = self.df.groupby(index_list)[value_list].agg(aggfunc)
        return table
        

    def generate_bar_chart(self, x_labels, values, title, y_labels, file_name, x_label_rotation=0, stacked=False):
        if stacked:
            bar_chart = pygal.StackedBar(width=1500, print_values=True, print_zeroes=False,
                                        show_x_labels=True, x_label_rotation=x_label_rotation, human_readable=True)
        else:
            bar_chart = pygal.Bar(width=1500, print_values=True, print_zeroes=False,
                                print_values_position='top', show_x_labels=True, x_label_rotation=x_label_rotation, human_readable=True)
        

        bar_chart.x_labels = x_labels
        bar_chart.title = title

        for i in range(len(y_labels)):
            bar_chart.add(y_labels[i], [x[i] for x in values])
                
        print(file_name)
        path = str(self.chart_path / (file_name + ".png"))
        bar_chart.render_to_png(path)
        return path

    def generate_bar_chart_from_pt(self, pt, title, stacked=True):
        
        x_labels = self.df[pt.index.name].unique()
        
        y_labels = []
        values = pt.values

        for (columnName, columnData) in pt.iteritems():
            if not isinstance(columnName, str):
                y_labels.append(columnName[len(columnName) - 1])
            else:
                y_labels.append(columnName)

        title = title
        file_name = "chart_" + title + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file_name = file_name.replace(" ", "")

        print("x_labels: " + str(x_labels))
        print("y_labels: " + str(y_labels))
        print("values: " + str(values))
        
        return self.generate_bar_chart(x_labels, values, title, y_labels, file_name, 45, stacked)

    def generate_excel_table(self, pt, title):
        y_labels = []
        values = pt.values

        for (columnName, columnData) in pt.iteritems():
            if not isinstance(columnName, str):
                y_labels.append(columnName[len(columnName) - 1])
            else:
                y_labels.append(columnName)

        file_name = "pivot_" + title + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file_name = file_name.replace(" ", "")

        path = str(self.table_path / (file_name + ".xlsx"))
        pt.to_excel(path)

    def csv_to_excel(self, csv):
        print("Generating Excel table...")
        print(self.table_path)
        read_file = pd.read_csv(str(csv), engine='python')
        name = str(csv).split(str(Path('csv_files')))[1].split('.')[0] + ".xlsx"
        base_path = Path(self.config_object['CREDENTIALS']['export_directory']) / "rally-data" / "xlsx_files"
        path = str(base_path) + "\\" + name

        print(path)

        writer = pd.ExcelWriter(str(path), engine='xlsxwriter')

        read_file.to_excel(writer, header=True, index=False, sheet_name='Sheet1')
        workbook  = writer.book
        worksheet = writer.sheets['Sheet1']

        cols = len(read_file.columns)
        worksheet.set_column(1, cols - 1, 25)

        writer.save()

        return read_file, writer, workbook, worksheet
        
