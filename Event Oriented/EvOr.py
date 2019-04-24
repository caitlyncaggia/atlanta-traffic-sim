
# Title: Peachtree Corridor Traffic Simulator
#                   <Event-Oriented>
# Author: Blaine Costello
# Date:   April 23, 2019
#======================================================================================================================#
# Description:  The code within this file defines a data structure representing the positions of cars in a roadway for
# a given time window.
#
# Execution Instructions:  Open Python, Navigate to Containing Folder, Run 'EvOr.py'.
# Note: please ensure modules containing 'random' and 'math' are loaded before running.
#
# Default set to run 1000 cars through the simulated window with a time limit of 2000 seconds.
# ** No special environments or libraries were used here, everything was done from scratch with native tools. **

import random
import math

#---------------------------------------------------------------------------------------------------------------------#
                                        # Class & Function Definitions #
#---------------------------------------------------------------------------------------------------------------------#

def circ(v,mx):
    if v > mx:
        return v-mx
    elif v < 0:
        return v + mx

def carGen(N):
    tST = 0
    for i in range(1, N):
        # Determine Entry time (tSTART + interarrival time)
        tiArr = random.randint(6, 11)
        tST = tiArr + tST
        car = Car(i, tST)
        # Corr[car.intIN].carInRoad(car.timeIN, car1)   # Allow cars to enter stochastically from any cross-road.
        Corr[0].carInRoad(car.timeIN, car)



#---------------------------------------------------------------------------------------------------------------------#
                                            #  Event Definitions & FEL  #
#---------------------------------------------------------------------------------------------------------------------#


# Event class representing a single event.
class Event:
    def __init__(self, ts, cid, iid, mot):
        self.timestamp = ts
        self.carID = cid
        self.intID = iid
        self.motion = mot   # 0 = stop; 1 = straight, 2 = left, 3 = right

    def handler(self):          # returns timestamp of processed event.
        if self.motion == -1:
            # handle "light change" event - for debugging & verification
            # trigger each car waiting at light to begin passing.... REDUNDANT?
            #             * Deprecated *
            print(["Light Turns Green at", self.intID.ID])
            return self.timestamp
        else:
            if self.motion == 0:

                self.carID.waitDelay = self.intID.lane.index(self.carID) * 2 # 2 seconds extra per car in front of this car
                print(self.intID.nextGreen(self.timestamp))
                xtime = self.intID.nextGreen(self.timestamp)+self.carID.waitDelay
                print(["Car: ", self.carID.ID, " Stops at Intersection: ", self.intID.ID, " at time: ", self.timestamp])
                # Car stops at light: Create next event for this car
                # EVENT: car crosses intersection once light turns green and all other preceding cars have crossed.
                print(["Creating New Event for INT crossing @ xtime: ", xtime])

                self.carID.timeStopped += xtime+2 - self.timestamp
                print("time stopped at single light")
                print(xtime+2 - self.timestamp)
                print(self.carID.timeStopped)

                evnt = Event(xtime+2, self.carID, self.intID, 1)
                FEList.addEvent(evnt)   # Redundant? double event creation? Could do this here or in INTERSECTION class
                #FEList.printEv()
            elif self.motion == 1:
                # Car passes through the specifiedIntersection
                print(["Car: ", self.carID.ID, " Passes Intersection: ", self.intID.ID, " at time: ", self.timestamp])
                self.intID.carPass(self.timestamp, self.carID)
            else:
                self.intID.carOut()

#---------------------------------------------------------------------------------------------------------------------#

