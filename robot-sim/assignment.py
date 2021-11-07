from __future__ import print_function
import time
from sr.robot import *

R = Robot()
""" instance of the class Robot"""

def drive(speed, seconds):
    """
    Function for setting a linear velocity

    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed, seconds):
    """
    Function for setting an angular velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

#threshold that indicates we are close enough to grab a box
grab_distance = 0.4

#threshold that indicates we are aligned with a box
grab_angle = 5

def control_silver():
    """
    Function for checking if there is a silver box near in front.
    If yes, the robot aligns to it and goes to put it behind.
    """
    for m in R.see():
        if m.info.marker_type is MARKER_TOKEN_SILVER and m.dist < 1.2 and abs(m.rot_y)<90:
            print("I've seen a silver box!")
            align_with_silver()
            put_silver_behind()
            return

def align_with_silver():
    """
    Function to align with the silver box.
    If it's well aligned it returns, otherwise he turn left/right (recursively check if
    until it's well aligned).
    """
    for m in R.see():
        if m.info.marker_type is MARKER_TOKEN_SILVER and m.dist < 1.2 and abs(m.rot_y)<90:

            #if it's well aligned, returns
            if abs(m.rot_y) <= grab_angle:   
                print("I'm aligned!")
                return

            #if it's not aligned, he turns a little bit right/left and checks again
            else:
                if m.rot_y < 0: 
                    print("Left a bit...")
                    turn(-2, 0.5)
									
                if m.rot_y > 0:
                    print("Right a bit...")
                    turn(+2, 0.5)
                return align_with_silver()

def put_silver_behind():
    """
    Function to put the (aligned) silver box behind.
    If it's close enough, he grabs it and releases it behind,
    else he get closer (recursively check if it's close enough).
    """
    for m in R.see():
        if m.info.marker_type is MARKER_TOKEN_SILVER and m.dist < 1.2:
            
            #if it's close enough, grab it and put it behind, then turn again.
            if m.dist <= grab_distance:
                
                #if he fails to grab, he takes a step back and retry
                if (R.grab() == False):
                    print("Failed to grab! I will retry")
                    if m.rot_y > 0:
                        turn(-2, 0.5)
                    else:
                        turn(2, 0.5)
                    drive(-30,1)
                    return control_silver()

                #this is to choose the turning direction to release it
                #so we don't hit golden boxes and we keep silvers in the centre
                if choose_direction():
                    right = -1
                else:
                    right = 1
                turn(right*16,4)
                drive(10,0.5)
                R.release()
                drive(-20,1)
                turn(-right*16,4)
                return

            # if it's not close enough, he gets closer
            else:
                print("Not close enough..")
                drive(100,0.05)
                return put_silver_behind()
        


def control_gold():
    """
    Function for checking if there are golden boxes near.
    If yes, the robot (recursively) turn right/left until there is no risk to hit them.
    First if checks if the golden box is at a critical angle(<|30|), we call choose_direction() function
    to decide at which direction is better to turn.

    """
    for m in R.see():
        if m.info.marker_type is MARKER_TOKEN_GOLD:

            #Critical angle!
            if abs(m.rot_y)<30 and m.dist<0.9:
                if choose_direction():
                    print("Golden box in front! Better turn left")
                    turn(-10, 0.5)
                else:
                    print("Golden box in front! Better turn right")
                    turn(10, 0.5)
                return control_gold()
            
            #it's close, turn a bit
            elif abs(m.rot_y)<70 and m.dist<0.7:
                print("Golden box near!")
                if m.rot_y > 0:
                    turn(-6, 0.5)
                else:
                    turn(6, 0.5)
                return control_gold()
            

				
def choose_direction():
    """
    Function for choose the better direction to turn(right/left).
    We count the golden box at the right and at the left, choosing the direction where
    there are less.
    The counting is weighted propoctionally to the distance(more near = more weight).

    RETURN:
    True -> more boxes at right
    False -> more boxes at left
    """
    left = right = 0
    for m in R.see():
        if m.info.marker_type is MARKER_TOKEN_GOLD:

            if 30 < abs(m.rot_y)<120:

                #major weight
                if m.dist<0.6:
                    if m.rot_y >0:
                        right += 3
                    else:
                        left += 3

                #medium weight
                elif m.dist < 1:
                    if m.rot_y >0:
                        right += 2
                    else:
                        left += 2

                #minor weight
                elif m.dist < 1.4:
                    if m.rot_y > 0:
                        right +=1
                    else:
                        left += 1   

    if right > left:
        return True
    else:
        #this includes the worst case right = false, but I never found it
        return False


"""
Main code:

First of all he checks if he's gonna hit a golden box and rotate until there is no risk,
then he checks if there are silver box to grab in front,
at the end of those checks he goes forward.

"""
while 1:
    control_gold()				  
    control_silver()
    drive(100,0.1)

