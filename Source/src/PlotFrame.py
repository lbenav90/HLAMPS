from tkinter import Tk, Frame
from .PltFigure import PltFigure

class PlotFrame(Frame):
    ''' Contains the matplotlib plot. All actions defered to PltFigure class. '''
    def __init__(self, window: Tk):
        super().__init__(window)
        self.window = window
        self.config({'width': int(self.window.winfo_width() * 0.55),
                     'height': int(self.window.winfo_height() * 0.65)})
        
        self.grid(column = 0, row = 0, 
                  rowspan = 2, sticky = 'news')
        
        self.update_idletasks()
        self.figure = PltFigure(self, window)
    
    def clean(self):
        ''' Clear widget elements and reinitialize the PltFigure element '''
        for widget in self.winfo_children():
            widget.destroy()
        self.figure = PltFigure(self, self.window)