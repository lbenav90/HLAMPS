from tkinter import Tk, Frame
from PltFigure import PltFigure

class PlotFrame(Frame):
    def __init__(self, master: Tk):
        super().__init__(master)
        self.master = master
        self.config({'width': int(self.master.winfo_width() * 0.55),
                     'height': int(self.master.winfo_height() * 0.65)})
        
        self.grid(column = 0, row = 0, 
                  rowspan = 2, sticky = 'news')
        
        self.update_idletasks()
        self.figure = PltFigure(self, master)
    
    def clean(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.figure = PltFigure(self, self.master)