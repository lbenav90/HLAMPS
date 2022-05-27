from Limits import Limits
from tkinter import Tk, Frame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

class PltFigure(plt.Figure):
    ''' Contains the methods for the matplotlib plot and its update functions '''
    def __init__(self, frame: Frame, window: Tk):
        self.frame = frame
        self.window = window
        # Initialize Figure element
        super().__init__(figsize = (int(self.window.winfo_width() * 0.55) / 96,
                                    int(self.window.winfo_height() * 0.65) / 96),
                         dpi = 96)
        self.subplots_adjust(top = 0.98)
        # Add the Tkinter backend of matplotlib and navigation toolbar
        self.canvas = FigureCanvasTkAgg(self, master = frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame)
        self.toolbar.update()

        # Connect mouse input in plot to collect data
        self.canvas.mpl_connect('button_press_event', window.mouseEvent)
        
        self.initPlot()
    
    def initPlot(self, data: list = None):
        ''' Initialize an empty plot '''
        self.plot1 = self.add_subplot(111,
                                      xlabel = 'Wavenumber (cm-1)', 
                                      ylabel = 'Raman Intensity')
        
        # Set arbitrary limits
        self.axes[0].set_xlim(xmin = 0, xmax = 100)
        self.axes[0].set_ylim(ymin = 0, ymax = 100)
        self.drawCanvas()

        # Save current limits to Limits class and counds
        self.saveLimits()
        return 0
    
    def saveLimits(self):
        ''' Save plot position in Figure and save axes limits to Limits class'''
        self.plotBounds = self.plot1.get_position()
        self.plotLimits = Limits(self.axes[0])
        return 0
    
    def getLimits(self):
        ''' Returns plot limits and bounds '''
        return self.plotBounds, self.plotLimits
    
    def drawCanvas(self):
        ''' Draw the plot canvas '''
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        return 0
    
    def reInitPlot(self):
        ''' Reinitialize plot and return it'''
        self.clear()
        self.plot1 = self.add_subplot(111,
                                      xlabel = 'Wavenumber (cm-1)', 
                                      ylabel = 'Raman Intensity')

        return self.plot1
    
    def changeXZoom(self, xmin: float = None, xmax: float = None):
        ''' Change zoom for x axis. If no limits are given, it autoscales it'''
        if (xmin, xmax) == (None, None):
            self.axes[0].autoscale(axis = 'x')
            return 0
        
        self.axes[0].set_xlim(xmin, xmax)

        # Save new limits
        self.saveLimits()
        return 0
    
    def changeYZoom(self, ymin: float = None, ymax: float = None):
        ''' Change zoom for y axis. If no limits are given, it autoscales it'''
        if (ymin, ymax) == (None, None):
            self.axes[0].autoscale(axis = 'y')
            return 0
        
        self.axes[0].set_ylim(ymin, ymax)
        # Save new limits
        self.saveLimits()
        return 0
