import numpy as np

# define quick function to handle periodic time calculations for easier light cycling
def circ(v,mx):
    if v > mx:
        return v-mx
    elif v < 0:
        return v + mx

# Define Car Class
class Car:
    def __init__(self, iD, aggr, spd, path):
        self.id = iD       # Car ID
        self.speed = spd    # is the car 1) driving? or 0) stopped?
        self.aggr = aggr    # is the car aggressive?  (inc. likelihood of passing other cars)
        self.lane = 0       # which lane is the car in? from left to right
        self.navig = path    # list of maneuvers corresponding to each intersection - describes the path of travel
        self.timeTo = 10*iD  # time to next event (first event is entry to corridor)
        self.Intersection = Tenth # by default, first intersection is tenth.. this will change

    # Define event: Pass Light
    def evnt(self, evID):
        if evID == 1:  # car moves from one intersection to the next
            self.passLight(self.Intersection, peachtreeCor)
        elif evID == 2:     # car stops at stop light
            self.stopLight(self.Intersection, peachtreeCor)
        elif evID == 3:     # car turns right
            self.turnRight(self.Intersection, peachtreeCor)
        elif evID == 4:     # car turns left
            self.turnLeft(self.Intersection, peachtreeCor)
        else:               # others?
            print("unidentified Event ID")

    def passLight(self, intersection, corridor):
        # first move car from old queue to new queue
            intersection.carOut(self)
            corridor.roadOrder[corridor.roadOrder.index(intersection) + 1].carIn(self)
        # compute time to stop at next light (maxCars - numCars
            tnext = corridor.roadOrder[corridor.roadOrder.index(intersection) + 1].numCars
            return tnext
    def stopLight(self, intersection, corridor):
            tnext = intersection.numCars
            return tnext

    def turnRight(self, intersection, corridor):
        return False
# not developed yet

    def turnLeft(self, intersection, corridor):
        return False
# not developed yet


# Define Intersection class
#    Represents the flow of traffic into an intersection coming from four directions.
#    uses queues to model cars in roadways
class Intersection:
    def __init__(self, rdCap, lights, ltTimes):
        self.light_init = lights  # initial state of lights for turning and through traffic
        self.light_state = self.light_init
        self.light_times = ltTimes                      # light times for the through lights only...
                                                        # add another variable for left turn lights
        self.roadway = []   # Northbound
        self.roadWb = []    # Westbound
        self.roadSb = []    # Southbound
        self.roadEb = []    # Eastbound
        self.numCars = 0
        self.length = rdCap *0.54
        self.maxCars = rdCap   # max number of cars allowed on the road before clogging.
                               # This value is related to  length of the road segment and travel time.
        self.roadBlocked = 0   # if the queue is full of cars, the road is blocked



    def carIn(self, car):
        # only support for northbound roadway currently
        self.roadway.append(car)
        self.numCars += 1

    def carOut(self, car):
        self.roadway.remove(car)

    def isGreen(self, tElap):
        if circ(tElap, 50) > 30:
            return True
        else:
            return False

    def isclogged(self):
        if self.numCars > self.maxCars:
            return True
        else:
            return False

    def printRoad(self):
        for x in range(1, self.maxCars):
            if x < self.numCars:
                print("{}".format(self.roadway[x-1].id))
            else:
                print(0)


# Representation of entire corridor made up of several roads in a specific order.
#   handles passing of cars from one road to the next through intersections
#   Stores and outputs relevant data
# runs entire time window of simulation, and stores data for each car's location and state in each time-frame.
# Extremely high level of abstraction in this model...



# Initialize light times array for each intersection directions N,W,S,E in that order
lT10 = np.array([[5, 5, 5, 5, 5, 5], [5, 5, 5, 5, 5, 5], [5, 5, 5, 5, 5, 5], [5, 5, 5, 5, 5, 5]])
lT11 = np.array([[5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5]])
lT12 = np.array([[5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5]])
lT14 = np.array([[5, 5, 5, 5, 5, 5], [5, 5, 5, 5, 5, 5], [5, 5, 5, 5, 5, 5], [5, 5, 5, 5, 5, 5]])

ltIni1 = np.array([[0, 0, 1], [1, 0, 0]])
ltIni2 = np.array([[0, 0, 0], [1, 0, 0]])
ltIni3 = np.array([[0, 0, 0], [1, 0, 0]])
ltIni4 = np.array([[0, 0, 1], [1, 0, 0]])
ltIni5 = np.array([[0, 0, 1], [1, 0, 0]])

# Initialize Intersections in Specified Corridor
Tenth = Intersection(30, ltIni1, lT10)
Elvth = Intersection(20, ltIni2, lT11)
Twlth = Intersection(40, ltIni3, lT12)
Thrtn = Intersection(30, ltIni4, lT10)                 # Through traffic, always green, Thirteenth street YIELDS to oncoming traffic
                                                       # (if roadway is clear (numcars == 0), cars can enter from thirteenth, otherwise, stop.)
Ftnth = Intersection(40, ltIni5, lT14)

#  Path defines events at each intersection - these define the car's path
#  1) go straight        2) turn right               3) turn left        0) not in corridor
path1 = np.array([1,1,1,1,1])     # car goes straight through corridor
path2 = np.array([1,1,2,0,0])     # car goes down two blocks then takes a right on twelfth street
path3 = np.array([1,1,1,1,3])     # car goes straight down corridor and turns left on 14th
path4 = np.array([0,0,0,2,1])     # car enters corridor on 13th and continues north

# Generate dummy cars to test corridor
c1 = Car(1,0,1,path1)
c2 = Car(2,0,1,path1)
c3 = Car(3,0,1,path1)
c4 = Car(4,0,1,path1)


# test of basic functionality of intersection class
r1 = Intersection(5, ltIni1, lT10)

r1.carIn(c1)
r1.carIn(c2)
r1.carIn(c3)
r1.carIn(c4)

r1.carOut(c2)

r1.printRoad()


print(Tenth.numCars)

# Model Corridor
class Corridor:
    def __init__(self):
        self.roadOrder = []
        self.roadOrder.append(Tenth)
        self.roadOrder.append(Elvth)
        self.roadOrder.append(Twlth)
        self.roadOrder.append(Thrtn)
        self.roadOrder.append(Ftnth)

peachtreeCor = Corridor()

