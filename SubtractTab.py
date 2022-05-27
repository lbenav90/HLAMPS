import os
import numpy as np
from Maps import Map
from Anchors import Anchors
from functools import partial
import matplotlib.pyplot as plt
from idlelib.tooltip import Hovertip
from settings import TEMP_PATH, COLORS
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, askyesno, showerror
from tkinter import Tk, Button, BooleanVar, Frame, Checkbutton, ttk

class SubtractTab(ttk.Frame):
    ''' Contains all variables and widgets of the Subtract baseline Tab '''
    def __init__(self, notebook: ttk.Notebook):
        super().__init__(notebook)
        self.master = notebook
        self.window = notebook.window ### GUI instance

        # Class instance that stores anchor points
        self.anchors = Anchors()
        # Stores anchor buttons
        self.anchorBut = []

        self.showSub = BooleanVar(value = False)
        self.varChkSubFig = BooleanVar(value = False)
        self.varChkOffset = BooleanVar(value = False)

        self.configureLayout()
        self.allChangesSaved = True
    
    def clearTab(self):
        ''' Reinitialize tab '''
        self.anchors.clear()
        self.anchorBut.clear()
        self.displayAnchors()
        self.showSub.set(False)
        self.varChkSubFig.set(False)
        self.varChkOffset.set(False)
        self.allChangesSaved = True
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
    
    def configureLayout(self):
        ''' Configure tab's widget layout '''
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
        return 0
    
    @staticmethod
    def averageBox(values: list, index: int, box: int):
        '''Values is a list of floats and the value of interest is at index. 
        Averages values in the index intervals (index-box, index + box) excluding out of bounds '''
        # Check if the interval is fully included in the values list, if not, defines limit indexes
        if index - box < 0:
            minIndex = None
            maxIndex = index + box + 1
        elif index + box >= len(values) - 1:
            minIndex = index - box
            maxIndex = None
        else:
            minIndex = index - box
            maxIndex = index + box + 1

        return sum(values[minIndex: maxIndex]) / len(values[minIndex: maxIndex])
    
    @staticmethod
    def findClosest(interest: float, values: list):
        ''' Given a valueof interest, finds the index for the nearest float in a list of value '''
        # Set an arbitrarily large minimum difference
        minDif = 1e9
        minIndex = 0
        for index, value in enumerate(values):
            dif = abs(interest - value)
            if dif < minDif:
                minDif = dif
                minIndex = index
        return minIndex        
    
    def subtractBaseline(self):
        ''' Subtract a linear baseline made by linear interpolation of anchor points contained in Anchors class object.
        Saves the subtracted map as the default map in temp folder and the individual spectra'''
        if self.window.maps.isEmpty():
            return 1 
    
        # For potentially long processes, a progress bar in the Status Frame is used to avoid user panic
        progressStep = 300 / (self.window.maps.length() * self.window.maps[0].spectraNum)
        self.window.statFrame.progressLabel.config(text = 'Processing:   Saving subtracted maps')
        
        for map in self.window.maps:
            os.chdir(map.directory)
            
            # Load map data
            mapData = self.window.readMap(map)
            
            # Add a suffix no the Map name, but only once
            if '_subtracted' not in map.name: 
                map.name = map.name + '_subtracted'
            
            frequencies = mapData.pop('freq')
            
            for key, intensities in mapData.items():
                
                # Get the intensity values for each frequency anchor point in Anchors object
                yAnchors = [self.averageBox(intensities, 
                                            self.findClosest(anchor, frequencies),
                                                             3) for anchor in self.anchors]   
            
                # Interpolate between anchor points in the range of frequencies
                yBase = np.interp(frequencies, 
                                  self.anchors.asList(),
                                  yAnchors)

                # Subtract the intensity data to interpolated data                  
                mapData[key] = np.array(mapData[key]) - yBase
                
                # Save individual spectra ( and figures, if chosen by user)
                self.saveSubSpectra(key, mapData[key], frequencies, map)
                if self.varChkSubFig.get():
                    self.saveSubFigures(key, map, frequencies, intensities, yAnchors, yBase)
                
                # Update progress bar
                self.window.statFrame.progressBar['value'] += progressStep
                self.window.statFrame.update_idletasks()
            
            # Add back the frequencies to the map and write the new map to temp and directory
            mapData['freq'] = frequencies
            self.window.writeMap(map, mapData)

            # Save the baseline parameters used
            self.saveBaselineParameters(map)
            
        # Reset progress bar
        self.window.statFrame.progressBar['value'] = 0
        self.window.statFrame.progressLabel.config(text = 'Processing: ')
        self.window.statFrame.update_idletasks()
        
        # Update legend to reflect new map names
        self.window.legFrame.updateLegend()
        
        # Log process
        self.window.insertLog('baseline_saveMap')
        
        showinfo('Save',  
                 'Subtracted maps saved successfully')
        
        # Log process
        self.window.insertLog('baseline')
        
        # Display new default maps
        self.displaySpectra()
        
        self.allChangesSaved = True    
        return 0

    def saveSubSpectra(self, key: tuple, intensities: list, frequencies: list, map: Map):
        ''' Saves the individual subtracted spectra and redirects the figure creation if chosen.'''
        os.chdir(map.directory)

        os.makedirs(f'{map.orig}_Files/Individual Spectra/Subtracted', exist_ok = True)
        
        os.chdir(f'{map.orig}_Files/Individual Spectra/Subtracted')
        
        # Remove decimal to avoid filename corruption
        x = key[0].replace('.', '')
        y = key[1].replace('.', '')

        # Save the number of decimals for the filename
        if '.' in key[0]:
            xDec = len(key[0]) - key[0].index('.') - 1
        else:
            xDec = 0
        
        if '.' in key[1]:
            yDec = len(key[1]) - key[1].index('.') - 1
        else:
            yDec = 0
        
        # Write file
        with open(f'{map.orig}_X_{x}_E-{xDec}_Y_{y}_E-{yDec}_subtracted.txt', 'w') as newFile:
            newFile.write('Wavenumber(cm-1)\tIntensity\n')

            for freq, inten in zip(frequencies, intensities):
                newFile.write(f'{freq:.2f}\t{inten:.2f}\n')
        return 0

    def saveSubFigures(self, key: tuple, map: Map, frequencies: list, intensities: list, yAnchors: np.ndarray, yBase: np.ndarray): 

        os.chdir(map.directory)

        os.makedirs(f'{map.orig}_Files/Figures/Subtracted', exist_ok = True)
        
        os.chdir(f'{map.orig}_Files/Figures/Subtracted')
        
        fig = plt.Figure()
        plot1 = fig.add_subplot(111, xlabel = 'Wavenumber (cm-1)', ylabel = 'Intensity')
        
        # Plot data, the baseline as a line and the anchor points
        plot1.plot(frequencies, intensities, 'k')
        plot1.plot(self.anchors.asList(), yAnchors, c = 'grey')
        plot1.plot(self.anchors.asList(), yAnchors, ' o', c = 'grey')
        
        # Remove decimal to avoid filename corruption
        x = key[0].replace('.', '')
        y = key[1].replace('.', '')

        # Save the number of decimals for the filename
        if '.' in key[0]:
            xDec = len(key[0]) - key[0].index('.') - 1
        else:
            xDec = 0
        
        if '.' in key[1]:
            yDec = len(key[1]) - key[1].index('.') - 1
        else:
            yDec = 0

        fig.savefig(f'{map.orig}_X_{x}_E-{xDec}_Y_{y}_E-{yDec}_baseline.png')
        plt.close()
        
        fig = plt.Figure()
        plot1 = fig.add_subplot(111, xlabel = 'Wavenumber (cm-1)', ylabel = 'Intensity')
        
        # Plot the subtracted data
        plot1.plot(frequencies, intensities - yBase, 'k')

        fig.savefig(f'{map.orig}_X_{x}_E-{xDec}_Y_{y}_E-{yDec}_subtracted.png')
        plt.close()
        
        os.chdir(map.directory)
        return 0

    def saveBaselineParameters(self, map: Map):
        ''' Save the baseline parameters used for future reference '''
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
        ''' Import a previously used baseline from a file output of saveBaselineParameters method'''
        if not self.anchors.isEmpty():
            response = askyesno('Warning',
                                 'Do you want to delete the ' + 
                                 'present baseline anchors?')
            if response:
                # Delete existing anchors upon user confirmation
                self.anchors.clear()
        
        # Don't check for baseline file name to allow users to rename it
        filename = askopenfilename(title = 'Open baseline file', 
                                   initialdir = '/', 
                                   filetypes = (('Text files', '*.txt'),))
    
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        # Check for correct content - can fail for an unfortunate selection
        if 'Linear interpolation' not in lines[0]:
            showerror('Wrong file type',
                      'Selected file is not the right ' + 
                      'format for baseline import\n' +
                      'File must be the result of a baseline subtraction')
            return 1
        
        # Use only anchors line
        lines = lines[2:]
        
        for line in lines:
            lineSplit = line.split()[3:]
            for anchor in lineSplit:
                # Add an anchor for each number in the list
                self.anchor.addAnchor(float(anchor))
        
        # Display new anchors and spectra
        self.displayAnchors()
        self.displaySpectra()
        
        # Log process
        self.window.insertLog('importbaseline')
        return 0
    
    def showSubtracted(self, show: bool = True):
        if self.window.maps.isEmpty():
            return 1
        
        # Get the current average spectra
        self.window.getAverageSpectra()
        
        for map, spectra in self.window.averages:
            # Get the intensity value for each anchor value
            yAnchors = [self.averageBox(spectra[1], 
                                        self.findClosest(anchor, spectra[0]),
                                                         3) for anchor in self.anchors]
            # Create interpolation between anchors
            yBase = np.interp(spectra[0], self.anchors.asList(), yAnchors)
            
            spectra[1] -= yBase
        
        # To differentiate between a function call from Show Subtracted button 
        # and a call from showSubtractedAvg method
        if show:
            self.showSub.set(True)
            self.displaySpectra()
            self.showSub.set(False)
        return 0
    
    def saveSubtractedAvg(self):
        ''' Save the subtracted average spectra files '''
        if self.window.maps.isEmpty():
            return 1
    
        # Generate the subtracted averages in window.averages but don't show them
        # This way, the maps are not saved but the averages are subtracted
        self.showSubtracted(False)
        
        for map, spectra in self.window.averages:
            os.chdir(map.directory)
            
            os.makedirs(f'{map.orig}_Files/Average Spectra', exist_ok = True) 
            
            os.chdir(f'{map.orig}_Files/Average Spectra')
            
            frequencies = spectra[0]
            intensities = spectra[1]
            
            # Write file
            with open(f'{map.name}_subAverage.txt', 'w') as file:
                file.write('Wavenumber(cm-1)\tIntensity\n')
                for freq, inten in zip(frequencies, intensities):
                    file.write(f'{freq:.2f}\t{inten:.2f}\n')

        # Log process    
        self.window.insertLog('subAverage_save')
        
        showinfo('Save', 'Subtracted average spectra saved')
        os.chdir(TEMP_PATH)
        return 0
    
    def displaySpectra(self, window: Tk = None):
        ''' Display current average spectra with the Tab specific plots. '''
        if window is None:
            window = self.window
            
        if window.maps.isEmpty():
            return 1
        
        # Used when called from showSubtracted method to bypass
        # the clearing and writing os window.averages containing the subtracted spectra
        if not self.showSub.get():
            window.getAverageSpectra()
        
        # Reinitialize PltFigure object
        plot = window.plotFrame.figure.reInitPlot()
        
        # Add the frequency extreme anchors, relevant only when accessing tab
        # as addAnchors method doesn't allow duplicates
        self.anchors.addAnchor(window.averages.averages[0][1][0][ 0])
        self.anchors.addAnchor(window.averages.averages[0][1][0][-1])
        
        for col, spectra in window.averages.enumerate():  
            if self.showSub.get() and self.varChkOffset.get():
                # Add an offset between spectra for clarity - hardcoded to 30% of y axis range
                # Maybe add an offset selector?
                limits = self.window.plotFrame.figure.getLimits()[1].getYLim()

                offset = (limits[1] - limits[0]) * 0.3 * (1 + col)

                plot.plot(spectra[1][0], spectra[1][1] + offset, 
                          color = COLORS[col % len(COLORS)])
            else:
                plot.plot(spectra[1][0], spectra[1][1], 
                          color = COLORS[col % len(COLORS)])
           
            if not self.showSub.get():
                # If it is not a showSubtracted method call, plot the anchor points and baseline 
                yAnchors = [self.averageBox(spectra[1][1], 
                                             self.findClosest(anchor, spectra[1][0]),
                                                              3) for anchor in self.anchors]
    
                plot.plot(self.anchors.asList(), yAnchors, '#808080')
                plot.plot(self.anchors.asList(), yAnchors, ' o', c = 'grey')

        # Save new limits
        window.plotFrame.figure.saveLimits()
        window.plotFrame.figure.drawCanvas()
        
        # Display new limits in Status Frame
        self.window.statFrame.getLimits()
        
        # Relevant on the firs call, upon adding the frequency extreme anchors
        self.displayAnchors()
        return 0
    
    def delAnchor(self, anchor: float):
        ''' Delete a selected anchor from Anchors object. Called from the anchor buttons'''
        self.anchors.delAnchor(anchor)
        self.displayAnchors()
        self.displaySpectra()
        return 0
    
    def displayAnchors(self):
        ''' Displays the current anchors in Anchors object as buttons with value label.
        Each buton calls for the deletion of the selected anchor'''
        # Destroy every button
        for widget in self.subAnchor.winfo_children():
            widget.destroy()
        
        # Clear the buttons
        self.anchorBut.clear()
        
        for index, anchor in self.anchors.enumerate():
            # Add a new button
            self.anchorBut.append(Button(self.subAnchor, text  = f'{anchor:.2f}', 
                                         command = partial(self.delAnchor, anchor)))
            # Place the last widget of the list
            self.anchorBut[-1].grid(column = index % 12, 
                                    row = int(index / 12), 
                                    ipadx = 0, ipady = 0)
        return 0

    def handleMouseEvent(self, x: float, y: float):
        ''' Function triggered upon a mouse event on the plot, when the Subtract tab is active. '''
        # If adding the anchor fails because it is repeated or out of bounds, return
        if self.anchors.addAnchor(x):
            return 1
        
        # Display anchors and spectra
        self.displayAnchors()
        self.displaySpectra()   
        self.allChangesSaved = False
        return 0 
