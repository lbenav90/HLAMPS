import os
import numpy as np
from Maps import Map
from settings import COLORS
import matplotlib.pyplot as plt
from idlelib.tooltip import Hovertip
from Bands import Band, Bands, FitBaseline
from tkinter.filedialog import askopenfilename
from lmfit import Parameters, Minimizer, fit_report
from tkinter.messagebox import showinfo, showwarning, askyesno, showerror
from tkinter import Tk, ttk, StringVar, BooleanVar, Canvas, Frame, Label, Button, Checkbutton

class FitTab(ttk.Frame):
    ''' Contains all variables and widgets of the Fit Spectra Tab '''
    def __init__(self, notebook: ttk.Notebook):
        super().__init__(notebook)
        self.notebook = notebook
        self.window = notebook.window # GUI class instance

        # Tab specific variables
        self.varSelectedBand = StringVar(value = 'None')
        self.varChkFix = BooleanVar(value = False)
        self.varChkFitFig = BooleanVar(value = False)
        self.varChkSaveHeat = BooleanVar(value = False)
        self.varChkInstructions = BooleanVar(value = False)

        self.configureLayout()
    
    def clearTab(self):
        ''' Reinitialize tab '''
        self.varSelectedBand.set('None')
        self.varChkFix.set(False)
        self.varChkFitFig.set(False)
        self.varChkSaveHeat.set(False)
        self.varChkInstructions.set(False)
        self.fitBase.clearBase()
        self.fitBands.clearBands()
        return 0
    
    def discardChanges(self):
        ''' Upon a tab change, checks for unsaved changes. If present,
        asks for confirmation. '''
        if self.checkChanges():
            self.clearTab()
            return True
        
        if askyesno('Warning', 'Discard all unsaved changes?'):
            self.clearTab()
            return True
        else:
            return False
    
    def checkChanges(self):
        ''' Check for unsaved changes. Returns True if there are none'''
        return self.fitBands.checkChanges() and self.fitBase.allChangesSaved
    
    def configureLayout(self):
        ''' Setup tab's widget layout '''

        # Make the tab scrollable
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
        # Make the tab scrollable
        
        # Frames for tab sectioning
        self.tabFitBaseline = Frame(self.tabFitScrollable)
        self.tabFitBaseline.grid(column = 0, row = 1, sticky = 'nw')

        self.tabFitBandsAll = Frame(self.tabFitScrollable)
        self.tabFitBandsAll.grid(column = 1, row = 1, sticky = 'nw')

        self.tabFitBandsButtons = Frame(self.tabFitBandsAll)
        self.tabFitBandsButtons.grid(column = 0, row = 0, sticky = 'w')

        self.tabFitBandsParams = Frame(self.tabFitBandsAll)
        self.tabFitBandsParams.grid(column = 0, row = 1, sticky = 'w')
        
        # Label configuration
        Label(self.tabFitBaseline, text = ' '       ).grid(column = 0, row = 1)
        Label(self.tabFitBaseline, text = 'Offset: ').grid(column = 0, row = 2, sticky = 'w')
        Label(self.tabFitBaseline, text = 'Slope: ' ).grid(column = 0, row = 3, sticky = 'w')
        Label(self.tabFitBandsParams, text = ' '          ).grid(column = 0, row = 0, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Position: ' ).grid(column = 0, row = 1, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Decay: '    ).grid(column = 0, row = 2, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Intensity: ').grid(column = 0, row = 3, sticky = 'w')
        
        # Button configuration
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
        
        # Create fit parameter elements
        self.fitBands = Bands()
        self.fitBase = FitBaseline(self.tabFitBaseline)
    
    def addBand(self):
        ''' Adds a new Band element with its corresponding name. '''
        bandNum = self.fitBands.getLength()
    
        # Create new Band element and add radiobutton
        newBand = Band(bandNum, self.tabFitBandsParams)
        newBand.addRadio(self.varSelectedBand)
        
        # Add new Band element to Bands class
        self.fitBands.addBand(newBand)

        # Select a band radiobutton if none is                       
        if self.varSelectedBand.get() == 'None':
            self.varSelectedBand.set(f'B{self.fitBands.getUsefulLength()}') 
        
        return 0
    
    def delBand(self):
        ''' Delete the Band element selected by radiobutton. '''
        if self.fitBands.getLength() == 0:
            return 1
        
        # Delete the Band element from Bands element
        self.fitBands.deleteBand(self.varSelectedBand.get())
        
        # Destroy everything in parameter containing Frame
        for widget in self.tabFitBandsParams.winfo_children():
            widget.destroy()
        
        # Reconfigure the Frame layout with the new band order
        Label(self.tabFitBandsParams, text = ' '          ).grid(column = 0, row = 0, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Position: ' ).grid(column = 0, row = 1, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Decay: '    ).grid(column = 0, row = 2, sticky = 'w')
        Label(self.tabFitBandsParams, text = 'Intensity: ').grid(column = 0, row = 3, sticky = 'w')
                
        self.fitBands.updateLayout(self.varSelectedBand)
        
        self.varSelectedBand.set('B0')
        
        # Display the spectra with the current Bands
        self.displaySpectra()
        
        return 0
    
    def selectBandParams(self):
        ''' Turns on Band parameter selection from plot. '''
        if self.window.maps.isEmpty():
            return 1
        
        # Only do it if a Band element is avaliable
        # Maybe if there are no Band elements, add one?
        if self.fitBands.getLength() == 0:
            showwarning('Warning', 
                        'No bands added')
            return 1
        
        # Shows information on how to collect parameters
        # Maybe put an image with the instructions also
        if self.varChkInstructions.get():
            showinfo('Instructions', 
                     'Select three point from the graph:\n\t' + 
                     'The first defines position\n\t' + 
                     'Difference between first and second defines decay\n\t' + 
                     'Difference between first and third defines intensity')
        
        # Deactivate fit baseline selection
        self.fitBase.select.set(False)
        
        # Change button color to represent selection
        self.btnSelectBand.config(bg = '#95CCD9')
        
        self.fitBands.changeCollecting()
        return 0
    
    def calculateModel(self, params: Parameters, x: list):
        '''
        Uses params to create the model y data. Corresponds to a sum of Lorentzian peaks on a linear baseline
        
        - params: Contains Parameter instances to be used for the model
        
        - x: list of x values to be computed in the creation of the model
        
        '''
        numPeaks = self.fitBands.getUsefulLength()
        
        # Create an empty array
        y = np.zeros(len(x))
        
        v = params.valuesdict()
        
        offset, slope = v['offset'], v['slope']
        
        # Add the linear baseline defined by slope and offset
        y += offset
        for i in range(len(x)):
            y[i] += slope * x[i]
            
        x = np.array(x)
        # For each peak, adds a lorentzian function with the corresponding parameters
        for i in range(numPeaks):
            p, d, h = v[f'x{i}'], v[f'd{i}'], v[f'h{i}']
            y += (h * ((0.5 * d) ** 2)) * (1 / (((x - p) ** 2) + ((0.5 * d) ** 2)))    
        
        return y
    
    def createGuideParams(self, bandCreate: dict = {}):
        ''' bandCreate is a dict returned from .bandDict() method in Bandas class, each value a Band element.
        If it is not given, the function uses all Band elements from Bands element. 
        It allows for a specific Band element dict as input to use the same function to plot individual peaks '''
        # If it is not given, use all Band elements
        if bandCreate == {}: bandCreate = self.fitBands.bandDict() 
        
        params = Parameters()
        
        # Add linear baseline parameters with corresponding fix parameter statuses
        params.add('offset', value = float(self.fitBase.getOffset()), 
                   vary = not self.fitBase.fixOffset.get())
        params.add('slope', value = float(self.fitBase.getSlope()), 
                   vary = not self.fitBase.fixSlope.get())
        
        for bandNum, band in enumerate(bandCreate):
            bandName = f'B{bandNum}'

            # If the band is collected, add the parameters
            if band.collected:
                params.add(f'x{bandNum}', 
                           value = float(band.getPos()), 
                           vary = not band.getFixes(0), 
                           min = self.window.plotFrame.figure.getLimits()[1].getXLim()[0], 
                           max = self.window.plotFrame.figure.getLimits()[1].getXLim()[1])
                params.add(f'd{bandNum}', 
                           value = float(band.getDec()), 
                           vary = not band.getFixes(1), min = 0)
                params.add(f'h{bandNum}', 
                           value = float(band.getInt()), 
                           vary = not band.getFixes(2), min = 0)

        return params
    
    def cost(self, params: Parameters, yData: list, xData: list):
        ''' Cost function to be minimized by lmfit
        
        - params: Initial guess for the fit. Contains Parameter instances to be used for the model
        
        - yData: intensity values for the model to be compared to
        
        - xData: frequency values to be computed in the creation of the model
        '''
        yModel = self.calculateModel(params, xData)
        return yData - yModel
    
    def importBands(self):
        ''' Import Band elements used in a previous fit by this program.
        The valid import files are created by the fit_report function in lmfit package. '''
        # Ask if it should delete current Band elements.
        # If not, only clear the bands not fully collected
        if self.fitBands.getUsefulLength() != 0:
            response = askyesno('Warning',
                                'Do you want to delete the ' + 
                                'present bands?')
            if response:
                self.fitBands.clearBands()
            else:
                self.fitBands.clearEmptyBands()
        
        # Open file dialog
        filename = askopenfilename(title = 'Open band parameters', 
                                   initialdir = '/', 
                                   filetypes = (('Text files', '*.txt'),))
    
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        # List of parameter values to be imported
        toImport = []
        
        # Due to variability of the file length, we need to check for specific lines,
        # between which the Band parameters are located
        startIndex = None
        endIndex = None
        for line in lines:
            if 'Variables' in line:
                startIndex = lines.index(line) + 1
            elif 'Correlations' in line:
                endIndex = lines.index(line)
        
        # Check if the file format is correct; both startIndex and endIndex must be changed
        if startIndex is None or endIndex is None:
            showerror('Wrong file type',
                                'Selected file is not the right' + 
                                ' format for parameter import\n' +
                                'File must be the result of a guide fit')
            return 1

        # Slice the file to include only the parameter section
        lines = lines[startIndex: endIndex]
        
        # Check for each remaining line, which parameter it corresponds to
        for line in lines:
            lineSplit = line.split()
            if 'offset' in lineSplit[0]:
                offset = round(float(lineSplit[1]), 2)
            elif 'slope' in lineSplit[0]:
                slope = round(float(lineSplit[1]), 2)
            elif 'x' in lineSplit[0] or 'd' in lineSplit[0] or 'h' in lineSplit[0]:
                toImport.append(round(float(lineSplit[1]),2))    
        
        # Check for error importing
        if toImport == [] or len(toImport) % 3 != 0:
            showerror('No parameters',
                      'No parameters to import or incorrect number of parameters to import')
            return 1

        # Get chunks of three parameters from toImport, corresponding to a Band element
        for i in range(0, len(toImport), 3):
            bandNum = self.fitBands.getLength()
            self.addBand()
            
            self.fitBands.band(f'B{bandNum}').setPos(toImport[i])
            self.fitBands.band(f'B{bandNum}').setDec(toImport[i + 1])
            self.fitBands.band(f'B{bandNum}').setInt(toImport[i + 2])
        
        # Set linear baseline parameters
        self.fitBase.setOffset(offset)
        self.fitBase.setSlope(slope)
        
        # Displat new fit configuration
        self.displaySpectra()
        
        # Log process
        self.window.insertLog('importfit')
        return 0
    
    def fitAverageSpectra(self):
        ''' Fit the selected average spectra with the current collected Band elements '''
        if self.window.maps.isEmpty():
            return 1
        
        # Only allow a fit with at least one fully collected Band element
        if self.fitBands.getUsefulLength() == 0:
            showerror('Error', 
                      'No defined bands to perform fit')
            return 1
        
        # Create initial guess
        params = self.createGuideParams()
        
        numPeaks = self.fitBands.getUsefulLength()
        
        # Get the index for the currently selected map in the Legend Frame
        for index, map in self.window.maps.enumerate():
            if self.window.varSelectedMap.get() == map.orig:
                mapIndex = index
                break
        
        # Gte the current average spectra from temp
        self.window.getAverageSpectra()
        
        # Gte the spectral data from the selected map
        intensities = self.window.averages[index][1][1]
        frequencies = self.window.averages[index][1][0]
        
        # Performs minimization of cost function
        minner = Minimizer(self.cost, params, 
                           fcn_args = (intensities, frequencies))
        result = minner.minimize()
        bestParams = result.params
        v = bestParams.valuesdict()
        
        # Set the baseline and Band parameters to the optimized result
        self.fitBase.setOffset(f'{v["offset"]:.2f}')
        self.fitBase.setSlope(f'{v["slope"]:.3f}')
        
        for peak in range(numPeaks):
            self.fitBands.band(f'B{peak}').setPos(round(v[f'x{peak}'], 2))
            self.fitBands.band(f'B{peak}').setDec(round(v[f'd{peak}'], 2))
            self.fitBands.band(f'B{peak}').setInt(round(v[f'h{peak}'], 2))
        
        # Display optimized result
        self.displaySpectra()
        
        # Check if the fit is acceptable
        answer = askyesno('Guide fit result', 
                          'Do you accept the fit?')
        
        # If acceptable, polish the program atatus and save the fit parameters
        if answer:
            self.fitBands.clearEmptyBands()
            self.varSelectedBand.set(f'B{self.fitBands.getUsefulLength() - 1}')
            self.saveFitParameters(mapIndex, result)
            self.fitBands.guideFitted()
            
            self.window.insertLog('fitGuide')
        
            return 0
        # If not acceptable, return displayed parameters to initial guess
        else:
            v = params.valuesdict()
            for peak in range(numPeaks):
                self.fitBands.band(f'B{peak}').setPos(round(v[f'x{peak}'], 2))
                self.fitBands.band(f'B{peak}').setDec(round(v[f'd{peak}'], 2))
                self.fitBands.band(f'B{peak}').setInt(round(v[f'h{peak}'], 2))
                
            self.fitBase.setOffset(f'{v["offset"]:.2f}')
            self.fitBase.setSlope(f'{v["slope"]:.3f}')
            self.displaySpectra()
            return 1
    
    def saveFitParameters(self, mapIndex: int, result):
        ''' Save the accepted fit parameters to a file for future reference and import. 
        For each of the currently analyzed maps, write a fit_report output in each folder. '''
        for map in self.window.maps:
            os.chdir(map.directory)
            
            os.makedirs(f'{map.orig}_Files/Parameters', exist_ok = True)
            
            with open(f'{map.orig}_Files/Parameters/GuideFitParams.txt', 'w') as newFile:
                newFile.write(fit_report(result))
            
        return 0
        
    def createMapParams(self):
        '''bandCreate is a dict returned from .bandDict() method in Bandas class, where each value a Band instance.
        Differs from createGuideParams in that it doesn't allow for full variation of positions and decays. '''
        # Get the current Bands element
        bandCreate = self.fitBands.bandDict()
        params = Parameters()
        
        # Add current linear baseline parameters
        params.add('offset', value = float(self.fitBase.getOffset()))
        params.add('slope', value = float(self.fitBase.getSlope()))
        
        # No need to check for empty bands, as the program only allows to fit the maps 
        # if no changes were made after last average fit
        for bandNum, band in enumerate(bandCreate.values()):
            # If position and decay fix Chechbutton True, vary = False for those parameters
            if self.varChkFix.get():
                params.add(f'x{bandNum}', 
                           value = float(band.getPos()), 
                           vary = False)
                params.add(f'd{bandNum}', 
                           value = float(band.getDec()), 
                           vary = False)
                params.add(f'h{bandNum}', 
                           value = float(band.getInt()), 
                           min = 0)
            # If not, allow a +- 3 in each parameter to accomodate inhomogeneity
            else:
                params.add(f'x{bandNum}', 
                           value = float(band.getPos()), 
                           min = float(band.getPos()) - 3, 
                           max = float(band.getPos()) + 3)
                params.add(f'd{bandNum}', 
                           value = float(band.getDec()),
                           min = float(band.getDec()) - 3, 
                           max = float(band.getDec()) + 3)
                params.add(f'h{bandNum}', 
                           value = float(band.getInt()), 
                           min = 0)
        return params
    
    def fitMap(self):
        ''' Fit all spectra in a map using the result of the average spectra fit. '''
        if self.window.maps.isEmpty():
            return 1
            
        # Only allow map fitting if there were no changes or additions to Bands element after
        # the last average spectra fit.
        if not self.fitBands.checkFitted():
            showerror('Error', 
                      'Average spectra is not fitted or changes were made after last fit')
            return 1
        
        params = self.createMapParams()
        numPeaks = self.fitBands.getLength()
        
        # Activate the progress bar in Status Frame to show progress to user 
        # and avoid panic
        progressStep = 300 / (self.window.maps.length() * self.window.maps[0].spectraNum)
        self.window.statFrame.progressLabel.config(text = 'Processing:   Fitting spectra')
        
        for map in self.window.maps:
            
            # Load map data to memory
            mapData = self.window.readMap(map)
            
            os.chdir(map.directory)
            
            # Create relevant directories
            os.makedirs(f'{map.orig}_Files/Fits', exist_ok = True)
            os.makedirs(f'{map.orig}_Files/Fits/Reports', exist_ok = True)
            os.makedirs(f'{map.orig}_Files/Fits/Heatmaps', exist_ok = True)
            if self.varChkFitFig.get():
                # Only create this if the user wants the fit figures
                os.makedirs(f'{map.orig}_Files/Fits/Figures', exist_ok = True)
                    
            frequencies = mapData.pop('freq')
            # dict to save the peak intensities for heatmaps
            mapIntensities = {}
            
            for key, intensity in mapData.items():
                
                # Perform minimization
                minner = Minimizer(self.cost, params, 
                                   fcn_args = (intensity, frequencies))
                result = minner.minimize()
                bestParams = result.params
                
                # Write the result to files 
                self.writeFitSpectra(bestParams, frequencies, intensity, key, map)
                self.writeFitReport(result, key, map)
                
                spectraInts = []

                v = bestParams.valuesdict()
                # Extract the intensity value for each peak and append it to mapIntensities
                for peak in range(numPeaks):
                    spectraInts.append(round(v[f'h{peak}'], 2))
                
                mapIntensities[key] = spectraInts
                
                # Update progress bar
                self.window.statFrame.progressBar['value'] += progressStep
                self.window.statFrame.update_idletasks()
            
            # Write the heatmap files for each peak and update progress bar
            self.writeHeatmaps(mapIntensities, map)
            self.window.statFrame.progressBar['value'] += progressStep
            self.window.statFrame.update_idletasks()
        
        # Reset progress bar
        self.window.statFrame.progressBar['value'] = 0
        self.window.statFrame.progressLabel.config(text = 'Processing: ')
        
        # Log process
        self.window.insertLog('fitMap')
        
        # Inform process finalization to user
        showinfo('Information', 
                 'Maps fitted successfully')
        
        # Update Bands and FitBaseline objects to show all changes saved
        self.fitBands.saveChanges()
        self.fitBase.allChangesSaved = True
        return 0
            
    def writeHeatmaps(self, mapIntensities: dict, map: Map):
        ''' Write the heatmap files from the fit result.
        A heatmap is a 2D representation of a 3D graph using color as a scale '''
        numPeaks = self.fitBands.getUsefulLength()
        
        os.chdir(f'{map.orig}_Files/Fits/Heatmaps')
        
        # Write the file
        with open(f'{map.name}_heatmaps.txt', 'w') as newFile:
            newFile.write('X(um)\tY(um)')
            
            for peak in range(numPeaks):
                newFile.write(f'\tI(B{peak})')
            
            for key, intensities in mapIntensities.items():
                newFile.write('\n')
                newFile.write(f'{key[0]}\t{key[1]}')
                for peak in range(numPeaks):
                    newFile.write(f'\t{intensities[peak]}')
        
        os.chdir(map.directory)
        
        # If the user wants, generate the figure for the saved heatmap
        if self.varChkSaveHeat.get():
            self.drawHeatFigure(mapIntensities, map)
        return 0
    
    def drawHeatFigure(self, mapIntensities: dict, map: Map):
        numPeaks = self.fitBands.getUsefulLength()
        
        # Create the x and y points of the map.
        # They generate the image that was scanned in the map
        x = np.array([])
        y = np.array([])
        for key in mapIntensities:
            x = np.append(x, key[0])
            y = np.append(y, key[1])
        
        # Eliminate repeats and sort them
        x = np.sort(np.unique(x))
        y = np.sort(np.unique(y))
        
        os.chdir(f'{map.orig}_Files/Fits/Heatmaps')
        
        for peak in range(numPeaks):
            # Add all the intensities for the given peak
            intensities = np.array([])
            for yValue in y:
                for xValue in x:
                    intensities = np.append(intensities, mapIntensities[(xValue, yValue)][peak])
            
            # Plot the heatmap in greyscale and save it
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
    def writeFitReport(fitResult, key: tuple, map: Map):
        # Remove the decimal part if present to avoid file name corruption
        x = key[0].split('.')[0]
        y = key[1].split('.')[0]
        
        os.chdir(f'{map.orig}_Files/Fits/Reports')
        
        # Write the fit report for this (x, y) point
        with open(f'{map.name}_X_{x}_Y_{y}.txt', 'w') as newFile:
            newFile.write(fit_report(fitResult))
        
        os.chdir(map.directory)
        return 0
        
    def writeFitSpectra(self, params: Parameters, frequencies: list, intensities: list, key: tuple, map: Map): 
        numPeaks = self.fitBands.getLength()
        v = params.valuesdict()
        
        # Get the intensity values for the optimized model
        fit = self.calculateModel(params, frequencies)
        
        # Remove decimal to avoid filename corruption
        x = key[0].split('.')[0]
        y = key[1].split('.')[0]
        
        os.chdir(f'{map.orig}_Files/Fits')
                
        with open(f'{map.name}_X_{x}_Y_{y}.txt', 'w') as newFile:
            newFile.write('Wavenumber(cm-1)\tIntData\tInt(FitTotal)\tInt(Baseline)')
            
            bandFit = {}
            for peak in range(numPeaks):
                # For each peak add an intensitity column header
                newFile.write(f'\tInt(B{peak})')
                
                # And add the intensity of a fit containing a single band
                bandParams = Parameters()
                bandParams.add('offset', value = v['offset'])
                bandParams.add('slope', value = v['slope'])
                bandParams.add('x0', value = v['x' + str(peak)])
                bandParams.add('d0', value = v['d' + str(peak)])
                bandParams.add('h0', value = v['h' + str(peak)])
                
                bandFit[f'B{peak}'] = self.calculateModel(bandParams, frequencies)
                
            newFile.write('\n')
            
            # Write the values for frequency, intensity data, fit data, baseline,
            # and the intensity of each single band
            for index, freq in enumerate(frequencies):
                newFile.write(f'{freq:.2f}\t{intensities[index]:.2f}\t{fit[index]:.2f}\t')
                newFile.write(f'{freq * v["slope"] + v["offset"]:.2f}')
                              
                for peak in range(numPeaks):
                    newFile.write(f'\t{bandFit["B" + str(peak)][index]:.2f}')
                newFile.write('\n')
        
        os.chdir(map.directory)
        
        if self.varChkFitFig.get():
            # If selected by user, generate the fit figures
            self.drawFitFigure(frequencies, intensities, key, fit, bandFit, params, map)
        return 0
    
    @staticmethod
    def drawFitFigure(frequencies: list, intensities: list, key: tuple, fit: list, bandFit: dict, params: Parameters, map: Map):
        ''' Generate figures for spectra fitting. '''
        fig = plt.Figure()
        
        # Add subplot
        plot1 = fig.add_subplot(111, xlabel = 'Wavenumber (cm-1)', ylabel = 'Intensity')
        
        # Plot data and total band fit
        plot1.plot(frequencies, intensities, 'k')
        plot1.plot(frequencies, fit, 'r', alpha = 0.8)
        
        # Plot each Band element
        for peak in range(len(bandFit)):
            plot1.plot(frequencies, bandFit[f'B{peak}'], alpha = 0.5)
        
        v = params.valuesdict()
        # Plot baseline
        plot1.plot(frequencies, np.array(frequencies) * v['slope'] + v['offset'], alpha = 0.5)
        
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
        
        os.chdir(f'{map.orig}_Files/Fits/Figures')
        
        fig.savefig(f'{map.name}_X_{x}_E-{xDec}_Y_{y}_E-{yDec}_fit.png')
        plt.close()
        
        os.chdir(map.directory)
        return 0

    def displaySpectra(self, window: Tk = None):
        ''' Display current average spectra with the Tab specific plots. '''
        if window is None:
            window = self.window
            
        if window.maps.isEmpty():
            return 1
        
        window.getAverageSpectra()
        
        # Reinitialize plot
        plot = window.plotFrame.figure.reInitPlot()
        
        # Get the index for the selected Map in Legend Frame
        for index, average in window.averages.enumerate():
            if average[0].orig == window.varSelectedMap.get():
                selectedMapIndex = index
                break
        
        for col, spectra in window.averages.enumerate(): 
            # Plot every average spectra 
            plot.plot(spectra[1][0], spectra[1][1], 
                      color = COLORS[col % len(COLORS)])
            
            # Only continue plotting Band elements for the currently selected Map
            if col != selectedMapIndex:
                continue
            
            # If there are collected Band elements, ensure that no baseline parameters are undefined
            if self.fitBands.getUsefulLength() != 0:
                if self.fitBase.getOffset() == '':
                    self.fitBase.setOffset('0.0')
                if self.fitBase.getSlope() == '':
                    self.fitBase.setSlope('0.0')
            
                # Only plot if there are collected Band elements
                offset = float(self.fitBase.getOffset())
                slope = float(self.fitBase.getSlope())
                spectraBase = np.array(spectra[1][0]) * slope + offset 
                            
                plot.plot(spectra[1][0], spectraBase, c = '#444444')
                
                fitParams = self.createGuideParams()
                
                # Calculate model for current Band elements and plot
                spectraFit = self.calculateModel(fitParams, spectra[1][0])
                
                plot.plot(spectra[1][0], spectraFit, c = '#191919')
                
                #Plot each individal Band elements
                for band in self.fitBands:
                    bandParams = self.createGuideParams({'B0': band})
                    bandFit = self.calculateModel(bandParams, spectra[1][0])
                    plot.plot(spectra[1][0], bandFit, alpha = 0.5) 

        window.plotFrame.figure.saveLimits()
        window.plotFrame.figure.drawCanvas()
        
        # Update limits in Status Frame
        self.window.statFrame.getLimits()
        return 0

    def handleMouseEvent(self, x: float, y: float):
        ''' Function triggered upon a mouse event on the plot, when the Fit tab is active. '''
        if self.fitBands.collecting():
            # If Band parameter collection is ON, add a reference point to the currently selected Band
            name = self.varSelectedBand.get()
            if self.fitBands.addReference(x, y, name):
                # addReference method returns True if all 3 reference points are gathered and collection is finished
                self.fitBands.changeCollecting()
                self.btnSelectBand.config(bg = '#f0f0f0')
                self.displaySpectra()
                
                # Change Radiobutton selection to next Band element un less this is the last one
                if self.varSelectedBand.get() != f'B{self.fitBands.getLength() - 1}':
                    newBand = int(self.varSelectedBand.get()[1:]) + 1
                    self.varSelectedBand.set(f'B{newBand}')
                
        elif self.fitBase.selectOn():
            # If fit baseline collection is ON, add a reference point to FitBaseline element
            if self.fitBase.addReference(x, y):
                # addReference method returns True if all 2 reference points were gathered and collection is finished
                self.fitBase.changeSelect()
                self.displaySpectra()
                
        return 0
