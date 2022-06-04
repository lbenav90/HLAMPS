from collections import OrderedDict
from idlelib.tooltip import Hovertip
from .Global_Functions import isNumber
from tkinter import StringVar, BooleanVar, Radiobutton, Entry, Checkbutton, Label, Frame, Button

class Band:
    ''' Contains the information and the widgets of a band '''
    def __init__(self, bandNum: int, frame: Frame):
        self.frame = frame
        
        self.name = f'B{bandNum}'
        
        # Lorentzian function parameters
        self.position = StringVar(value = '')
        self.decay = StringVar(value = '')
        self.intensity = StringVar(value = '')
        
        # Fix parameters in spectrum fit
        self.posFix = BooleanVar(value = False)
        self.decFix = BooleanVar(value = False)
        self.intFix = BooleanVar(value = False)
        
        # All parameters are were collected
        
        # Widgets for the Band
        self.radio = Radiobutton(frame)
        self.label = Label(frame)
        self.posEntry = Entry(frame)
        self.decEntry = Entry(frame)
        self.intEntry = Entry(frame)
        self.posFixChk = Checkbutton(frame)
        self.decFixChk = Checkbutton(frame)
        self.intFixChk = Checkbutton(frame)
        
        # Were the parameters changed from the last average spectra fit
        self.unchangedFromLastFit = False
        
        self.allChangesSaved = True
    
        self.displayLayout()
        
        # Trace the variables to detect unsaved changes and collection
        self.position.trace('w', self.detectEntry)
        self.decay.trace('w', self.detectEntry)
        self.intensity.trace('w', self.detectEntry)

        self.collected = False
        
    def getName(self):
        ''' Returns the name of the band '''
        return self.name
    
    def setPos(self, s: float):
        ''' Sets position variable '''
        self.position.set(s)
        return 0
    
    def setDec(self, s: float):
        ''' Sets decay variable '''
        self.decay.set(s)
        return 0
    
    def setInt(self, s: float):
        ''' Sets intensity variable '''
        self.intensity.set(s)
        return 0
    
    def getPos(self):
        ''' Gets position variable '''
        return self.position.get()
    
    def getDec(self):
        ''' Gets decay variable '''
        return self.decay.get()
    
    def getInt(self):
        ''' Gets the intensity variable '''
        return self.intensity.get()
    
    def detectEntry(self, name, index, trigger):
        ''' Function triggered everytime a band parameter is changed.
        Detects if the band parameter is fully collected and viable for plotting '''

        # If any of the variables is the empty string, tha band is not collected
        if self.getPos() != '' and self.getDec() != '' and self.getInt() != '':
            self.collected = True       
        else:
            self.collected = False  
        
        # If it was just initialized or the average spectra was just fitted, 
        # a parameter change generates unsaved changes and fit changes.
        if self.unchangedFromLastFit:
            self.unchangedFromLastFit = False
            self.allChangesSaved = False
        return 0
    
    def getFixes(self, index: int):
        ''' Gets the fix parameter status for the average spectra fit.
        index 0, 1 and 2 are for postion, decay and intensity, respectively. '''
        fixes = [self.posFix, self.decFix, self.intFix]
        return fixes[index].get()
    
    def rename(self, numBand):
        ''' Rename a Band element and return it '''
        self.name = f'B{numBand}'
        return self
    
    def destroy(self):
        ''' Destroys all band widgets '''
        self.label.destroy()
        self.radio.destroy()
        self.posEntry.destroy()
        self.decEntry.destroy()
        self.intEntry.destroy()
        self.posFixChk.destroy()
        self.decFixChk.destroy()
        self.intFixChk.destroy()
        return 0
    
    def addRadio(self, radioVar: StringVar):
        ''' Adds the radiobutton for the band '''
        self.radio = Radiobutton(self.frame, value = self.name, 
                                      variable = radioVar)
    
        self.radio.grid(column = 2 * int(self.name[1:]) + 1, row = 4, sticky = 'w')
        return 0
    
    def displayLayout(self):
        ''' Generates widget display on the GUI '''
        # Label with band name
        self.label = Label(self.frame, text = self.name)
        
        self.label.grid(column = 2 * int(self.name[1:]) + 1, row = 0)
        
        # Entrys with input validation for parameters
        self.posEntry = Entry(self.frame, textvariable = self.position, 
                              width = 10, validate = 'all', 
                              validatecommand = (self.frame.register(isNumber), '%P'))
        
        self.decEntry = Entry(self.frame, textvariable = self.decay,
                              width = 10, validate = 'all', 
                              validatecommand = (self.frame.register(isNumber), '%P'))
                        
        self.intEntry =  Entry(self.frame, textvariable = self.intensity, 
                               width = 10, validate = 'all', 
                                validatecommand = (self.frame.register(isNumber), '%P'))
        
        self.posEntry.grid(column = 2 * int(self.name[1:]) + 1, row = 1)
        self.decEntry.grid(column = 2 * int(self.name[1:]) + 1, row = 2)
        self.intEntry.grid(column = 2 * int(self.name[1:]) + 1, row = 3)
        
        # Checkboxes for parameter fix in spectra fitting
        self.posFixChk = Checkbutton(self.frame, variable = self.posFix)
        self.decFixChk = Checkbutton(self.frame, variable = self.decFix)
        self.intFixChk = Checkbutton(self.frame, variable = self.intFix)
    
        self.posFixChk.grid(column = 2 * int(self.name[1:]) + 2, row = 1)
        self.decFixChk.grid(column = 2 * int(self.name[1:]) + 2, row = 2)
        self.intFixChk.grid(column = 2 * int(self.name[1:]) + 2, row = 3)

        return 0
        
