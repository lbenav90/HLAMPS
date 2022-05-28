import numpy as np
from lmfit import Parameters

def isNumber(s):
    ''' Used to validate Entry widgets' input for ints, floats or empty strings'''
    return s.isdigit() or s.replace('.', '0', 1).isdigit() or s == ''

def findClosest(value: float, samples: list):
    ''' Finds the index of the closest element to value in the list sample. '''
    minDif = 1e9
    minIndex = 0
    for index, sample in enumerate(samples):
        dif = abs(value - sample)
        if dif < minDif:
            minDif = dif
            minIndex = index
    return minIndex

def calculateModel(params: Parameters, x: list):
    '''Uses params to create the model y data. Corresponds to a sum of Lorentzian peaks on a linear baseline
    - params: Contains Parameter instances to be used for the model
    - x: list of x values to be computed in the creation of the model'''
    numPeaks = (len(params) - 2) / 3
    
    # Create an empty array
    y = np.zeros(len(x))
    
    v = params.valuesdict()
    
    offset, slope = v['offset'], v['slope']
    
    # Add the linear baseline defined by slope and offset
    y += offset
    for i in range(len(x)):
        y[i] += slope * x[i]
        
    x = np.array(x)
    # For each peak, adds a lorentzian function with the corresponding parameters
    for i in range(numPeaks):
        p, d, h = v[f'x{i}'], v[f'd{i}'], v[f'h{i}']
        y += (h * ((0.5 * d) ** 2)) * (1 / (((x - p) ** 2) + ((0.5 * d) ** 2)))    
    
    return y

def averageBox(values: list, index: int, box: int):
    '''Values is a list of floats and the value of interest is at index. 
    Averages values in the index intervals (index-box, index + box) excluding out of bounds '''
    # Check if the interval is fully included in the values list, if not, defines limit indexes
    if index - box < 0:
        minIndex = None
        maxIndex = index + box + 1
    elif index + box >= len(values) - 1:
        minIndex = index - box
        maxIndex = None
    else:
        minIndex = index - box
        maxIndex = index + box + 1

    return sum(values[minIndex: maxIndex]) / len(values[minIndex: maxIndex])