from dataclasses import dataclass

class Maps:
    def __init__(self):
        self.maps = []
    
    def addMap(self, directory: str, name: str, orig: str):
        self.maps.append(Map(directory, name, orig))
    
    def delMap(self, orig):
        for i, map in enumerate(self.maps):
            if orig == map.orig:
                self.maps.pop(i)
                return 0
        return None
    
    def length(self):
        return len(self.maps)
    
    def enumerate(self):
        return enumerate(self.maps)
        
    def isEmpty(self):
        return len(self.maps) == 0
        
    def clear(self):
        self.maps.clear()
    
    def __iter__(self):
        return iter(self.maps)
    
    def __getitem__(self, index):
        return self.maps[index]
    
@dataclass
class Map:
    directory: str
    name: str
    orig: str
    spectraNum: int = None