class Bands:
    ''' Contains all Band objects added to the GUI '''
    def __init__(self):
        self.bands = OrderedDict()

        # Used to signal if Band parameter collection is ON
        self.collect = False

        # Used to store (x, y) points while Band parameter collection is ON
        self.references = []
    
    def __iter__(self):
        ''' Iteration happens over the dict values'''
        return iter(self.bands.values())
    
    def collecting(self):
        ''' Checks if data collection is ON '''
        return self.collect
    
    def changeCollecting(self):
        ''' Changes collection status '''
        self.collect = not self.collect
        return 0
    
    def guideFitted(self):
        ''' Passes the average spectra successful fit to the Band elements'''
        for band in self.bands.values():
            band.unchangedFromLastFit = True
    
    def checkFitted(self):
        ''' Checks if any Band element parameters were changed since
        last average spectra fit '''
        for band in self.bands.values():
            if not band.unchangedFromLastFit:
                return False
        return True
    
    def checkChanges(self):
        ''' Checks for unsaved changes '''
        for band in self.bands.values():
            if not band.allChangesSaved:
                return False
        return True
    
    def saveChanges(self):
        ''' Passes the saved changes update to the Band elements '''
        for band in self.bands.values():
            band.allChangesSaved = True
        return 0
    
    def addBand(self, band: Band):
        ''' Adds a new Band element '''
        self.bands[band.getName()] = band
        return 0
    
    def getUsefulLength(self):
        ''' Returns the number of Band elements which are fully collected '''
        useful = 0
        for name in self.bands:
            if self.bands[name].collected:
                useful += 1
        return useful

    def getLength(self):
        ''' Returns the total Band elements '''
        return len(self.bands)
    
    def bandDict(self):
        ''' Returns a copy of the Bands as a dict of non empty Band elements'''
        newDict = {}
        for name, band in self.bands.items():
            if band.collected:
                newDict[name] = band
        return newDict
    
    def __getitem__(self, name: str):
        ''' Returns a Band element on name input '''
        return self.bands[name]
    
    def enumerate(self):
        ''' For enumeration of the Band elements '''
        return enumerate(self.bands.values())
    
    def deleteBand(self, name: str):
        ''' Delete the currently selected band '''
        self.bands.pop(name)
        
        tempBands = OrderedDict()

        # Populate a new OrderedDict renaming all remaining Bans elements
        for index, band in enumerate(self.bands):
            tempBands[f'B{index}'] = self.bands[band].rename(index)
        
        # Copy the tempBands onto the real bands dict
        self.bands = tempBands.copy()
        return 0
    
    def clearBands(self):
        ''' Destroys all Band elements and reinitializes the class '''
        for name in self.bands:
            self.bands[name].destroy()

        self.bands.clear()
        self.collect = False
        self.references = []
        return 0
    
    def clearEmptyBands(self):
        ''' Destroys all Band elements which are not fully collected '''
        for name in self.bands:
            if not self.bands[name].collected:
                self.bands[name].destroy()
        self.collect = False
        self.references = []
        return 0
 
    def updateLayout(self, radioVar: StringVar):
        ''' Updates the GUI layout and adds Radiobuttons '''
        for band in self.bands:
            self.bands[band].displayLayout()
            self.bands[band].addRadio(radioVar)
        return 0
    
    def addReference(self, x: float, y: float, name: str):
        ''' Adds a new reference point while collecting Band parameters.
        If upon collection, references has 3 datapoints, it extracts the parameters.'''
        self.references.append([x, y])
        if len(self.references) == 3:
            self.extractParameters(name)
            return True
        else:
            return False
    
    def extractParameters(self, name: str):
        ''' Uses 3 reference points collected to calculate Band parameters '''
        band = self.bands[name]
        
        # Set Band parameters
        band.setPos(f'{self.references[0][0]:.2f}')
        band.setDec(f'{abs(self.references[0][0] - self.references[1][0]):.2f}')
        band.setInt(f'{abs(self.references[2][1] - self.references[0][1]):.2f}')
        
        # Turn collection OFF and reinitialize references
        self.references.clear()
        self.changeCollecting()
        return 0

