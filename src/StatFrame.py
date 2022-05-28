import time
from Global_Functions import isNumber
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Separator, Progressbar
from tkinter import Tk, Frame, StringVar, Label, Entry, Button

class StatFrame(Frame):
    ''' Contains information about the status of the program. '''
    def __init__(self, window: Tk):
        super().__init__(window)
        self.config({'width': int(window.winfo_width() * 0.45),
                     'height': int(self.window.winfo_height() * 0.3)})
        
        self.grid(column = 1, row = 1, sticky = 'news')
        self.update_idletasks()

        # Variables for keeping track of current plot limits
        self.xmin, self.xmax  = StringVar(value = ''), StringVar(value = '')
        self.ymin, self.ymax = StringVar(value = ''), StringVar(value = '')

        # Get current limits
        self.getLimits()
        self.configureLayout()
    
    def clean(self):
        ''' Reinitialize tab. Assumes prior clearing of plot frame'''
        self.getLimits()
        return 0
    
    def getLimits(self):
        ''' Gets the current limits from the PltFigure object '''
        bounds, limits = self.master.plotFrame.figure.getLimits()
        self.xmin.set(f'{limits.getXLim()[0]:.2f}')
        self.xmax.set(f'{limits.getXLim()[1]:.2f}')
        self.ymin.set(f'{limits.getYLim()[0]:.2f}')
        self.ymax.set(f'{limits.getYLim()[1]:.2f}')
        return 0
        
    def changeZoom(self):
        ''' Change plot limits to the current entry values '''
        self.master.plotFrame.figure.changeXZoom(xmin = float(self.xmin.get()),
                                                 xmax = float(self.xmax.get()))
        self.master.plotFrame.figure.changeYZoom(ymin = float(self.ymin.get()),
                                                 ymax = float(self.ymax.get()))
        return 0
    
    def resetZoom(self):
        ''' Autoscale zoom for the current data '''
        self.master.plotFrame.figure.changeXZoom()
        self.master.plotFrame.figure.changeYZoom()
        return 0
    
    def configureLayout(self):
        ''' Configure widget layout for the Frame'''
        Separator(self, orient = 'horizontal').grid(column = 0, columnspan = 11,  
                                                    row = 0, sticky = 'we')
        
        # Setup progress bar
        self.progressLabel = Label(self, text = 'Processing: ')
        self.progressLabel.grid(column = 0, row = 1, sticky = 'w')
        self.progressBar = Progressbar(self, length = 250, 
                                       mode = 'determinate')
        self.progressBar.grid(column = 0, columnspan = 4, 
                              row = 2, rowspan = 2, 
                              padx = 5, pady = 5, sticky = 'we')
        
        Separator(self, orient = 'vertical').grid(column = 5, row = 1, rowspan = 3,
                                                  sticky = 'ns', pady = 5)
        # Setup progress bar

        # Setup current limits frame        
        Label(self, text = 'Limits', 
              font = 'Helvetica 10 bold').grid(column = 6, row = 1, sticky = 'nw')
        Label(self, text = 'X min:').grid(column = 6, row = 2, sticky = 'nw')
        Label(self, text = 'X max:').grid(column = 6, row = 3, sticky = 'nw')
        Label(self, text = 'Y min:').grid(column = 8, row = 2, sticky = 'nw')
        Label(self, text = 'Y max:').grid(column = 8, row = 3, sticky = 'nw')
        
        # Entries with input validation for changing limits
        Entry(self, textvariable = self.xmin, width = 10, validate = 'all', 
              validatecommand = (self.register(isNumber), '%P')
              ).grid(column = 7, row = 2, sticky = 'nw')
        Entry(self, textvariable = self.xmax, width = 10, validate = 'all', 
              validatecommand = (self.register(isNumber), '%P')
              ).grid(column = 7, row = 3, sticky = 'nw')
        Entry(self, textvariable = self.ymin, width = 10, validate = 'all', 
              validatecommand = (self.register(isNumber), '%P')
              ).grid(column = 9, row = 2, sticky = 'nw')
        Entry(self, textvariable = self.ymax, width = 10, validate = 'all', 
              validatecommand = (self.register(isNumber), '%P')
              ).grid(column = 9, row = 3, sticky = 'nw')
        
        # Buttons
        self.butChangeZoom = Button(self, text = 'Apply', command = self.changeZoom)
        self.butChangeZoom.grid(column = 10, row = 2, 
                                sticky = 'nw')
        
        self.butZoomOut = Button(self, text = 'Restore', command = self.resetZoom)
        self.butZoomOut.grid(column = 10, row = 3,
                             sticky = 'nw')
        
        Separator(self, orient = 'horizontal').grid(column = 0, columnspan = 11, 
                                                    row = 4, sticky = 'we', pady = 5)
        # Setup current limits frame

        # Setup scrollable text Log
        self.logFrame = Frame(self, width = int(self.master.winfo_width() * 0.45), height = 120)
        self.logFrame.grid(column = 0, columnspan = 13, row = 5, sticky = 'news', pady = 5, padx = 5)
        self.logFrame.grid_propagate(False)
        self.logText = ScrolledText(self.logFrame, width = 70, height = 5)
        self.logText.pack(side = 'left', anchor = 'center')
        
        # Insert first log
        self.logText.insert('end', 'Session Log:\n\n')
        self.logText.insert('end', time.ctime(time.time()).split()[3] + ' Initiated\n')
        self.logText.config(state = 'disabled')
        # Setup scrollable text Log
        return 0