class FEL:
    # FEL is modeled as a queue of future events sorted by timestamp.
    def __init__(self, corr, endTime):
        self.events = []    # How do i implement a list of "Events"
        self.sorted = True
        self.endT = endTime
        self.time = 0
        self.numEv = 0
        self.numInts = 5   # Number of intersections in this simulation

        self.EVlog = []

        # Populate Event list with all light changes (Temporarily disabled: replacing these events with "nextGreen()")
        # for i in range(0, self.numInts):
        #     # Get all light changes for each intersection in the corridor
        #     cycT = corr[i].cycletime
        #     numGreens = round(endTime/cycT)
        #     for j in range(0, numGreens):
        #         tst = j*cycT
        #         self.events.append(Event(tst, -1, Corr[i], -1))
        #         self.numEv += 1
        #
        # # Sort the event list by event timestamp
        # self.sortFEL()



    def addEvent(self, evnt):   # Figure out more efficient way to add events to list in timestamp order
                                # Use binary search to find insert location...? (time permitting)
        self.events.append(evnt)
        self.numEv += 1
        self.sortFEL()
        # Add event to FEL, must ensure it is in proper timestamp order

    def subEvent(self, evnt):
        self.events.remove(evnt)
        # Remove event from FEL

    def sortFEL(self):
        self.events.sort(key=lambda x: x.timestamp)
        # sort FEL by timestamp (this function may be redundant)

    def printEv(self):
        # Print timestamp of all events in FEL
        print()
        print("Printing Future Event List: [Time, Motion, Intersection, Car]")
        print(["length: ", len(self.events)])
        for x in range(0, len(self.events)):
            print([self.events[x].timestamp, self.events[x].motion, self.events[x].intID.ID, self.events[x].carID.ID])
        print("----- End of FEL -----")
        print()

    def printLog(self):
        print()
        print("Printing Future Event List: [Time, Motion, Intersection, Car]")
        for x in range(0, len(self.EVlog)):
            print([self.EVlog[x].timestamp, self.EVlog[x].motion, self.EVlog[x].intID.ID])
        print("----- End of Log -----")
        print()

    def handleNext(self):  # execute next event in FEL and remove from Event list
        thisEv = self.events[0]
        self.EVlog.append(thisEv)
        print(['Handling Next Event: ', len(self.events)+1, len(self.EVlog)+1])
        thisEv.handler()

        print("Removing most recently processed Event")
        self.events.remove(thisEv)

        # self.numEv -= 1




#---------------------------------------------------------------------------------------------------------------------#
                                            #  Entities and Resources  #
#---------------------------------------------------------------------------------------------------------------------#

class Car:
    def __init__(self, id, tIN):
        self.ID = id
        self.intIN = 0          # Default to "straight
        self.intOUT = 4         # down peachtree" path
        self.timeIN = tIN
        self.timeOUT = -1       # time out is negative until this car exits the road.
        self.waitDelay = 1      # wait delay to be set when stopped, depends on how many cars are in front of this car.
        self.timeStopped = 0    # cumulative amount of time spent stopped at red lights or in gridlock
                                # (used to quantify traffic delay.)

#---------------------------------------------------------------------------------------------------------------------#

