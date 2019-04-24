########################################################################################################################
# ECE 6730: Modeling and Simulation
# Project 2, Part 3: Activity Scanning
# Caitlyn Caggia
# April 23, 2019


import numpy as np
import time

########################################################################################################################
# CLASSES
########################################################################################################################
# Reusable classes specific to an activity scanning simulation of traffic modeling.

class activity:

    # Instance Attributes
    def __init__(self, name, startConditionName, startConditionValue, endConditionName, endConditionValue, ID):
        self.name = name
        self.startConditionName = startConditionName
        self.startConditionValue = startConditionValue
        self.endConditionName = endConditionName
        self.endConditionValue = endConditionValue
        self.ID = ID

    def startBehavior(self, activityList, activeV, vehicleList):
        return activityList, activeV, vehicleList

    def endBehavior(self, activityList):
        return activityList


class lightChange(activity):
    def startBehavior(self, activityList, activeVehList, vehicleList):
        intersectionNum = int(self.name[-1]) - 1
        intersectionList[intersectionNum].state = intersectionList[intersectionNum].getNextState()
        nextLightTime = round(intersectionList[intersectionNum].getDuration() / deltat)
        endTime = activityList[-1].endConditionValue
        newAct = activity(['lightChange' + str(intersectionNum + 1)], 'time', nextLightTime, 'time',
                          endTime, activityList[-1].ID + 1)
        activityList.append(newAct)
        return activityList, activeVehList, vehicleList


class addVehicle(activity):
    def startBehavior(self, activityList, activeVehList, vehicleList):
        activeVehList.append(vehicleList[self.ID])
        return activityList, activeVehList, vehicleList


class vehicle:

    # Instance Attributes
    def __init__(self, Vehicle_ID, Frame_ID, Tot_Frames, Epoch_ms, Local_X, Local_Y, Global_X, Global_Y, Veh_Len,
                 Veh_Wid, Veh_Class, Veh_Velocity, Veh_Accel, Lane_ID, Org_Zone, Dest_Zone, Intersection, Section,
                 Direction, Movement, Preceding_Veh, Following_Veh, Spacing, Headway, stoppedTime):
        self.Vehicle_ID = Vehicle_ID        # Vehicle identification number (cannot be 0)
        self.Frame_ID =  Frame_ID           # Frame identification number
        self.Tot_Frames = Tot_Frames        # Total number of frames car is in
        self.Epoch_ms = Epoch_ms            # Time since Jan 1, 1970 [ms]
        self.Local_X = Local_X              # Distance from median of Peachtree Street to front center of vehicle [feet]
        self.Local_Y = Local_Y              # Dist from southmost data point to front center of vehicle [feet]
        self.Global_X = Global_X            # X Coordinate of the front center of the vehicle [feet]
        self.Global_Y = Global_Y            # X Coordinate of the front center of the vehicle [feet]
        self.Veh_Len = Veh_Len              # Length of vehicle [feet]
        self.Veh_Wid = Veh_Wid              # Width of vehicle [feet]
        self.Veh_Class = Veh_Class          # Type of vehicle, 1: motorcycle, 2: car, 3: truck
        self.Veh_Velocity = Veh_Velocity    # Instantaneous velocity of vehicle [feet/sec]
        self.Veh_Accel = Veh_Accel          # Instantaneous acceleration of vehicle [feet/sec^2]
        self.Lane_ID = Lane_ID              # Lane identification number, starting from the left, 0 means not in a lane
        self.Org_Zone = Org_Zone            # Origin of vehicle
        self.Dest_Zone = Dest_Zone          # Destination of vehicle
        self.Intersection = Intersection    # Nearest intersection, 0 if not nearby
        self.Section = Section              # Current section, 0 if in an intersection
        self.Direction = Direction          # Direction, 4: Southbound
        self.Movement = Movement            # Vehicle's intended movement, TR: through, LT: left turn, RT: right turn
        self.Preceding_Veh = Preceding_Veh  # Vehicle ID of the vehicle immediately ahead of this vehicle, 0 if none
        self.Following_Veh = Following_Veh  # Vehicle ID of the vehicle immediately behind of this vehicle, 0 if none
        self.Spacing = Spacing              # Space headway [feet]
        self.Headway = Headway              # Time headway [sec]
        self.stoppedTime = stoppedTime      # Amount of time spent stopped while in transit

    def accelerate(self, delt):
        if self.Veh_Accel < 12.27:
            self.Veh_Accel += 1
        else:
            self.Veh_Accel = 12.27  # Max acceleration gathered from NGSIM dataset [ft/s^2]
        if self.Veh_Velocity < 56:
            # Based on NGSIM dataset, most cars don't speed more than 5 mph over
            self.Veh_Velocity += + delt * self.Veh_Accel

    def decelerate(self, delt):
        # Assume it takes an average car about 75 feet to go from 30 mph to a full stop
        self.Veh_Accel = (30 ^ 2) / (2 * 75)  # Kinematic equation for a 75 ft stopping distance from 30mph to 0 [ft/s]
        if self.Veh_Velocity >= 0:
            self.Veh_Velocity -= self.Veh_Accel * delt
        if self.Veh_Velocity < 0:
            self.Veh_Velocity = 0
        if self.Veh_Velocity < 1:
            self.stoppedTime += delt


