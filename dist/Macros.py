import xlsxwriter
from xlsxwriter import *
from xlsxwriter.workbook import Workbook
import pandas as pd



def highlight_missing(df, writer, workbook, worksheet, headers=["Iteration", "PlanEstimate", "AcceptanceCriteria"]):
    
    row_count = len(df)

    format1 = workbook.add_format({'bg_color':   '#FFC7CE',
                                   'font_color': '#9C0006'})

    for x in headers:
        col = df.columns.get_loc(x)
        worksheet.conditional_format(0, col, row_count, col, {
            'type': 'blanks',
            'format' : format1
        })

    writer.save()



    
