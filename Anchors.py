from tkinter.messagebox import showerror

class Anchors:
    def __init__(self):
        self.anchors = []
        self.button = []
    
    def addAnchor(self, anchor: float):
        if anchor in self:
            return 1
        
        if self.length() >= 2 and (anchor < self.anchors[0] or anchor > self.anchors[-1]):
            return 1
        
        self.anchors.append(anchor)
        self.anchors.sort()
        return 0
        
    def delAnchor(self, anchor: float):
        index = self.anchors.index(anchor)
        
        if index == 0 or index == len(self.anchors) - 1:
            showerror('Error', 
                      'Cannot remove the spectra limits')
            return 1
        
        self.anchors.pop(index)
    
    def isEmpty(self):
        return len(self.anchors) == 0
    
    def enumerate(self):
        return enumerate(self.anchors)
    
    def asList(self):
        return self.anchors
    
    def length(self):
        return len(self.anchors)
    
    def clear(self):
        self.anchors.clear()
        return 0
    
    def __iter__(self):
        return iter(self.anchors)
    
    def __getitem__(self, index):
        return self.anchors[index]