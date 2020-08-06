import tkinter as tk
from tkinter import *
from .ReorderableListbox import ReorderableListbox

class ListBuilderComponent(Frame):

    def __init__(self, master, data_var):
        Frame.__init__(self, master)
        self.data_var = data_var
        self.index_list = ReorderableListbox(self)
        self.index_list.grid(row=0, column=0, columnspan=2, sticky='nsew')

        query_add_button = Button(self, text="Add Field",
                                  command=self.handle_list_add)
        query_add_button.grid(row=1, column=0, sticky='nsew')
        query_delete_button = Button(self, text="Delete Field", command=self.handle_list_delete)
        query_delete_button.grid(row=1, column=1, sticky='nsew')

        up_button = Button(self, text="↑", command=self.move_up)
        up_button.grid(row=0, column=2, sticky='sw')

        down_button = Button(self, text="↓", command=self.move_down)
        down_button.grid(row=1, column=2, sticky='nw')

    def handle_list_add(self):
        if (self.data_var.get() not in self.get_selected()):
            self.index_list.insert(1, self.data_var.get())

    def add_element(self, text):
        if (text not in self.get_selected()):
            self.index_list.insert(1, text)

    def handle_list_delete(self):
        i = self.index_list.curselection()
        self.index_list.delete(i)

    def clear_list(self):
        self.index_list.delete(0, 'end')

    def get_selected(self):
        return list(self.index_list.get(0, 'end'))

    def get_size(self):
        return len(self.get_selected())

    def move_up(self):
        """ Moves the item at position pos up by one """
        pos = self.index_list.curselection()[0]
        if pos == 0:
            return

        text = self.index_list.get(pos)
        self.index_list.delete(pos)
        self.index_list.insert(pos-1, text)
    
    def move_down(self):
        """ Moves the item at position pos down by one """
        pos = self.index_list.curselection()[0]
        n = self.get_size()
        if n == 1 or pos == n - 1:
            return

        
        text = self.index_list.get(pos)
        self.index_list.delete(pos)
        self.index_list.insert(pos+1, text)
