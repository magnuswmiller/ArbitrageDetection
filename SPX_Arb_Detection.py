# S&P 500 Options Arbitrage Detector
# Requirements When Running:

# Required Libraries and Versions:
# python -v 3.12.6

# Library Import:
import pandas as pd
import numpy as np
from scipy.optimize import linprog
from math import *
from datetime import date
from datetime import timedelta

# loadData
def loadData(filePath):
    print("* Loading data from file...")
    data = pd.read_csv(filePath, skiprows=3)
    dataArr = data.to_numpy()
    for i in range(len(dataArr)):
        if dataArr[i][1].startswith('SPXW'):
            dataArr[i][0] = dataArr[i][1][4:10]
        else:
            dataArr[i][0] = dataArr[i][1][3:9]
        dataArr[i][0] = int("20" + dataArr[i][0])
    data = pd.DataFrame(dataArr)
    data.columns = ["Expiry",
                    "CID",
                    "CLast",
                    "CNet",
                    "CBid",
                    "CAsk",
                    "CVol",
                    "CIV",
                    "CDelta",
                    "CGamma",
                    "COpenInt",
                    "Strike",
                    "PID",
                    "PLast",
                    "PNet",
                    "PBid",
                    "PAsk",
                    "PVol",
                    "PIV",
                    "PDelta",
                    "PGamma",
                    "POpenInt"]
    print("* Data successfully loaded.")
    return data

# filter data
def filterData(rawData, ed, wmType):
    print("* Filtering data based on option type and expiration date...")
    rawData = rawData.drop(columns=['CLast',
                                    'CNet',
                                    'CVol',
                                    'CIV',
                                    'CDelta',
                                    'CGamma',
                                    'COpenInt',
                                    'PLast',
                                    'PNet',
                                    'PVol',
                                    'PIV',
                                    'PDelta',
                                    'PGamma',
                                    'POpenInt'])
    if(wmType == 'w'):
        filteredData = rawData[(rawData['Expiry'] == ed) & (rawData['CID'].str.contains('W'))]
    else:
        filteredData = rawData[(rawData['Expiry'] == ed) & (rawData['CID'].str.startswith('SPX2'))]
    print("* Data filtering successful.")
    return filteredData

# subAConstructor
def subAConstructor(strikes, strikeLen, isCall):
    A = np.zeros((strikeLen, strikeLen))
    for j, K_j in enumerate(strikes):
        row = []
        for i, K_i in enumerate(strikes):
            if(isCall == 1):
                longPayoff = max(K_j - K_i, 0)
            else:
                longPayoff = max(K_i - K_j, 0)

            # append payoff to row
            row.extend([longPayoff])
        # set row
        A[j] = row
    return A

