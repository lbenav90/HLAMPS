from dataclasses import dataclass

class Maps:
    ''' Contains the Map elements for the currently running program '''
    def __init__(self):
        self.maps = []
    
    def addMap(self, directory: str, name: str, orig: str):
        ''' Add a new Map element '''
        self.maps.append(Map(directory, name, orig))
    
    def delMap(self, orig):
        ''' If it exists, deletes a Map element by its original name (orig).
        Returns None if it does not exist. '''
        for i, map in enumerate(self.maps):
            if orig == map.orig:
                self.maps.pop(i)
                return 0
        return None
    
    def length(self):
        ''' Returns the number of Map elements'''
        return len(self.maps)
    
    def enumerate(self):
        ''' For enumeration '''
        return enumerate(self.maps)
        
    def isEmpty(self):
        ''' Checks if the class is empty '''
        return len(self.maps) == 0
        
    def clear(self):
        ''' Clears the class '''
        self.maps.clear()
        return 0
    
    def __iter__(self):
        ''' For iteration '''
        return iter(self.maps)
    
    def __getitem__(self, index):
        ''' Defines subscription '''
        return self.maps[index]
    
@dataclass
class Map:
    ''' Dataclass to store the map directory and name.
    orig and name start out the same, but name evolves with processing.
    spectraNum is set afterwards with the number of spectra in the map'''
    directory: str
    name: str
    orig: str
    spectraNum: int = None
