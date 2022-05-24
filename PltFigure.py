from tkinter import Tk, Frame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from Limits import Limits

class PltFigure(plt.Figure):
    def __init__(self, frame: Frame, window: Tk):
        self.frame = frame
        self.window = window
        super().__init__(figsize = (int(self.window.winfo_width() * 0.55) / 96,
                                    int(self.window.winfo_height() * 0.65) / 96),
                         dpi = 96)
        self.subplots_adjust(top = 0.98)
        self.canvas = FigureCanvasTkAgg(self, master = frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame)
        self.toolbar.update()
        self.canvas.mpl_connect('button_press_event', window.mouseEvent)
        
        self.initPlot()
    
    def initPlot(self, data: list = None):
        self.plot1 = self.add_subplot(111,
                                      xlabel = 'Wavenumber (cm-1)', 
                                      ylabel = 'Raman Intensity')
        
        self.axes[0].set_xlim(xmin = 0, xmax = 100)
        self.axes[0].set_ylim(ymin = 0, ymax = 100)
        self.drawCanvas()
        self.saveLimits()
    
    def saveLimits(self):
        self.plotBounds = self.plot1.get_position()
        self.plotLimits = Limits(self.axes[0])
    
    def getLimits(self):
        return self.plotBounds, self.plotLimits
    
    def drawCanvas(self):
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
    
    def reInitPlot(self):
        self.clear()
        self.plot1 = self.add_subplot(111,
                                      xlabel = 'Wavenumber (cm-1)', 
                                      ylabel = 'Raman Intensity')

        return self.plot1
    
    def changeXZoom(self, xmin: float = None, xmax: float = None):
        if (xmin, xmax) == (None, None):
            self.axes[0].autoscale(axis = 'x')
            return 0
        
        self.axes[0].set_xlim(xmin, xmax)
        self.saveLimits()
        return 0
    
    def changeYZoom(self, ymin: float = None, ymax: float = None):
        if (ymin, ymax) == (None, None):
            self.axes[0].autoscale(axis = 'y')
            return 0
        
        self.axes[0].set_ylim(ymin, ymax)
        self.saveLimits()
        return 0
