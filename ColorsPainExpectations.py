# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 14:01:29 2022

@author: Karolina Wiercioh-Kuzianik

Study title: Expectatation manipulation effect on the influence of colors on
pain perception.

"""

###############################################################################
# %% Import necessary libraries
###############################################################################

import numpy as np
import random
import os
import serial
import time
from psychopy import prefs
from psychopy import gui, visual, core, data, event, logging, clock
from psychopy.hardware import keyboard
from scipy.optimize import curve_fit # Import curve fitting package from scipy
from ds8r import DS8R # Import library to control Digitimer (electrical stimulation)

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

###############################################################################
# %% Dialogue box at the beginning of the experiment 
###############################################################################

expName = 'Experiment K5'
expInfo = {'ID': '', 'Group': ['congruent', 'incongruent', 'color-ctrl']}
dialog  = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dialog.OK == False:
    core.quit()  # user pressed cancel

# Store necessary information
subID = dialog.data[0]
group = dialog.data[1]
expDate = data.getDateStr()
psychopyVersion = '2021.2.3'

###############################################################################
# %% Data saving
###############################################################################

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
# File for data from main task
filename = _thisDir + os.sep + u'K5_data\\%s_%s_%s_%s' % (subID, group, expName, expDate) + '.csv' # create 'comma-separated-values' file
dataFile = open(filename, 'w')     # open file for writing
dataFile.write('group, blockType, blockCounter, bcgColor, marker, VAS\n')    # name columns
dataFile.close()

# File for data from calibration
filenameCal = _thisDir + os.sep + u'K5_data/%s_%s_%s_%s' % (subID, group, expName, expDate) + '_CAL.csv'
dataFileCal = open(filenameCal, 'w')
dataFileCal.write('group, intensity, VAS\n')
dataFileCal.close()

###############################################################################
# %% Hardware setup (Labjack + Biopac)
###############################################################################

# Labjack setup
# Check if labjack library is installed
try:
    from psychopy.hardware.labjacks import u3
    print('Labjack library imported.')
except:
    print('No Labjack library found.')

# Check if labjack is connected and recognized by the u3 library
try:
    trigger = u3.U3()
    labjack = True
    TRIG = 6701  # the address of EIO1 schock
    trigger.writeRegister(6751,0xFFFF) #set EIO1 as output
    trigger.writeRegister(TRIG,0xFF00) #start low
except:
    print('No Labjack device connected. Switching to test mode.')
    labjack = False

# Biopac EDA setup and start-up
ser = serial.Serial('COM4', 115200, timeout=0) #address the serial port
ser.flush() # clear
ser.write(str.encode('00')) # set marker to '00' at start
time.sleep(0.001)
ser.write(str.encode('00')) # double-check setting

###############################################################################
# %% Different parameters
###############################################################################

# Setup the Window
win = visual.Window(
    size=[2560, 1440], fullscr=False, screen=0, #2560, 1440 1280, 720
    winType='pyglet', allowGUI=False, monitor='testMonitor', 
    color= 'black', colorSpace='rgb', units='norm')

# Frame rate of the monitor
frate = round(win.getActualFrameRate(), 0) 

# Set up keyboard
kb = keyboard.Keyboard()
# Hide mouse
mimo = event.Mouse(visible=False, newPos=None, win=win)

# Keys for the experiment
rsp_keysCal = ['a', 'l'] # keys for calibration

# Additional grating for changing background
slideColor = visual.GratingStim(
        win=win, name='slideColor',units='norm', tex=None, mask=None,
        ori=0, pos=(0, 0), size=(2,2), sf=None, phase=0.0,color=[-1.000,-1.000,-1.000],
        colorSpace='rgb', opacity=1, blendmode='avg', texRes=128, interpolate=True, 
        depth=0.0)

# Number of blocks
intBlockNr = 6      # pain blocks 
expectBlockNr = 1   # expectation blocks
colorBlockNr = 1    # color only blocks
baseBlockNr = 6

# Presentation times
intWait = 6     # intensity trials
expectWait = 6  # expectation trials
calWait = 6     # calibration trials (time to next stimulus)
colorOnlyWait = 6

# how to abort the experiment
def close_exp():    # define a function
    ser.close()
    event.globalKeys.remove(key='q')   # which key
    win.close();                           # what to do when this key is pressed
# add it as a background event; psychopy will constantly check it
event.globalKeys.add(key='q', func=close_exp, name='shutdown')

# Import our own functions from a separate file
exec(open('./functions.py', encoding='utf8').read())

###############################################################################
# %% Pain stimulation
###############################################################################

# Set parameters for electrical stimulation
    # demand = instensity of the stimulus (1 = 0.1mA) -> limited to 150
    # pulse_width =  shock duration in microseconds
electricShock = DS8R(demand=10, pulse_width=200, enabled=1, dwell=1, mode=1, polarity=1, source=1, recovery=100)

#Apply electric shocks in series. Number of shocks in series determined by 'rep'
def electricalStim(rep):
    i = 0
    if labjack == True:
        electricShock.run()
        core.wait(0.2) # interval between stimuli
        i += 1
        while i < rep:
            trigger.writeRegister(TRIG,65280+255)
            trigger.writeRegister(TRIG,65280+0)
            core.wait(0.2)
            i += 1

###############################################################################
# %% Color stimuli parameters and markers
###############################################################################

# Color definitions, creating dictionaries
red = {'colorName': 'red', 'colorRGB': [1.000,-1.000,-1.000], 'colorMarker': 1}
blue = {'colorName': 'blue', 'colorRGB': [-1.000,0.004,1.000], 'colorMarker': 2}
green = {'colorName': 'green', 'colorRGB': [-1.000,1.000,-1.000], 'colorMarker': 3}
orange = {'colorName': 'orange', 'colorRGB': [1.000,0.004,-1.000], 'colorMarker': 4}
yellow = {'colorName': 'yellow', 'colorRGB': [1.000,1.000,-1.000], 'colorMarker': 5}
pink = {'colorName': 'pink', 'colorRGB': [1.000,-1.000,0.004], 'colorMarker': 6}
grey = {'colorName': 'grey', 'colorRGB': [0.004,0.004,0.004], 'colorMarker': 7}
white = {'colorName': 'white', 'colorRGB': [1.000,1.000,1.000], 'colorMarker': 8}
black = {'colorName': 'black', 'colorRGB': [-1.000,-1.000,-1.000], 'colorMarker': 0}

# Trial lists
colorTrials = [red, blue, green, orange, yellow, pink, grey, white]   # list for color trials
baselineTrials = [black]    # list for beseline trials

# Markers
calMarker = '01'    # marker for cailbration trials
baseMarker = '02'
baseExpectMarker = '03'
colorsOnlyMarker = 10
expectationMarker = 20
painMarker = 30

###############################################################################
# %% Texts, scales and other elements
###############################################################################

# Rating scales
ratingScale = visual.RatingScale(win, low=0, high=100, labels=['0\n brak bólu', '100\n najsilniejszy ból'], scale=None, tickMarks=[0, 100],
                                 markerColor='grey', markerStart=random.randint(0, 100), stretch=1.5, showValue=False, 
                                 acceptPreText='Wybierz ocenę', acceptText='Akceptuj', acceptSize=1.5, skipKeys=None,
                                 textColor='white', mouseOnly=True)

ratingScaleSample = visual.RatingScale(win, pos=(0, 0.15), low=0, high=100, labels=['0\n brak bólu', '100\n najsilniejszy ból'], scale=None, tickMarks=[0, 100],
                                 markerColor='grey', stretch=1.5, showValue=False, acceptPreText='Wybierz ocenę',
                                 acceptText='Akceptuj', acceptSize=1.5, skipKeys=None, textColor='white')

# Instruction texts
instructionStart = visual.TextStim(win=win, name='Start instruction',
    text=
'''W badaniu będziesz otrzymywać bodźce elektryczne w seriach. Każda seria będzie składała się z trzech bodźców. 

W czasie aplikacji każdej serii bodźców na ekranie będzie wyświetlał się punkt fiksacji.
Aby go zobaczyć, wciśnij ENTER.''',
    font='Arial', pos=(-0.9, 0), height=0.075, wrapWidth=1.75, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0, anchorHoriz = 'left', alignText= 'left')

instructionStart2 = visual.TextStim(win=win, name='Start instruction',
    text=
'''Będziemy prosili, żebyś oceniał_a swoje doznania za pomocą skali, która będzie wyglądała w ten sposób:

    







Aby przejść dalej wciśnij ENTER.    
''',
    font='Arial', pos=(-0.9, 0), height=0.075, wrapWidth=1.75, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0, anchorHoriz = 'left', alignText= 'left')

instructionStart3 = visual.TextStim(win=win, name='Start instruction 3',
    text=
'''Gdy na ekranie pojawi się skala, oceń swoje doznania. Pamiętaj, że: 

0 - oznacza brak bólu. Jeżeli dana seria bodźców była odczuwalna, ale nie spowodowała bólu, a jedynie wrażenie dotyku lub nieprzyjemne odczucie, oceń tę serię na 0 przesuwając suwak maksymalnie w lewą stronę

100 - oznacza najsilniejszy ból wywołany elektryczną stymulacją, jaki jesteś w stanie znieść w tej sytuacji eksperymentalnej 


Swoje doznania oceniaj możliwie szybko, ustawiając suwak na skali i akceptując swoją ocenę przyciskiem 'Akceptuj'. 

Aby przejść dalej wciśnij ENTER. ''',
    font='Arial', pos=(-0.9, 0), height=0.075, wrapWidth=1.75, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0, anchorHoriz = 'left', alignText= 'left')

instructionStart4 = visual.TextStim(win=win, name='Start instruction 4',
    text=
'''Za chwilę przejdziemy do pierwszej części badania.

W tej częsci będziesz otrzymywał_a bodźce elektryczne w seriach. Każda seria będzie składała się z trzech bodźców. Nasilenie kolejnych serii będzie stopniowo wzrastało, ale ten wzrost nie będzie gwałtowny. Serie bodźców będą aplikowane co 5 sekund, ale pierwsze bodźce mogą nie być w ogóle odczuwalne.

Aby rozpocząć, wciśnij ENTER.''',
    font='Arial', pos=(-0.9, 0), height=0.075, wrapWidth=1.75, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0, anchorHoriz = 'left', alignText= 'left')

instructionPractice = visual.TextStim(win=win, name='Practice instruction',
    text=
'''Przećwiczmy teraz korzystanie ze skali do oceny bólu. Zaznacz na skali za pomocą myszki ocenę '0' i zaakceptuj swój wybór.''',
    font='Arial', pos=(-0.9, 0.3), height=0.075, wrapWidth=1.75, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0, anchorHoriz = 'left', alignText= 'left')

instructionPracticeOnceAgain = visual.TextStim(win=win, name='Try one more time',
    text=
'Wybrałe_aś ocenę powyżej 0. Spróbuj jeszcze raz.',
    font='Arial', pos=(-0.9, 0.3), height=0.075, wrapWidth=1.75, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0, anchorHoriz = 'left', alignText= 'left')

instructionExpect = visual.TextStim(win=win, name='expectation instruction',
    text=
'''W następnej części badania NIE będziesz otrzymywał_a bodźców bólowych. 
Tym razem poprosimy Cię o ocenę, jak silnego bólu się spodziewasz. 


Aby przejść do zadania, naciśnij ENTER.''',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=2, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

instructionInt = visual.TextStim(win=win, name='intensity instruction',
    text=
'''W następnej części badania będziesz otrzymywał_a bodźce bólowe, a w momencie ich aplikacji, tak jak wcześniej, na ekranie będzie wyświetlany punkt fiksacji.
Twoim zadaniem jest ocenienie na skali, jak silny był ból wywołany aplikowanymi bodźcami. 


Aby przejść do zadania, naciśnij ENTER.''',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=1.75, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

instructionColors = visual.TextStim(win=win, name='colors only instruction',
    text=
'''W następnej części badania NIE będziesz otrzymywał_a bodźców bólowych. 
Twoim zadaniem będzie obserwowanie wyświetlanych na ekranie kolorowych slajdów. 


Aby przejść do zadania, naciśnij ENTER.''',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=2, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

instructionRepeat = visual.TextStim(win=win, name='repeat baseline instruction',
    text=
'''W następnej części badania nadal będziesz otrzymywał_a bodźce bólowe, a w momencie ich aplikacji, tak jak wcześniej, na ekranie będzie wyświetlany punkt fiksacji.
Twoim zadaniem jest w dalszym ciągu ocenienie na skali, jak silny był ból wywołany aplikowanymi bodźcami. 


Aby przejść do zadania, naciśnij ENTER.''',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=1.75, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

instructionManipulation1 = visual.TextStim(win=win, name='manipulation instruction, part 1',
    text=
'''W poprzednim etapie badania określiliśmy Twoją wrażliwość na bodźce bólowe wywołane elektryczną stymulacją. Sprawdziliśmy również Twoje reakcje fizjologiczne (tj. tętno oraz reakcję skórno-galwaniczną) w odpowiedzi na prezentację różnych kolorów.

Na podstawie tych pomiarów algorytm komputerowy obliczy teraz Twój wzorzec reakcji bólowej i dopasuje go do modelu stworzonego na podstawie wcześniejszych badań naukowych.

Naciśnij ENTER, aby kontynuować.
''',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=1.75, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0, alignText= 'left')

instructionManipulation2 = visual.TextStim(win=win, name='manipulation instruction, part 2',
    text=
'''PRZERWA

Trwa przeliczanie danych...
''',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=2, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

instructionManipulation3Congruent = visual.TextStim(win=win, name='manipulation instruction, part 3 - congruent group',
    text=
'''Na podstawie pomiarów określiliśmy, że Twój wzorzec reakcji bólowej jest zbliżony do osób, u których kolor czerwony zwiększa siłę odczuwanego bólu, a kolor biały zmniejsza ból.

Za chwilę rozpoczniemy następny etap badania. Celem tego etapu jest rozbudowanie istniejącego modelu rekacji bólowych na podstawie uzyskanych danych.
Twoim zadaniem ponownie będzie ocenianie swoich doznań na skali. Będziemy również w dalszym ciągu rejestrowali Twoje reakcje fizjologiczne.


Aby przejść dalej, naciśnij ENTER.
''',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=1.75, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0, alignText= 'left')

instructionManipulation3Incongruent = visual.TextStim(win=win, name='manipulation instruction, part 3 - congruent group',
    text=
'''Na podstawie pomiarów określiliśmy, że Twój wzorzec reakcji bólowej jest zbliżony do osób, u których kolor biały zwiększa siłę odczuwanego bólu, a kolor czerwony zmniejsza ból.

Za chwilę rozpoczniemy następny etap badania. Celem tego etapu jest rozbudowanie istniejącego modelu rekacji bólowych.
Twoim zadaniem ponownie będzie ocenianie swoich doznań na skali. Będziemy również w dalszym ciągu rejestrowali Twoje reakcje fizjologiczne.


Aby przejść dalej, naciśnij ENTER.
''',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=1.75, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0, alignText= 'left')

# Fixation cross
fixCross = visual.TextStim(win=win, name='fixation point',
    text='+',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=1.5, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

# Rating scale texts
intRatingScale = visual.TextStim(win=win, name='intensity rating',
    text='Oceń jak bardzo bolesna była ta seria bodźców',
    font='Arial', pos=(0, 0.5), height=0.15, wrapWidth=1.5, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

baseExpectRatingScale = visual.TextStim(win=win, name='intensity rating',
    text='Oceń jak silnego bólu się spodziewasz',
    font='Arial', pos=(0, 0.5), height=0.15, wrapWidth=1.5, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

expectRatingScale = visual.TextStim(win=win, name='expectation rating',
    text='Oceń jak silnego bólu spodziewasz się po prezentacji tego koloru',
    font='Arial', pos=(0, 0.5), height=0.15, wrapWidth=1.7, ori=0, color='black', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

noScale = visual.TextStim(win=win, name='no scale',
    text=' ',
    font='Arial', pos=(0, 0.5), height=0.15, wrapWidth=1.5, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

feelSth = visual.TextStim(win=win, name='feel or not',
    text=
'''Czy poczułeś_aś bodziec?


TAK/NIE
''',
    font='Arial', pos=(0, 0), height=0.1, wrapWidth=1.5, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

# Break text
pause = visual.TextStim(win=win, name='break text',
    text='PRZERWA',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=1.5, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

pauseCalContinue = visual.TextStim(win=win, name='Continue text',
    text='Za chwilę procedura zostanie powtórzona',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=1.5, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

pauseContinue = visual.TextStim(win=win, name='Continue text',
    text='Za chwilę badanie będzie kontynuowane',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=1.5, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)

# End text
goodbye = visual.TextStim(win=win, name='end text',
    text='KONIEC',
    font='Arial', pos=(0, 0), height=0.075, wrapWidth=1.5, ori=0, color='white', 
    colorSpace='rgb', opacity=1, languageStyle='LTR', depth=-2.0)  

###############################################################################
# %% EXPERIMENT FLOW
###############################################################################

# Present start instructions
instructionStart.draw() # prepare an object to be drawn on-screen
win.flip()    # make the object visible with the next screen refresh flipq
event.waitKeys(keyList=['return', 'q'])    # wait for any of these keys to be pressed
win.flip()
fixCross.draw()
win.flip()
core.wait(2)
instructionStart2.draw()
ratingScaleSample.draw()
win.flip()
event.waitKeys(keyList=['return', 'q'])
win.flip()
instructionStart3.draw()
win.flip()
event.waitKeys(keyList=['return', 'q'])
win.flip()

# Practice using rating scale
ratingPractice()

# Present calibration instruction
instructionStart4.draw()
win.flip()
event.waitKeys(keyList=['return', 'q'])
win.flip()

# Run calibration
calibration()
pause.draw()
win.flip()
core.wait(60)    # should be 60
pauseCalContinue.draw()
win.flip()
core.wait(5)    # should be 5
win.flip()
calibration()
curveFit()

# Baseline
instructionInt.draw()
win.flip()
event.waitKeys(keyList=['return', 'q'])

estimationVAS = estimationVAS50
painBlocks('baseline')   # run baseline block
baselineMean = sum(baselineRatings)/len(baselineRatings)
print(baselineMean)

if baselineMean <= 20:  # change the intensity of stimuli and repeat baseline if the mean ratings where lower than 20
    instructionRepeat.draw()
    win.flip()
    event.waitKeys(keyList=['return', 'q'])
    win.flip()
    estimationVAS = estimationVAS60
    painBlocks('baseline')   # run baseline block again

if baselineMean > 80:   # change the intensit of stimuli and repeat baseline if the mean ratings where higher than 40
    instructionRepeat.draw()
    win.flip()
    event.waitKeys(keyList=['return', 'q'])
    win.flip()
    estimationVAS = estimationVAS40
    painBlocks('baseline')   # run baseline block again

# Expectations for baseline
instructionExpect.draw()
win.flip()
event.waitKeys(keyList=['return', 'q'])
baselineExpectation()   # run baseline expectations block
    
# Colors only
instructionColors.draw()
win.flip()
event.waitKeys(keyList=['return', 'q'])

noPainBlocks('colors')   # run colors only block

# Manipulation instruction depending on the group
instructionManipulation1.draw()
win.flip()
event.waitKeys(keyList=['return', 'q'])
instructionManipulation2.draw()
win.flip()
core.wait(45)   # should be 45
if group == 'congruent':
    instructionManipulation3Congruent.draw()
    win.flip()
    event.waitKeys(keyList=['return', 'q'])
elif group == 'incongruent':
    instructionManipulation3Incongruent.draw()
    win.flip()
    event.waitKeys(keyList=['return', 'q'])

# Expectations
instructionExpect.draw()
win.flip()
event.waitKeys(keyList=['return', 'q'])

noPainBlocks('expectation')   # run expectations block

# Pain
instructionInt.draw()
win.flip()
event.waitKeys(keyList=['return', 'q'])

painBlocks('intensity')   # run pain blocks

goodbye.draw()
win.flip()
event.waitKeys(keyList=['space', 'q'])

###############################################################################
# %% Close up
###############################################################################
ser.write(str.encode('00'))
ser.close()
event.globalKeys.remove(key='q')
win.close()
core.quit()