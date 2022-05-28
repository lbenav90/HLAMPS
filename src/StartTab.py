from settings import COLORS
from tkinter import Tk, Button
from tkinter.ttk import Frame, Notebook

class StartTab(Frame):
    ''' Start tab is an almost empty tab '''
    def __init__(self, notebook: Notebook):
        super().__init__(notebook)
        self.notebook = notebook
        self.window = notebook.window # GUI class instance
        self.resetButton = Button(self, text = 'Restore program settings', 
                                  command = lambda: [self.window.resetGUI(), 
                                                     self.window.legFrame.updateLegend()]
                                  ).grid(column = 3, row = 0, sticky = 'w')
    
    def clearTab(self):
        ''' Noting to clear '''
        pass
    
    def discardChanges(self):
        ''' No unsaved changes possible '''
        return True
        
    def displaySpectra(self, window: Tk = None):
        ''' Display current average spectra with the Tab specific plots. '''
        if window is None:
            window = self.window
            
        if window.maps.isEmpty():
            return 1
        
        # Get current average spectra
        window.getAverageSpectra()
        
        # Reinitialize plot
        plot = window.plotFrame.figure.reInitPlot()
        
        for col, spectra in window.averages.enumerate():  
            # Plot all average spectra
            plot.plot(spectra[1][0],spectra[1][1], 
                      color = COLORS[col % len(COLORS)])

        window.plotFrame.figure.saveLimits()
        window.plotFrame.figure.drawCanvas()
        
        self.window.statFrame.getLimits()
        
        return 0

    def handleMouseEvent(self, x: float, y: float):
        ''' No mouse event handling needed in this Tab '''
        return 0
