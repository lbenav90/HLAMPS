import os
import numpy as np
from settings import TEMP_PATH, COLORS
from tkinter.ttk import Frame, Notebook
from tkinter.messagebox import showinfo, askyesno
from tkinter import StringVar, BooleanVar, Label, Entry, Button

class ShiftTab(Frame):
    def __init__(self, master: Notebook):
        super().__init__(master)
        self.master = master
        self.window = master.master
        self.actual = StringVar(value = ''), StringVar(value = '')
        self.reference = StringVar(value = ''), StringVar(value = '')
        self.selectOn = BooleanVar(value = False)
        self.configureLayout()
        self.allChangesSaved = True
        
        self.reference[0].trace('w', self.changeMade)
        self.reference[1].trace('w', self.changeMade)
    
    def clearTab(self):
        self.initPoints()
        self.selectOn.set(False)
        self.allChangesSaved = True
    
    def discardChanges(self):
        if self.allChangesSaved:
            return True
        
        if askyesno('Warning', 'Discard all unsaved changes?'):
            self.clearTab()
            return True
        else:
            return False
    
    def changeMade(self, x, y, z):
        self.allChangesSaved = False
    
    def initPoints(self):
        self.actual[0].set('') 
        self.actual[1].set('') 
        self.reference[0].set('') 
        self.reference[1].set('') 
    
    def configureLayout(self):
        Label(self, text = 'Selected point').grid(column = 0, columnspan = 2, row = 4)
        Label(self, text = 'X').grid(column = 0,  row = 5)
        Label(self, text = 'Y').grid(column = 1,  row = 5)
        
        self.entry_actualX = Entry(self, textvariable = self.actual[0], width = 10)
        self.entry_actualX.grid(column = 0, row = 6)
        self.entry_actualX.config(state = 'readonly')
        
        self.entry_actualY = Entry(self, textvariable = self.actual[1], width = 10)
        self.entry_actualY.grid(column = 1, row = 6)
        self.entry_actualY.config(state = 'readonly')
        
        Label(self, text = 'Reference point').grid(column = 0, columnspan = 2, row = 7)
        Label(self, text = 'X').grid(column = 0,  row = 8)
        Label(self, text = 'Y').grid(column = 1,  row = 8)
        
        self.entry_refX = Entry(self, textvariable = self.reference[0], width = 10,
                                validate = 'all', validatecommand = (self.register(self.isNumber), '%P'))
        self.entry_refX.grid(column = 0, row = 9)
        
        self.entry_refY = Entry(self, textvariable = self.reference[1], width = 10,
                                validate = 'all', validatecommand = (self.register(self.isNumber), '%P'))
        self.entry_refY.grid(column = 1, row = 9)
        
        self.btnSelectXY = Button(self, text = 'Select', command = self.selectXY)
        self.btnSelectXY.grid(column = 2, row = 5, rowspan = 2, sticky ='sw')
        
        self.btnApplyShift = Button(self, text = 'Apply', command = self.applyShift)
        self.btnApplyShift.grid(column = 2, row = 8, rowspan = 2, sticky ='sw')
    
    def selectXY(self):
        if self.window.maps.isEmpty():
            return 1
    
        self.selectOn.set(not self.selectOn.get())
        
        self.btnSelectXY.config(bg = '#f0f0f0' * (not self.selectOn.get()) 
                                   + '#95CCD9' *      self.selectOn.get())      
        return 0
    
    @staticmethod
    def isNumber(s):
        return s.isdigit() or s.replace('.', '0', 1).isdigit() or s == '' 

    def handleMouseEvent(self, x, y):
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
        if self.window.maps.isEmpty():
            return 1
        
        if self.selectOn.get(): self.selectXY() 
            
        shiftX = float(self.reference[0].get()) - float(self.actual[0].get())
        shiftY = float(self.reference[1].get()) - float(self.actual[1].get())
        
        self.actual[0].set(self.reference[0].get())
        self.actual[1].set(self.reference[1].get())
        
        progressStep = 300 / (self.window.maps.length() * self.window.maps[0].spectraNum)
        self.window.statFrame.progressLabel.config(text = 'Processing:   Saving shifted maps')
        
        for map in self.window.maps:
            os.chdir(map.directory)
            
            mapData = self.window.readMap(map)
            
            if '_shifted' not in map.name:
                name = map.name + '_shifted'
            
            for key in mapData:
                self.window.statFrame.progressBar['value'] += progressStep
                self.window.statFrame.update_idletasks()
                
                if key == 'freq':
                    mapData[key] = list(np.array(mapData[key]) + shiftX)
                else:
                    mapData[key] = list(np.array(mapData[key]) + shiftY)       
            map.name = name
            
            self.window.writeMap(map, mapData)
        
        self.window.statFrame.progressBar['value'] = 0
        self.window.statFrame.progressLabel.config(text = 'Processing: ')
        
        self.window.legFrame.updateLegend()
        
        self.initPoints()
        
        self.displaySpectra()
        
        self.window.insertLog('shift')
        
        showinfo(title = 'Save',  message = 'Shifted maps saved successfully')
        os.chdir(TEMP_PATH)
        self.allChangesSaved = True
        return 0
    
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
        
        if self.actual[0].get() != '':
            plot.plot(float(self.actual[0].get()), 
                      float(self.actual[1].get()), 'kx', markersize = 20)

        window.plotFrame.figure.saveLimits()
        window.plotFrame.figure.drawCanvas()
        
        self.window.statFrame.getLimits()
        
        return 0
