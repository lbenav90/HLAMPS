import os
import numpy as np
from settings import COLORS
import matplotlib.pyplot as plt
from idlelib.tooltip import Hovertip
from Bands import Band, Bands, FitBaseline
from tkinter.filedialog import askopenfilename
from lmfit import Parameters, Minimizer, fit_report
from tkinter.messagebox import showinfo, showwarning, askyesno, showerror
from tkinter import ttk, StringVar, BooleanVar, Canvas, Frame, Label, Button, Checkbutton

class FitTab(ttk.Frame):
    def __init__(self, master: ttk.Notebook):
        super().__init__(master)
        self.master = master
        self.window = master.master # GUI class instance
        self.varSelectedBand = StringVar(value = 'None')
        self.varChkFix = BooleanVar(value = False)
        self.varChkFitFig = BooleanVar(value = False)
        self.varChkSaveHeat = BooleanVar(value = False)
        self.varChkInstructions = BooleanVar(value = False)
        self.configureLayout()
    
    def clearTab(self):
        self.varSelectedBand.set('None')
        self.varChkFix.set(False)
        self.varChkFitFig.set(False)
        self.varChkSaveHeat.set(False)
        self.varChkInstructions.set(False)
        self.fitBase.clearBase()
        self.fitBands.clearBands()
    
    def discardChanges(self):
        if self.checkChanges():
            self.clearTab()
            return True
        
        if askyesno('Warning', 'Discard all unsaved changes?'):
            self.clearTab()
            return True
        else:
            return False
    
    def checkChanges(self):
        return self.fitBands.checkChanges() and self.fitBase.allChangesSaved
    
    def configureLayout(self):
        self.tabFitCanvas = Canvas(self)
        self.tabFitScrollbar = ttk.Scrollbar(self, orient = 'horizontal', 
                                             command = self.tabFitCanvas.xview)
        self.tabFitScrollable = ttk.Frame(self.tabFitCanvas)
        
        self.tabFitScrollable.bind("<Configure>", 
                              lambda e: self.tabFitCanvas.configure(
                                  scrollregion = self.tabFitCanvas.bbox('all')))
        self.tabFitCanvas.create_window((0,0), window = self.tabFitScrollable, anchor = 'nw')
        self.tabFitCanvas.config(xscrollcommand = self.tabFitScrollbar.set)
        self.tabFitCanvas.pack(side = 'bottom', fill = 'both', expand = True)
        self.tabFitScrollbar.pack()
        
        self.tabFitBaseline = Frame(self.tabFitScrollable)
        self.tabFitBaseline.grid(column = 0, row = 1, sticky = 'nw')
        self.tabFitBandsAll = Frame(self.tabFitScrollable)
        self.tabFitBandsAll.grid(column = 1, row = 1, sticky = 'nw')
        self.tabFitBandsButtons = Frame(self.tabFitBandsAll)
        self.tabFitBandsButtons.grid(column = 0, row = 0, sticky = 'w')
        self.tabFitBandsParams = Frame(self.tabFitBandsAll)
        self.tabFitBandsParams.grid(column = 0, row = 1, sticky = 'w')
        
        Label(self.tabFitBaseline, text = ' '       ).grid(column = 0, row = 1)
        Label(self.tabFitBaseline, text = 'Offset: ').grid(column = 0, row = 2, sticky = 'w')
        Label(self.tabFitBaseline, text = 'Slope: ' ).grid(column = 0, row = 3, sticky = 'w')
        Label(self.tabFitBandsParams, text = ' '          ).grid(column = 0, row = 0, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Position: ' ).grid(column = 0, row = 1, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Decay: '    ).grid(column = 0, row = 2, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Intensity: ').grid(column = 0, row = 3, sticky = 'w')
        
        self.btnShowFitBase = Button(self.tabFitBaseline, text = 'Show', 
                                     command = self.displaySpectra)
        self.btnShowFitBase.grid(column = 1, row = 0, sticky = 'nw')
        
        self.btnAddBand = Button(self.tabFitBandsButtons, text = '+ Band', 
                                 command = self.addBand)
        self.btnAddBand.grid(column = 0, row = 0, sticky = 'w') 
        
        self.btnDelBand = Button(self.tabFitBandsButtons, text = '- Band', 
                                 command = self.delBand)
        self.btnDelBand.grid(column = 1, row = 0, sticky = 'w')
        
        self.btnSelectBand = Button(self.tabFitBandsButtons, text = 'Select', 
                                      command = self.selectBandParams)
        self.btnSelectBand.grid(column = 2, row = 0, sticky = 'w') 
        
        self.btnImportBands = Button(self.tabFitBandsButtons, text = 'Import', 
                                     command = self.importBands)
        self.btnImportBands.grid(column = 3, row = 0, sticky = 'w')
        
        self.btnFitAvg = Button(self.tabFitBandsButtons, text = 'Fit average', 
                                command = self.fitAverageSpectra)
        self.btnFitAvg.grid(column = 4, row = 0, sticky = 'w')
        
        self.btnFitMap = Button(self.tabFitBandsButtons, text = 'Fit maps', 
                                command = self.fitMap)
        self.btnFitMap.grid(column = 5, row = 0, sticky = 'w')
        
        self.chkFixBase = Checkbutton(self.tabFitBandsButtons, text = 'Fix position and decay', 
                                      variable = self.varChkFix)
        self.chkFixBase.grid(column = 6, row = 0, sticky = 'w')
        
        self.chkSaveFig = Checkbutton(self.tabFitBandsButtons, text = 'Save fit figures', 
                                      variable = self.varChkFitFig)
        self.chkSaveFig.grid(column = 7, row = 0, sticky = 'w')
        
        self.chkSaveHeat = Checkbutton(self.tabFitBandsButtons, text = 'Save heatmap figures', 
                                       variable = self.varChkSaveHeat)
        self.chkSaveHeat.grid(column = 8, row = 0, sticky = 'w')
        
        self.fitBands = Bands()
        self.fitBase = FitBaseline(self.tabFitBaseline)
        
        Hovertip(self.btnShowFitBase, 
                 'Show current baseline and bands', 
                 hover_delay = 1000)
        Hovertip(self.btnAddBand, 
                 'Add a band', 
                 hover_delay = 1000)
        Hovertip(self.btnDelBand, 
                 'Delete selected band', 
                 hover_delay = 1000)
        Hovertip(self.btnSelectBand, 
                 'Select band parameters in graph', 
                 hover_delay = 1000)
        Hovertip(self.btnFitAvg, 
                 'Fit average spectra', 
                 hover_delay = 1000)
        Hovertip(self.btnFitMap, 
                 'Fits all maps with the parameters from average fit', 
                 hover_delay = 1000)
        Hovertip(self.chkFixBase, 
                 'If not, allows them to move +- 3 for flexibility', 
                 hover_delay = 1000)
        Hovertip(self.chkSaveFig, 
                 'Saves figures with individual bands', 
                 hover_delay = 1000)
        Hovertip(self.chkSaveHeat, 
                 'Generates heat maps for each band in each map', 
                 hover_delay = 1000)
        
        Checkbutton(self.tabFitBaseline, text = 'Show\ninstructions', 
                    variable = self.varChkInstructions
                    ).grid(column = 0, columnspan = 2, row = 4, sticky = 'w')
    
    def addBand(self):
        bandNum = self.fitBands.getLength()
    
        newBand = Band(bandNum, self.tabFitBandsParams)
        
        newBand.addRadio(self.varSelectedBand)
        
        self.fitBands.addBand(newBand)
                                                 
        if self.varSelectedBand.get() == 'None':
            self.varSelectedBand.set(f'B{self.fitBands.getUsefulLength()}') 
        
        return 0
    
    def delBand(self):
        if self.fitBands.getLength() == 0:
            return 1
        
        self.fitBands.deleteBand(self.varSelectedBand.get())
        
        for widget in self.tabFitBandsParams.winfo_children():
            widget.destroy()
        
        Label(self.tabFitBandsParams, text = ' '          ).grid(column = 0, row = 0, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Position: ' ).grid(column = 0, row = 1, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Decay: '    ).grid(column = 0, row = 2, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Intensity: ').grid(column = 0, row = 3, sticky = 'w')
                
        self.fitBands.updateLayout(self.varSelectedBand)
        
        self.varSelectedBand.set('B0')
        
        self.displaySpectra()
        
        return 0
    
    def selectBandParams(self):
        if self.window.maps.isEmpty():
            return 1
        
        if self.fitBands.getLength() == 0:
            showwarning('Warning', 
                        'No bands added')
            return 1
        
        if self.varChkInstructions.get():
            showinfo(title = 'Instructions', 
                     message = 'Select three point from the graph:\n\t' + 
                               'The first defines position\n\t' + 
                               'Difference between first and second defines decay\n\t' + 
                               'Difference between first and third defines intensity')
        
        self.fitBase.select.set(False)
        
        self.btnSelectBand.config(bg = '#95CCD9')
        
        self.fitBands.changeCollecting()
    
    @staticmethod
    def calculateModel(params, x):
        '''
        Uses params to create the model y data. Corresponds to a sum of Lorentzian peaks on a linear baseline
        
        - params (Parameters): Contains Parameter instances to be used for the model
        
        _ x: list of x values to be computed in the creation of the model
        
        '''
        numPeaks = int((len(params) - 2) / 3)
        
        y = np.zeros(len(x))
        
        v = params.valuesdict()
        
        offset, slope = v['offset'], v['slope']
        
        y += offset
        for i in range(len(x)):
            y[i] += slope * x[i]
            
        x = np.array(x)
        for i in range(numPeaks):
            p, d, h = v['x' + str(i)], v['d' + str(i)], v['h' + str(i)]
            y += (h * ((0.5 * d) ** 2)) * (1 / (((x - p) ** 2) + ((0.5 * d) ** 2)))    
        
        return y
    
    def createGuideParams(self, bandCreate = {}):
        '''
        bandCreate is a dict returned from .bandDict() method in Bandas class, each value a Band element
        '''
        if bandCreate == {}: bandCreate = self.fitBands.bandDict() 
        
        params = Parameters()
        
        params.add('offset', value = float(self.fitBase.getOffset()), 
                   vary = not self.fitBase.fixOffset.get())
        params.add('slope', value = float(self.fitBase.getSlope()), 
                   vary = not self.fitBase.fixSlope.get())
        
        for bandNum in range(len(bandCreate)):
            bandName = f'B{bandNum}'
            if bandCreate[bandName].collected:
                params.add(f'x{bandNum}', value = float(bandCreate[bandName].getPos()), 
                           vary = not bandCreate[bandName].getFixes(0), 
                           min = self.window.plotFrame.figure.getLimits()[1].getXLim()[0], 
                           max = self.window.plotFrame.figure.getLimits()[1].getXLim()[1])
                params.add(f'd{bandNum}', value = float(bandCreate[bandName].getDec()), 
                           vary = not bandCreate[bandName].getFixes(1), min = 0)
                params.add(f'h{bandNum}', value = float(bandCreate[bandName].getInt()), 
                           vary = not bandCreate[bandName].getFixes(2), min = 0)
        return params
    
    def cost(self, params, yData, x):
        '''
        Cost function to be minimized by lmfit
        
        - params (Parameters): Guess for the fit. Contains Parameter instances to be used for the model
        
        - y_data: list of Y values fot he model to be compared to
        
        _ x: list of x values to be computed in the creation of the model
        '''
        yModel = self.calculateModel(params, x)
        return yData - yModel
    
    def importBands(self):
        if self.fitBands.getUsefulLength() != 0:
            response = askyesno('Warning',
                                'Do you want to delete the ' + 
                                'present bands?')
            if response:
                self.fitBands.clearBands()
            else:
                self.fitBands.clearEmptyBands()
        
        filename = askopenfilename(title = 'Open band parameters', 
                                   initialdir = '/', 
                                   filetypes = (('Text files', '*.txt'),))
    
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        toImport = []
        
        for line in lines:
            if 'Variables' in line:
                startIndex = lines.index(line) + 1
            elif 'Correlations' in line:
                endIndex = lines.index(line)
        
        lines = lines[startIndex: endIndex]
        
        for line in lines:
            lineSplit = line.split()
            if 'offset' in lineSplit[0]:
                offset = round(float(lineSplit[1]), 2)
            elif 'slope' in lineSplit[0]:
                slope = round(float(lineSplit[1]), 2)
            elif 'x' in lineSplit[0] or 'd' in lineSplit[0] or 'h' in lineSplit[0]:
                toImport.append(round(float(lineSplit[1]),2))    
        
        if toImport == []:
            showerror('Wrong file type',
                      'Selected file is not the right' + 
                      ' format for parameter import\n' +
                      'File must be the result of a guide fit')
            return 1
        
        for i in range(0, len(toImport), 3):
            bandNum = self.fitBands.getLength()
            self.addBand()
            
            self.fitBands.band(f'B{bandNum}').setPos(toImport[i])
            self.fitBands.band(f'B{bandNum}').setDec(toImport[i + 1])
            self.fitBands.band('fB{bandNum}').setInt(toImport[i + 2])
        
        self.fitBase.setOffset(offset)
        self.fitBase.setSlope(slope)
        
        self.displaySpectra()
        
        self.window.insertLog('importfit')
        return 0
    
    def fitAverageSpectra(self):
        if self.window.maps.isEmpty():
            return 1
            
        if self.fitBands.getUsefulLength() == 0:
            showerror('Error', 
                      'No defined bands to perform fit')
            return 1
        
        params = self.createGuideParams()
        
        numPeaks = int((len(params) - 2) / 3)
        
        for index, map in self.window.maps.enumerate():
            if self.window.varSelectedMap.get() == map.orig:
                mapIndex = index
                break
        
        self.window.getAverageSpectra()
        
        intensities = self.window.averages[index][1][1]
        frequencies = self.window.averages[index][1][0]
        
        minner = Minimizer(self.cost, params, 
                           fcn_args = (intensities, frequencies))
        result = minner.minimize()
        bestParams = result.params
        v = bestParams.valuesdict()
        
        self.fitBase.setOffset(f'{v["offset"]:.2f}')
        self.fitBase.setSlope(f'{v["slope"]:.3f}')
        
        for peak in range(numPeaks):
            self.fitBands.band(f'B{peak}').setPos(round(v[f'x{peak}'], 2))
            self.fitBands.band(f'B{peak}').setDec(round(v[f'd{peak}'], 2))
            self.fitBands.band(f'B{peak}').setInt(round(v[f'h{peak}'], 2))
        
        self.displaySpectra()
        
        answer = askyesno('Guide fit result', 
                          'Do you accept the fit?')
        
        if not answer:
            v = params.valuesdict()
            for peak in range(numPeaks):
                self.fitBands.band(f'B{peak}').setPos(round(v[f'x{peak}'], 2))
                self.fitBands.band(f'B{peak}').setDec(round(v[f'd{peak}'], 2))
                self.fitBands.band(f'B{peak}').setInt(round(v[f'h{peak}'], 2))
                
            self.fitBase.setOffset(f'{v["offset"]:.2f}')
            self.fitBase.setSlope(f'{v["slope"]:.3f}')
            self.displaySpectra()
            return 1
        else:
            self.fitBands.clearEmptyBands()
            self.varSelectedBand.set(f'B{self.fitBands.getUsefulLength() - 1}')
            self.saveFitParameters(mapIndex, result)
            self.fitBands.guideFitted()
            
            self.window.insertLog('fitGuide')
        
            return 0
    
    def saveFitParameters(self, mapIndex, result):
        for map in self.window.maps:
            os.chdir(map.directory)
            
            os.makedirs(f'{map.orig}_Files/Parameters', exist_ok = True)
            
            with open(f'{map.orig}_Files/Parameters/GuideFitParams.txt', 'w') as newFile:
                newFile.write(fit_report(result))
            
            return 0
        
    def createMapParams(self):
        '''
        bandCreate is a dict returned from .bandDict() method in Bandas class, 
        Each value a Band instance
        '''
        bandCreate = self.fitBands.bandDict()
        params = Parameters()
        
        params.add('offset', value = float(self.fitBase.getOffset()))
        params.add('slope', value = float(self.fitBase.getSlope()))
        
        for bandName in bandCreate:
            if self.varChkFix.get():
                params.add(f'x{bandName[1:]}', 
                           value = float(bandCreate[bandName].getPos()), 
                           vary = False)
                params.add(f'd{bandName[1:]}', 
                           value = float(bandCreate[bandName].getDec()), 
                           vary = False)
                params.add(f'h{bandName[1:]}', 
                           value = float(bandCreate[bandName].getInt()), 
                           min = 0)
            else:
                params.add(f'x{bandName[1:]}', 
                           value = float(bandCreate[bandName].getPos()), 
                           min = float(bandCreate[bandName].getPos()) - 3, 
                           max = float(bandCreate[bandName].getPos()) + 3)
                params.add(f'd{bandName[1:]}', 
                           value = float(bandCreate[bandName].getDec()),
                           min = float(bandCreate[bandName].getDec()) - 3, 
                           max = float(bandCreate[bandName].getDec()) + 3)
                params.add(f'h{bandName[1:]}', 
                           value = float(bandCreate[bandName].getInt()), 
                           min = 0)
        return params
    
    def fitMap(self):
        if self.window.maps.isEmpty():
            return 1
            
        if not self.fitBands.checkFitted():
            showerror('Error', 
                      'Average spectra is not fitted or changes were made after last fit')
            return 1
        
        params = self.createMapParams()
        numPeaks = int((len(params) - 2) / 3)
        
        progressStep = 300 / (self.window.maps.length() * self.window.maps[0].spectraNum)
        self.window.statFrame.progressLabel.config(text = 'Processing:   Fitting spectra')
        
        for map in self.window.maps:
            
            mapData = self.window.readMap(map)
            
            os.chdir(map.directory)
            
            os.makedirs(f'{map.orig}_Files/Fits', exist_ok = True)
            os.makedirs(f'{map.orig}_Files/Fits/Reports', exist_ok = True)
            os.makedirs(f'{map.orig}_Files/Fits/Heatmaps', exist_ok = True)
            if self.varChkFitFig.get():
                os.makedirs(f'{map.orig}_Files/Fits/Figures', exist_ok = True)
                    
            frequencies = mapData['freq']
            mapIntensities = {}
            
            for key in mapData:
                if key == 'freq':
                    continue
                
                minner = Minimizer(self.cost, params, 
                                   fcn_args = (mapData[key], frequencies))
                result = minner.minimize()
                bestParams = result.params
                
                self.writeFitSpectra(bestParams, mapData['freq'], mapData[key], key, map)
                self.writeFitReport(result, key, map)
                
                spectraInts = []
                numPeaks = int((len(params)-2)/3)
                v = bestParams.valuesdict()
                
                for peak in range(numPeaks):
                    spectraInts.append(round(v[f'h{peak}'], 2))
                
                mapIntensities[key] = spectraInts
                
                self.window.statFrame.progressBar['value'] += progressStep
                self.window.statFrame.update_idletasks()
            
            self.writeHeatmaps(mapIntensities, map)
            self.window.statFrame.progressBar['value'] += progressStep
            self.window.statFrame.update_idletasks()
        
        self.window.statFrame.progressBar['value'] = 0
        self.window.statFrame.progressLabel.config(text = 'Processing: ')
        
        self.window.insertLog('fitMap')
        
        showinfo('Information', 
                 'Maps fitted successfully')
        
        self.fitBands.saveChanges()
        self.fitBase.allChangesSaved = True
        return 0
            
    def writeHeatmaps(self, mapIntensities, map):
        numPeaks = self.fitBands.getUsefulLength()
        
        os.chdir(f'{map.orig}_Files/Fits/Heatmaps')
        
        with open(f'{map.name}_heatmaps.txt', 'w') as newFile:
            newFile.write('X(um)\tY(um)')
            
            for peak in range(numPeaks):
                newFile.write(f'\tI(B{peak})')
            
            for key in mapIntensities:
                newFile.write('\n')
                newFile.write(f'{key[0]}\t{key[1]}')
                for peak in range(numPeaks):
                    newFile.write(f'\t{mapIntensities[key][peak]}')
        
        os.chdir(map.directory)
        
        if self.varChkSaveHeat.get():
            self.drawHeatFigure(mapIntensities, map)
    
    def drawHeatFigure(self, mapIntensities, map):
        numPeaks = self.fitBands.getUsefulLength()
        
        x = np.array([])
        y = np.array([])
        for key in mapIntensities:
            x = np.append(x, key[0])
            y = np.append(y, key[1])
            
        x = np.sort(np.unique(x))
        y = np.sort(np.unique(y))
        
        os.chdir(f'{map.orig}_Files/Fits/Heatmaps')
        
        for peak in range(numPeaks):
            intensities = np.array([])
            for yValue in y:
                for xValue in x:
                    intensities = np.append(intensities, mapIntensities[(xValue, yValue)][peak])
            
            fig, ax = plt.subplots()
            pc = ax.imshow(intensities.reshape(len(x), len(y)), 
                           aspect = 'auto', origin = 'lower',
                           interpolation = 'gaussian', cmap = 'Greys')
            plt.colorbar(pc)
            
            fig.savefig(f'{map.name}_heatmap_band{peak}.png')
            plt.close(fig)
        
        os.chdir(map.directory)
        return 0
    
    @staticmethod
    def writeFitReport(fitResult, key, map):
        x = key[0].split('.')[0]
        y = key[1].split('.')[0]
        
        os.chdir(f'{map.orig}_Files/Fits/Reports')
        
        with open(f'{map.name}_X_{x}_Y_{y}.txt', 'w') as newFile:
            newFile.write(fit_report(fitResult))
        
        os.chdir(map.directory)
        return 0
        
    def writeFitSpectra(self, params, frequencies, intensities, key, map): 
        numPeaks = int((len(params) - 2) / 3)
        v = params.valuesdict()
        
        fit = self.calculateModel(params, frequencies)
        
        x = key[0].split('.')[0]
        y = key[1].split('.')[0]
        
        os.chdir(f'{map.orig}_Files/Fits')
                
        with open(f'{map.name}_X_{x}_Y_{y}.txt', 'w') as newFile:
            newFile.write('Wavenumber(cm-1)\tIntData\tInt(FitTotal)\tInt(Baseline)')
            
            bandFit = {}
            for peak in range(numPeaks):
                newFile.write(f'\tInt(B{peak})')
                
                bandParams = Parameters()
                bandParams.add('offset', value = v['offset'])
                bandParams.add('slope', value = v['slope'])
                bandParams.add('x0', value = v['x' + str(peak)])
                bandParams.add('d0', value = v['d' + str(peak)])
                bandParams.add('h0', value = v['h' + str(peak)])
                
                bandFit[f'B{peak}'] = self.calculateModel(bandParams, frequencies)
                
            newFile.write('\n')
            
            for index, freq in enumerate(frequencies):
                newFile.write(f'{freq:.2f}\t{intensities[index]:.2f}\t{fit[index]:.2f}\t')
                newFile.write(f'{freq * v["slope"] + v["offset"]:.2f}')
                              
                for peak in range(numPeaks):
                    newFile.write(f'\t{bandFit["B" + str(peak)][index]:.2f}')
                newFile.write('\n')
        
        os.chdir(map.directory)
        
        if self.varChkFitFig.get():
            self.drawFitFigure(frequencies, intensities, key, fit, bandFit, params, map)
    
    @staticmethod
    def drawFitFigure(frequencies, intensities, key, fit, bandFit, params, map):
            
        fig = plt.Figure()
        
        plot1 = fig.add_subplot(111, xlabel = 'Wavenumber (cm-1)', ylabel = 'Intensity')
        
        plot1.plot(frequencies, intensities, 'k')
        plot1.plot(frequencies, fit, 'r', alpha = 0.8)
        
        for peak in range(len(bandFit)):
            plot1.plot(frequencies, bandFit[f'B{peak}'], alpha = 0.5)
        
        v = params.valuesdict()
        plot1.plot(frequencies, np.array(frequencies) * v['slope'] + v['offset'], alpha = 0.5)
        
        x = key[0].split('.')[0]
        y = key[1].split('.')[0]
        
        os.chdir(f'{map.orig}_Files/Fits/Figures')
        
        fig.savefig(f'{map.name}_X_{x}_Y_{y}_fit.png')
        plt.close()
        
        os.chdir(map.directory)
        return 0

    def displaySpectra(self, window = None):
        if window is None:
            window = self.master.master
            
        if window.maps.isEmpty():
            return 1
        
        window.getAverageSpectra()
        
        plot = window.plotFrame.figure.reInitPlot()
        
        for index, average in window.averages.enumerate():
            if average[0].orig == window.varSelectedMap.get():
                selectedMapIndex = index
                break
        
        for col, spectra in window.averages.enumerate():  
            plot.plot(spectra[1][0], spectra[1][1], 
                      color = COLORS[col % len(COLORS)])
            
            if col != selectedMapIndex:
                continue
            
            if self.fitBase.getOffset() == '' and self.fitBase.getSlope() == '' and self.fitBands.getUsefulLength() != 0:
                self.fitBase.setOffset('0.0')
                self.fitBase.setSlope('0.0')
            
            if self.fitBase.getOffset() != '' and self.fitBase.getSlope() != '':
                offset = float(self.fitBase.getOffset())
                slope = float(self.fitBase.getSlope())
                spectraBase = np.array(spectra[1][0]) * slope + offset 
                            
                plot.plot(spectra[1][0], spectraBase, c = '#444444')
        
            if self.fitBands.getUsefulLength() != 0 :
                
                fitParams = self.createGuideParams()
                
                spectraFit = self.calculateModel(fitParams, spectra[1][0])
                
                plot.plot(spectra[1][0], spectraFit, c = '#191919')
                
                for band in self.fitBands:
                    bandParams = self.createGuideParams({'B0': band})
                    bandFit = self.calculateModel(bandParams, spectra[1][0])
                    plot.plot(spectra[1][0], bandFit, alpha = 0.5) 

        window.plotFrame.figure.saveLimits()
        window.plotFrame.figure.drawCanvas()
        
        self.window.statFrame.getLimits()
        
        return 0

    def handleMouseEvent(self, x, y):
        if self.fitBands.collecting():
            name = self.varSelectedBand.get()
            if self.fitBands.addReference(x, y, name):
                self.fitBands.changeCollecting()
                self.btnSelectBand.config(bg = '#f0f0f0')
                self.displaySpectra()
                
                if self.varSelectedBand.get() != f'B{self.fitBands.getLength() - 1}':
                    newBand = int(self.varSelectedBand.get()[1:]) + 1
                    self.varSelectedBand.set(f'B{newBand}')
                
        elif self.fitBase.selectOn():
            if self.fitBase.addReference(x, y):
                self.fitBase.changeSelect()
                self.displaySpectra()
                
        return 0
