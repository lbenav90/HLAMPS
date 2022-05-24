class Limits:
    def __init__(self, axes):
        self.axes = axes
        self.xmin, self.xmax  = axes.get_xlim()
        self.ymin, self.ymax  = axes.get_ylim()
    
    def getXLim(self):
        return [self.xmin, self.xmax]

    def getYLim(self):
        return [self.ymin, self.ymax]