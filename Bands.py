from tkinter import StringVar, BooleanVar, Radiobutton, Entry, Checkbutton, Label, Frame, Button
from collections import OrderedDict
from idlelib.tooltip import Hovertip

class Band:
    def __init__(self, bandNum: int, frame: Frame):
        ''' Initialize Band '''
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
        self.collected = False
        
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
        self.unchangedFromLastFit = True
        
        self.allChangesSaved = True
    
        self.displayLayout()
        
        # Trace the variables to detect unsaved changes and collection
        self.position.trace('w', self.detectEntry)
        self.decay.trace('w', self.detectEntry)
        self.intensity.trace('w', self.detectEntry)
        
    def getName(self):
        return self.name
    
    def setPos(self, s):
        self.position.set(s)
    
    def setDec(self, s):
        self.decay.set(s)
    
    def setInt(self, s):
        self.intensity.set(s)
    
    def getPos(self):
        return self.position.get()
    
    def getDec(self):
        return self.decay.get()
    
    def getInt(self):
        return self.intensity.get()
    
    def detectEntry(self, name, index, trigger):
        if self.getPos() != '' and self.getDec() != '' and self.getInt() != '':
            self.collected = True       
        else:
            self.collected = False  
        
        if self.unchangedFromLastFit:
            self.unchangedFromLastFit = False
            self.allChangesSaved = False
    
    def getFixes(self, index):
        fixes = [self.posFix, self.decFix, self.intFix]
        return fixes[index].get()

    def getAll(self):
        print(self.getName(), self.getPos(), self.getDec(),
              self.getInt(), self.getFixes(0), self.getFixes(1), 
              self.getFixes(2), self.collected)
    
    def rename(self, numBand):
        self.name = 'B' + str(numBand)
        return self
    
    @staticmethod
    def isNumber(s):
        return s.isdigit() or s.replace('.', '0', 1).isdigit() or s == ''
    
    def destroy(self):
        self.label.destroy()
        self.radio.destroy()
        self.posEntry.destroy()
        self.decEntry.destroy()
        self.intEntry.destroy()
        self.posFixChk.destroy()
        self.decFixChk.destroy()
        self.intFixChk.destroy()
    
    def addRadio(self, radioVar):
        self.radio = Radiobutton(self.frame, value = self.name, 
                                      variable = radioVar)
    
        self.radio.grid(column = 2 * int(self.name[1:]) + 1, row = 4, sticky = 'w')
    
    def displayLayout(self):
        self.label = Label(self.frame, text = self.name)
        
        self.label.grid(column = 2 * int(self.name[1:]) + 1, row = 0)
        
        self.posEntry = Entry(self.frame, textvariable = self.position, 
                              width = 10, validate = 'all', 
                              validatecommand = (self.frame.register(self.isNumber), '%P'))
        
        self.decEntry = Entry(self.frame, textvariable = self.decay,
                              width = 10, validate = 'all', 
                              validatecommand = (self.frame.register(self.isNumber), '%P'))
                        
        self.intEntry =  Entry(self.frame, textvariable = self.intensity, 
                               width = 10, validate = 'all', 
                                validatecommand = (self.frame.register(self.isNumber), '%P'))
        
        self.posEntry.grid(column = 2 * int(self.name[1:]) + 1, row = 1)
        self.decEntry.grid(column = 2 * int(self.name[1:]) + 1, row = 2)
        self.intEntry.grid(column = 2 * int(self.name[1:]) + 1, row = 3)
        
        self.posFixChk = Checkbutton(self.frame, variable = self.posFix)
        self.decFixChk = Checkbutton(self.frame, variable = self.decFix)
        self.intFixChk = Checkbutton(self.frame, variable = self.intFix)
    
        self.posFixChk.grid(column = 2 * int(self.name[1:]) + 2, row = 1)
        self.decFixChk.grid(column = 2 * int(self.name[1:]) + 2, row = 2)
        self.intFixChk.grid(column = 2 * int(self.name[1:]) + 2, row = 3)
        