def constructA(filteredData):
    # strike prices
    strikes = filteredData['Strike'].to_numpy()

    # number of variables
    n = len(strikes)
    numVars = 4 * n

    # construct sub matices
    print("* Constructing A matrix...")
    # first constraint
    z = np.zeros(numVars)
    for i in range(numVars//4):
        z[(numVars//2)+i] = strikes[i]
    for i in range(numVars//4):
        z[(numVars//2)+(numVars//4)+i] = -strikes[i] 

    # last constraint
    o = np.zeros(numVars)
    for i in range(numVars//4):
        o[i] = 1
    for i in range(numVars//4):
        o[(numVars//4)+i] = -1
    
    # middle constraints
    Alc = subAConstructor(strikes, n, 1)
    Asc = -Alc
    Alp = subAConstructor(strikes, n, 0)
    Asp = -Alp
    Aint1 = np.concatenate((Alc, Asc, Alp, Asp), axis=1)

    # construct A
    A = np.vstack((z, Aint1, o))

    # saving A to csv for easier debugging
    DF = pd.DataFrame(A) 
    DF.to_csv("data1.csv")
    print("* A construction successful.")

    return A

def constructB(filteredData):
    strikes = filteredData['Strike'].to_numpy()

    # create b
    print("* Constructing b matrix...")
    b = np.zeros(len(strikes) + 2)
    b[len(strikes) + 1] = 0
    print("* b construction successful.")

    return b

def constructC(filteredData):
    # bid, ask for both call and puts
    xca = filteredData['CAsk'].to_numpy()
    xcb = filteredData['CBid'].to_numpy()
    xpa = filteredData['PAsk'].to_numpy()
    xpb = filteredData['PBid'].to_numpy()

    print("* Constructing LP...")
    print("* Constructing c matrix")
    # initialize objective
    c = []
    
    # populate objective
    for i in range(len(xca)):
        c.append(xca[i])
    for i in range(len(xcb)):
        c.append(-xcb[i])
    for i in range(len(xpa)):
        c.append(xpa[i])
    for i in range(len(xpb)):
        c.append(-xpb[i])

    c = np.array(c)
    print("* c construction successful.")
    return c 

def findCurPos(isLong, isCall, strike, numVars):
    curPos = 0
    if(isCall == 1):
        if(isLong == 1):
            curPos = strike
        else:
            curPos = (numVars // 4) + strike
    else:
        if(isLong == 1):
            curPos = (numVars // 2) + strike
        else:
            curPos = (numVars // 2) + (numVars // 4) + strike
    return curPos 

def writeBounds(curPos, numVars, weight):
    bounds = []
    for i in range(numVars + 1):
        tempBound = (0,1000000)
        if(i == curPos):
            tempBound = (weight, weight)
        if(i == numVars):
            tempBound = (-1000000,1000000)
        bounds.append(tempBound)
    return bounds

# lpArbSolver
def lpArbSolver(A, b, c):
    # running solver
    print("* Running LP arbitrage solver...")
    result = linprog(c, A_ub=-A, b_ub=b, bounds=(0, 100), method='highs')

    # interpreting results
    if result.success:
        print("* Optimization successful")
        if result.fun < 0:
            print("*** Arbitrage Detected ***")
            print("Minimum cost to enter: ", -result.fun)
            print(result.x)
        else:
            print("*** No Arbitrage Detected ***")
    else:
        print("* Optimization failed: ", result.message)

    return -1

# arbitrageDetection
def arbitrageDetection(ed, wmType, filePath):
    rawData = loadData(filePath)
    filteredData = filterData(rawData, ed, wmType)
    c = constructC(filteredData)
    A = constructA(filteredData)
    b = constructB(filteredData)
    result = lpArbSolver(A, b, c)
    return -1

def lpExitSolver(A, b, c, bounds, strikeIndex, strikes):
    # running solver
    print("* Running LP exit solver...")
    result = linprog(c, A_eq=A, b_eq=b, bounds=bounds, method='highs')
    if result.success:
        print("* Optimization successful")
        for i in range(len(result.x)):
            if(i != strikeIndex):
                if(i < (len(result.x)-2)//4):
                    if(result.x[i] > 0.05):
                        print("Long ", result.x[i], " calls at strike ", strikes[i%len(strikes)])
                elif(i < (len(result.x)-2)//2):
                    if(result.x[i] > 0.05):
                        print("Short ", result.x[i], " calls at strike ", strikes[i%len(strikes)])
                elif(i < (((len(result.x)-2)//2)+((len(result.x)-2)//4))):
                    if(result.x[i] > 0.05):
                        print("Long ", result.x[i], " puts at strike ", strikes[i%len(strikes)])
                elif(i < (len(result.x)-2)):
                    if(result.x[i] > 0.05):
                        print("Short ", result.x[i], " puts at strike ", strikes[i%len(strikes)])
                elif(i < (len(result.x)-1)):
                    if(result.x[i] > 0.05):
                        print("Sell ", result.x[i], " zero coupon bonds.")
                else:
                    if(result.x[i] > 0):
                        print("Buy ", result.x[i], " zero coupon bonds.")
                    else:
                        print("Sell", result.x[i], " zero coupon bonds.")
                
        print("Minimum cost to exit: ", result.fun)
    else:
        print("* Optimization failed: ", result.message)
    return -1

# posExitOptimize
def positionExitOptimize(sd, ed, wmType, filePath, isLong, isCall, strike, weight, riskFreeRate):
    # load and filter data set
    rawData = loadData(filePath)
    filteredData = filterData(rawData, ed, wmType)
    numStrikes = len(filteredData.index)

    # construct c matrix
    c = constructC(filteredData).tolist()
    #TODO: figure out date difference
    settlementDate = date.fromisoformat(str(sd))
    expiryDate = date.fromisoformat(str(ed))
    timeDelta = ((expiryDate - settlementDate).days)/365

    zcbPrice = exp(-(riskFreeRate)*timeDelta)

    c.append(zcbPrice)
    c = np.array(c)

    # construct A matrix
    A = constructA(filteredData)
    rf = np.zeros((numStrikes + 2, 1))
    for i in range(numStrikes + 2):
        for j in range(1):
            if(j == 0):
                rf[i][j] = 1
            if(i == numStrikes+1):
                rf[i][j] = 0
    A = np.hstack((A, rf))

    # saving A to csv for easier debugging
    DF = pd.DataFrame(A) 
    DF.to_csv("data2.csv")

    # construct b matrix
    b = constructB(filteredData)

    # Find current position to exit
    strikes = filteredData['Strike'].to_numpy()
    numVars = (numStrikes * 4)
    strikeIndex = 0
    for i in range(numStrikes):
        if(strikes[i] == strike):
            break
        else:
            strikeIndex += 1
    curPos = findCurPos(isLong, isCall, strikeIndex, numVars)

    # write bounds
    bounds = writeBounds(curPos, numVars, weight)

    # running solver
    #A
    result = lpExitSolver(A, b, c, bounds, strikeIndex, strikes)
    
    return -1

# main function of program
def main():
    # Explanation
    print("*** Welcome to the Arbitrage Detection and Position Exit Optimization Calculator ***")
    partNum = int(input(" * Would you ARBITRAGE DETECTION (0) or POSITION EXIT CALULATOR (1): (0/1) "))

    # branch path for part 1 (Arbitrage) or part 2 (Position Exit)
    while(partNum != 3):
        # part 1
        if(int(partNum) == 0):
            print("*** You have selected ARBITRAGE DETECTION ***")
            filePath = input("* Please enter the file path to the option data: ")
            wmType = input("* Are you looking at weekly or monthly options? (w/m): ")
            ed = int(input("* Please enter expiration date: (yyyymmdd) "))
            arbitrageDetection(ed, wmType, filePath)
        # part 2
        else:
            print("*** You have selected POSITION EXIT CALCULATOR ***")
            filePath = input("* Please enter the file path to the option data: ")
            wmType = input("* Are you looking at weekly or monthly options? (w/m): ")
            sd = int(input("* Please enter settlement date/pricing date: (yyyymmdd) "))
            ed = int(input("* Please enter expiration date: (yyyymmdd) "))
            print("* Some information is necessary to calculate the position exit.")
            isLong = int(input("* Are you short (0) or long (1) your position? (0/1): "))
            isCall = int(input("* Are you in a put (0) or call (1) position? (0/1) "))
            strike = int(input("* What is the strike of your position? "))
            weight = int(input("* How many options do you hold? "))
            riskFreeRate = float(input("* Please enter the risk free rate: "))
            positionExitOptimize(sd, ed, wmType, filePath, isLong, isCall, strike, weight, riskFreeRate)

        # repeat or exit
        ans = input("Would you like to continue with another use? (y/n): ")
        if(ans == 'y'):
            partNum = int(input(" * Would you ARBITRAGE DETECTION (0) or POSITION EXIT CALULATOR (1): (0/1) "))
        else:
            partNum = 3

    print("*** Thank you for using the calculator ***")

    return -1

# automatically calls and runs the main function
if __name__ == '__main__':
    main()
