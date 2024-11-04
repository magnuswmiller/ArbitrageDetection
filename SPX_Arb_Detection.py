# S&P 500 Options Arbitrage Detector
# Requirements When Running:
# - 

# Required Libraries and Versions:
# python -v 3.12.6

# Library Import:
import pandas as pd
import numpy as np
from scipy.optimize import linprog

# loadData
def loadData(filePath):
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
    return data

# filter data
def filterData(rawData, date, wmType):
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
        filteredData = rawData[(rawData['Expiry'] == date) & (rawData['CID'].str.contains('W'))]
    else:
        filteredData = rawData[(rawData['Expiry'] == date) & (rawData['CID'].str.startswith('SPX2'))]
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

# lpArbSolver
def lpArbSolver(filteredData):
    # bid, ask for both call and puts
    xca = filteredData['CAsk'].to_numpy()
    xcb = filteredData['CBid'].to_numpy()
    xpa = filteredData['PAsk'].to_numpy()
    xpb = filteredData['PBid'].to_numpy()

    # strike prices
    strikes = filteredData['Strike'].to_numpy()

    # number of variables
    n = len(strikes)
    numVars = 4 * n
    m = len(xca)

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
    print(c)

    #construct sub matices
    z = np.zeros(numVars)
    for i in range(numVars//4):
        z[(numVars//2)+i] = -1
    for i in range(numVars//4):
        z[(numVars//2)+(numVars//4)+i] = 1
    print(z)
    o = np.zeros(numVars)
    for i in range(numVars//4):
        o[i] = 1
    for i in range(numVars//4):
        o[(numVars//4)+i] = -1
    print(o)
    Alc = subAConstructor(strikes, n, 1)
    Asc = -Alc
    Alp = subAConstructor(strikes, n, 0)
    Asp = -Alp
    Aint1 = np.concatenate((Alc, Asc, Alp, Asp), axis=1)
    print(Aint1)
    print(len(Aint1[0]))

    # construct A
    A = np.vstack((z, Aint1, o))
    print(Alc)
    print(Asc)
    print(Alp)
    print(Asp)
    print(A)
    DF = pd.DataFrame(A) 
    DF.to_csv("data1.csv")

    # create b
    b = np.zeros(len(strikes) + 2)
    b[len(strikes) + 1] = 1

    result = linprog(c, A_ub=-A, b_ub=b, bounds=(0, 100), method='highs')
    if result.success:
        print("Optimization successful. Portfolio structure:", result.x)
        print("Minimum cost:", result.fun)
    else:
        print("Optimization failed:", result.message)

    return -1

# arbitrageDetection
def arbitrageDetection(date, wmType, filePath):
    rawData = loadData(filePath)
    filteredData = filterData(rawData, date, wmType)
    print(filteredData)
    result = lpArbSolver(filteredData)
    return -1

# posExitOptimize
def positionExitOptimize():
    rawData = loadData(filePath)
    filteredData = filterData(rawData, date, wmType)
    print(filteredData)
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
            date = int(input("* Please enter expiration date: (yyyymmdd) "))
            arbitrageDetection(date, wmType, filePath)
        # part 2
        else:
            print("*** You have selected POSITION EXIT CALCULATOR ***")
            filePath = input("* Please enter the file path to the option data: ")
            wmType = input("* Are you looking at weekly or monthly options? (w/m): ")
            date = int(input("* Please enter expiration date: (yyyymmdd) "))
            print("* Some information is necessary to calculate the position exit.")
            maturityDate = int(input("* What is the maturity date of your position? "))
            isLong = int(input("* Are you short (0) or long (1) your position? (0/1): "))
            number = int(input("* How many options do you hold? "))
            riskFreeRate = int(input("* Please enter the risk free rate: "))
            positionExitOptimize(date, wmType, filePath, maturityDate, isLong, number, riskFreeRate)

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
