import os
import numpy as np
from settings import TEMP_PATH, COLORS
from tkinter.ttk import Frame, Notebook
from tkinter.messagebox import showinfo, askyesno
from tkinter import Tk, StringVar, BooleanVar, Label, Entry, Button

class ShiftTab(Frame):
    ''' Contains all variables and widgets of the Shift Spectra Tab '''
    def __init__(self, notebook: Notebook):
        super().__init__(notebook)
        self.notebook = notebook
        self.window = notebook.window

        # Variables of data and reference to perform shift
        self.actual = StringVar(value = ''), StringVar(value = '')
        self.reference = StringVar(value = ''), StringVar(value = '')

        self.selectOn = BooleanVar(value = False)
        self.configureLayout()
        self.allChangesSaved = True
        
        # Trace the reference variables to detect unsaved changes
        self.reference[0].trace('w', self.changeMade)
        self.reference[1].trace('w', self.changeMade)
        return 0
    
    def clearTab(self):
        ''' Reinitialize tab '''
        self.initPoints()
        self.selectOn.set(False)
        self.allChangesSaved = True
        return 0
    
    def discardChanges(self):
        ''' Upon a tab change, checks for unsaved changes. If present,
        asks for confirmation. '''
        if self.allChangesSaved:
            return True
        
        if askyesno('Warning', 'Discard all unsaved changes?'):
            self.clearTab()
            return True
        else:
            return False
    
    def changeMade(self, name, index, trigger):
        ''' Function triggered everytime a reference variable is changed '''
        self.allChangesSaved = False
        return 0
    
    def initPoints(self):
        ''' Initialize real and reference points' variables '''
        self.actual[0].set('') 
        self.actual[1].set('') 
        self.reference[0].set('') 
        self.reference[1].set('')
        return 0
    
    def configureLayout(self):
        ''' Configure tab's widget layout '''
        Label(self, text = 'Selected point').grid(column = 0, columnspan = 2, row = 4)
        Label(self, text = 'X').grid(column = 0,  row = 5)
        Label(self, text = 'Y').grid(column = 1,  row = 5)
        
        # Read-only entries for the actual selected data point
        self.entry_actualX = Entry(self, textvariable = self.actual[0], width = 10)
        self.entry_actualX.grid(column = 0, row = 6)
        self.entry_actualX.config(state = 'readonly')
        
        self.entry_actualY = Entry(self, textvariable = self.actual[1], width = 10)
        self.entry_actualY.grid(column = 1, row = 6)
        self.entry_actualY.config(state = 'readonly')
        
        Label(self, text = 'Reference point').grid(column = 0, columnspan = 2, row = 7)
        Label(self, text = 'X').grid(column = 0,  row = 8)
        Label(self, text = 'Y').grid(column = 1,  row = 8)

        # Regular entries to change the actual selectes point to a reference  
        self.entry_refX = Entry(self, textvariable = self.reference[0], width = 10,
                                validate = 'all', validatecommand = (self.register(self.isNumber), '%P'))
        self.entry_refX.grid(column = 0, row = 9)
        
        self.entry_refY = Entry(self, textvariable = self.reference[1], width = 10,
                                validate = 'all', validatecommand = (self.register(self.isNumber), '%P'))
        self.entry_refY.grid(column = 1, row = 9)
        
        # Buttons
        self.btnSelectXY = Button(self, text = 'Select', command = self.selectXY)
        self.btnSelectXY.grid(column = 2, row = 5, rowspan = 2, sticky ='sw')
        
        self.btnApplyShift = Button(self, text = 'Apply', command = self.applyShift)
        self.btnApplyShift.grid(column = 2, row = 8, rowspan = 2, sticky ='sw')
    
    def selectXY(self):
        ''' Change selection status and change button color to reflect it '''
        if self.window.maps.isEmpty():
            return 1
    
        self.selectOn.set(not self.selectOn.get())
        
        self.btnSelectXY.config(bg = '#f0f0f0' * (not self.selectOn.get()) 
                                   + '#95CCD9' *      self.selectOn.get())      
        return 0
    
    @staticmethod
    def isNumber(s):
        ''' For Entry input validation '''
        return s.isdigit() or s.replace('.', '0', 1).isdigit() or s == '' 

    def handleMouseEvent(self, x: float, y: float):
        ''' Function triggered upon a mouse event on the plot, when the Shift tab is active. '''
        if not self.selectOn.get():
            return 1
        self.actual[0].set(f'{x:.2f}')
        self.actual[1].set(f'{y:.2f}')
        self.reference[0].set(f'{x:.2f}')
        self.reference[1].set(f'{y:.2f}')
        self.selectXY()
        self.displaySpectra()
        return 0
    
    def applyShift(self):
        ''' Apply the shift to the actual reference points, saving the shifted Map elements '''
        if self.window.maps.isEmpty():
            return 1
        
        # If selection is ON, turn OFF
        if self.selectOn.get(): self.selectXY() 
            
        # Define shifts
        shiftX = float(self.reference[0].get()) - float(self.actual[0].get())
        shiftY = float(self.reference[1].get()) - float(self.actual[1].get())
        
        # Set the actual data point to the reference to show the shift
        self.actual[0].set(self.reference[0].get())
        self.actual[1].set(self.reference[1].get())
        
        # For potentially long processes, the progress bar in the Status Frame is used
        progressStep = 300 / (self.window.maps.length() * self.window.maps[0].spectraNum)
        self.window.statFrame.progressLabel.config(text = 'Processing:   Saving shifted maps')
        
        for map in self.window.maps:
            os.chdir(map.directory)
            
            #Get the map data as a dict
            mapData = self.window.readMap(map)
            
            # Add a suffix to filename to denote the change, but only once
            if '_shifted' not in map.name:
                name = map.name + '_shifted'
            
            shiftedData = {}
            for key, intensities in mapData.values():                
                if key == 'freq':
                    shiftedData[key] = list(np.array(intensities) + shiftX)
                else:
                    shiftedData[key] = list(np.array(intensities) + shiftY)       
                
                #Update progress bar
                self.window.statFrame.progressBar['value'] += progressStep
                self.window.statFrame.update_idletasks()
            map.name = name
            
            # Write the resulting map to temp folder and corresponding directory
            self.window.writeMap(map, mapData)
        
        # Reset progress bar
        self.window.statFrame.progressBar['value'] = 0
        self.window.statFrame.progressLabel.config(text = 'Processing: ')
        
        # Update legend in Legend Frame
        self.window.legFrame.updateLegend()
        
        # Reinitialize actual and reference points
        self.initPoints()
        
        # Display new spectra
        self.displaySpectra()
        
        # Log process
        self.window.insertLog('shift')
        
        showinfo(title = 'Save',  message = 'Shifted maps saved successfully')
        os.chdir(TEMP_PATH)
        self.allChangesSaved = True
        return 0
    
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
        
        # If an actual data point was selected, plot it with a big X
        if self.actual[0].get() != '':
            plot.plot(float(self.actual[0].get()), 
                      float(self.actual[1].get()), 'kx', markersize = 20)

        # Save new limits
        window.plotFrame.figure.saveLimits()
        window.plotFrame.figure.drawCanvas()
        
        # Update Status Frame
        self.window.statFrame.getLimits()
        return 0
