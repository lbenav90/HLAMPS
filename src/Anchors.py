from tkinter.messagebox import showerror

class Anchors:
    ''' Contains the baseline information for the spectra baseline correction '''
    def __init__(self):
        self.anchors = []
        self.buttons = []
    
    def addAnchor(self, anchor: float):
        ''' Add a new baseline anchor that comes from a mouse event '''
        # No duplicates
        if anchor in self.anchors:
            return 1
        
        # No out of frequency range anchors
        if self.length() >= 2 and (anchor < self.anchors[0] or anchor > self.anchors[-1]):
            return 1
        
        # Append anchor and sort
        self.anchors.append(anchor)
        self.anchors.sort()
        return 0
        
    def delAnchor(self, anchor: float):
        ''' Deletes an existing anchor, which is determined by the button that is pressed'''
        index = self.anchors.index(anchor)
        
        # Don't allow fot the frequency endpoins to be deleted
        if index == 0 or index == len(self.anchors) - 1:
            showerror('Error', 
                      'Cannot remove the spectra limits')
            return 1
        
        self.anchors.pop(index)
        return 0
    
    def isEmpty(self):
        ''' Checks if there are anchors '''
        return len(self.anchors) == 0
    
    def enumerate(self):
        ''' For enumeration '''
        return enumerate(self.anchors)
    
    def asList(self):
        ''' Returns the anchor list '''
        return self.anchors
    
    def length(self):
        ''' Returns the length of the anchor list '''
        return len(self.anchors)
    
    def clear(self):
        ''' Clears anchor list '''
        self.anchors.clear()
        return 0
    
    def __iter__(self):
        ''' For iteration '''
        return iter(self.anchors)
    
    def __getitem__(self, index):
        ''' For subscrption '''
        return self.anchors[index]