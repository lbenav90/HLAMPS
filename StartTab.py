from settings import COLORS
from tkinter import Button
from tkinter.ttk import Frame

class StartTab(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.window = master.master # GUI class instance
        self.resetButton = Button(self, text = 'Restore program settings', 
                                     command = lambda: [self.master.master.resetGUI(), 
                                                        self.master.master.legFrame.updateLegend()]
                                     ).grid(column = 3, row = 0, sticky = 'w')
    
    def clearTab(self):
        pass
    
    def discardChanges(self):
        return True
        
    def displaySpectra(self, window = None):
        if window is None:
            window = self.master.master
            
        if window.maps.isEmpty():
            return 1
        
        window.getAverageSpectra()
        
        plot = window.plotFrame.figure.reInitPlot()
        
        for col, spectra in window.averages.enumerate():  
            plot.plot(spectra[1][0],spectra[1][1], 
                      color = COLORS[col % len(COLORS)])

        window.plotFrame.figure.saveLimits()
        window.plotFrame.figure.drawCanvas()
        
        self.window.statFrame.getLimits()
        
        return 0

    def handleMouseEvent(self, x, y):
        #do nothing
        return 0