class intersection:
    # Instance Attributes
    def __init__(self, ID, state, redDuration, yellowDuration, greenDuration, ypos, exits):
        self.ID = ID                                # Increases from south to north starting at 1
        self.state = state                          # Green, red, yellow
        self.redDuration = redDuration              # Amount of time light is red [sec]
        self.yellowDuration = yellowDuration        # Amount of time light is yellow [sec]
        self.greenDuration = greenDuration          # Amount of time light is green [sec]
        self.ypos = ypos                            # Southmost boundary of the intersection
        self.exits = exits                          # Destination zones associated with this intersection

    def getDuration(self):
        if self.state == 'green':
            nextLight = self.greenDuration
        elif self.state == 'yellow':
            nextLight = self.yellowDuration
        elif self.state == 'red':
            nextLight = self.redDuration
        else:
            nextLight = 'ERROR'
        return nextLight

    def getNextState(self):
        if self.state == 'green':
            nextState = 'yellow'
        elif self.state == 'yellow':
            nextState = 'red'
        elif self.state == 'red':
            nextState = 'green'
        else:
            nextState = 'ERROR'
        return nextState


########################################################################################################################
# GENERATE RANDOM PARAMETERS
########################################################################################################################
# Uses a blend of components of the NGSIM data set and randomization to determine key simulation parameters specific to
# Peachtree. If this model was applied to other datasets, this function would need to be modified.

