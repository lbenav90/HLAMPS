import os
import numpy as np
from Anchors import Anchors
from functools import partial
import matplotlib.pyplot as plt
from idlelib.tooltip import Hovertip
from settings import TEMP_PATH, COLORS
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, askyesno, showerror
from tkinter import Button, BooleanVar, Frame, Checkbutton, ttk

class SubtractTab(ttk.Frame):
    def __init__(self, master: ttk.Notebook):
        super().__init__(master)
        self.master = master
        self.window = master.master ### GUI instance
        self.anchors = Anchors()
        self.anchorBut = []
        self.showSub = BooleanVar(value = False)
        self.varChkSubFig = BooleanVar(value = False)
        self.varChkOffset = BooleanVar(value = False)
        self.configureLayout()
        self.allChangesSaved = True
    
    def clearTab(self):
        self.anchors.clear()
        self.anchorBut.clear()
        self.displayAnchors()
        self.showSub.set(False)
        self.varChkSubFig.set(False)
        self.varChkOffset.set(False)
        self.allChangesSaved = True
    
    def discardChanges(self):
        if self.allChangesSaved:
            self.clearTab()
            return True
        
        if askyesno('Warning', 'Discard all unsaved changes?'):
            self.clearTab()
            return True
        else:
            return False
    
    def configureLayout(self):
        self.subControl = Frame(self)
        self.subControl.grid(column = 0, row = 0, sticky = 'nw')
        self.subOptions = Frame(self)
        self.subOptions.grid(column = 0, row = 1, sticky = 'nw')
        self.subAnchor = Frame(self)
        self.subAnchor.grid(column = 0, row = 2, sticky = 'nw')
        
        self.btnSubtract = Button(self.subControl, text = 'Subtract', 
                                  command = self.subtractBaseline)
        self.btnSubtract.grid(column = 0, row = 1, pady = 5, padx = 5)
        Hovertip(self.btnSubtract, 
                 'Apply current baseline to all spectra.\n Saves new files and map', 
                 hover_delay = 1000)
        
        self.btnImportBase = Button(self.subControl, text = 'Import', 
                                    command = self.importBaseline)
        self.btnImportBase.grid(column = 1, row = 1, pady = 5, padx = 5)
        Hovertip(self.btnImportBase, 
                 'Import baseline used previously', 
                 hover_delay = 1000)
        
        self.btnShowBase = Button(self.subControl, text = 'Show baseline', 
                                  command = self.displaySpectra)
        self.btnShowBase.grid(column = 2, row = 1, pady = 5, padx = 5)
        Hovertip(self.btnShowBase, 
                 'Shows current baseline', 
                 hover_delay = 1000)
        
        self.btnShowSub = Button(self.subControl, text = 'Show subtracted', 
                                 command = self.showSubtracted)
        self.btnShowSub.grid(column = 3, row = 1, pady = 5, padx = 5)
        Hovertip(self.btnShowSub, 
                 'Shows the current subtracted spectra', 
                 hover_delay = 1000)
        
        self.btnSaveSub = Button(self.subControl, text = 'Save subtracted', 
                                 command = self.saveSubtractedAvg)
        self.btnSaveSub.grid(column = 4, row = 1, pady = 5, padx = 5)
        Hovertip(self.btnSaveSub, 
                 'Saves the current subtracted averages spectra as .txt', 
                 hover_delay = 1000)
        
        self.chkSubFig = Checkbutton(self.subOptions, text = 'Save figures', 
                                     variable = self.varChkSubFig)
        self.chkSubFig.grid(column = 0, row = 2)
        Hovertip(self.chkSubFig, 
                 'Saves subtracted and baselines figures when applying baseline', 
                 hover_delay = 1000)
        
        self.chkSubOffset = Checkbutton(self.subOptions, text = 'Offset subtracted', 
                                        variable = self.varChkOffset)
        self.chkSubOffset.grid(column = 2, row = 2)
        Hovertip(self.chkSubOffset, 
                 'Shows subtracted averages with an offset for clarity', 
                 hover_delay = 1000)
    
    @staticmethod
    def averageBox(values, index, box):
        '''
        Values is a list of floats and the value of interest is at index. 
        Averages the interest value with its box neighbours
        '''
        if index - box < 0 or index + box > len(values) - 1:
            newBox = min(index, box, len(values) - 1 - index)
        else:
            newBox = box
            
        minIndex = index - newBox
        maxIndex = index + newBox
        
        if minIndex == len(values) - 1:
            return sum(values[minIndex:]) / len(values[minIndex:])
        else:
            return sum(values[minIndex: maxIndex + 1]) / (2 * newBox + 1)
    
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
    
    def subtractBaseline(self):
        if self.window.maps.isEmpty():
            return 1 
    
        progressStep = 300 / (self.window.maps.length() * self.window.maps[0].spectraNum)
        self.window.statFrame.progressLabel.config(text = 'Processing:   Saving subtracted maps')
        
        for map in self.window.maps:
            os.chdir(map.directory)
            
            mapData = self.window.readMap(map)
            
            if '_subtracted' not in map.name: 
                map.name = map.name + '_subtracted'
            
            frequencies = mapData.pop('freq')
            
            for key, value in mapData.items():
                
                yAnchors = [self.averageBox(value, 
                                            self.findClosest(anchor, frequencies),
                                                             3) for anchor in self.anchors]   
            
                yBase = np.interp(frequencies, 
                                  self.anchors.asList(),
                                  yAnchors)
                mapData[key] = np.array(mapData[key]) - yBase
                
                self.saveSubSpectra(key, mapData[key], frequencies, map, yAnchors, yBase, figures = self.varChkSubFig.get())
                
                self.window.statFrame.progressBar['value'] += progressStep
                self.window.statFrame.update_idletasks()
            
            mapData['freq'] = frequencies
            self.window.writeMap(map, mapData)
            self.saveBaselineParameters(map)
            
        
        self.window.statFrame.progressBar['value'] = 0
        self.window.statFrame.progressLabel.config(text = 'Processing: ')
        self.window.statFrame.update_idletasks()
        
        self.window.legFrame.updateLegend()
        
        self.window.insertLog('baseline_saveMap')
        
        showinfo('Save',  
                 'Subtracted maps saved successfully')
        
        
        self.window.insertLog('baseline')
        
        self.displaySpectra()
        
        self.allChangesSaved = True    
        return 0

    def saveSubSpectra(self, key, intensities, frequencies, map, yAnchors, yBase, figures):
        
        os.chdir(map.directory)
        os.makedirs(f'{map.orig}_Files/Individual Spectra/Subtracted', exist_ok = True)
        
        os.chdir(f'{map.orig}_Files/Individual Spectra/Subtracted')
        
        x = key[0].split('.')[0]
        y = key[1].split('.')[0]
        
        with open(f'{map.orig}_X_{x}_Y_{y}_subtracted.txt', 'w') as newFile:
            newFile.write('Wavenumber(cm-1)\tIntensity\n')

            for freq, inten in zip(frequencies, intensities):
                newFile.write(f'{freq:.2f}\t{inten:.2f}\n')
        
        if figures:
            os.chdir(map.directory)
            os.makedirs(f'{map.orig}_Files/Figures/Subtracted', exist_ok = True)
            os.chdir(f'{map.orig}_Files/Figures/Subtracted')
            
            fig = plt.Figure()
            plot1 = fig.add_subplot(111, xlabel = 'Wavenumber (cm-1)', ylabel = 'Intensity')
            
            plot1.plot(frequencies, intensities, 'k')
            plot1.plot(self.anchors.asList(), yAnchors, c = 'grey')
            plot1.plot(self.anchors.asList(), yAnchors, ' o', c = 'grey')
            
            fig.savefig(f'{map.orig}_X_{x}_Y_{y}_baseline.png')
            plt.close()
            
            fig = plt.Figure()
            plot1 = fig.add_subplot(111, xlabel = 'Wavenumber (cm-1)', ylabel = 'Intensity')
            
            plot1.plot(frequencies, intensities + yBase, 'k')
            
            fig.savefig(f'{map.orig}_X_{x}_Y_{y}_subtracted.png')
            plt.close()
        
        os.chdir(map.directory)
        return 0

    def saveBaselineParameters(self, map):
        os.chdir(map.directory)
        os.makedirs(f'{map.orig}_Files/Parameters', exist_ok = True)
        
        with open(f'{map.orig}_Files/Parameters/BaselineParameters.txt', 'w') as newFile:
            newFile.write('Linear interpolation between anchor points.\n')
            newFile.write('Intensity value for each anchor is an average intensity of box = 3.\n\n')
            newFile.write('Anchor points (cm-1):')
            
            for anchor in self.anchors:
                newFile.write(f' {anchor:.2f}')
    
        return 0
    
    def importBaseline(self):
        if not self.anchors.isEmpty():
            response = askyesno('Warning',
                                 'Do you want to delete the ' + 
                                 'present baseline anchors?')
            if response:
                self.anchors.clear()
        
        filename = askopenfilename(title = 'Open baseline file', 
                                   initialdir = '/', 
                                   filetypes = (('Text files', '*.txt'),))
    
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        if 'Linear interpolation' not in lines[0]:
            showerror('Wrong file type',
                      'Selected file is not the right ' + 
                      'format for baseline import\n' +
                      'File must be the result of a baseline subtraction')
            return 1
        
        lines = lines[2:]
        
        for line in lines:
            lineSplit = line.split()[3:]
            for anchor in lineSplit:
                self.anchor.addAnchor(anchor)
        
        self.displayAnchors()
        self.displaySpectra()
        
        self.window.insertLog('importbaseline')
    
        return 0
    
    def showSubtracted(self, show = True):
        if self.window.maps.isEmpty():
            return 1
        
        self.window.getAverageSpectra()
        
        for map, spectra in self.window.averages:
            yAnchors = [self.averageBox(spectra[1], 
                                        self.findClosest(anchor, spectra[0]),
                                                         3) for anchor in self.anchors]
            
            yBase = np.interp(spectra[0], self.anchors.asList(), yAnchors)
            
            spectra[1] -= yBase
        
        if show:
            self.showSub.set(True)
            self.displaySpectra()
            self.showSub.set(False)
        return 0
    
    def saveSubtractedAvg(self):
        if self.window.maps.isEmpty():
            return 1
    
        self.showSubtracted(False)
        
        for map, spectra in self.window.averages:
            os.chdir(map.directory)
            
            os.makedirs(f'{map.orig}_Files/Average Spectra', exist_ok = True) 
            
            os.chdir(f'{map.orig}_Files/Average Spectra')
            
            frequencies = spectra[0]
            intensities = spectra[1]
            
            with open(f'{map.name}_subAverage.txt', 'w') as file:
                file.write('Wavenumber(cm-1)\tIntensity\n')
                for freq, inten in zip(frequencies, intensities):
                    file.write(f'{freq:.2f}\t{inten:.2f}\n')
                    
        self.window.insertLog('subAverage_save')
        
        showinfo('Save', 'Subtracted average spectra saved')
        os.chdir(TEMP_PATH)
        return 0
    
    def displaySpectra(self, window = None):
        if window is None:
            window = self.window
            
        if window.maps.isEmpty():
            return 1
        
        if not self.showSub.get():
            window.getAverageSpectra()
        
        plot = window.plotFrame.figure.reInitPlot()
        
        self.anchors.addAnchor(window.averages.averages[0][1][0][ 0])
        self.anchors.addAnchor(window.averages.averages[0][1][0][-1])
        
        for col, spectra in window.averages.enumerate():  
            if self.showSub.get() and self.varChkOffset.get():
                limits = self.window.plotFrame.figure.getLimits()[1].getYLim()
                offset = (limits[1] - limits[0]) * 0.3 * (1 + col)
                plot.plot(spectra[1][0], spectra[1][1] + offset, 
                          color = COLORS[col % len(COLORS)])
            else:
                plot.plot(spectra[1][0], spectra[1][1], 
                          color = COLORS[col % len(COLORS)])
           
            if not self.showSub.get():
                yAnchors = [self.averageBox(spectra[1][1], 
                                             self.findClosest(anchor, spectra[1][0]),
                                                              3) for anchor in self.anchors]
    
                plot.plot(self.anchors.asList(), yAnchors, '#808080')
                plot.plot(self.anchors.asList(), yAnchors, ' o', c = 'grey')

        window.plotFrame.figure.saveLimits()
        window.plotFrame.figure.drawCanvas()
        
        self.window.statFrame.getLimits()
        
        self.displayAnchors()
        return 0
    
    def delAnchor(self, anchor):
        self.anchors.delAnchor(anchor)
        self.displayAnchors()
        self.displaySpectra()
    
    def displayAnchors(self):
        for widget in self.subAnchor.winfo_children():
            widget.destroy()
        
        self.anchorBut.clear()
        
        for index, anchor in self.anchors.enumerate():
            self.anchorBut.append(Button(self.subAnchor, text  = f'{anchor:.2f}', 
                                         command = partial(self.delAnchor, anchor)))
            self.anchorBut[-1].grid(column = index % 12, 
                                    row = int(index / 12), 
                                    ipadx = 0, ipady = 0)
        
        return 0

    def handleMouseEvent(self, x, y):
        if self.anchors.addAnchor(x):
            return 1
        
        self.displayAnchors()
        self.displaySpectra()   
        self.allChangesSaved = False
        return 0 