class Intersection:
    def __init__(self, id, mc):
        self.ID = id
        self.crossroad = 'unk'
        self.lane = []
        self.traffInc = 0    # Incoming traffic? (Number of cars on road, in motion...)
        self.numCarStop = 0

        # Flag to denote whether or not there is a functional light at this intersection.
        self.hasLight = True

        self.maxCars = mc
        self.blocked = False
        # Timing of each light, used to determine the next green light
        self.redtime = 10
        self.grntime = 10
        self.yeltime = 5
        # Timing of left turn lights (set green to zero if not needed.)
        self.lredtime = 1
        self.lgrntime = 0
        self.lyeltime = 0

        # timing constants for cars and lights
        self.cycletime = self.redtime + self.grntime + self.yeltime    # total time to cycle through all lights.
        self.ttimeA = 40        # traverse time with acceleration
        self.ttime = 20         # Traverse time without acceleration


    def ctReset(self):
        self.cycletime = self.redtime + self.grntime + self.yeltime    # total time to cycle through all lights.
        print(["Traffic light cycle-time has been reset for. ", self.ID])

    def carPass(self, Ctstmp, theCar):  # this timestamp is always chosen to be within the temporal bounds of green lights
        # Define function to handle car passing from this intersection to the next
        # remove car from front of lane
        if self.isGreen(Ctstmp):
            if len(self.lane) > 0:
                if(self.lane.__contains__(theCar)):
                    self.lane.remove(theCar)
                    self.numCarStop -= 1

                if self.ID == theCar.intOUT:
                    # Car leaves roadway and does not enter next
                    theCar.timeOUT = Ctstmp
                    OutDat.append(theCar)

                else:
                    # insert car into next roadway
                    # Creates new event using carInRoad() function
                    Corr[self.ID+1].carInRoad(Ctstmp, theCar)
                    print(["Roadway not empty: car ", theCar.ID, " passes intersection ", self.ID, "at time ", Ctstmp])

            else:
                print("No car in roadway, unable to pass to next intersection.")
        else:
            print("Light is not green, Car Cannot pass through light...")
            print("Create new event for car passing intersection on nextGreen")
            if len(self.lane) > 0:
                theCar = self.lane[0]
            else:
                # # Create instance of a car turning onto PT? (This section should NEVER Run)
                print("No cars in requested lane...")
                # idCount +=
                # theCar = Car(idCount, (self.nextGreen() + self.grntime))
            # Create delayed Event for passing through light (doublechecker for green lights)
            nxTime = self.nextGreen(Ctstmp)
            theCar.timeStopped += nxTime - Ctstmp  # Update stopped time variable
            ev = Event(nxTime, theCar, self, 0)
            FEList.addEvent(ev)

    def carOut(self, Ctstmp):       # Event
        print("CarOut")

        # Define function to handle car leaving queue (left or right turns)
        theCar = self.lane[0]
        self.lane.remove(theCar)
        self.numCarStop -= 1
        theCar.timeOUT = Ctstmp
        OutDat.append(theCar)

    # CREATES EVENT WHEN CARS ENTER ROADWAY
    def carInRoad(self, Ctstmp, theCar):
        print("CarInRoad Function")
        # if cars are stopped... (if light is not green/yellow)
        # Compute drive time to back of queue
        tstop = Ctstmp + self.ttime - len(self.lane)*2
        tpass = Ctstmp + self.ttime
        print(["tstop: ", tstop])
        # include car in the lane
        self.lane.append(theCar)   # Add car to the queue, compute time till this car passes intersection (use light timing)
        if self.isGreen(tpass):
            # continue through light
            print("Create Event: Light is Green, Pass Intersection ")
            evnt = Event(tpass, theCar, self, 1)   # Car crosses to next intersection road queue
        else:
            # stop in queue
            print("Create Event: Light is Red, car stops in queue.")
            print(["Time of Stop: ", tstop])
            evnt = Event(tstop, theCar, self, 0)                  # Car stops behind last car at current intersection
            theCar.waitDelay = 2*self.numCarStop
            #self.carInQueue(theCar)   Do this somewhere else... (create an event for car stopping behind other cars)

        print(["adding event to FEL: ", ])
        FEList.addEvent(evnt)



        self.traffInc += 1
        print("Car in Road Event Creation Complete...")
        #FEList.printEv()

        print()
        # Define function to handle car entering queue.
        # time to (back) position in queue decreases as more cars are in the road

        # will it pass intersection or will it stop at intersection?

    def carInQueue(self, theCar):
        pass
        # evnt = Event(self.nextGreen + theCar.waitDelay, theCar, self, 1)
        # FEList.addEvent
        # Redundant?


    def nextGreen(self,tstmp):
        # Outputs time of next green light - used to compute the light passing time for each car.

        numCyc = math.floor(tstmp / self.cycletime)
        return((numCyc+1)*self.cycletime)

    def isGreen(self,tstmp):
        if self.ID == 3:    # 13th is ALWAYS Green
            return True
        t = tstmp
        numCyc = math.floor(t / self.cycletime)
        # print( ((numCyc)*self.cycletime))
        # print(numCyc*self.cycletime - (self.redtime))
        if t > ((numCyc)*self.cycletime-1) and t < (numCyc*self.cycletime + (self.grntime)):
            return True
        else:
            return False




#---------------------------------------------------------------------------------------------------------------------#
                                                #  Simulation Code Body  #