def randomParams():

    # Timing Informtaion
    totalSimTime = 15*60  # Full time duration of simulation [seconds]
    trafficFlow = totalSimTime/1000  # Time duration between additional vehicles entering [seconds]
    deltat = 0.1  # [sec]
    totalFrames = round(totalSimTime/deltat)

    # Create list of starting y positions of sections with values pulled from NGSIM data
    sect1 = 0  # First bit of road [ft]
    sect2 = sect1 + 127.391 + 99.654  # Start from section 1, add length of section 2 and the first intersection, etc.
    sect3 = sect2 + 441.437 + 129.795
    sect4 = sect3 + 412.070 + 73.815
    sect5 = sect4 + 353.727 + 66.979
    sect6 = sect5 + 343.922 + 117.411
    sectionList = [sect1, sect2, sect3, sect4, sect5, sect6]

    # Create intersections, assume all start on green, with durations pulled from NGSIM data
    tenthSt = intersection(1, 'green', 49.3, 3.6, 34.7, sect1 + 127.391, [202, 223])
    eleventhSt = intersection(2, 'green', 55.4, 3.2, 41.5, sect2 + 441.437, [203, 222])
    twelfthSt = intersection(3, 'green', 35.7, 3.2, 60.9, sect3 + 412.070, [206, 221])
    thirteenthSt = intersection(4, 'green', 0, 0, totalFrames, sect4 + 353.727, [212]) # Treat stop sign as always green
    fourteenthSt = intersection(5, 'green', 46.1, 3.2, 34.6, sect5 + 343.922, [213, 215])
    intersectionList = [tenthSt, eleventhSt, twelfthSt, thirteenthSt, fourteenthSt]

    # Destinations
    rightTurnDests = [202, 203, 206, 212, 213]
    leftTurnDests = [223, 222, 221, 215]

    # Vehicle setup
    vehicleList = []
    allLeft = [0]
    allRight = [0]
    allStraight = [0]

    # Have vehicles enter at time interval specified by traffic flow at the southmost entry and choose a random exit
    numRandVehs = int(np.ceil(totalSimTime/trafficFlow * deltat))
    randVehArrival = np.linspace(0, totalFrames, numRandVehs)  # in frames
    id = 1

    for n in list(range(len(randVehArrival))):

        startFrame = round(n)

        # Randomly choose a destination. For simplicity, only include streets, not parking/etc.
        randNum = np.random.random()
        dest = 0
        if randNum < 0.1:
            dest = 202  # Turn right on 10th
        elif 0.1 < randNum <= 0.2:
            dest = 223  # Turn left on 10th
        elif 0.2 < randNum <= 0.3:
            dest = 203  # Turn right on 11th
        elif 0.3 < randNum <= 0.4:
            dest = 222  # Turn left on 11th
        elif 0.4 < randNum <= 0.5:
            dest = 206  # Turn right on 12th
        elif 0.5 < randNum <= 0.6:
            dest = 221  # Turn left on 12th
        elif 0.6 < randNum <= 0.7:
            dest = 212  # Turn right on 13th
        elif 0.7 < randNum <= 0.8:
            dest = 213  # Turn right on 14th
        elif 0.8 < randNum <= 0.9:
            dest = 215  # Turn left on 14th
        elif 0.9 < randNum <= 1.0:
            dest = 214  # Continue down Peachtree toward 15th

        # Try to avoid lane changes by keeping vehicles in left lane if they turn left, right lane if they turn right,
        # or center lane if they go straight.
        preceding = 0
        if dest in rightTurnDests:
            lane = 3
            preceding = allRight[-1]
            allRight.append(id)
        elif dest in leftTurnDests:
            lane = 1
            preceding = allLeft[-1]
            allLeft.append(id)
        else:
            lane = 2
            preceding = allStraight[-1]
            allStraight.append(id)

        # Update starting x value based on lane, assuming each lane is 10 feet wide
        xpos = 5 + (lane - 1) * 10

        veh = vehicle(id, startFrame, totalFrames - startFrame, xpos, 0, 0, 0, 0, 14, 7,
                      2, 10, 1, lane, 101, dest, 0, 1, 2, 1,
                      preceding, 0, 0, 0, 0)
        # ID, frame, totFrame, time, locx, locy, glox, gloy, len, width
        # class, velocity, accel, lane, org, dest, intersection, sect, dir, movement,
        # preceding, following, spacing, headway, stoppedTime

        vehicleList.append(veh)
        id += 1  # Give each vehicle a unique ID

    return intersectionList, sectionList, vehicleList, totalFrames, deltat


########################################################################################################################
# GENERATE SIMULATION
########################################################################################################################
# Run a new simulation based on training parameters and random values. This function should work regardless of the data
# set being used provided trainSim() is run prior to calling this function.

