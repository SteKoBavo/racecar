from BrickPi import *
import picamera
import picamera.array
import time



def isRed(pixel):
    pixelRedMinusThreshold = pixel[0] - 50
    if pixelRedMinusThreshold>pixel[2] and pixelRedMinusThreshold>pixel[1]:
        return True
    else:
        return False

def isInRedRegion(i,j,data):
    if isRed(data[i][j]) and isRed(data[i][j-1]) and isRed(data[i][j+1]) and isRed(data[i+1][j]) and isRed(data[i-1][j]) and isRed(data[i-1][j-1]) and isRed(data[i-1][j+1]) and isRed(data[i+1][j-1]) and isRed(data[i+1][j-1]):
        return True
    else:
        return False

def searchHorizontalCentre(data,i,j):
    end = len(data[0])-1
    minj=j
    maxj=j
    row = data[i]
    while isRed(row[minj]) and (minj>0):
        minj-=1
    while isRed(row[maxj]) and (maxj<end):
        maxj+=1
    return (maxj+minj)//2

def centreOfRed(data):
    centre = len(data[0])//2
    for i in range(len(data)-5,1,-10):
        for dj in range(0,centre-2,5):
            j = centre+dj
            if isInRedRegion(i,j,data):
                return searchHorizontalCentre(data,i,j)
            j = centre-dj
            if isInRedRegion(i,j,data):
                return searchHorizontalCentre(data,i,j)
    centrepixel = data[len(data)//2][centre]
    if centrepixel[0]+centrepixel[1]+centrepixel[2] < 100:
        updateSpeed(motor1,0)
        updateSpeed(motor2,0)
    return 0



############################################################################

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
BrickPi.Timeout=3600000
BrickPiSetTimeout()

updateSpeed(motor1,motorSpeed)
updateSpeed(motor2,motorSpeed)
updateSpeed(motor1,motorSpeed)
updateSpeed(motor2,motorSpeed)
updateSpeed(motor1,motorSpeed)
updateSpeed(motor2,motorSpeed)
updateSpeed(motor1,motorSpeed)
updateSpeed(motor2,motorSpeed)
updateSpeed(motor1,motorSpeed)
updateSpeed(motor2,motorSpeed)

with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as output:
        camera.resolution = (320, 240)
        while True:
            camera.capture(output, 'rgb', use_video_port = True)
            if centreOfRed(output.array)>160:
                updateSpeed(steering,steeringSpeed)
            else:
                updateSpeed(steering,-steeringSpeed)
            output.truncate(0)







