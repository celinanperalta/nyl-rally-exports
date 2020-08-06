import datetime
import os
import re
import sys
import tkinter as tk
from functools import partial
from tkinter import *
from tkinter import messagebox
from pathlib import Path

import pandas as pd
from pyral import Rally, rallyWorkset


class RallyExportTool:

    def __init__(self, config):
        self.RALLY = None
        self.USERNAME = None
        self.PASSWORD = None
        self.API_KEY = None
        self.WORKSPACE_LIST = []
        self.PROJECT_LIST = []
        self.config_object = config
        self.WORKSPACE = self.config_object['CREDENTIALS']['WORKSPACE']
        self.PROJECT = self.config_object['CREDENTIALS']['PROJECT']

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def cleandata(self, key, val):
        if val == "" or val is None:
            return
        if key == "Feature":
            return val.FormattedID
        elif '.' in key:
            attr = key.split(".")[1]
            return val.__dict__.get(attr, "")
        elif key in ["Milestones", "Tags"]:
            return str([x.Name for x in val])
        elif key in ["Owner", "SubmittedBy", "Project", "Iteration", "Release"]:
            return val.__dict__.get("Name", "")
        elif key in ["CreationDate", "LastUpdateDate"]:
            return val.split('T')[0]
        elif key == "AcceptanceCriteria":
            return self.cleanhtml(val)
        else:
            return val

    def get_data(self, data_type, headers, csv_dest, query="", limit=200, order=""):

        print(data_type)
        print(headers)
        
        # Create fields for query from df column headers
        formatted_headers = list(map(lambda x: x.replace(" ", ""), headers))

        cleaned_headers = [x.split(".")[0] if '.' in x else x for x in formatted_headers]
        fetch_data = ",".join(cleaned_headers)

        # Construct pandas df
        formatted_headers.append("_ref")
        df = pd.DataFrame(columns=headers)

        df["URL"] = []

        # Get response and clean data
        try:
            response = self.RALLY.get(data_type, fetch=fetch_data, query=query, start=1, pagesize=200, order=order, limit=limit)
            if "QueryResult" in response.content:
                results = response.content["QueryResult"]["TotalResultCount"]
            count = 0
            # print(response.content)
            if results != 0:
                for rls in response:
                    data = []
                    for key in formatted_headers:
                        try:
                            if ('.' in key):
                                attr = key.split(".")
                                x = rls.__dict__.get(attr[0], "")
                                if x != "" and x is not None:
                                    data.append(x.__dict__.get(attr[1], ""))
                                else:
                                    data.append("")
                            elif key in ["Tags", "Milestones"]:
                                ref = rls.__dict__.get("__collection_ref_for_" + key, "")
                                if ref != "":
                                    collection = [x for x in self.RALLY.getCollection(ref)]
                                    data.append(self.cleandata(key, collection))
                                else:
                                    data.append("")
                            else:
                                val = rls.__dict__.get(key, "")
                                data.append(self.cleandata(key, val))
                        except Exception as e:
                            print("Error: " + str(e))
                            if len(data) != len(formatted_headers):
                                data.append("")
                            pass
                    df.loc[count] = data
                    count += 1
        except Exception as e:
            messagebox.showinfo(message="Error retrieving data for project " +
                                self.RALLY.getProject().Name + ": " + str(e))
                
        if count == 0:
            messagebox.showinfo(message=str("No " + data_type + " rows loaded."))
            return None
        else:
            base_path = Path(self.config_object["CREDENTIALS"]["export_directory"]) / "rally-data" / "csv_files"
            path = base_path / csv_dest
            df.to_csv(Path(path), index=False)
            messagebox.showinfo(message=str(count) + " " + data_type + " rows loaded in " + str(path))
            return path


    #TODO: allow user to select headers
    def get_exports(self, data_type, query, limit, order):
            return self.get_data(data_type=data_type, headers=self.config_object.getlist('DEFAULT_FIELDS', data_type),
                          csv_dest=data_type + "_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".csv", query=query, limit=limit, order=order)
            
    def get_exports_custom_fetch(self, data_type, headers, query, limit, order):
            print(self.RALLY.getProject())
            return self.get_data(data_type=data_type, headers=headers,
                          csv_dest=data_type + "_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".csv", query=query, limit=limit, order=order)

    def get_workspaces(self):
        return self.WORKSPACE_LIST
    
    def set_workspace(self, workspaceName):
        self.RALLY.setWorkspace(workspaceName)

    def get_projects(self):
        return self.PROJECT_LIST

    def set_project(self, projectName):
        self.RALLY.setProject(projectName)

    def validate_login(self, username, password):
        # Configure pyral variables
        self.USERNAME = username
        self.PASSWORD = password

        options = [arg for arg in sys.argv[1:] if arg.startswith('--')]
        args = [arg for arg in sys.argv[1:] if arg not in options]
        server, user, password, apikey, workspace, project = rallyWorkset(options)

        try:
            if (self.config_object['CREDENTIALS']["API_KEY"] != ""):
                print("Login 1")
                self.API_KEY = self.config_object['CREDENTIALS']["API_KEY"]
                self.RALLY = Rally(server="rally1.rallydev.com", apikey=self.API_KEY,
                            workspace=self.WORKSPACE, project=self.PROJECT, warn=True)
            else:
                print("Login 2")
                self.RALLY = Rally(server="rally1.rallydev.com", username=self.USERNAME, password=self.PASSWORD,
                                    workspace=self.WORKSPACE, project=self.PROJECT, warn=True)

            self.WORKSPACE_LIST = list(map(lambda x: x.Name, self.RALLY.getWorkspaces()))

            project_list = []
            
            for wksp in self.WORKSPACE_LIST:
                projects = self.RALLY.getProjects(workspace=wksp)
                for proj in projects:
                    project_list.append(proj.Name)

            self.PROJECT_LIST = project_list

            print("WORKSPACES + PROJECTS")
            print(self.WORKSPACE_LIST)
            print(self.PROJECT_LIST)


            return True
        except Exception as e:
            print("WORKSPACES + PROJECTS")
            print(self.WORKSPACE_LIST)
            print(self.PROJECT_LIST)
            print(e)
            return False

    def set_api_key(self, key):
        self.API_KEY = key

    def has_api_key(self):
        return self.API_KEY is not None

    def get_allowed_values(self, data_type, attribute):
        return self.RALLY.getAllowedValues(data_type, attribute)

    def typedef(self, item):
        res = list(map(lambda x: x.replace(" ", ""), [
                   x.Name for x in self.RALLY.typedef(item).Attributes]))
        res.append("")
        return res
