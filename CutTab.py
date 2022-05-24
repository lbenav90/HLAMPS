import os
from functools import partial
from idlelib.tooltip import Hovertip
from tkinter.ttk import Frame, Notebook
from settings import TEMP_PATH, COLORS, IMAGES
from tkinter.messagebox import showerror, askyesno, showinfo
from tkinter import StringVar, BooleanVar, Label, Entry, PhotoImage, Button

class CutTab(Frame):
    def __init__(self, master: Notebook):
        super().__init__(master)
        self.master = master
        self.window = master.master
        self.varInitCut = StringVar(value = '')
        self.varFinCut = StringVar(value = '')
        self.selectOn = BooleanVar(value = False)
        self.configureLayout()
        self.allChangesSaved = True
        
        self.varInitCut.trace('w', self.changeMade)
        self.varFinCut.trace('w', self.changeMade)
    
    def clearTab(self):
        self.varInitCut.set('')
        self.varFinCut.set('')
        self.selectOn.set(False)
        self.allChangesSaved = True
        self.initCut.config(bg = '#ffffff')
        self.finCut.config(bg = '#ffffff')
    
    def discardChanges(self):
        if self.allChangesSaved:
            self.clearTab()
            return True
        
        if askyesno('Warning', 'Discard all unsaved changes?'):
            self.clearTab()
            return True
        else:
            return False
    
    def changeMade(self, x, y, z):
        self.allChangesSaved = False
    
    def configureLayout(self):
        Label(self, text = 'Start: ').grid(column = 0, row = 0, sticky = 'E')
        Label(self, text = 'End: ').grid(column = 0, row = 1, sticky = 'E')
        
        self.initCut = Entry(self, textvariable = self.varInitCut,
                                validate = 'all', 
                                validatecommand = (self.register(self.isNumber), '%P'))
        
        self.initCut.grid(column = 1, row = 0, sticky = 'W')
        
        self.finCut = Entry(self, textvariable = self.varFinCut,
                               validate = 'all', 
                               validatecommand = (self.register(self.isNumber), '%P'))
        
        self.finCut.grid(column = 1, row = 1, sticky = 'W')
        
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
        
        Label(self, text = ' ').grid(column = 4, row = 0)
        Label(self, text = ' ').grid(column = 4, row = 1)
        
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
    
    def showCutSpectra(self):
        if self.window.maps.isEmpty():
            return 1
        
        if self.varInitCut.get() == '' or self.varFinCut.get() == '':
            showerror('Error', 
                      'Undefined limits')
            return 1
        
        start = float(self.varInitCut.get())
        end = float(self.varFinCut.get())
        
        self.window.plotFrame.figure.changeXZoom(xmin = start,
                                                 xmax = end)
        self.window.plotFrame.figure.changeYZoom()
        self.window.plotFrame.figure.drawCanvas()
        
        self.window.statFrame.getLimits()
        
        if self.selectOn.get():
            self.selectOn.set(False)
            self.initCut.config(bg = '#ffffff')
            self.finCut.config(bg = '#ffffff')
        
        return 0
    
    def restoreView(self):
        if self.window.maps.isEmpty():
            return 1
        
        if self.varInitCut.get() == '' or self.varFinCut.get() == '':
            showerror('Error', 
                      'Full data shown')
            return 1
        
        self.window.plotFrame.figure.changeXZoom()
        self.window.plotFrame.figure.changeYZoom()
        self.window.plotFrame.figure.drawCanvas()
        
        self.window.statFrame.getLimits()
        
        return 0
    
    @staticmethod
    def findClosest(value, sample):
        '''
        Given a value (float), finds the index for the nearest value in a list of samples
        '''
        minDif = 1e9
        minIndex = 0
        for i in range(len(sample)):
            dif = abs(value - sample[i])
            if dif < minDif:
                minDif = dif
                minIndex = i
        return minIndex
    
    @staticmethod
    def isNumber(s):
        return s.isdigit() or s.replace('.', '0', 1).isdigit() or s == '' 
    
    def selectLimits(self):
        if self.selectOn.get():
            self.selectOn.set(False)
            self.initCut.config(bg = '#ffffff')
            self.finCut.config(bg = '#ffffff')
        else:
            self.selectOn.set(True)
            self.initCut.config(bg = '#95CCD9')
        return 0
    
    def saveCutMaps(self):
        if self.window.maps.isEmpty():
            return 1
    
        self.showCutSpectra()
        
        response = askyesno('Result', 
                            'Do you accept the cut spectra?')
        
        if not response:
            self.restoreView()
            return 1
        
        start = float(self.varInitCut.get())
        end = float(self.varFinCut.get())
        
        startIndex = None
        endIndex = None
        
        for map in self.window.maps:
            os.chdir(map.directory)
            
            mapData = self.window.readMap(map)
            
            if '_cut' not in map.name: 
                map.name = map.name + '_cut'
            
            if startIndex is None:
                startIndex = self.findClosest(start, mapData['freq'])
                endIndex = self.findClosest(end, mapData['freq']) + 1
            
            for key in mapData:
                mapData[key] = mapData[key][startIndex: endIndex]
            
            self.window.writeMap(map, mapData)
        
        self.window.legFrame.updateLegend()
        
        self.window.insertLog('cut_saveMap')
        
        showinfo('Save', 
                 'Cut maps saved successfully')
        os.chdir(TEMP_PATH)
        
        self.window.statFrame.getLimits()
        
        self.allChangesSaved = True
        return 0
    
    def clearLimit(self, limIndex):
        if limIndex == 0:
            self.varInitCut.set('')
            if self.selectOn.get():
                self.initCut.config(bg = '#95CCD9')
                self.finCut.config(bg = '#ffffff')
        else:
            self.varFinCut.set('')
            if self.selectOn.get():
                self.initCut.config(bg = '#ffffff')
                self.finCut.config(bg = '#95CCD9')
        
        self.displaySpectra()
        
    def displaySpectra(self, window = None):
        if window is None:
            window = self.window
            
        if window.maps.isEmpty():
            return 1
        
        window.getAverageSpectra()
        
        plot = window.plotFrame.figure.reInitPlot()
        
        for col, spectra in window.averages.enumerate():  
            plot.plot(spectra[1][0],spectra[1][1], 
                      color = COLORS[col % len(COLORS)])
        
        if self.varInitCut.get() != '':
            plot.axvline(x = float(self.varInitCut.get()))
        if self.varFinCut.get() != '':
            plot.axvline(x = float(self.varFinCut.get()))

        window.plotFrame.figure.saveLimits()
        window.plotFrame.figure.drawCanvas()
        
        self.window.statFrame.getLimits()

    def handleMouseEvent(self, x, y):
        if not self.selectOn.get():
            return 1
        
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
