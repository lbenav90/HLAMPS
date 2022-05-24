from StartTab import StartTab
from ShiftTab import ShiftTab
from CutTab import CutTab
from SubtractTab import SubtractTab
from FitTab import FitTab
from dataclasses import dataclass, field


@dataclass
class Tabs:
    startTab: StartTab
    shiftTab: ShiftTab
    cutTab: CutTab
    subtractTab: SubtractTab
    fitTab: FitTab
    tabDict: dict = field(default_factory= lambda: ({}))
    
    def __post_init__(self):
        self.tabDict['Start'] = self.startTab
        self.tabDict['Shift spectra'] = self.shiftTab
        self.tabDict['Cut spectra'] = self.cutTab
        self.tabDict['Subtract baseline'] = self.subtractTab
        self.tabDict['Fit spectra'] = self.fitTab
    
    def __iter__(self):
        return iter(self.tabDict.values())
