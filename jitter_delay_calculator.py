#!/usr/bin/env python
# -*- coding: utf-8 -*-	    ## Türkçe karakter desteği

import os
#import commands
import argparse

def readFromFile(fileName):
    """
    reads from file and returns the file content

    input:
        fileName: string

    output:
        content: string
    """
    with open(fileName, 'rb') as file:
        content = file.read().decode("utf-16").rstrip("\n")
        # content = file.read().rstrip("\n")
    return content
    
def parseTime(content, duration, opSys):
    """
    parses time values from content and return as string array

    input:
        content: string
        duration: int
    output:
        delay_float: float array
        contentList: string array
    """

    contentList = content.split("from")
    listLong = len(contentList)
    timeValues = []
    delays_float = []

    for i in range(1,listLong):
        if opSys == "windows":
            if contentList[i].find("sent") == -1:
                timeValues.append(contentList[i].__str__().split()[2])
            else:
                timeValues.append(contentList[i].__str__().split()[4])
        
        if timeValues[i-1].find("=") == -1:
            print("olası kopukluk tespit edildi!")
            # burada dosyanın sonundaki lost değerini de kontrol et
        elif timeValues[i-1].find("=") == 4:
            timeValues[i-1] = timeValues[i-1].split("=")[1][:-2]
        
    for i in range(len(timeValues)): 
        delays_float.append(float(timeValues[i])) 

    return delays_float, contentList

def calculateJitter(delays):
    """
    reads delay values, calculates and returns jitter

    input:
        delays: float array
    output:
        calculatedJitter: float
    """
    jitter = []

    for i in range(len(delays)-1):
        jitter.append(abs(delays[i] - delays[i+1]))

    calculatedJitter = round(sum(jitter) / len(jitter),2)

    return calculatedJitter

def calculateAverageDelay(delays):
    """
    calculates average delay value

    input: 
        delays: float array
    output:
        calcultedDelay: float
    """
    calculatedDelay = round(sum(delays) / len(delays),2)
    
    return calculatedDelay

def readAverageDelay(content, opSys):
    """
    reads the latest companent in content, parses and returns the average value

    input:
        content: string array
        opSyst: string(operating system windows/linux/mac)
    output:
        average: float
    """
    if opSys.lower() in ("linuxmac"):
        data = content[-1]
        average = data.split("=")[-1].strip().split("/")[1]

    elif opSys.lower() == "windows":
        data = content[-1]
        average = data.split(",")[-1].split("=")[-1].strip()[:-2]

    else:
        print("Hata! Isletim sistemi bilgisinde sorun var!")

    return float(average)

def readLost(content, duration, opSys):
    """
    reads the content and calculates the lost

    input:
        content: string list
        duration: int
        opSys: string(operating system windows/linux/mac)
    output:
        lost: int
        info: string
    """
    info = "OK"

    if opSys.lower() in ("linuxmac"):
        data = content[-1]

        readTotalPacket = data.split("---")[2].split("packets")[0].strip()
        readReceivedPacket = data.split("---")[-1].split(",")[1].split(" ")[1]
        readPacketLost = int(readTotalPacket) - int(readReceivedPacket)

        calculatedPacketLost = duration - (len(content)-1)
        
        if readPacketLost != calculatedPacketLost:
            info = f"""Okunan ve hesaplanan kayip ayni degil!
            Okunan Kayip: {readPacketLost}, Hesaplanan Kayip: {calculatedPacketLost}
            """
        lost = readPacketLost

    elif opSys.lower() == "windows":
        data = content[-1]
        readPacketLost = data.split(",")[2].replace(" ", "").split("=")[-1].split("(")[0]
        readPacketLost = int(readPacketLost)

        calculatedPacketLost = duration - (len(content)-1)
        
        if readPacketLost != calculatedPacketLost:
            info = f"""Okunan ve hesaplanan kayip ayni degil!
            Okunan Kayip: {readPacketLost}, Hesaplanan Kayip: {calculatedPacketLost}
            """
        lost = readPacketLost

    else:
        print("Hata! Isletim sistemi bilgisinde sorun var!")

    return readPacketLost, calculatedPacketLost, info

def combineLogs(*args):
    """
    puts every single parameter that sent into a list

    input:
        argument(s)
    
    output:
        log: list
    """
    log = []
    for i in range(len(args)):
        log.append(args[i])
    
    return log
        
def writeLogsToFile(fileName, log):
    """
    Writes logs to file

    input:
        fileName: string
        log: list
    output:
        none
    """
    logFileName = "results_" + fileName

    fullLog = f"""
    *********** Anaylsis Results ***********
    Calculated Jitter\t\t: {log[0]}
    Calculated Average Delay\t: {log[1]}
    Read Average Delay\t\t: {log[2]}
    Calculated Lost\t\t: {log[3]}
    Read Lost\t\t\t: {log[4]}

    Analysed File\t: {fileName}
    """

    # combineLogs(calculatedJitter, calculatedAverageDelayValue, readAverageDelayValue, readLostValue, calculatedLostValue)

    with open(logFileName, "w") as file:
        file.writelines(fullLog)

def main():
    # print("Script is running...")
    parser = argparse.ArgumentParser()

    parser.add_argument("fileName", help="Analiz edilecek ping logu")
    parser.add_argument("testDuration", help="Testin yapildigi sure")
    parser.add_argument("isletimSistemi", help="windows/macos/linux")

    args = parser.parse_args()

    fileName = args.fileName
    duration = args.testDuration
    osValue = args.isletimSistemi

    duration = int(duration)

    fileContent = readFromFile(fileName)
    timeSeries, content = parseTime(fileContent, duration, osValue)
    print(fileContent)
    print(content)
    print(timeSeries)
    calculatedJitter = calculateJitter(timeSeries)
    calculatedAverageDelayValue = calculateAverageDelay(timeSeries)
    readAverageDelayValue = readAverageDelay(content, osValue)
    readLostValue, calculatedLostValue, info = readLost(content, duration, osValue)

    print("calculatedJitter", calculatedJitter)
    print("calculatedAverageDelay", calculatedAverageDelayValue)
    print("readAverageDelayValue", readAverageDelayValue)
    if info != "OK":
        print(info)
    else:
        print("readLostValue", readLostValue)
        print("calculatedLostValue", calculatedLostValue)

    logs = combineLogs(calculatedJitter, calculatedAverageDelayValue, readAverageDelayValue, readLostValue, calculatedLostValue)

    writeLogsToFile(fileName, logs)

if __name__ == "__main__":
    main()


