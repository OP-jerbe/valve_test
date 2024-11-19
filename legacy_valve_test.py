"""
Created on Fri Jan 14 09:34:12 2022

authors: Logan Ridings: Motor Control, GUI
         Joshua Erbe: Pressure Reading, Test Algorithm

The Automated Valve Test tests the performance of the VAT leak valve by 
commanding the motor to open the valve by 1/20th of a turn and waiting for the 
pressure reading to stabilize within a user-selected window of time, all 
while logging the pressure reading once per second. Once the pressure reaches a
user-selected high limit (default = 1e-5 mbar) the motor opens the valve by 
one full turn, waits for 10 seconds, logs the pressure reading, then closes the
valve by one full turn. If the pressure reading goes above 1e-2 mBar, the
valve closes completely and the test is stopped. Otherwise, the pressure is 
monitored and logged for the user-selected wait time and the valve closes by 
1/20th of turn until either the pressure drops below the initial base pressure 
(very uncommon) or the valve gets to 0.0 turns (most likely scenario).

If the pressure is within a set window (5e-7 - 1e-5 mBar) the valve will not 
open/close until the pressure reading is stable for the user-selected amount of
time (default = 3 seconds). If the pressure is outside of this window (either 
above or below) the valve will open after the user-selected wait time 
regardless of pressure reading stability. This speeds up the test test time per
valve by ignoring unstable readings outside of the pressure window of interest.
"""

import os
import serial
import csv
import numpy as np
import matplotlib.pyplot as plt

from tkinter import *
from tkinter import ttk
from datetime import datetime
from api.pfeiffer_tpg26x import TPG261 as TPG

fileName = ""

def gotoZero():
    """Moves the motor to the zero position"""
    currentTurns.set(0)
    goToTurn()


def sendCommand(commandString):
    """Sends a command to the motor"""
    with serial.Serial('COM3', timeout=0.1) as ser:
        ser.write(commandString.encode() + b'\r') # write a string
        response = ser.read(15)
        motorStatus.set("Motor Status: " + str(response))
    #print("command: "+commandString)
    

def checkAng():
    """Checks angle of motor"""
    commandString = "/1?0R\r"
    with serial.Serial('COM3', timeout=0.1) as ser:
        ser.write(commandString.encode())
        code = ser.read(15)
        #print(code)
        #code = "1@100000\\1"
        try:
            step = str(code).split("`")[1]
        except:
            step = str(code).split("@")[1]
        step = step.split("\\")[0]
        #print(step)
        currentTurns.set(stepsToTurn(step))
    return currentTurns.get()


def turnToSteps(turns):
    steps = round(float(turns)*256*200)
    return str(steps)


def stepsToTurn(steps):
    turn = (float(steps)/(256*200))
    return turn


# Step Motor relatively
def changeStep(stepSize):
    newPosition = float(currentTurns.get())+float(stepSize)
    if newPosition < 0:
        errorWindow()
        return
    currentTurns.set(str(newPosition))
    goToTurn()


def goToTurn(*args):
    commandString = "/1A"+turnToSteps(currentTurns.get())+"R"
    sendCommand(commandString)
    
    
def killWindow(window):
    stopMotor()
    holdBool.set(False)
    recipeOn.set(False)
    window.destroy()


def stopMotor():
    commandString = "/1TR"
    sendCommand(commandString)
    root.after(50)
    checkAng()


def gotoTarget():
    newPosition = degTurn.get()
    newInt = 0
    try:
        newInt = float(newPosition)
        if newInt < 0:
            errorWindow()
            return
    except Exception as e:
        err2 = Toplevel(root)
        err2.geometry("300x150")
        err2.title("Error: Invalid Target")
        Label(err2, text="Only numeric decimal positions valid.").pack()
        Button(err2, text="Ok", command=err2.destroy).pack()
        return
    
    currentTurns.set(newPosition)
    goToTurn()
    
    
# Show error for illegal position
def errorWindow():
    errFrm = Toplevel(root)
    errFrm.geometry("300x150")
    errFrm.title("Error: Valve Position")
    Label(errFrm, text="Motor should not overtighten valve.").pack()
    Button(errFrm, text="Ok", command=errFrm.destroy).pack()
    
    
# Set current position as zero
def zeroAngle():
    """Sets the current current motor position to position zero."""
    currentTurns.set(0)
    commandString = "/1z0R"
    sendCommand(commandString)


