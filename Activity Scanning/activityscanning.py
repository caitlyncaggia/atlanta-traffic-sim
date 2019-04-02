#############################################################################################################################################################
# ECE 6730: Modeling and Simulation
# Project 2, Part 3: Activity Scanning
# Caitlyn Caggia
# April 1, 2019


import numpy as np

############################################################################################################################################################
# CLASSES
############################################################################################################################################################

class activity:

    # Instance Attributes
    def __init__(self, name, startConditionName, startConditionValue, endConditionName, endConditionValue, ID):
        self.name = name
        self.startConditionName = startConditionName
        self.startConditionValue = startConditionValue
        self.endConditionName = endConditionName
        self.endConditionValue = endConditionValue
        self.ID = ID

    def startBehavior(self):
        pass

    def endBehavior(self):
        pass


class vehicle:

    # Instance Attributes
    def __init__(self, Vehicle_ID, Frame_ID, Tot_Frames, Epoch_ms, Local_X, Local_Y, Global_X, Global_Y, Veh_Len, Veh_Wid, \
        Veh_Class, Veh_Velocity, Veh_Accel, Lane_ID, Org_Zone, Dest_Zone, Intersection, Section, Direction, Movement, \
        Preceding_Veh, Following_Veh, Spacing, Headway):
        self.Vehicle_ID = Vehicle_ID        # Vehicle identification number (cannot be 0)
        self.Frame_ID =  Frame_ID           # Frame identification number
        self.Tot_Frames = Tot_Frames        # Total number of frames car is in
        self.Epoch_ms = Epoch_ms            # Time since Jan 1, 1970 [ms]
        self.Local_X = Local_X              # Distance from median of Peachtree Street to front center of vehicle [feet]
        self.Local_Y = Local_Y              # Distance from starting southmost data point along Peachtree to front center of vehicle [feet]            
        self.Global_X = Global_X            # X Coordinate of the front center of the vehicle based on Georgia West State Plane in NAD83.M [feet]
        self.Global_Y = Global_Y            # X Coordinate of the front center of the vehicle based on Georgia West State Plane in NAD83.M [feet]         
        self.Veh_Len = Veh_Len              # Length of vehicle [feet]
        self.Veh_Wid = Veh_Wid              # Width of vehicle [feet]
        self.Veh_Class = Veh_Class          # Type of vehicle, 1: motorcycle, 2: car, 3: truck
        self.Veh_Velocity = Veh_Velocity    # Instantaneous velocity of vehicle [feet/sec]
        self.Veh_Accel = Veh_Accel          # Instantaneous acceleration of vehicle [feet/sec^2]
        self.Lane_ID = Lane_ID              # Lane identification number, starting from the left, 0 means not in a lane (turning/entering)
        self.Org_Zone = Org_Zone            # Origin of vehicle
        self.Dest_Zone = Dest_Zone          # Destination of vehicle
        self.Intersection = Intersection    # Indicates nearest intersection, starting from southmost intersection at 1, 0 if not nearby
        self.Section = Section              # Indicates current section, starting with southmost section as 1, 0 if in an intersection
        self.Direction = Direction          # Indicates direction, 1: Eastbound, 2: Northbound, 3: Westbound, 4: Southbound
        self.Movement = Movement            # Indicates vehicle's intended movement, TR: through, LT: left turn, RT: right turn
        self.Preceding_Veh = Preceding_Veh  # Vehicle ID of the vehicle immediately ahead of this vehicle, 0 if none
        self.Following_Veh = Following_Veh  # Vehicle ID of the vehicle immediately behind of this vehicle, 0 if none
        self.Spacing = Spacing              # Space headway [feet]
        self.Headway = Headway              # Time headway [sec]

    def stop(self):
        # Add more sophisticated code later to smooth deceleration
        self.Veh_Velocity = 0
        self.Veh_Accel = 0

    def go(self):
        # Add more sopsticated code later to smooth acceleration
        self.Veh_Velocity = 10
        self.Veh_Accel = 1


