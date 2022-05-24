import os
import time
import numpy as np
from Maps import Maps, Map
from shutil import copy
from PlotFrame import PlotFrame
from LegFrame import LegFrame
from StatFrame import StatFrame
from TabNotebook import TabNotebook
from Averages import Averages
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askyesno, showinfo
from settings import TEMP_PATH, LOGS, IMAGES, ABOUT_TITLE, ABOUT_TEXT
from tkinter import Tk, BooleanVar, StringVar, END, Menu, Toplevel, Label, Entry, Button

class GUI(Tk):
    ''' Graphical User Interface Class - Defines all top level elements and methods '''
    def __init__(self):
        ''' Initialize a GUI '''
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', self.onClose)
        self.title('HLAMPS')
        self.iconbitmap(rf'{IMAGES}/main.ico')
        self.state('zoomed')
        
        ### Create program Maps and Averages instances to keep track
        self.maps = Maps()
        self.averages = Averages()
        
        ### Configure the GUI
        self.configMenu()
        self.configFrames()
        
        ### Define variables for program state checking
        self.firstOpen = BooleanVar(value = True)
        self.varSelectedMap = StringVar(value = '')
        self.reversingTabChange = False
        
    def onClose(self):
        ''' Callback on exit button or menu option. 
        Checks for user acceptance and resets GUI variables '''
        response = askyesno('Exit', 
                            'Are you sure you want to exit?')
        if response:
            self.resetGUI()
            try:
                self.destroy()
            except:
                self.quit()
    
    def resetGUI(self):
        ''' Clears all program variables '''
        self.maps.clear()
        self.averages.clear()
        self.firstOpen.set(True)
        self.varSelectedMap.set('')
        self.cleanAll()
    
        for file in os.listdir(TEMP_PATH):
            os.remove(TEMP_PATH + '/' + file)

        return 0
    
    def openMaps(self):
        ''' Opens dialog to choose the map files to be processed.
            If the file name is more than 80 characters long, 
            is requests aliases to stay away from maximum path length'''
        if not self.maps.isEmpty():
            # Only allow to open one batch of maps at a time
            response = askyesno('Confirm',
                                'All unsaved data will be deleted and replaced.\n' + 
                                'Agree?')
            
            if response:
                # Reset program and log the replacement
                self.insertLog('replace')
                self.resetGUI()
            else:
                return 1
    
        filenames = askopenfilename(title = 'Open Maps', 
                                    initialdir = '/', 
                                    filetypes = (('Text files', '*.txt'),), 
                                    multiple = True)
        
        # Check for filename length and if it exceedes asks for aliases
        reqAlias = False
        for filename in filenames:
            if len(filename.split('/')[-1]) > 80:
                aliases = self.requireAliases(filenames)
                if aliases == {}: return 1
                reqAlias = True
                break

        # For each map file, it adds a Map instance to self.maps
        for filename in filenames:
            fnSplit = filename.split('/')[-1][:-4]
            directory = filename[: filename.index(fnSplit) - 1]
            name = aliases[filename].get()[:-4] + '.txt' if reqAlias else fnSplit
            orig = aliases[filename].get()[:-4] + '.txt' if reqAlias else fnSplit
            self.maps.addMap(directory, name, orig)
        
        # Check for errors
        if self.maps.isEmpty():
            return 1
        else:
            self.insertLog('open')
    
        # Update legend to display open files
        self.legFrame.updateLegend()
        
        # Define the current active tab
        currentTab = self.tabNotebook.activeTab()
        tabText = self.tabNotebook.tab(currentTab, 'text')
        self.tabNotebook.setActive(tabText)
        
        # Calls the active tab's displaySpectra method
        self.onTabChange()
        
        # Writes all the map data in temp folder
        for map in self.maps:
           self.writeMap(map)
        
        self.firstOpen.set(False)
        return 0
    
    def requireAliases(self, filenames):
        ''' If map file names exceed 80 characters, this function 
        is called to provide aliases for each map'''
        def checkAliases():
            ''' Checks if the given aliases are less than 80 characters.
            If they ar, it destoys the window and it not, it displays error label '''
            for alias in aliases.values():
                if len(alias.get()) > 80:
                    error = Label(aliasWindow, text = 'Filenames still too long!', font = ('Courier', 10))
                    error.config(fg = 'red')
                    error.grid(column = 1, row = 0, sticky = 'ns', padx = 10, pady = 5)
                    return 1
            aliasWindow.destroy()
        
        # Disable exit button
        def doNothing():
            pass
        
        # Generate new window
        aliasWindow = Toplevel()
        aliasWindow.title('Generate Aliases')
        aliasWindow.iconbitmap(rf'{IMAGES}/main.ico')
        aliasWindow.geometry('600x400')
        aliasWindow.protocol('WM_DELETE_WINDOW', doNothing)
        
        Label(aliasWindow, text = 'Warning!', font = ('Courier', 20)
              ).grid(column = 0, row = 0, columnspan = 2, 
                     sticky = 'nw', padx = 10, pady = 5)
                     
        Label(aliasWindow, text = 'Some filenames are larger than 80 characters,' +
              ' please provide aliases for each sample'
              ).grid(column = 0, row = 1, columnspan = 2, 
                     sticky = 'news', padx = 10, pady = 5)
        
        Label(aliasWindow, text = 'Filenames:').grid(column = 0, row = 2, sticky = 'nw')
        Label(aliasWindow, text = 'Aliases:').grid(column = 1, row = 2, sticky = 'nw')
        
        # Creates a Label Entry pair for each filename 
        aliases = {}
        for index, filename in enumerate(filenames):
            aliases[filename] = StringVar(value = filename.split('/')[-1][:-4])           
            Label(aliasWindow, text = filename.split('/')[-1][:-4]).grid(column = 0, row = index + 3, sticky = 'nw')
            Entry(aliasWindow, textvariable = aliases[filename], width = 40).grid(column = 1, row = index + 3, sticky = 'nw')

        Button(aliasWindow, text = 'Done', command = checkAliases).grid(column = 0, row = index + 4)
        Button(aliasWindow, text = 'Cancel', command = lambda:[aliases.clear(), aliasWindow.destroy]).grid(column = 0, row = index  + 4, sticky = 'e')
        
        self.wait_window(aliasWindow)
        return aliases

    def openAbout(self):
        ''' Opens a window with a brief program description and full name'''
        aboutWindow = Toplevel()
        aboutWindow.title('About HLAMPS')
        aboutWindow.iconbitmap(rf'{IMAGES}/main.ico')
        aboutWindow.geometry('600x400')
        
        Label(aboutWindow, text = ABOUT_TITLE, font = ('Courier', 20)).pack()
        Label(aboutWindow, text = ABOUT_TEXT, anchor='w').pack()
        
        Button(aboutWindow, text = 'Close', command = aboutWindow.destroy, anchor='w').pack()       
        
        self.wait_window(aboutWindow)
        return 1
    
    def saveAvgSpectra(self):
        ''' Saves the displayed average spectra '''
        if self.maps.isEmpty():
            return 1
    
        # Refreshed the current average spectra with the temp folder
        self.getAverageSpectra()
        
        for map, spectra in self.averages:
            os.chdir(map.directory)
            
            # Make new dirs if necessary
            os.makedirs(f'{map.orig}_Files/Average Spectra', exist_ok = True) 
            
            os.chdir(f'{map.orig}_Files/Average Spectra')
            
            frequencies = spectra[0]
            intensities = spectra[1]
            
            # Writes average spectra file
            with open(f'{map.name}_average.txt', 'w') as file:
                file.write('Wavenumber(cm-1)\tIntensity\n')
                for freq, inten in zip(frequencies, intensities):
                    file.write(f'{freq:.2f}\t{inten:.2f}\n')
        
        # Log process
        self.insertLog('average_save')
        
        showinfo('Save', 'Average spectra saved')
        os.chdir(TEMP_PATH)
        return 0
    
    def saveIndSpectra(self):
        ''' Saves hte spectra for each point in the current maps '''
        if self.maps.isEmpty():
            return 1
        
        # For potentially long processes, a progress bar is displayed
        progressStep = 300 / (self.maps.length() * self.maps[0].spectraNum)
        self.statFrame.progressLabel.config(text = 'Processing:   Saving individual spectra')
        
        for map in self.maps:
            
            # Gets map data as a dict
            mapData = self.readMap(map)
            
            os.chdir(map.directory)
            
            os.makedirs(f'{map.orig}_Files/Individual Spectra', exist_ok = True)
            
            os.chdir(f'{map.orig}_Files/Individual Spectra')
            
            frequencies = mapData.pop('freq')
            
            # For each key, write a new file
            for key in mapData:
                x = key[0].split('.')[0] 
                y = key[1].split('.')[0]
                
                with open(f'{map.name}_X_{x}_Y_{y}.txt', 'w') as file:
                    file.write('Wavenumber(cm-1)\tIntensity\n')
                    
                    intensities = mapData[key]   
                    
                    for freq, inten in zip(frequencies, intensities):
                        file.write(f'{freq:.2f}\t{inten:.2f}\n')
                
                # Update progress bar
                self.statFrame.progressBar['value'] += progressStep
                self.statFrame.update_idletasks()
        
        # Reset progress bar
        self.statFrame.progressBar['value'] = 0
        self.statFrame.progressLabel.config(text = 'Processing: ')
        
        # Log process
        self.insertLog('individual_save')
        showinfo('Save', 'Individual spectra saved')
        os.chdir(TEMP_PATH)
        return 0
    
    def onTabChange(self, event = None):
        ''' Function called each time a tab is changed. 
            When exiting a tab, checks for unsaved changes, and if present, asks user for confirmation.
            Lastly, uses the new active tab's displaySpectra method '''
        if self.maps.isEmpty():
            return 2
        
        # This prevents a double call when the users declines confirmation
        if self.reversingTabChange:
            self.reversingTabChange = False
            return 2            
        
        
        currentTab = self.tabNotebook.activeTab()
        
        # For the unique call from openMaps method
        if event is None:
            currentTab.displaySpectra(self)
            return 1
        
        # Gets the active tab's id as recorded in TabNotebook class
        oldTabId = self.tabNotebook.getActiveId()
        oldTab = self.tabNotebook.selectTab(oldTabId)
        
        tabText = self.tabNotebook.tab(currentTab, 'text')

        # Checks the exit tab for unsaved data and asks confirmation
        if oldTab.discardChanges():
            # If confirmed, set new tab and uses its displaySpectra method
            self.tabNotebook.setActive(tabText)
            currentTab.displaySpectra(self)
            return 0
        else:
            # If not, reverses change and selects the exit tab
            self.reversingTabChange = True
            self.tabNotebook.select(oldTabId)
            return 1
    
    def insertLog(self, logType): 
        ''' Inserts log text into the StatFrame.logText ScrolledText widget '''
        self.statFrame.logText.config(state = 'normal')
        self.statFrame.logText.insert(END, 
                                      time.ctime(time.time()).split()[3] + 
                                      ' ' + LOGS[logType] + '\n')
        self.statFrame.logText.config(state = 'disabled')
        return 0
    
    def readMap(self, map: Map):
        ''' For a Map class instance, it returns a dictionary for the map data.
            For the key 'freq', its values are the frequencies.
            For a key (x, y) the coordintes in the map, its values are the intensities at each frequency. '''
        mapData = {}    
    
        # The first time the programs calls this, use the original file, else use the temp files
        os.chdir(map.directory) if self.firstOpen.get() else os.chdir(TEMP_PATH)
        
        with open(f'{map.orig}.txt', 'r') as file:
            lines = file.readlines()
        
        # Get the frequencies
        mapData['freq'] = [float(freq) for freq in lines[0].split()]
        
        lines = lines[1:]
        for line in lines:
            lineSplit = line.split()
            y = lineSplit[0]
            x = lineSplit[1]

            # Get the x, y point intensities
            mapData[(x,y)] = [float(intensity) for intensity in lineSplit[2:]]
    
        return mapData
    
    def writeMap(self, map: Map, mapData: dict = None):
        '''
        For a Map class instance, it writes the map data for it in the temp foldes.
        If mapData(dict) is given, it also writes the new data in the original folder, 
        with the current Map.name 
        '''
        fnTemp = f'{TEMP_PATH}/{map.orig}.txt'
        
        # If mapData is not given, only update temp file
        temp = False
        if mapData is None:
            temp = True
            mapData = self.readMap(map)
        
        # Used for progress bar checking
        if map.spectraNum is None:
            map.spectraNum = len(mapData) - 1
        
        # Write file exactly as the input file formats
        with open(fnTemp, 'w') as tempFile:
            tempFile.write('\t\t')
            [tempFile.write(f'{freq:.3f}\t') for freq in mapData['freq']]
            tempFile.write('\n')
            mapData.pop('freq')
            
            for key in mapData:
                
                tempFile.write(f'{key[0]}\t{key[1]}\t')
                [tempFile.write(f'{intensity:.2f}\t') for intensity in mapData[key]]
                tempFile.write('\n')
        
        # If mapData is given, the file is copied to the original directory
        if not temp:
            copy(f'{TEMP_PATH}/{map.orig}.txt', f'{map.directory}/{map.name}.txt')
            
        return 0
    
    def mouseEvent(self, event):
        ''' Handles mouse clicking inside the matplotlib Figure '''
        # Only handle events if inside the axes 
        if not event.inaxes:
            return 1
        
        # Gets box bounds and axes limits form Limits instance of PltFigure instance
        bounds, limits = self.plotFrame.figure.getLimits()

        # Convert event x value into a frequency corresponding with the data
        x = event.x - bounds.x0 * int(self.winfo_width() * 0.55)
        x /= int(self.winfo_width() * 0.55) * (bounds.x1 - bounds.x0)
        x *= limits.getXLim()[1] - limits.getXLim()[0]
        x += limits.getXLim()[0]
        
        # Convert event y value into an intensity corresponding with the data
        y = event.y - bounds.y0 * int(self.winfo_height() * 0.65)
        y /= int(self.winfo_width() * 0.65) * (bounds.y1 - bounds.y0)
        y *= limits.getYLim()[1] - limits.getYLim()[0]
        y += limits.getYLim()[0]
        
        # Redirect the event handling to the active tab
        self.chooseMouseEvent(x, y)
        return 0
    
    def chooseMouseEvent(self, x, y):
        ''' Redirects the mouse event handling to the active tab'''
        currentTab = self.tabNotebook.activeTab()
        currentTab.handleMouseEvent(x, y)
        return 0
    
    def getAverageSpectra(self): 
        ''' Reads current temp files and populates Averages instance '''
        self.averages.clear()
        
        for map in self.maps:
            
            mapData = self.readMap(map)
            frequencies = mapData.pop('freq')
            
            # Add all the intensity lists for (x, y) keys from mapData
            sumSpectra = np.zeros(len(mapData['freq']))
            for key in mapData:
                sumSpectra += np.array(mapData[key])
            
            # Divide sum spectra to get average
            avgSpectra = sumSpectra / len(mapData)
            
            # Add the average spectra to Averages
            self.averages.addSpectra(map, [frequencies, avgSpectra])
        return 0
    
    def configMenu(self):
        ''' Configures menu for the GUI '''
        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff = 0)
        filemenu.add_command(label = 'Open map files', 
                             command = self.openMaps)
        filemenu.add_command(label = 'Save average spectra', 
                             command = self.saveAvgSpectra)
        filemenu.add_command(label = 'Save individual spectra', 
                             command = self.saveIndSpectra)
        filemenu.add_command(label = 'Restore program settings', 
                             command = self.resetGUI)
        filemenu.add_separator()
        filemenu.add_command(label = 'About', 
                             command = self.openAbout)
        filemenu.add_command(label = 'Exit', 
                             command = self.onClose)

        menubar.add_cascade(label = 'File', menu = filemenu)
        self.config(menu = menubar)
    
    def configFrames(self):
        ''' Configures the main program Frames '''
        self.plotFrame = PlotFrame(self)
        self.legFrame = LegFrame(self)
        self.statFrame = StatFrame(self)
        self.tabNotebook = TabNotebook(self)
    
    def cleanAll(self):
        ''' Calls the clean() method for each Frame'''
        self.plotFrame.clean()
        self.legFrame.clean()
        self.statFrame.clean()
        self.tabNotebook.clean()
    
if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()