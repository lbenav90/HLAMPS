from Tabs import Tabs
from StartTab import StartTab
from ShiftTab import ShiftTab
from CutTab import CutTab
from SubtractTab import SubtractTab
from FitTab import FitTab
from tkinter import Tk
from tkinter.ttk import Notebook
from collections import OrderedDict

class TabNotebook(Notebook):
    ''' Notebook containing the tabs '''
    def __init__(self, window: Tk):
        ''' Initialize Notebook '''
        super().__init__(window)
        self.window = window
        self.configure({'width': window.winfo_width(),
                        'height': int(window.winfo_height() * 0.35)})
        
        ### Ordered Dict to keep track of active Tab
        self.active = OrderedDict()
        self.configureActive()
        
        self.configureTabs()
        
        self.grid(column = 0, columnspan = 2, 
                  row = 2, sticky = 'news')
        
        self.update_idletasks()
        return 0
    
    def configureActive(self):
        ''' Sets the self.active dictionary. This allows to keep a memory 
            of the exit tab on a tab change '''
        self.active['Start'] = [0, False]   ### [tab_id, current]
        self.active['Shift spectra'] = [1, False]
        self.active['Cut spectra'] = [2, False]
        self.active['Subtract baseline'] = [3, False]
        self.active['Fit spectra'] = [4, False]
        return 0
        
    def setActive(self, tabText):
        ''' Sets the active tab on self.active '''
        for text in self.active:
            self.active[text][1] = text == tabText
        return 0
    
    def getActiveId(self):
        ''' Returns the tab_id of the currently active tab '''
        for tab in self.active.values():
            if tab[1]:
                return tab[0]
        return None
    
    def clean(self):
        ''' Calls the clean() method for all tabs '''
        for tab in self.allTabs:
            tab.clearTab()
    
    def configureTabs(self):
        ''' Configures the tabs'''
        self.allTabs = Tabs(StartTab(self),
                            ShiftTab(self),
                            CutTab(self),
                            SubtractTab(self),
                            FitTab(self))
        
        # Binds the Notebook to call Tk.onTabChange method 
        self.bind('<<NotebookTabChanged>>', self.window.onTabChange)
        
        self.add(self.allTabs.startTab, text = 'Start')
        self.add(self.allTabs.shiftTab, text = 'Shift spectra')
        self.add(self.allTabs.cutTab, text = 'Cut spectra')
        self.add(self.allTabs.subtractTab, text = 'Subtract baseline')
        self.add(self.allTabs.fitTab, text = 'Fit spectra')
    
    def activeTab(self):
        ''' Returns the tab element that is active '''
        tabText = self.tab(self.select(), 'text')
        return self.allTabs.tabDict[tabText]

    def selectTab(self, tabId):
        ''' Returns a tab element  from a tabId defined in self.active '''
        texts = ['Start', 'Shift spectra', 'Cut spectra', 'Subtract baseline', 'Fit spectra']
        return self.allTabs.tabDict[texts[tabId]]