class intersection:
    # Instance Attributes
    def __init__(self, ID, state, redDuration, yellowDuration, greenDuration, ypos): 
        self.ID = ID                                # increases from south to north starting at 1
        self.state = state                          # green, red, yellow
        self.redDuration = redDuration*10*60        # amount of time light is red, in frames
        self.yellowDuration = yellowDuration*10*60  # amount of time light is yellow, in frames
        self.greenDuration = greenDuration*10*60    # amount of time light is green, in frames
        self.ypos = ypos                            # southmost boundary of the intersection


############################################################################################################################################################
# INITALIZATION
############################################################################################################################################################

# Simulation time
simTime = 0
endSimTime = 15*60*60*1000 # 15 min in ms
deltat = 0.1 # Length of one frame

# Use frames instead of time to avoid floating point arithmetic errors
currentFrame = 0
totalFrames = 10*60*15 # Each frame is 0.1 sec, 15 minutes of data

# List of active activities and vehicles
activityList = []
numActivities = 0
vehiclesList = []
numVehicles = 0

# Randomization
vehicleArrivalInterval = 1*1000 # 1 sec in ms, controlls traffic. Later, this will create events of vehicles entering Peachtree

# Create intersections, assume all start on green, with durations pulled from NGSIM data
tenthSt = intersection(1, 'green', 49.3, 3.6, 34.7, 20)
eleventhSt = intersection(2, 'green', 55.4, 3.2, 41.5, 40)
twelfthSt = intersection(3, 'green', 35.7, 3.2, 60.9, 60)
# for now, treat 13th as always a green light
fourteenthSt = intersection(4, 'green', 46.1, 3.2, 34.6, 80)
intersectionList = [tenthSt, eleventhSt, twelfthSt, fourteenthSt]

# Create test vehicles
veh1 = vehicle(1, 1, 10*60*15, 0, 0, 0, 0, 0, 14, 7, # ID, frame, totFrame, time, locx, locy, glox, gloy, len, width
        2, 10, 1, 1, 102, 214, 1, 0, 2, 1,           # class, velocity, accel, lane, org, dest, intersection, sect, dir, movement
        0, 0, 0, 0)                                  # preceding, following, spacing, headway
veh2 = vehicle(2, 1, 10*60*15, 0, 0, 0, 0, 0, 14, 7, 
        2, 5, 1, 2, 102, 214, 1, 0, 2, 1, 
        1, 0, 0, 0)

vehicleList = [veh1, veh2]
print('Vehicle List: ', (list(range(len(vehicleList)))))

############################################################################################################################################################
# RUN SIMULATION
############################################################################################################################################################

while currentFrame < totalFrames:

    # Check for B-type (bound) activities starting or ending
    for i in list(range(len(activityList))):
        # Check if time matches current simulation time     
        if activityList[i].startConditionName == 'time' and (activityList[i].startConditionValue*10*60) == currentFrame:
                activityList[i].startBehavior()
        elif activityList[i].endConditionName == 'time' and (activityList[i].endConditionValue*10*60) == currentFrame:
                activityList[i].endBehavior()   

    # Check for C-type (conditional) activities
    for j in list(range(len(vehicleList))):
        
        # Update vehicle positions
        vehicleList[j].Local_Y += round(vehicleList[j].Veh_Velocity * deltat)
        for k in list(range(len(intersectionList))):
            if vehicleList[j].Local_Y == intersectionList[k].ypos:
                vehicleList[j].Intersection = k

        # Check if position is approaching/already in intersection
        if vehicleList[j].Intersection != 0:
            # If near an intersection, check the state of the intersection
            if intersectionList[vehicleList[j].Intersection].state == 'green':
                pass
                # More sophisticated code here to determine turns later, for now let vehicle keep going
            elif intersectionList[vehicleList[j].Intersection].state == 'yellow':
                pass 
                # Add more code here later to handle if a car should stop or accelerate
            elif intersectionList[vehicleList[j].Intersection].state == 'red':
                vehicleList[j].stop()
        else:
            # If in a section, add additional conditional to check for tailgating
            pass
            

    # Increment simulation time (or current frame)
    currentFrame += 1
    simTime += deltat

print('Total Frames: ', totalFrames)
print('Current Frame: ', currentFrame)
print('Final Intersection of Vehicle 1: ', veh1.Intersection)
print('Final Section of Vehicle 1: ', veh1.Section)
print('Final Intersection of Vehicle 2: ', veh2.Intersection)
print('Final Section of Vehicle 2: ', veh2.Section)






    
