def getPressure():
    """Gets the current pressure reading from gauge controller"""
    pressureRead = curPres.get()
    tpg = TPG(port='COM4')
    pressureRead, (status_code, status_string) = tpg.pressure_gauge(1)
    if status_code != 0:
        print(f'\nstatus code = {status_code}')
        print(f'\nmessage = "{status_string}"')
        print('\nSomething went wrong reading the data.')
    if pressureRead >= 1e-2:
        print('Over pressure. Closing Valve...')
        gotoZero() # close valve completely
        root.after(20000) # wait 20 seconds so motor has time to close valve completely
        writeDataToCSV() # write the data to the csv file
        killWindow(testWindow)
        tpg.close_port()
        raise Exception("Pressure went too high.")
        
    curPres.set(pressureRead)
    return pressureRead

def getBasePressure():
    """This function is called when the test is started. It gets the starting
    pressure."""
    global base_pressure
    base_pressure = lowPres.get()

def createFigure():
    global ax, valve_turns_up, datalog_up, valve_turns_down, datalog_down
    valve_turns_up = []
    datalog_up = []
    valve_turns_down = []
    datalog_down = []
    
    fig, ax = plt.subplots(dpi=200, frameon=True, edgecolor='k', linewidth=2, figsize=(4.8,4.775))
    fig.set_tight_layout(True)
    fig.canvas.manager.window.move(950,0)
    ax.set_axisbelow(True)
    ax.grid(True)
    ax.set_title(f'VAT Valve #{serVar.get()}')
    ax.set_ylabel('Pressure (mBar)')
    ax.set_xlabel('Valve Turns')
    ax.set_yscale('log')
    ax.set_xlim(0,12)
    ax.set_ylim(1e-7,1e-3)


def plotDataUp():
    plt.pause(0.05)
    ax.cla()
    ax.set_axisbelow(True)
    ax.grid(True)
    ax.set_title(f'VAT Valve #{serVar.get()}')
    ax.set_ylabel('Pressure (mBar)')
    ax.set_xlabel('Valve Turns')
    ax.set_yscale('log')
    ax.set_xlim(0,12)
    ax.set_ylim(1e-7,1e-3)
    ax.plot(valve_turns_up, datalog_up, marker='o', markersize=2, linewidth=1, c='blue', label='Pressure Up')
    plt.pause(0.05)


def plotDataDown():
    plt.pause(0.05)
    ax.cla()
    ax.set_axisbelow(True)
    ax.grid(True)
    ax.set_title(f'VAT Valve #{serVar.get()}')
    ax.set_ylabel('Pressure (mBar)')
    ax.set_xlabel('Valve Turns')
    ax.set_yscale('log')
    ax.set_xlim(0,12)
    ax.set_ylim(1e-7,1e-3)
    ax.plot(valve_turns_up, datalog_up, marker='o', markersize=2, linewidth=1, c='blue', label='Pressure Up')
    ax.plot(valve_turns_down, datalog_down, marker='o', markersize=2, linewidth=1, c='lightblue', label='Pressure Down')
    plt.pause(0.05)

def createTimeLog():
    global time_log_up, time_log_down
    time_log_up = []
    time_log_down = []
    
def logData():
    """Logs valve position, current pressure reading, current time, and
    direction of valve test to a csv file"""
    direction = ""
    ang = checkAng()
    pres = getPressure()
    curTime = str(datetime.now().strftime("%H:%M:%S:%f"))
    
    if up.get():
        direction = "UP"
        time_log_up.append(curTime)
        valve_turns_up.append(float(ang))
        datalog_up.append(pres)
        plotDataUp()
    if top.get():
        direction = "TOP"
        time_log_up.append(curTime)
        time_log_down.append(curTime)
        valve_turns_up.append(float(ang))
        datalog_up.append(pres)
        valve_turns_down.append(float(ang))
        datalog_down.append(pres)
        plotDataDown()
    if down.get():
        direction = "DOWN"
        time_log_down.append(curTime)
        valve_turns_down.append(float(ang))
        datalog_down.append(pres)
        plotDataDown()
    

    print(f'logged: [{ang}, {pres}, {curTime}, {direction}]')



