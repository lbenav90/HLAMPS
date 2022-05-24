from settings import COLORS
from tkinter.ttk import Scrollbar
from idlelib.tooltip import Hovertip
from tkinter import Tk, Frame, Canvas, Label, Button, Radiobutton

class LegFrame(Frame):
    def __init__(self, master: Tk):
        super().__init__(master)
        self.master = master
        self.config({'width': master.winfo_width() - 700,
                     'height': 200})
        
        self.grid(column = 1, row = 0, sticky = 'news')
        
        self.configureLayout()
        self.update_idletasks()
    
    def clean(self):
        self.updateLegend()
        return 0
    
    def deleteMap(self):
        if self.master.maps.delMap(self.master.varSelectedMap.get()) is not None:
            self.updateLegend()
            self.master.chooseDisplay()
            return 0
        return None
    
    def configureLayout(self):
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
        
        self.btnDelMap = Button(self.realLegFrame, text = 'Delete map', 
                              command = self.deleteMap, name = 'mapDel')
        self.btnDelMap.grid(column = 0, columnspan = 3, row = 0, pady = 5, padx = 5, sticky = 'W')
        Hovertip(self.btnDelMap, 
                 'Delete selected map', 
                 hover_delay = 1000)
    
    def updateLegend(self):
        for widget in self.realLegFrame.winfo_children():
            if widget.winfo_name() != 'mapDel':
                widget.destroy()
    
        if self.master.maps.isEmpty():
            return 1
            
        for i, map in enumerate(self.master.maps):
            
            Radiobutton(self.realLegFrame, text = '', value = map.orig, 
                        variable = self.master.varSelectedMap).grid(column = 0, row = i + 1)
            
            color_canvas = Canvas(self.realLegFrame, height = 15, width = 15)
            color_canvas.grid(column = 1, row = i + 1)
            color_canvas.create_rectangle(0, 0, 15, 15, outline = '#000000', fill = COLORS[i])
            
            Label(self.realLegFrame, text = map.name).grid(column = 2, row = i + 1, sticky = 'W')
        
        self.master.varSelectedMap.set(self.master.maps.maps[0].orig)

        return 0