class Bands:
    def __init__(self):
        self.bands = OrderedDict()
        self.collect = False
        self.references = []
    
    def __iter__(self):
        return iter(self.bands.values())
    
    def collecting(self):
        return self.collect
    
    def changeCollecting(self):
        self.collect = not self.collect
    
    def guideFitted(self):
        for band in self.bands.values():
            band.unchangedFromLastFit = True
    
    def checkFitted(self):
        for band in self.bands.values():
            if not band.unchangedFromLastFit:
                return False
        return True
    
    def checkChanges(self):
        for band in self.bands.values():
            if not band.allChangesSaved:
                return False
        return True
    
    def saveChanges(self):
        for band in self.bands.values():
            band.allChangesSaved = True
        return 0
    
    def addBand(self, band):
        self.bands[band.getName()] = band
    
    def getUsefulLength(self):
        useful = 0
        for name in self.bands:
            if self.bands[name].collected:
                useful += 1
        return useful

    def getLength(self):
        return len(self.bands)
    
    def bandDict(self):
        return self.bands.copy()
    
    def band(self, name):
        return self.bands[name]
    
    def enumerate(self):
        return enumerate(self.bands.values())
    
    def deleteBand(self, name):
        self.bands.pop(name)
        
        tempBands = OrderedDict()
        newNumBand = 0
        for band in self.bands:
            tempBands['B' + str(newNumBand)] = self.bands[band].rename(newNumBand)
            newNumBand += 1
        
        self.bands = tempBands.copy()
    
    def clearBands(self):
        for name in self.bands:
            self.bands[name].destroy()
        self.bands.clear()
        self.collect = False
        self.references = []
    
    def clearEmptyBands(self):
        for name in self.bands:
            if not self.bands[name].collected:
                self.bands[name].destroy()
        self.collect = False
        self.references = []
 
    def updateLayout(self, radioVar):
        for band in self.bands:
            self.bands[band].displayLayout()
            self.bands[band].addRadio(radioVar)
    
    def addReference(self, x, y, name):
        self.references.append([x, y])
        if len(self.references) == 3:
            self.extractParameters(name)
            return True
        else:
            return False
    
    def extractParameters(self, name):
        
        band = self.band(name)
        
        band.setPos(round(self.references[0][0], 2))
        band.setDec(round(abs(self.references[0][0] - 
                              self.references[1][0]), 2))
        band.setInt(round(abs(self.references[2][1] - 
                              self.references[0][1]), 2))
        
        self.references.clear()
        self.changeCollecting()

class FitBaseline:
    def __init__(self, frame):
        self.slope = StringVar(value = '')
        self.offset = StringVar(value = '')
        self.fixSlope = BooleanVar(value = False)
        self.fixOffset = BooleanVar(value = False)
        self.select = BooleanVar(value = False)
        self.references = []
        self.allChangesSaved = True
        
        self.defButton = Button(frame, text = 'Select', command = self.changeSelect)
        self.defButton.grid(column = 0, row = 0, sticky = 'nw')

        Hovertip(self.defButton, 
                 'Define baseline by selecting in graph', 
                 hover_delay = 1000)
        
        self.offsetEntry = Entry(frame, textvariable = self.offset, 
                                 width = 10, validate = 'all', 
                                 validatecommand = (frame.register(self.isNumber), '%P'))
        self.offsetEntry.grid(column = 1, row = 2, sticky = 'w')
        
        self.offsetCheck = Checkbutton(frame, text = '', 
                                       variable = self.fixOffset)
        self.offsetCheck.grid(column = 2, row = 2, sticky = 'w')
        
        self.slopeEntry = Entry(frame, textvariable = self.slope, 
                                width = 10,validate = 'all', 
                                validatecommand = (frame.register(self.isNumber), '%P'))
        self.slopeEntry.grid(column = 1, row = 3, sticky = 'w')
        
        self.slopeCheck = Checkbutton(frame, text = '', 
                                      variable = self.fixSlope)
        self.slopeCheck.grid(column = 2, row = 3, sticky = 'w')
        
        self.offset.trace('w', self.changeMade)
        self.slope.trace('w', self.changeMade)
    
    def changeMade(self, x, y, z):
        self.allChangesSaved
    
    def getSlope(self):
        return self.slope.get()

    def getOffset(self):
        return self.offset.get()
    
    def setOffset(self, s):
        self.offset.set(s)
    
    def setSlope(self, s):
        self.slope.set(s)
    
    def addReference(self, x, y):
        self.references.append([x, y])
        if len(self.references) == 2:
            self.extractParameters()
            return True
        else:
            return False
    
    def selectOn(self):
        return self.select.get()
    
    def clearBase(self):
        self.slope.set('')
        self.offset.set('')
        self.fixOffset.set(False)
        self.fixSlope.set(False)
        self.references.clear()
        self.select.set(False)
        self.defButton.config(bg = '#f0f0f0')
        self.allChangesSaved = True
    
    def changeSelect(self):
        self.select.set(not self.select.get()) 
        self.defButton.config(bg = '#95CCD9' * self.select.get() + 
                              '#f0f0f0' * (1 - self.select.get()))
    
    def extractParameters(self):
        self.slope.set(str(round((self.references[0][1] - self.references[1][1])
                                 /(self.references[0][0] - self.references[1][0]), 3)))
        self.offset.set(str(round(self.references[0][1] 
                                  - float(self.getSlope()) * self.references[0][0], 3)))
        
        self.references.clear()
    
        self.defButton.config(bg = '#f0f0f0')
        
    @staticmethod
    def isNumber(s):
        return s.isdigit() or s.replace('.', '0', 1).isdigit() or s == ''
