from BrickPi import *
import picamera
import picamera.array
import time
from datetime import datetime

#Necessary imports
from math import atan2
from math import tan

RED = 0
GREEN = 1
BLUE = 2

ANGLEBINSIZE = 10



######
##
## Utility functions (FOR TESTING PURPOSES ONLY)
##
######
def colorPixel(pixel,redValue,greenValue,blueValue):
    pixel[RED] = redValue
    pixel[GREEN] = greenValue
    pixel[BLUE] = blueValue

def drawLine(data,x0,y0,x1,y1):
    if x1<0:
        x1=0
    elif x1>=len(data):
        x1=len(data)-1
    if y1<0:
        y1=0
    elif y1>=len(data[0]):
        y1=len(data[0])-1
    for i in range(1,100):
        alpha = i/100.0
        colorPixel(data[int(round(x0+alpha*(x1-x0)))][int(round(y0+alpha*(y1-y0)))],255,255,255)





######
##
## Determine the Start Point
##
######
def isRed(pixel):                           #Optimized version of isRed
    pixelRedMinusThreshold = pixel[0] - 50
    if pixelRedMinusThreshold>pixel[2] and pixelRedMinusThreshold>pixel[1]:
        return True
    else:
        return False

def isInRedRegion(i,j,data):                #Returns True when the pixel and its 8 neighbouring pixels are Red
    if i<1 or j<1 or i>(len(data)-2) or j>(len(data[0])-2):     #We are at the border of the picture, so the pixel is not surrounded by Red pixels.
        return False
    elif isRed(data[i][j]) and isRed(data[i][j-1]) and isRed(data[i][j+1]) and isRed(data[i+1][j]) and isRed(data[i-1][j]) and isRed(data[i-1][j-1]) and isRed(data[i-1][j+1]) and isRed(data[i+1][j-1]) and isRed(data[i+1][j-1]):
        return True
    else:
        return False

def searchHorizontalCentre(data,starti,startj):                 #Go left as far as you can (while staying in the Red region), go right as far as you can. Return the centre of this.
    minj=startj
    maxj=startj
    while (minj>0) and isRed(data[starti][minj]):
        minj-=1
    while (maxj<len(data[0])-1) and isRed(data[starti][maxj]):
        maxj+=1
    return int((maxj+minj)/2)

def correctStartPoint(data,starti,startj,centre):
    startj = searchHorizontalCentre(data,starti,startj)
    while (starti<len(data)-1) and isRed(data[starti+1][startj]):   #Make sure the StartPoint is on the border of the main Red region.
        starti += 1
    return [starti,startj]

def determineStartPoint(data):              #The StartPoint is determined by searching for the first pixel that is in a Red region.
    centre = len(data[0])//2
    for i in range(len(data)-2,1,-10):      #Start from the bottom row.
        for dj in range(0,centre-2,2):      #Search outwards from the centre.
            j = centre+dj
            if isInRedRegion(i,j,data):
                return correctStartPoint(data,i,j,centre)
            j = centre-dj
            if isInRedRegion(i,j,data):
                return correctStartPoint(data,i,j,centre)
    return [len(data)-1,0]                  #We did not find a proper StartPoint. This return value results in a large steering angle, so that the car can turn around.





######
##
## Angle and Distance
##
######
def distance(i0,j0,i1,j1):
    deltai = i1-i0
    deltaj = j1-j0
    #return deltai*(deltai*deltai+deltaj*deltaj)
    return deltai*deltai*deltai+deltaj*deltaj

def angle(i0,j0,i1,j1):
    return int(round(atan2(j1-j0,i1-i0)*57.29578))

def angleToBin(angle):
    if (angle == 180):      #Fix for a problem that appears because of rounding in angle(). This is unavoidable if we want proper rounding in angle().
        angle = 179
    return (angle+180)//ANGLEBINSIZE