#---------------------------------------------------------------------------------------------------------------------#


# Output data, cars are pushed to this every time they leave the corridor, this data is then saved for animations.
OutDat = []





Gtime = 0  # Global Time Variable

# Create Corridor Structure
tenth = Intersection(0,40)
elvth = Intersection(1,40)
twlth = Intersection(2,40)
thrth = Intersection(3,40)
ftnth = Intersection(4,40)



# Adjust signal timing for northbound simulation
tenth.redtime = 49.3
tenth.yeltime = 3.6
tenth.grntime = 34.7
tenth.ctReset()
tenth.ttime = 6
tenth.ttimeA = 9
print("cycletime at 10th")
print(tenth.cycletime)

elvth.redtime = 55.4
elvth.yeltime = 3.2
elvth.grntime = 41.5
elvth.ctReset()
elvth.ttime = 18
elvth.ttimeA = 27

twlth.redtime = 49.3
twlth.yeltime = 3.2
twlth.grntime = 60.4
twlth.ctReset()
twlth.ttime = 20
twlth.ttimeA = 25

# Special Case:  No light, so signal is dictated by whether or not any cars are in the roadway.
thrth.redtime = 0
thrth.yeltime = 0
thrth.grntime = 1
thrth.ctReset()
thrth.ttime = 16
thrth.ttimeA = 21

ftnth.redtime = 49.3
ftnth.yeltime = 3.6
ftnth.grntime = 34.7
ftnth.ctReset()
ftnth.ttime = 15
ftnth.ttimeA = 20


# Pack into rudimentary corridor structure
Corr = []
Corr.append(tenth)
Corr.append(elvth)
Corr.append(twlth)
Corr.append(thrth)
Corr.append(ftnth)

# Initialize future event list & other variables
FEList = FEL(Corr, 2000)   # Start Future event list to track the next 1000 seconds of events.
print("Is first light green at time of first car arrival?")
print(Corr[0].isGreen(40))
print()


# Create Test-Car object
# car1 = Car(id = 1, tIN = 20)  # Car with ID = 1 enters the corridor 25 seconds after simulation window begins
# car2 = Car(id = 2, tIN = 40)  # Car with ID = 1 enters the corridor 25 seconds after simulation window begins
# car3 = Car(id = 3, tIN = 60)  # Car with ID = 1 enters the corridor 25 seconds after simulation window begins
# idCount = 3

# insert car into roadway
entrance = Corr[0]

print("LOAD CAR ENTRY EVENTS")

# Corr[0].carInRoad(car1.timeIN, car1)
# Corr[0].carInRoad(car2.timeIN, car2)
#Corr[0].carInRoad(car3.timeIN, car3)

# print("Printing FEL Timestamps")
# FEList.printEv()

carGen(200)

print("======================================================================")
#print()
print("========================  SIMULATION BODY ============================")
#print()
term = 100000
c = 0
# Simulation Body Loop
while FEList.endT > Gtime and c < term and FEList.events:
    c += 1
    print("======================================================================")
    print()
    # Compute global time
    Gtime = FEList.events[0].timestamp# + (Gtime + 100)
    #print(['(GLOBAL) Event Timestamp: ',FEList.events[0].timestamp])
    #print(['(GLOBAL) length of Event List: ', len(FEList.events)])
    #print()
    FEList.handleNext()
    # increment global time
    print()
    print(["Global Gtime: ", Gtime])

    #print(len(FEList.events))

    print()

print("======================================================================")


# time stopped at light includes delay caused by preceding cars and "acceleration lag."
sumStp = 0
numCout = len(OutDat)
print(numCout)
for n in range(0, numCout):
    print(OutDat[n].timeStopped)
    sumStp += OutDat[n].timeStopped


aveStp = sumStp/n

print("Average cumulative time stopped at Lights")
print(aveStp)

# write output file
with open('output1.txt', 'w') as f:
    for itemi in OutDat:
        f.write("%s\n" % itemi)

    for itemj in FEList.EVlog:
        f.write("%s\n" % itemj)



