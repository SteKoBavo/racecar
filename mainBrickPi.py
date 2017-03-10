from BrickPi import *
import picamera
import picamera.array
import time

#Necessary imports
from math import atan2
from math import tan



######
##
## Determine the Start Point
##
######
def isRed(pixel):                           #Optimized version of isRed
    pixelRedMinusThreshold = pixel[0] - 25
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
    if (startj != centre):                                      #Correct startj if the StartPoint in not in the centre. Otherwise assume that startj is OK.
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
    return angle+180





######
##
## Main method
##
#####
def determineAngleFromPicture(data):
    #Measurement containers
    numberOfBins = 360
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
                direction = (direction+3)%4                 #(x+3)%4 corresponds to (x-1)%4
            else:                                           #Not-Red
                direction = (direction+1)%4



    #Process measurements
    maximumLength = 0
    maximumBin = 0
    for binBinBin in range(0,numberOfBins):
        length = arrowLengths[binBinBin]
        if length>maximumLength and length != 1999999999:
            maximumLength = length
            maximumBin = binBinBin

    angleToTarget = angle(arrowI[maximumBin],arrowJ[maximumBin],len(data)-1,len(data[0])//2)
    relativeVerticalFreeSpace = abs(starti-arrowI[maximumBin])/(1.0*len(data))
    return [angleToTarget,relativeVerticalFreeSpace]










def updateSpeed(motor,speed):
    BrickPi.MotorSpeed[motor] = speed
    BrickPiUpdateValues()
    time.sleep(.01)
    BrickPi.MotorSpeed[motor] = speed
    BrickPiUpdateValues()
    time.sleep(.01)
    BrickPi.MotorSpeed[motor] = speed
    BrickPiUpdateValues()
    time.sleep(.01)


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
BrickPi.Timeout=2000
BrickPiSetTimeout()


with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as output:
        camera.resolution = (320, 240)
        while True:
            updateSpeed(motor1,motorSpeed)
            updateSpeed(motor2,motorSpeed)
            camera.capture(output, 'rgb', use_video_port = True)
            target,vspace = determineAngleFromPicture(output.array)
            print(target,vspace)
            output.truncate(0)
            if target < 0:
                updateSpeed(steering,steeringSpeed)
            else:
                updateSpeed(steering,-steeringSpeed)
            