def generateSim(intersectionList, sectionList, vehicleList, totalFrames, deltat):
    # INPUTS
    # intersectionList: List of intersections and associated parameters from South to North
    # totalSimTime: Full time duration of simulation [seconds]
    # trafficFlow: Time duration between additional vehicles entering [seconds]
    # deltat: length of one frame [seconds]

    # INITIALIZATION
    # Time setup
    currentFrame = 0
    simTime = 0

    # Vehicle setup
    numVehicles = list(range(len(vehicleList)))
    activeV = []
    numActiveV = []
    updatedV = []
    numIntersections = list(range(len(intersectionList)))

    # Activity setup
    activityList = []

    # Generate list of activities given provided vehicle information
    for n in numVehicles:
        thisVeh = vehicleList[n]
        startTime = thisVeh.Frame_ID
        endTime = totalFrames
        newAct = addVehicle(['newVeh'+str(n+1)], 'time', startTime, 'time', endTime, n)
        activityList.append(newAct)

    # Set initial timers for stop lights
    for i in numIntersections:
        nextLightTime = round(intersectionList[i].getDuration()/deltat)  # Next light signal switch in frames
        endTime = totalFrames
        newAct = lightChange('lightChange' + str(i+1), 'time', nextLightTime, 'time', endTime, activityList[-1].ID+1)
        activityList.append(newAct)

    numActivities = list(range(len(activityList)))

    # RUN SIMULATION
    while currentFrame < totalFrames:

        # Check for B-type (bound) activities starting or ending triggered by time
        for a in numActivities:
            # Check if time matches current simulation time
            if ('time' in activityList[a].startConditionName) and activityList[a].startConditionValue == currentFrame:
                (activityList, activeV, vehicleList) = activityList[a].startBehavior(activityList, activeV, vehicleList)
            elif ('time' in activityList[a].endConditionName) and activityList[a].endConditionValue == currentFrame:
                activityList = activityList[a].endBehavior(activityList)
        # Update active simulation elements after B-type events
        numActiveV = list(range(len(activeV)))
        numActivities = list(range(len(activityList)))

        # Check for C-type (conditional) activities triggered by vehicle position
        removeV = []
        for v in numActiveV:

            # Update vehicle positions and spacing
            activeV[v].Local_Y += activeV[v].Veh_Velocity * deltat
            currentVelocity = activeV[v].Veh_Velocity
            preceding = activeV[v].Preceding_Veh
            if preceding == 0:
                activeV[v].Spacing = sectionList[-1]
            else:
                # activeV[v].Spacing = activeV[preceding].Local_Y - activeV[v].Local_Y
                activeV[v].Spacing = sectionList[-1]

            # Check if vehicle is approaching an intersection
            activeV[v].Intersection = 0
            for i in numIntersections:
                # If a vehicle is less than 75 feet (i.e., stopping distance at 30 mph) from an intersection, consider
                # it to be approaching that intersection.
                if (intersectionList[i].ypos - 75) < activeV[v].Local_Y < sectionList[i+1]:
                    activeV[v].Intersection = i+1
                    break

            if activeV[v].Intersection > 0:
                # If near an intersection, check the state of the intersection
                lightNum = activeV[v].Intersection
                thisIntersection = intersectionList[lightNum-1]
                lightState = thisIntersection.state
                if lightState == 'green':
                    # Check if vehicle is trying to turn at this intersection
                    if activeV[v].Dest_Zone in thisIntersection.exits:
                        removeV.append(v)
                    else:
                        # Otherwise vehicle is going straight
                        activeV[v].accelerate(deltat)
                elif lightState == 'yellow' or lightState == 'red':
                    activeV[v].decelerate(deltat)
            else:
                # Check for tailgating
                stopdist = activeV[v].Spacing
                speed = activeV[v].Veh_Velocity
                if (stopdist < 75 and speed > 30) or (stopdist < 40 and speed > 20) or (stopdist < 30 and speed > 10):
                    activeV[v].decelerate(deltat)
                else:
                    activeV[v].accelerate(deltat)
        # Update active simulation elements after C-type events
        for r in list(range(len(removeV))):
            updatedV.append(activeV[r])
            activeV.pop(r)
        removeV = []
        numActiveV = list(range(len(activeV)))
        numActivities = list(range(len(activityList)))

        # Update counters
        currentFrame += 1  # Increase simulation time by frame
        simTime += deltat  # Increase simulation time by time

    for u in list(range(len(activeV))):
        updatedV.append(activeV[u])

    # Calcualtions for output analysis
    avgStopTime = 0
    for j in list(range(len(updatedV))):
        avgStopTime += updatedV[j].stoppedTime
    avgStopTime = avgStopTime / len(updatedV)

    return simTime, len(numActiveV), len(vehicleList), avgStopTime


########################################################################################################################
# MEASURE ACTUAL PARAMETERS
########################################################################################################################
# Uses calculated and measured data from the NGSIM dataset to determine key simulation parameters specific to
# Peachtree. If this model was applied to other datasets, this function would need to be modified.

def actualParams():
    pass


########################################################################################################################
# COMPARE DATA
########################################################################################################################
# Train simulation based on data from Peachtree at noon, generate simulation to replicate a similar traffic flow, and
# compare simulated data to real data for V&V purposes.

if __name__ == '__main__':

    tic = time.time()

    (intersectionList, sectionList, vehicleList, totalSimTime, deltat) = randomParams()
    (simTime, activeVehicles, totalVehicles, avgStopTime) = generateSim(intersectionList, sectionList, vehicleList, totalSimTime, deltat)

    toc = time.time()

    print('Total Simulation Time: \t\t\t\t\t\t\t', simTime)
    print('Number of Vehicles Currently on Peachtree: \t\t', activeVehicles)
    print('Total Number of Vehicles to travel Peachtree: \t', totalVehicles)
    print('Average Amount of Time Stopped in Seconds: \t\t', avgStopTime)
    print('Elapsed Time in Seconds: ', toc-tic)










    
