######
##
## Main method
##
#####
def determineAngleFromPicture(data):
    #Measurement containers
    numberOfBins = 360//ANGLEBINSIZE
    arrowLengths = [1999999999] * numberOfBins
    arrowI = [0] * numberOfBins
    arrowJ = [0] * numberOfBins

    #Initialization
    starti,startj = determineStartPoint(data)
    i = starti
    j = startj
    direction = 2
    steps = 0


    
    #Square Tracing Algorithm
    while True:
        #Make a step
        steps += 1
        if direction == 0:      #Up
            i -= 1
        elif direction == 1:    #Right
            j += 1
        elif direction == 2:    #Down
            i += 1
        elif direction == 3:    #Left
            j -= 1

        #Stop condition
        if (i == starti and j == startj and steps>20) or (steps>40*len(data)):
            break

        #Measure arrow length
        if steps%2 == 1:
            binBin = angleToBin(angle(i,j,starti,startj))
            length = distance(i,j,starti,startj)
            if (arrowLengths[binBin]>length):
                arrowLengths[binBin] = length
                arrowI[binBin] = i
                arrowJ[binBin] = j

        #Determine direction
        if i>=len(data) or j<0 or j>=len(data[0]) or i<0:   #Outside the picture region. Pixel is Not-Red.
            direction = (direction+1)%4
        else:
            if isRed(data[i][j]):                           #Red
                #colorPixel(data[i][j],255,200,200)          #FOR TESTING PURPOSES ONLY
                direction = (direction+3)%4                 #(x+3)%4 corresponds to (x-1)%4
            else:                                           #Not-Red
                #colorPixel(data[i][j],200,255,255)          #FOR TESTING PURPOSES ONLY
                direction = (direction+1)%4



    #Process measurements
    maximumLength = 0
    maximumBin = 0
    for binBinBin in range(0,numberOfBins):
        length = arrowLengths[binBinBin]
        if length>maximumLength and length != 1999999999:
            maximumLength = length
            maximumBin = binBinBin
    
    #drawLine(data,len(data)-1,len(data[0])//2,arrowI[maximumBin],arrowJ[maximumBin])      #FOR TESTING PURPOSES ONLY
    angleToTarget = angle(arrowI[maximumBin],arrowJ[maximumBin],len(data)-1,len(data[0])//2)
    relativeVerticalFreeSpace = abs(starti-arrowI[maximumBin])/(1.0*len(data))
    return [angleToTarget,relativeVerticalFreeSpace,startj]














###############################################################################################################################


steering = PORT_A
motor1 = PORT_B
motor2 = PORT_C
steeringSpeed = -75
motorSpeed = -50

BrickPiSetup()
BrickPi.MotorEnable[steering] = 1
BrickPi.MotorEnable[motor1] = 1
BrickPi.MotorEnable[motor2] = 1
BrickPiSetupSensors()
BrickPi.Timeout=20000
BrickPiSetTimeout()



def updateSpeed(sSpeed,mSpeed):
    BrickPi.MotorSpeed[steering] = sSpeed
    BrickPi.MotorSpeed[motor1] = mSpeed
    BrickPi.MotorSpeed[motor2] = mSpeed
    BrickPiUpdateValues()
    time.sleep(.01)
    BrickPi.MotorSpeed[steering] = sSpeed
    BrickPi.MotorSpeed[motor1] = mSpeed
    BrickPi.MotorSpeed[motor2] = mSpeed
    BrickPiUpdateValues()
    time.sleep(.01)
    BrickPi.MotorSpeed[steering] = sSpeed
    BrickPi.MotorSpeed[motor1] = mSpeed
    BrickPi.MotorSpeed[motor2] = mSpeed
    BrickPiUpdateValues()
    time.sleep(.01)



with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as output:
        camera.resolution = (320, 240)
        i=0
        while True:
            i+=1
            #if i%2 == 0:
                #camera.capture("output_%s.jpg" % str(datetime.now()), format='jpeg', use_video_port = True)
            camera.capture(output, 'rgb', use_video_port = True)
            target,vspace,startj = determineAngleFromPicture(output.array)
            print(target,vspace,startj)
            output.truncate(0)
            if startj>165:
                    updateSpeed(steeringSpeed,motorSpeed)
            elif startj<155:
                    updateSpeed(-steeringSpeed,motorSpeed)
            else:
                if target < 0:
                    updateSpeed(steeringSpeed,motorSpeed)
                else:
                    updateSpeed(-steeringSpeed,motorSpeed)
            