def makeFile():
    """Creates the csv file"""
    global filepath, fileName
    if fileName == f"{str(datetime.now().strftime('%b %d %H_%M'))} ser_{serVar.get()}.csv":
        return
    fileName = f"{str(datetime.now().strftime('%b %d %H_%M'))} ser_{serVar.get()}.csv"
    try:
        filepath = os.path.join(f"\\\opdata2\\Company\\PRODUCTION FOLDER\\VAT Leak Valve Test Data\\VAT Data by SN\\{serVar.get()}", fileName)
        if not os.path.exists(f"\\\opdata2\\Company\\PRODUCTION FOLDER\\VAT Leak Valve Test Data\\VAT Data by SN\\{serVar.get()}"):
            os.makedirs(f"\\\opdata2\\Company\\PRODUCTION FOLDER\\VAT Leak Valve Test Data\\VAT Data by SN\\{serVar.get()}")
            
        print(f"{filepath} created")
        file = open(filepath, 'w')
        file.write("Time,")
        file.write("Valve Turns UP,")
        file.write("Pressure UP,")
        file.write("Valve Turns DOWN,")
        file.write("Pressure DOWN,")
        file.write('\n')
        file.close()
    except:
        print('Could not make the csv file. PC probably not connected to network.')


def writeDataToCSV():
    try:
        print("Saving Data...")
        with open(filepath, 'a', newline='') as file:
            wtr = csv.writer(file)
            for i,data in enumerate(datalog_up):
                wtr.writerow([time_log_up[i], valve_turns_up[i], datalog_up[i]])
            for i,data in enumerate(datalog_down):
                wtr.writerow([time_log_down[i], '', '', valve_turns_down[i], datalog_down[i]])
        print("Data Saved")
    except:
        print("Could not write data to csv file. PC probably not connected to network.")


## *args = [low/start, high/end, holdtime, valvetest?]
def recipeCommand(*args):
    """Runs the valve test"""
    low,high,holdArg,valveBool = args
    testCondition.set('RUNNING RECIPE')
    pressure = getPressure() # get the current pressure
    holdTime = int(holdArg)
    # tolerance is the maximum percent change between pressure readings when checking for stability
    tolerance = 1 # %
    # Window that determines if program will wait for stability set by "tolerance" variable
    low_pressure_window = 6e-7
    high_pressure_window= 6e-6

    # If pressure reading is above the high point and valve is opening up,
    # then change up setting to false.
    if (pressure > high) and up.get() and recipeOn.get():
        up.set(False)
        # If not at the top, then set the top setting to True
        # otherwise, if valve is at the top (top==True) then set down to True.
        if not top.get() and valveBool:
            top.set(True)
        else:
            down.set(True)


    # If pressure reading is below the low point setting or currentTurns is zero
    # and valve is closing, then set recipeOn to False (ie. stop the test)
    if (pressure <= low or (float(currentTurns.get()) == False)) and down.get():
        if float(currentTurns.get()) != False:
            gotoZero()
            root.after(10000)
        recipeOn.set(False)
        writeDataToCSV()
        killWindow(testWindow)
        print('\nVALVE TEST COMPLETE')
    
    ########## VALVE OPENING UP ##########
    if (pressure < high) and recipeOn.get() and up.get():
        print('\nOpening 1/20th of a turn')
        changeStep(1/20)
        root.after(250)
        print(f'Valve Position = {float(currentTurns.get()):.2f}')
        
        checkList = []
        for i in range(0,holdTime):
            logData()
            checkList.append(getPressure())
            print(f'\ncheckList = {checkList}')
            root.after(900)
            
        percentChange = abs(checkList[-1]-checkList[0])/checkList[0] * 100
        print(f'percentChange = {percentChange:.2f} %')
        
        if pressure > low_pressure_window and pressure < high_pressure_window:
            while percentChange > tolerance:
                print("\nWhile loop activated")
                checkList = []
                for i in range(0,holdTime):
                    logData()
                    checkList.append(getPressure())
                    print(f'\ncheckList = {checkList}')
                    if len(checkList) >= 2:
                        percentChange = abs(checkList[-1]-checkList[0])/checkList[0] * 100
                        if percentChange < tolerance:
                            root.after(900)
                            break
                    root.after(900)
                percentChange = abs(checkList[-1]-checkList[0])/checkList[0] * 100
                print(f'percentChange = {percentChange:.2f} %')

    ########## VALVE AT TOP ##########
    elif recipeOn.get() and top.get():
        
        changeStep(1) # increase valve turns by 1 turn
        
        # Check the pressure every second for ten seconds as a safety measure
        # to make sure the pressure hasn't gone too high
        for i in range(10):
            getPressure()
            root.after(1000)
        
        logData()
        
        top.set(False)
        down.set(True)
        
        changeStep(-1)
        root.after(1000)
        
        checkList = []
        for i in range(30):
            logData()
            checkList.append(getPressure())
            print(f'\ncheckList = {checkList}')
            root.after(900)
            
        percentChange = abs(checkList[-1]-checkList[0])/checkList[0] * 100
        print(f'percentChange = {percentChange:.2f} %')
        
        if pressure > low_pressure_window and pressure < high_pressure_window:
            while percentChange > tolerance:
                print('\nWhile loop activated')
                checkList = []
                for i in range(0,holdTime):
                    logData()
                    checkList.append(getPressure())
                    print(f'\ncheckList = {checkList}')
                    if len(checkList) >= 2:
                        percentChange = abs(checkList[-1]-checkList[0])/checkList[0] * 100
                        if percentChange < tolerance:
                            root.after(900)
                            break
                    root.after(900)
                percentChange = abs(checkList[-1]-checkList[0])/checkList[0] * 100
                print(f'percentChange = {percentChange:.2f} %')
    
    ########## VALVE CLOSING DOWN ##########
    elif (pressure > low) and twoWay.get() and recipeOn.get() and down.get():
        if float(currentTurns.get()) > 0:
            print('\nClosing 1/20th of a turn')
            changeStep(-1/20)
            root.after(250)
            print(f'Valve Position = {float(currentTurns.get()):.2f}')
            
            checkList = []
            for i in range(0,holdTime):
                logData()
                checkList.append(getPressure())
                print(f'\ncheckList = {checkList}')
                root.after(900)
                
            percentChange = abs(checkList[-1]-checkList[0])/checkList[0] * 100
            print(f'percentChange = {percentChange:.2f} %')
            
            if pressure > low_pressure_window and pressure < high_pressure_window:
                while percentChange > tolerance:
                    print("\nWhile loop activated")
                    checkList = []
                    for i in range(0,holdTime):
                        logData()
                        checkList.append(getPressure())
                        print(f'\ncheckList = {checkList}')
                        if len(checkList) >= 2:
                            percentChange = abs(checkList[-1]-checkList[0])/checkList[0] * 100
                            if percentChange < tolerance:
                                root.after(900)
                                break
                        root.after(900)
                    percentChange = abs(checkList[-1]-checkList[0])/checkList[0] * 100
                    print(f'percentChange = {percentChange:.2f} %')
        else:
            recipeOn.set(False)
            print('Valve Test Complete (2)')
            
            
    # set lastPres equal to the current pressure reading
    #lastPres.set(getPressure())
    
    # If running a recipe, wait 1.5 seconds the execute the recipeCommand
    # function with low, high, holdArg, and valveBool as *args. Otherwise,
    # set the test condition to not running, up to True, top to False, and
    # down to False.
    if recipeOn.get():
        root.after(1000, lambda: recipeCommand(low,high,holdArg,valveBool))
    else:
        testCondition.set("Not Running")
        up.set(True)
        top.set(False)
        down.set(False)
        
        
