from .Maps import Map

class Averages:
    ''' Contains average spectra for the current maps '''
    def __init__(self):
        self.averages = []
    
    def addSpectra(self, map: Map, spectraData: list):
        ''' Adds a new average spectra '''
        self.averages.append([map, spectraData])  
        return 0
        
    def getSpectra(self, map: Map):
        ''' Gets a spectrum data from the Map object '''
        for spectra in self.averages:
            if map == spectra[0]:
                return spectra[1]
        return None
    
    def clear(self):
        ''' Clears the averages list'''
        self.averages.clear()
        return 0
    
    def copy(self):
        ''' Returns a copy of the averages data '''
        return self.averages.copy()
    
    def enumerate(self):
        ''' For enumeration '''
        return enumerate(self.averages)
    
    def __iter__(self):
        ''' For iteration '''
        return iter(self.averages)
    
    def __getitem__(self, index):
        ''' For subscription '''
        return self.averages[index]