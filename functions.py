# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 15:18:39 2022

@author: karol
"""
import numpy as np
import matplotlib.pyplot as plt
from math import log
from scipy.optimize import curve_fit

# Using rating scale pratice
def ratingPractice():
    while ratingScale.noResponse:
        instructionPractice.draw()
        ratingScale.draw()
        win.flip()
    ratingPrac = ratingScale.getRating()
    ratingScale.noResponse = True

    while ratingPrac != 0:
        instructionPracticeOnceAgain.draw()
        win.flip()
        core.wait(3)
        while ratingScale.noResponse:
            instructionPractice.draw()
            ratingScale.draw()
            win.flip()
        ratingPrac = ratingScale.getRating()
        ratingScale.noResponse = True
        
###############################################################################
# %% Calibration
###############################################################################
stimInt = []    # stimulus intensities for one repeat of calibration
stimVAS = []    # stimulus ratings from one repeat of calibration
stimIntTotal =[]    # all stimulus intensities from calibration
stimVASTotal =[]    # all stimulus ratings from calibration

def calibration():
       
    stimRange = np.arange(1, 150, 1)
        
    for stim in stimRange:
        ratingScale = visual.RatingScale(win, low=0, high=100, labels=['0', '100'], scale=None, tickMarks=[0, 100],
                                     markerColor='grey', markerStart=0, stretch=1.5, showValue=False, acceptPreText='Wybierz ocenę',
                                     acceptText='Akceptuj', acceptSize=1.5, skipKeys=None, textColor='white', mouseOnly = True)
        
        ser.write(str.encode(calMarker))    # send calibration marker
        core.wait(calWait)  # time to next stimulus
        fixCross.draw()     # display fixation point
        win.flip()
        core.wait(0.2)
        
        ser.write(str.encode('00')) # clear marker
        
        electricShock.demand = int(stim*10) # change electric shock intensity based on steps from calibration; value must be integer
        electricalStim(3) # apply series of 3 electric shocks
        
        if not stimVAS:         # check if stimVAS list is empty; empty list will return bool=False; if stimVAS not empty it means pp already felt sth and no need to ask about it
            feelSth.draw()     # display question if pp feel anything
            win.flip()
        
            answer = event.waitKeys(keyList=['a', 'apostrophe'])     # wait for keypress
        
            if answer[0] == 'apostrophe':       # if not feeling stimulus continue to the next intensity; else show raint scale
                win.flip()
                continue
        
        while ratingScale.noResponse:   # wait for rating
            intRatingScale.draw()
            ratingScale.draw()
            win.flip()
        
        rating = ratingScale.getRating()   # write rating to variable
        ratingScale.noResponse = True   # clear response from rating scale

        stimVAS.append(rating)
        stimInt.append(stim)
        win.flip()
        
        # quit loop if rating is 7 or more
        if rating >= 70:
            break

        # Save current calibration series data to the file
        dataFileCal = open(filenameCal, 'a')     # open for writing 'comma-separated-values' file
        dataFileCal.write('%s,%s\n' %(stimInt, stimVAS))
        dataFileCal.close()
    
    # Add intensity and rating values from current calibration series to total list
    global stimIntTotal, stimVASTotal
    stimIntTotal += stimInt
    stimVASTotal += stimVAS
    
    # Clear current list
    stimVAS.clear()
    stimInt.clear()

###############################################################################
# %% Exponential curve fit
###############################################################################

def curveFit():
    
    x=stimIntTotal
    y=stimVASTotal
    
    # set plot parameters
    curvepoints_qty=100
    y_height=100
    
    # Fit the function a * np.exp(b * t) to x and y
    popt, pcov = curve_fit(lambda t, a, b: a * np.exp(b * t), x, y)
    
    # Extract the optimised parameters # nothing to change here
    a = popt[0]
    b = popt[1]
    x_fitted = np.linspace(np.min(x), np.max(x), curvepoints_qty)
    y_fitted = a * np.exp(b * x_fitted)

    global estimationVAS40, estimationVAS50, estimationVAS60
    estimationVAS40 = log(40/a) / b
    estimationVAS50 = log(50/a) / b
    estimationVAS60 = log(60/a) / b

    print('VAS 40, VAS 50, VAS 60:', estimationVAS40, estimationVAS50, estimationVAS60)
    
    # Plot
    ax = plt.axes()
    ax.scatter(x, y, label='Raw data')
    ax.plot(x_fitted, y_fitted, 'k', label='Fitted curve')
    ax.set_title(r'Using curve\_fit() to fit an exponential function')
    ax.set_ylabel('VAS rating')
    ax.set_ylim(0, y_height)
    ax.set_xlabel('intensity [mA]')
    ax.legend()

    #mark point in graph
    ax.axhline(50, ls="--", color="grey")
    ax.axvline(estimationVAS50, ls="--", color="grey")
    ax.plot(estimationVAS50, 50, c="tab:orange", marker="o", markersize=15, alpha=0.5)
    plt.show()
    
    # Save total calibration data to the file
    dataFileCal = open(filenameCal, 'a')     # open for writing 'comma-separated-values' file
    dataFileCal.write('%s,%s,%s\n' %(group, stimIntTotal, stimVASTotal))
    dataFileCal.write('\nEstimation for 40 on VAS: %f\n' %(estimationVAS40))
    dataFileCal.write('\nEstimation for 50 on VAS: %f\n' %(estimationVAS50))
    dataFileCal.write('\nEstimation for 60 on VAS: %f\n' %(estimationVAS60))
    dataFileCal.close()
    
###############################################################################
# %% Blocks without pain stimulation
###############################################################################

def noPainBlocks(blockType):
    blockCounter = 0   # set block counter to 0
    bcgColor = colorTrials
    
    # Assign block parameters
    if blockType == 'expectation':
        nrBlocks = expectBlockNr
        VASratingScale = expectRatingScale
        colorWait = expectWait
        marker = expectationMarker
    elif blockType == 'colors':
        nrBlocks = colorBlockNr
        VASratingScale = noScale
        colorWait = colorOnlyWait
        marker = colorsOnlyMarker
    
    VASratingScale.setColor('black', colorSpace='rgb')
    fixCross.setColor('black', colorSpace='rgb')
    
    while blockCounter != nrBlocks :   # check if the desired number of blocks is reached
        # Shuffle the list with background colors
        random.shuffle(bcgColor)
        blockCounter += 1   # adds one to block counter

        # Single trial: present colors and ask for expectation ratings
        for thisColor in bcgColor:
            # Reset the rating scale marker position aka initialize rating scale component once again
            if blockType == 'expectation':
                ratingScale = visual.RatingScale(win, low=0, high=100, labels=['0', '100'], scale=None, tickMarks=[0, 100],
                                                 markerColor='black', markerStart=0, stretch=1.5, showValue=False, acceptPreText='Wybierz ocenę',
                                                 acceptText='Akceptuj', acceptSize=1.5, skipKeys=None, textColor='black', lineColor='black', mouseOnly=True)

            thisMarker = marker + thisColor['colorMarker']  # set the marker value
            ser.write(str(thisMarker).encode())
            
            rating = None
            slideColor.setColor(thisColor['colorRGB'], colorSpace='rgb') # change the background color
            slideColor.draw()
            win.flip()
            
            core.wait(colorWait)    # color presentation time
            
            ser.write(str.encode('00')) # clear marker
            
            if blockType == 'expectation':
                while ratingScale.noResponse:   # wait for rating via slider
                    slideColor.draw()
                    VASratingScale.draw()
                    ratingScale.draw()
                    win.flip()
                        
                rating = ratingScale.getRating()   # write rating to variable
                ratingScale.noResponse = True   # clear response from rating scale
                
            # Save rating to the file
            dataFile = open(filename, 'a')     # open for writing 'comma-separated-values' file
            dataFile.write('%s,%s,%i,%s,%i,%s\n' %(group, blockType, blockCounter, thisColor["colorName"], thisMarker, rating))
            dataFile.close()
            
def baselineExpectation():
    blockType = 'baselineExpectation'
    blockCounter = 0   # set block counter to 0
    bcgColor = baselineTrials
    nrBlocks = expectBlockNr
    VASratingScale = baseExpectRatingScale
    colorWait = expectWait

    while blockCounter != nrBlocks :   # check if the desired number of blocks is reached
        blockCounter += 1   # adds one to block counter

        # Single trial: present colors and ask for expectation ratings
        for thisColor in bcgColor:
            # Reset the rating scale marker position aka initialize rating scale component once again
            ratingScale = visual.RatingScale(win, low=0, high=100, labels=['0', '100'], scale=None, tickMarks=[0, 100],
                                             markerColor='grey', markerStart=0, stretch=1.5, showValue=False, acceptPreText='Wybierz ocenę',
                                             acceptText='Akceptuj', acceptSize=1.5, skipKeys=None, textColor='white', mouseOnly=True)
                
            marker = baseExpectMarker  # set the marker value
            ser.write(marker.encode())
            
            rating = None
            slideColor.setColor(thisColor['colorRGB'], colorSpace='rgb') # change the background color
            slideColor.draw()
            win.flip()
            
            core.wait(colorWait)    # color presentation time
            
            ser.write(str.encode('00')) # clear marker
            
            while ratingScale.noResponse:   # wait for rating via slider
                slideColor.draw()
                VASratingScale.draw()
                ratingScale.draw()
                win.flip()
                        
            rating = ratingScale.getRating()   # write rating to variable
            ratingScale.noResponse = True   # clear response from rating scale
                
            # Save rating to the file
            dataFile = open(filename, 'a')     # open for writing 'comma-separated-values' file
            dataFile.write('%s,%s,%i,%s,%s,%s\n' %(group, blockType, blockCounter, thisColor["colorName"], marker, rating))
            dataFile.close()            

###############################################################################
# %% Blocks with pain stimulation
###############################################################################
baselineRatings = []   # sets a list to gather ratings from the baseline

def painBlocks(blockType):
    blockCounter = 0   # set block counter to 0

    VASratingScale = intRatingScale    # refers to intensity rating text
    colorWait = intWait     # refers to time of color background display

    # Assign block parameters
    if blockType == 'intensity':
        nrBlocks = intBlockNr   # refers to number of intensity blocks
        bcgColor = colorTrials  # refers to list of colors used in experiment
        VASratingScale.setColor('black', colorSpace='rgb')
        fixCross.setColor('black', colorSpace='rgb')
    elif blockType == 'baseline':
        nrBlocks = baseBlockNr
        bcgColor = baselineTrials
        VASratingScale.setColor('white', colorSpace='rgb')
        fixCross.setColor('white', colorSpace='rgb')
    
    while blockCounter != nrBlocks :   # check if the desired number of blocks is reached
        # Shuffle the list with background colors
        random.shuffle(bcgColor)
        blockCounter += 1   # adds one to block counter

        # Single trial: present colors and ask for expectation ratings
        for thisColor in bcgColor:
            # Reset the rating scale marker position aka initialize rating scale component once again
            if blockType == 'baseline':
                ratingScale = visual.RatingScale(win, low=0, high=100, labels=['0', '100'], scale=None, tickMarks=[0, 100],
                                             markerColor='grey', markerStart=0, stretch=1.5, showValue=False, acceptPreText='Wybierz ocenę',
                                             acceptText='Akceptuj', acceptSize=1.5, skipKeys=None, textColor='white', mouseOnly=True)
                marker = baseMarker
            elif blockType == 'intensity':
                ratingScale = visual.RatingScale(win, low=0, high=100, labels=['0', '100'], scale=None, tickMarks=[0, 100],
                                                 markerColor='black', markerStart=0, stretch=1.5, showValue=False, acceptPreText='Wybierz ocenę',
                                                 acceptText='Akceptuj', acceptSize=1.5, skipKeys=None, textColor='black', lineColor='black',
                                                 mouseOnly=True)
                thisMarker = painMarker + thisColor['colorMarker']
                marker = str(thisMarker)
                
            ser.write(marker.encode())
            
            slideColor.setColor(thisColor['colorRGB'], colorSpace='rgb') # change the background color
            slideColor.draw()
            win.flip()
            
            core.wait(colorWait)    # color presentation time
            
            ser.write(str.encode('05'))

            slideColor.draw()
            fixCross.draw()
            win.flip()
            
            electricShock.demand = int(estimationVAS*10) # set electric shock intensity
            electricalStim(3) # apply series of 3 electric shocks
            
            slideColor.draw()
            win.flip()
            core.wait(colorWait)
            ser.write(str.encode('00'))
            
            while ratingScale.noResponse:   # wait for rating
                slideColor.draw()
                VASratingScale.draw()
                ratingScale.draw()
                win.flip()
                    
            rating = ratingScale.getRating()   # write rating to variable
            ratingScale.noResponse = True   # clear response from rating scale
            
            if blockType == 'baseline':
                baselineRatings.append(rating)
            
            # Save rating to the file
            dataFile = open(filename, 'a')     # open for writing 'comma-separated-values' file
            dataFile.write('%s,%s,%i,%s,%s,%s\n' %(group, blockType, blockCounter, thisColor["colorName"], marker, rating))
            dataFile.close()