def recipeWindow():
    """Creates the recipe window GUI"""
    rFrm = Toplevel(root)
    up.set(True)
    down.set(False)
    top.set(False)
    rFrm.geometry("300x500")
    rFrm.title("Recipe Set")
    testCondition.set("Not Running")
    Entry(rFrm, textvariable=serVar).pack()
    Label(rFrm, text="Serial #").pack()
    Label(rFrm, text="Set lower, upper pressures \nand the rest time per adjustment.\n").pack()
    Entry(rFrm, textvariable=lowPres).pack()
    Label(rFrm, text="Base Pressure (mBar)\n").pack()
    Entry(rFrm, textvariable=highPres).pack()
    Label(rFrm, text="End Pressure/Upper Limit (mBar)\n").pack()
    #expTime = Entry(rFrm)
    #expTime.pack()
    #Label(rFrm, text="Time Up/Down (min)").pack()
    timeRes = Entry(rFrm, textvariable=waitTime).pack()
    Label(rFrm, text="Hold Time per Pressure (s)\n").pack()
    #Entry(rFrm).pack()
    twoWayCheck = Checkbutton(rFrm, text="2-way", variable=twoWay)
    twoWayCheck.pack()
    repeatCheck = Checkbutton(rFrm, text="Repeat", variable=recRepeat)
    repeatCheck.pack()
    recipeOn.set(True)
    Button(rFrm, text="Make and execute recipe from inputs.")
    Button(rFrm, text="Run Valve Test", command=lambda: [valveTest(),lastPres.set(getPressure())]).pack()
    Button(rFrm, text="Exit Recipe Window", command=rFrm.destroy).pack()
    Label(rFrm,textvariable=testCondition).pack()
    root.after(10, getPressure)
