from StartTab import StartTab
from ShiftTab import ShiftTab
from CutTab import CutTab
from SubtractTab import SubtractTab
from FitTab import FitTab
from dataclasses import dataclass, field

@dataclass
class Tabs:
    ''' Data class containing all the Tabs in the notebook '''
    startTab: StartTab
    shiftTab: ShiftTab
    cutTab: CutTab
    subtractTab: SubtractTab
    fitTab: FitTab
    ''' Initialize with an empty dictionary'''
    tabDict: dict = field(default_factory= lambda: ({}))
    
    def __post_init__(self):
        ''' Populate tabDict with the Tabs after class initialization'''
        self.tabDict['Start'] = self.startTab
        self.tabDict['Shift spectra'] = self.shiftTab
        self.tabDict['Cut spectra'] = self.cutTab
        self.tabDict['Subtract baseline'] = self.subtractTab
        self.tabDict['Fit spectra'] = self.fitTab
    
    def __iter__(self):
        ''' For iteration '''
        return iter(self.tabDict.values())
