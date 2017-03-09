#FOR TESTING PURPOSES ONLY
import scipy.ndimage as image
import scipy.misc as misc
import time
from os import listdir

#Necessary imports
from math import atan2
from math import tan

RED = 0
GREEN = 1
BLUE = 2

#Parameters
THRESHOLD = 25
ANGLEBINSIZE = 1
CONTOURSAMPLEINTERVAL = 1



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
    for i in range(1,100):
        alpha = i/100.0
        colorPixel(data[int(round(x0+alpha*(x1-x0)))][int(round(y0+alpha*(y1-y0)))],255,255,255)





######
##
## Determine the Start Point
##
######
def isRed(pixel):
    if pixel[RED]>(pixel[GREEN]+THRESHOLD) and pixel[RED]>(pixel[BLUE]+THRESHOLD):
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
    while (starti>0) and isRed(data[starti-1][startj]):         #Make sure the StartPoint is on the border of the main Red region.
        starti -= 1
    return [starti,startj]

def determineStartPoint(data):              #The StartPoint is determined by searching for the first pixel that is in a Red region.
    centre = len(data[0])//2
    for i in range(1,len(data)-1,10):       #Start from the top row.
        for dj in range(0,centre-2,2):      #Search outwards from the centre.
            j = centre+dj
            if isInRedRegion(i,j,data):
                return correctStartPoint(data,i,j,centre)
            j = centre-dj
            if isInRedRegion(i,j,data):
                return correctStartPoint(data,i,j,centre)
    return [0,0]                            #We did not find a proper StartPoint. This return value results in a large steering angle, so that the car can turn around.





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

def angle(x0,y0,x1,y1):
    return int(round(atan2(y1-y0,x1-x0)*57.29578))

def angleToBin(angle):
    if (angle == 180):      #Fix for a problem that appears because of rounding in angle(). This is unavoidable if we want proper rounding in angle().
        angle = 179
    return int((angle+180)/ANGLEBINSIZE)





######
##
## Main method
##
#####
def determineAngleFromPicture(data):
    #Measurement containers
    numberOfBins = int(360/ANGLEBINSIZE)
    arrowLengths = [1999999999] * numberOfBins
    arrowI = [0] * numberOfBins
    arrowJ = [0] * numberOfBins

    #Initialization
    starti,startj = determineStartPoint(data)
    i = starti
    j = startj
    direction = 0
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
        if (i == starti and j == startj) or (steps>40*len(data)):
            break

        #Measure arrow length
        if steps%CONTOURSAMPLEINTERVAL == 0:
            binBin = angleToBin(angle(starti,startj,i,j))
            length = distance(starti,startj,i,j)
            if (arrowLengths[binBin]>length):
                arrowLengths[binBin] = length
                arrowI[binBin] = i
                arrowJ[binBin] = j

        #Determine direction
        if i<0 or j<0 or i>=len(data) or j>=len(data[0]):   #Outside the picture region. Pixel is Not-Red.
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

    #drawLine(data,0,len(data[0])//2,arrowI[maximumBin],arrowJ[maximumBin])      #FOR TESTING PURPOSES ONLY
    return angle(0,len(data[0])//2,arrowI[maximumBin],arrowJ[maximumBin])










######
##
## Process images for testing
##
#####
def convert_image(in_name, out_name):
    data = image.imread(in_name)
    start_time = time.clock()
    determineAngleFromPicture(data)
    print( time.clock() - start_time, "seconds")
    misc.imsave(out_name, data)

in_dir = './test_data/test1/'
out_dir = './result/'
all_items = listdir(in_dir)
index = 0
for item in all_items:
    out_name = out_dir + "sample_" + str(index) + ".png"
    in_name = in_dir + item
    convert_image(in_name, out_name)
    index += 1
