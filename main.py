#FOR TESTING PURPOSES ONLY
import mainBrickPi
import scipy.ndimage as image
import scipy.misc as misc
import time
from os import listdir

######
##
## Process images for testing
##
#####
def convert_image(in_name, out_name):
    data = image.imread(in_name)
    start_time = time.clock()
    angle,vertical,startj = mainBrickPi.determineAngleFromPicture(data)
    print( time.clock() - start_time, "seconds", angle, vertical,startj)
    misc.imsave(out_name, data)

in_dir = './test_data/test3/'
out_dir = './result/'
all_items = listdir(in_dir)
index = 0
for item in all_items:
    out_name = out_dir + "pic" + str(index) + ".png"
    if index<10:
        out_name = out_dir + "pic000" + str(index) + ".png"
    elif index<100:
        out_name = out_dir + "pic00" + str(index) + ".png"
    elif index<1000:
        out_name = out_dir + "pic0" + str(index) + ".png"
    in_name = in_dir + item
    convert_image(in_name, out_name)
    index += 1