#%% Valve Test commands
def valveTest():
    """Creates the valve test window GUI"""
    global testWindow
    twoWay.set(1)
    up.set(True)
    top.set(False)
    down.set(False)
    testWindow = Toplevel(root)
    testWindow.geometry("300x150")
    testWindow.title("Valve Test")
    Button(testWindow,text="Begin Valve Test", command=lambda: [createTimeLog(),makeFile(),createFigure(),recipeCommand(lowPres.get(),highPres.get(),waitTime.get(),True),getBasePressure()]).pack()
    Button(testWindow, text="Save Data and Stop Test", command=lambda: [writeDataToCSV(),killWindow(testWindow)]).pack()
    Button(testWindow, text="Close Window", command=lambda: killWindow(testWindow)).pack()
    

def holdToggle():
    if holdingState.get()!="Paused":
        holdingState.set("Paused")
        holdBool.set(False)
    else:
        holdBool.set(True)
    

def pressureHold():
    target = targetHold.get()
    holdFrm = Toplevel(root)
    holdFrm.geometry("370x400")
    Label(holdFrm, text="May respond slowly during pressure adjustments."+
          "\n Clicking on exit will register within 15 seconds and stop the program.").pack()
    holdingState.set("Paused")
    Label(holdFrm, textvariable=holdingState).pack()
    Label(holdFrm, text="Target:" + target).pack()
    Button(holdFrm, text="Go", command=lambda: holdFunc(targetHold.get())).pack()
    Button(holdFrm, text="Pause", command=holdToggle).pack()
    Checkbutton(holdFrm,text="Check to maintain hold", variable=holdBool).pack()
    Button(holdFrm, text="Exit", command=lambda: killWindow(holdFrm)).pack()
    holdFrm.title("Hold Pressure")
    placeHold = Scale(holdFrm,from_=5,to=60, variable = curPres)
    placeHold.pack()
    Label(holdFrm,textvariable=curPres).pack()


def holdFunc(target):
    try:
        percentOff = (getPressure()-float(target))/float(target)
        quickCheck = holdBool.get()
        # If pressure much higher than target, close valve
        if percentOff > 0.2 and quickCheck:
            changeStep(-0.05)
            holdingState.set("ADJUSTING")
            for i in range(100): root.after(100)
        # If pressure much lower than target, open valve
        elif percentOff < -0.2 and quickCheck:
            changeStep(0.05)
            holdingState.set("ADJUSTING")
            for i in range(10*10): root.after(100)
        # If pressure higher than target, close valve
        elif percentOff > 0.05 and percentOff < 0.2 and quickCheck:
            changeStep(1/90)
            holdingState.set("ADJUSTING")
            for i in range(50): root.after(100)
        # If pressure lower than target, open valve
        elif percentOff < -0.05 and percentOff > -0.2 and quickCheck:
            changeStep(-1/90)
            holdingState.set("ADJUSTING")
            for i in range(50): root.after(100)
        else:
            holdingState.set("HOLDING")
    except Exception as e:
        holdingState.set(str(e) + "\nClosing 1/10 turn")
        changeStep(-1/10)
    if holdBool.get():
        root.after(5000, lambda: holdFunc(target))
    else:
        holdingState.set("Paused")
        
        
#%% Tkinter GUI setup and vars
root = Tk()
styleEn = ttk.Style()
styleDis = ttk.Style()
root.geometry('500x500')
motorPosition = StringVar()
motorStatus = StringVar()
motorStatus.set("Init")
#startAng = checkAng()
currentTurns = StringVar()
holdBool = BooleanVar()
recipeOn = BooleanVar()
recRepeat = BooleanVar()
testCondition = StringVar()
serVar = StringVar()
#lowPres = DoubleVar()
#highPres = DoubleVar()
up = BooleanVar()
waitTime = IntVar()
waitTime.set(4)
top = BooleanVar()
down = BooleanVar()
testCondition.set("WAITING")
#%% Motor param commands
#forward motor direction (more positive is more open, 0=closed)
sendCommand("/1F0R")
# Increase motor-on current %99 max (higher torque)
sendCommand("/1m99R")
# Decrease motor-off current: 2% max (Able to hand-turn)
sendCommand("/1h2R")
#set velocity ustep/second
sendCommand("/1V35000R")
#set velocity ustep/second
sendCommand("/1L10R")
#set ustep resolution
sendCommand("/1j256R")
#%% GUI tkinter code
frm = ttk.Frame(root, padding=10)
frm.grid()
root.title("Valve Control")
runState = ttk.Button(frm, text="Set Recipe", command=recipeWindow)
runState.grid()
holdingState = StringVar()

