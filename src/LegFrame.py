from settings import COLORS
from tkinter.ttk import Scrollbar
from idlelib.tooltip import Hovertip
from tkinter import Tk, Frame, Canvas, Label, Button, Radiobutton

class LegFrame(Frame):
    ''' Contains the widgets for displaying the Legend for the currently loaded Map elements '''
    def __init__(self, window: Tk):
        super().__init__(window)
        self.window = window
        self.config({'width': int(window.winfo_width() * 0.45),
                     'height': int(self.window.winfo_height() * 0.35)})
        
        self.grid(column = 1, row = 0, sticky = 'news')
        
        self.configureLayout()
        self.update_idletasks()
    
    def clean(self):
        ''' Reinitialize tab, previous clearing of window.maps is assumed. '''
        self.updateLegend()
        return 0
    
    def deleteMap(self):
        ''' Delete the currently selected Map element by Radiobutton '''
        # If deletion is successful, update the legend and display the appropiate spectra
        if self.window.maps.delMap(self.window.varSelectedMap.get()) is not None:
            self.updateLegend()
            self.window.chooseDisplay()
            return 0
        return None
    
    def configureLayout(self):
        ''' Configure widget layout for this Frame. '''

        # Make if a scrollable Frame
        self.legendCanvas = Canvas(self)
        self.legendScrollBar = Scrollbar(self, orient = 'vertical', 
                                             command = self.legendCanvas.yview)
        self.realLegFrame = Frame(self)
        
        self.realLegFrame.bind("<Configure>", 
                          lambda e: self.legendCanvas.configure(scrollregion = self.legendCanvas.bbox('all')))
        self.realLegFrame.grid()
        self.legendCanvas.create_window((0,0), window = self.realLegFrame, anchor = 'nw')
        self.legendCanvas.config(yscrollcommand = self.legendScrollBar.set)
        self.legendCanvas.pack(side = 'left', fill = 'both', expand = True)
        self.legendScrollBar.pack(side = 'right', fill = 'y', anchor = 'se')
        # Make if a scrollable Frame
        
        self.btnDelMap = Button(self.realLegFrame, text = 'Delete map', 
                              command = self.deleteMap, name = 'mapDel')
        self.btnDelMap.grid(column = 0, columnspan = 3, row = 0, pady = 5, padx = 5, sticky = 'W')
        Hovertip(self.btnDelMap, 
                 'Delete selected map', 
                 hover_delay = 1000)
    
    def updateLegend(self):
        ''' Reconfigure Frame to changes. '''
        # Destroy everything except deleteMap button
        if self.window.maps.isEmpty():
            return 1
        
        for widget in self.realLegFrame.winfo_children():
            if widget.winfo_name() != 'mapDel':
                widget.destroy()
            
        for i, map in enumerate(self.window.maps):
            
            # Add a radiobutton for each Map
            Radiobutton(self.realLegFrame, text = '', value = map.orig, 
                        variable = self.window.varSelectedMap).grid(column = 0, row = i + 1)
            
            # Add a square with the color o hte correpsonding plot data
            color_canvas = Canvas(self.realLegFrame, height = 15, width = 15)
            color_canvas.grid(column = 1, row = i + 1)
            color_canvas.create_rectangle(0, 0, 15, 15, outline = '#000000', fill = COLORS[i])
            
            # Add the current Map name
            Label(self.realLegFrame, text = map.name).grid(column = 2, row = i + 1, sticky = 'W')
        
        # Set Radiobutton to first Map
        self.window.varSelectedMap.set(self.window.maps.maps[0].orig)

        return 0