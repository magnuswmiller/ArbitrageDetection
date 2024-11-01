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
    if(wmType == 'w'):
        filteredData = rawData[(rawData['Expiry'] == date) & (rawData['CID'].str.contains('W'))]
    else:
        filteredData = rawData[(rawData['Expiry'] == date) & (rawData['CID'].str.startswith('SPX2'))]
    return filteredData

# lpArbSolver
def lpArbSolver():
    return -1

# checkArbitrage
def checkArbitrage():
    return -1

# arbitrageDetection
def arbitrageDetection(date, wmType, filePath):
    rawData = loadData(filePath)
    print(rawData)
    filteredData = filterData(rawData, date, wmType)
    print(filteredData)
    return -1

# posExitOptimize
def positionExitOptimize():
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
