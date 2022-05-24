class Averages:
    def __init__(self):
        self.averages = []
    
    def addSpectra(self, map, data):
        self.averages.append([map, data])  
        
    def getSpectra(self, map):
        for spectra in self.averages:
            if map == spectra[0]:
                return spectra[1]
        return None
    
    def clear(self):
        self.averages.clear()
    
    def copy(self):
        return self.averages.copy()
    
    def enumerate(self):
        return enumerate(self.averages)
    
    def __iter__(self):
        return iter(self.averages)
    
    def __getitem__(self, index):
        return self.averages[index]