lowPres = DoubleVar()
highPres = DoubleVar()
highPres.set(1e-5)
turns = DoubleVar()

twoWay = IntVar()
curPres = DoubleVar()
lastPres = DoubleVar()
ttk.Button(frm, text="Stop Motor", command=stopMotor).grid()
# Enter absolute pos target
degTurn = Entry(frm, textvariable=turns)
#
degTurn.delete(0,END)
degTurn.insert(0,"0")
degTurn.grid(column=0,row=3)
Label(frm,text="Target Motor Position (Turns)").grid(column=1,row=3)
Label(frm,text="Current Motor Position (Turns)").grid(column=1,row=4)
# Nominal Step Angle
ttk.Label(frm,textvariable=currentTurns).grid(column=0,row=4)
# Go to specified target angle
ttk.Button(frm, text='Go To Target', command=gotoTarget).grid()
# Go to absolute position 0
Button(frm, text='Close Valve Completely', command=gotoZero).grid()
# Define Motor Position as Zero
ttk.Button(frm, text="Calibrate Motor (Zero Position)", command = zeroAngle).grid()
# Open or close valve incrementally
Button(frm, text="Open 1/60", command = lambda: changeStep(1/60)).grid(column=0,row=10)
Button(frm, text="Close 1/60", command = lambda: changeStep(-1/60)).grid(column=1,row=10)
Button(frm, text="Open 1/20", command = lambda: changeStep(1/20)).grid(column=0,row=11)
Button(frm, text="Close 1/20", command = lambda: changeStep(-1/20)).grid(column=1,row=11)
Button(frm, text="Open Full Turn", command = lambda: changeStep(1)).grid(column=0,row=12)
Button(frm, text="Close Full Turn", command = lambda: changeStep(-1)).grid(column=1,row=12)
# Enter pressure target and open pressure hold window
targetHold = Entry(frm)
targetHold.grid()
Label(frm, text="Pressure to Hold (10e-7 mBar)").grid()
Label(frm,textvariable=curPres).grid(column=1,row=13)
Label(frm,text="Current Pressure (10e-7 mBar)").grid(column=1,row=14)
Button(frm, text="Hold Pressure", command=pressureHold).grid()
Button(frm, text="Update Pressure", command=getPressure).grid()
ttk.Button(frm, text="Exit", command=lambda: killWindow(root)).grid()
checkAng()
getPressure()

root.mainloop()

try: 
    file.close()
    print('file closed')
except: pass

#%% Plot pressure vs valve turns

fig, ax = plt.subplots(frameon=True, dpi=300, edgecolor='k', linewidth=2, figsize=(8*0.55,6*0.5))
fig.set_tight_layout(True)
ax.set_axisbelow(True)
ax.grid(True)
ax.set_title(f'VAT Valve #{serVar.get()}',fontsize=10)
ax.set_ylabel('Normalized Pressure (mBar)',fontsize=7)
ax.set_xlabel('Valve Turns',fontsize=7)
ax.set_yscale('log')
ax.fill_betweenx([0.5,5],[0],[12],alpha = 0.25,color='silver')
#ax.set_xlim(0,4)
ax.set_ylim(0.001,1000)

ax.set_yticks([0.001, 0.01, 0.1, 1, 10, 100, 1000])
ax.set_yticklabels(['$10^{-9}$', '$10^{-8}$', '$10^{-7}$', '$10^{-6}$', '$10^{-5}$', '$10^{-4}$', '$10^{-3}$'],fontsize=7)
#ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10,11,12])
#ax.set_xticklabels(['0','1','2','3','4','5','6','7','8','9','10','11','12'],fontsize=7)

x_data_up = valve_turns_up
y_data_up = (np.array(datalog_up) - base_pressure) * 1e6
#y_data_up = (np.array(datalog_up)) * 1e6
x_data_down = valve_turns_down
y_data_down = (np.array(datalog_down) - base_pressure) * 1e6
#y_data_down = (np.array(datalog_down)) * 1e6

ax.plot(x_data_up,y_data_up,markersize=1,marker='o',linewidth=1,c='blue',label='Pressure up')
ax.plot(x_data_down,y_data_down,markersize=1,marker='o',linewidth=1,c='lightblue',label='Pressure down')

ax.legend(loc='upper left',fontsize=7)

