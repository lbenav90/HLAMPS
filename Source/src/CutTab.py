import os
from functools import partial
from idlelib.tooltip import Hovertip
from tkinter.ttk import Frame, Notebook
from settings import TEMP_PATH, COLORS, IMAGES
from .Global_Functions import isNumber, findClosest
from tkinter.messagebox import showerror, askyesno, showinfo
from tkinter import StringVar, BooleanVar, Label, Entry, PhotoImage, Button

class CutTab(Frame):
    ''' Contains variables and widgets for the Cut Spectra Tab '''
    def __init__(self, notebook: Notebook):
        super().__init__(notebook)
        self.notebook = notebook
        self.window = notebook.window

        self.varInitCut = StringVar(value = '')
        self.varFinCut = StringVar(value = '')

        # Plot data collection status
        self.selectOn = BooleanVar(value = False)

        self.configureLayout()
        self.allChangesSaved = True
        
        # Trace variables for changes
        self.varInitCut.trace('w', self.changeMade)
        self.varFinCut.trace('w', self.changeMade)
    
    def clearTab(self):
        ''' Reinitialize tab '''
        self.varInitCut.set('')
        self.varFinCut.set('')
        self.selectOn.set(False)
        self.allChangesSaved = True
        self.initCut.config(bg = '#ffffff')
        self.finCut.config(bg = '#ffffff')
        return 0
    
    def discardChanges(self):
        ''' Upon a tab change, checks for unsaved changes. If present,
        asks for confirmation. '''
        if self.allChangesSaved:
            self.clearTab()
            return True
        
        if askyesno('Warning', 'Discard all unsaved changes?'):
            self.clearTab()
            return True
        else:
            return False
    
    def changeMade(self, name, index, trigger):
        ''' Upon a new change, reflect the unsaved change '''
        self.allChangesSaved = False
        return 0
    
    def configureLayout(self):
        ''' Configures the tab layout '''
        Label(self, text = 'Start: ').grid(column = 0, row = 0, sticky = 'E')
        Label(self, text = 'End: ').grid(column = 0, row = 1, sticky = 'E')
        
        # Entry widgets for new frequency limits
        self.initCut = Entry(self, textvariable = self.varInitCut, validate = 'all', 
                             validatecommand = (self.register(isNumber), '%P'))
        
        self.initCut.grid(column = 1, row = 0, sticky = 'W')
        
        self.finCut = Entry(self, textvariable = self.varFinCut, validate = 'all', 
                            validatecommand = (self.register(isNumber), '%P'))
        
        self.finCut.grid(column = 1, row = 1, sticky = 'W')
        
        # Configure buttons to delete current limit
        self.clearLimPhoto = PhotoImage(file = rf'{IMAGES}/xIcon.png')
        
        self.btnCutCleanInit = Button(self, command = partial(self.clearLimit, 0), image = self.clearLimPhoto)
        self.btnCutCleanInit.grid(column = 3, row = 0, sticky = 'w')
        Hovertip(self.btnCutCleanInit, 
                 'Delete lower limit', 
                 hover_delay = 1000)
        
        self.btnCutCleanFin = Button(self, command = partial(self.clearLimit, 1), image = self.clearLimPhoto)
        self.btnCutCleanFin.grid(column = 3, row = 1, sticky = 'w')
        Hovertip(self.btnCutCleanFin, 
                 'Delete higher limit', 
                 hover_delay = 1000)
        
        # Spacers
        Label(self, text = ' ').grid(column = 4, row = 0)
        Label(self, text = ' ').grid(column = 4, row = 1)
        
        # Tab buttons
        self.btnCutShow = Button(self, text = 'Show', command = self.showCutSpectra)
        self.btnCutShow.grid(column = 5, row = 0, sticky = 'w')
        Hovertip(self.btnCutShow, 
                 'Show selected range', 
                 hover_delay = 1000)
        
        self.btnCutRest = Button(self, text = 'Restore', command = self.restoreView)
        self.btnCutRest.grid(column = 6, row = 0, sticky = 'w')
        Hovertip(self.btnCutRest, 
                 'Show selected range', 
                 hover_delay = 1000)
        
        self.btnCutSelect = Button(self, text = 'Select', command = self.selectLimits)
        self.btnCutSelect.grid(column = 7, row = 0, sticky = 'w')
        Hovertip(self.btnCutSelect, 
                 'Define limits in graph', 
                 hover_delay = 1000)
        
        self.btnCutSave = Button(self, text = 'Save cut maps', command = self.saveCutMaps)
        self.btnCutSave.grid(column = 5, columnspan = 3, row = 1, sticky = 'w')
        Hovertip(self.btnCutSave, 
                 'Save current files as a map file', 
                 hover_delay = 1000)
        return 0
    
    def showCutSpectra(self):
        ''' Shows the current limits when applied, but cahnges are not saved. '''
        if self.window.maps.isEmpty():
            return 1
        
        # Only show when both limits are defined
        # Maybe if there is an undefined limit, use the default?
        if self.varInitCut.get() == '' or self.varFinCut.get() == '':
            showerror('Error', 
                      'Undefined limits')
            return 1
        
        start = float(self.varInitCut.get())
        end = float(self.varFinCut.get())
        
        # Show the current limits applied as a zoom change in the X direction
        self.window.plotFrame.figure.changeXZoom(xmin = start,
                                                 xmax = end)
        self.window.plotFrame.figure.changeYZoom()
        self.window.plotFrame.figure.drawCanvas()
        
        self.window.statFrame.getLimits()
        
        # Turns OFF data collection
        if self.selectOn.get():
            self.selectOn.set(False)
            self.initCut.config(bg = '#ffffff')
            self.finCut.config(bg = '#ffffff')
        
        return 0
    
    def restoreView(self):
        ''' Restores the view to the default per the last saved changes '''
        if self.window.maps.isEmpty():
            return 1
        
        self.window.plotFrame.figure.changeXZoom()
        self.window.plotFrame.figure.changeYZoom()
        self.window.plotFrame.figure.drawCanvas()
        
        self.window.statFrame.getLimits()
        
        return 0 
    
    def selectLimits(self):
        ''' Changes the current data selection status. '''
        if self.selectOn.get():
            # If ON, turns OFF and reverts colors to white
            self.selectOn.set(False)
            self.initCut.config(bg = '#ffffff')
            self.finCut.config(bg = '#ffffff')
        else:
            # If OFF, turns ON and sets initial Entry widget color
            self.selectOn.set(True)
            self.initCut.config(bg = '#95CCD9')
        return 0
    
    def saveCutMaps(self):
        ''' Saves the maps with the current limits applied. '''
        if self.window.maps.isEmpty():
            return 1
    
        # Shows the current limits applied
        self.showCutSpectra()
        
        # Asks for confirmation of the result
        response = askyesno('Result', 
                            'Do you accept the cut spectra?')
        
        if not response:
            # If not, restore the original view and return
            self.restoreView()
            return 1
        
        start = float(self.varInitCut.get())
        end = float(self.varFinCut.get())
        
        startIndex = None
        endIndex = None
        
        for map in self.window.maps:
            os.chdir(map.directory)
            
            # Load the map data
            mapData = self.window.readMap(map)
            
            # Add a suffix to denote cut, but only once
            if '_cut' not in map.name: 
                map.name = map.name + '_cut'
            
            # Define cut indexes if not defined
            if startIndex is None:
                startIndex = findClosest(start, mapData['freq'])
                endIndex = findClosest(end, mapData['freq']) + 1
            
            # For each key in the map data, slice the value accoding to the indexes
            for key in mapData:
                mapData[key] = mapData[key][startIndex: endIndex]
            
            # Writes the new map data to the temp and original folder
            self.window.writeMap(map, mapData)
        
        # Update legend to reflect new names
        self.window.legFrame.updateLegend()
        
        # Logs process
        self.window.insertLog('cut_saveMap')
        
        # Display the new limits in status Frame
        self.window.statFrame.getLimits()
        
        self.allChangesSaved = True

        showinfo('Save', 
                 'Cut maps saved successfully')
        os.chdir(TEMP_PATH)
        return 0
    
    def clearLimit(self, index):
        ''' Clears one of the limit variables. Index 0 = Initial - Index 1 = Final. '''
        if index:
            self.varFinCut.set('')
            if self.selectOn.get():
                self.initCut.config(bg = '#ffffff')
                self.finCut.config(bg = '#95CCD9')
        else:
            self.varInitCut.set('')
            if self.selectOn.get():
                self.initCut.config(bg = '#95CCD9')
                self.finCut.config(bg = '#ffffff')
        return 0
        
        # Display new maps
        self.displaySpectra()
        
    def displaySpectra(self, window = None):
        ''' Displays the average spectra with specific need of the Cut Tab. '''
        if window is None:
            window = self.window
            
        if window.maps.isEmpty():
            return 1
        
        # Get the current average spectra
        window.getAverageSpectra()
        
        # Reinitialize plot
        plot = window.plotFrame.figure.reInitPlot()
        
        # Plot the spectra
        for col, spectra in window.averages.enumerate():  
            plot.plot(spectra[1][0],spectra[1][1], 
                      color = COLORS[col % len(COLORS)])
        
        # Show a vertical line for each collected limit
        if self.varInitCut.get() != '':
            plot.axvline(x = float(self.varInitCut.get()))
        if self.varFinCut.get() != '':
            plot.axvline(x = float(self.varFinCut.get()))

        window.plotFrame.figure.saveLimits()
        window.plotFrame.figure.drawCanvas()
        
        # Display limits in status Frame
        self.window.statFrame.getLimits()

    def handleMouseEvent(self, x: float, y: float):
        ''' Function triggered upon a mouse event on the plot, when the Cut tab is active. '''
        # If collection is OFF, return
        if not self.selectOn.get():
            return 1
        
        # Detect which limit is being collected and set it, changing Entry colors to next collection
        elif self.initCut['bg'] == '#95CCD9' and (self.varFinCut.get() == '' or x < float(self.varFinCut.get())):
            self.varInitCut.set(f'{x:.2f}')
            self.initCut.config(bg = '#ffffff')
            self.finCut.config(bg = '#95CCD9')
            
        elif self.finCut['bg'] == '#95CCD9' and x > float(self.varInitCut.get()):
            self.varFinCut.set(f'{x:.2f}')
            self.initCut.config(bg = '#95CCD9')
            self.finCut.config(bg = '#ffffff')
        
        self.displaySpectra()
        return 0