class FitBaseline:
    ''' Contains the parameters and relevant widgets for the linear baseline
    used for spectra fitting '''
    def __init__(self, frame: Frame):
        # Variables and fix statuses
        self.slope = StringVar(value = '')
        self.offset = StringVar(value = '')
        self.fixSlope = BooleanVar(value = False)
        self.fixOffset = BooleanVar(value = False)

        # Plot data collection status and reference point temp list
        self.select = BooleanVar(value = False)
        self.references = []

        # All changes were saved
        self.allChangesSaved = True
        
        # Button to turn collection ON
        self.defButton = Button(frame, text = 'Select', command = self.changeSelect)
        self.defButton.grid(column = 0, row = 0, sticky = 'nw')

        Hovertip(self.defButton, 
                 'Define baseline by selecting in graph', 
                 hover_delay = 1000)
        
        # Entrys with input validation for baseline parameters and checkbuttons for fix status
        self.offsetEntry = Entry(frame, textvariable = self.offset, 
                                 width = 10, validate = 'all', 
                                 validatecommand = (frame.register(isNumber), '%P'))
        self.offsetEntry.grid(column = 1, row = 2, sticky = 'w')
        
        self.offsetCheck = Checkbutton(frame, text = '', 
                                       variable = self.fixOffset)
        self.offsetCheck.grid(column = 2, row = 2, sticky = 'w')
        
        self.slopeEntry = Entry(frame, textvariable = self.slope, 
                                width = 10,validate = 'all', 
                                validatecommand = (frame.register(isNumber), '%P'))
        self.slopeEntry.grid(column = 1, row = 3, sticky = 'w')
        
        self.slopeCheck = Checkbutton(frame, text = '', 
                                      variable = self.fixSlope)
        self.slopeCheck.grid(column = 2, row = 3, sticky = 'w')
        
        # Trace the parameter variables to detect when unsaved changes 
        self.offset.trace('w', self.changeMade)
        self.slope.trace('w', self.changeMade)
    
    def changeMade(self, name, index, trigger):
        ''' Function triggers upon parameter change '''
        self.allChangesSaved = False
        return 0
    
    def getSlope(self):
        ''' Get slope parameter'''
        return self.slope.get()

    def getOffset(self):
        ''' Get offset parameter '''
        return self.offset.get()
    
    def setOffset(self, s: str):
        ''' Sets offset parameter '''
        self.offset.set(s)
        return 0
    
    def setSlope(self, s: str):
        ''' Sets slope parameter '''
        self.slope.set(s)
        return 0
    
    def addReference(self, x: float, y: float):
        ''' Add a reference point to temp list.
        If upon collection, the list has 2 points, extracts the baseline parameters.'''
        self.references.append([x, y])
        if len(self.references) == 2:
            self.extractParameters()
            return True
        else:
            return False
    
    def selectOn(self):
        ''' Checks if baseline parameter collection is ON '''
        return self.select.get()
    
    def clearBase(self):
        ''' Reinitializes class '''
        self.slope.set('')
        self.offset.set('')
        self.fixOffset.set(False)
        self.fixSlope.set(False)
        self.references.clear()
        self.select.set(False)
        self.defButton.config(bg = '#f0f0f0')
        self.allChangesSaved = True
        return 0
    
    def changeSelect(self):
        ''' Changes baseline parameter collection status '''
        self.select.set(not self.select.get()) 
        # Change color of button to reflect status
        self.defButton.config(bg = '#95CCD9' * self.select.get() 
                                 + '#f0f0f0' * (not self.select.get()))

        return 0
    
    def extractParameters(self):
        ''' Uses the 2 reference points in references to calculate baseline parameters'''
        newSlope = (self.references[0][1] - self.references[1][1]) / (self.references[0][0] - self.references[1][0])
        newOffset = self.references[0][1] - newSlope * self.references[0][0]

        self.slope.set(f'{newSlope:.3f}')
        self.offset.set(f'{newOffset:.2f}')
        
        #Reinitialize 
        self.references.clear()
        self.changeSelect()
        return 0
