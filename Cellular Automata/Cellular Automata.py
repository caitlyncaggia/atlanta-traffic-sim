import numpy as np
import random 
import matplotlib.pyplot as plt

class Peachtree_2lane:
    
    def __init__(self, length = 106, cars = 4):
        self.length = length #length of road, split Peachtree into cells of 15ft(average car length)
        self.cars = cars 
        
        #Some needed variables
        self.density = self.cars/(2*self.length);
        self.max_velocity = 5
        
        #Create 2 lane system & intersections
        self.lane1 = -np.ones(self.length, dtype=int)
        self.lane2 = -np.ones(self.length, dtype=int)
        self.int   = -np.ones(self.length, dtype=int)
        
        #Instantiating Four Cars
        self.lane1[1] = 2;
        self.lane1[7] = 2;
        self.lane2[2] = 2;
        self.lane2[5] = 2;
        
        #Adding Intersections to Lanes
        self.int[2] = -5; #10th
        self.int[30] = -5; #11th
        self.int[60] = -5; #12th
        self.int[90] = -7; #13th stop light
        self.int[100] = -5; #14th
        
    def update(self): 
        vmax = self.max_velocity
        
        #for single lane movement update
        lane1_update = -np.ones(self.length, dtype=int)
        lane2_update = -np.ones(self.length, dtype=int)
        
        #Subset1: Check exchange of vehicles between lanes, currently implementing symmetric, will change to stochastic
        
        #current car locations
        locs1 = np.transpose(np.nonzero(self.lane1 > -1))
        locs2 = np.transpose(np.nonzero(self.lane2 > -1))
        
        #Change from lane 1 to lane 2
        for i in range(len(locs1)):
            loc = locs1[i]
            next_loc = locs1[(i+1) % len(locs1)]    
            
            gap = next_loc - loc
            gapo = np.argmax(locs2>loc) - loc
            gapoback = loc - np.argmax(locs2>loc) - 1
            
            if gap%self.length-1 >= self.lane1[loc] + 1:
                break #gap < v+1 (T1)
                
            if self.lane2[loc] > -1 or gapo%self.length-1 <= self.lane1[loc] + 1:
                break #gapo > v+1 (T2)
                
            if gapoback%self.length-1 <= vmax:
                break #gapoback > vmax (T3) backwards causality
            
            #not implementing randomness yet
            
            #made it this far, then changing to lane 2
            self.lane2[loc] = self.lane1[loc]
            self.lane1[loc] = -1
            locs1 = np.delete(locs1,i);
            locs2 = np.insert(locs2,np.argmax(locs2 > i), i)
        
              
        #Repeat for Lane 2 to lane 1
        for i in range(len(locs2)):
            loc = locs2[i]
            next_loc = locs2[(i+1) % len(locs2)]    
            
            gap = next_loc - loc
            gapo = np.argmax(locs1>loc) - loc
            gapoback = loc - np.argmax(locs1>loc) - 1
            
            if gap%self.length-1 >= self.lane2[loc] + 1:
                break #gap < v+1 (T1)
                
            if self.lane1[loc] > -1 or gapo%self.length-1 <= self.lane2[loc] + 1:
                break #gapo > v+1 (T2)
                
            if gapoback%self.length-1 <= vmax:
                break #gapoback > vmax (T3) backwards causality
            
            #not implementing randomness yet
            
            #made it this far, then changing to lane 2
            self.lane1[loc] = self.lane2[loc]
            self.lane2[loc] = -1
            locs2 = np.delete(locs2,i);
            locs1 = np.insert(locs1,np.argmax(locs1 > i), i)
        
        #single lane car movements in each lane now
        
        #lane 1
        for i in range(len(locs1)):
            loc = locs1[i]
            next_loc = locs1[(i+1) % len(locs1)]  
            
            v = self.lane1[loc]
            
            next_int = np.argmax(self.int>loc)
            gap = next_loc - loc
            
            #add deceleration for intersections, needs to be more fleshed out
            if vmax <= next_int:
                v = v-1;
            
            if v < vmax and gap%self.length-1 > v:
                v = v+1 #(S1)
                
            if v > gap%self.length-1:
                v = gap%self.length-1 #(s2)
            
            #not including randomness yet
            lane1_update[loc+v] = v
            
        #repeat for lane 2
        for i in range(len(locs2)):
            loc = locs2[i]
            next_loc = locs2[(i+1) % len(locs2)]  
            
            v = self.lane2[loc]
            
            next_int = np.argmax(self.int>loc)
            gap = next_loc - loc
            
            #add deceleration for intersections, needs to be more fleshed out
            if vmax <= next_int:
                v = v-1;
            
            if v < vmax and gap%self.length-1 > v:
                v = v+1 #(S1)
                
            if v > gap%self.length-1:
                v = gap%self.length-1 #(s2)
            
            #not including randomness yet
            lane2_update[loc+v] = v
            
        self.lane1 = lane1_update
        self.lane2 = lane2_update
        
    def display(self):
        #print("Lane 1")
        #print(self.lane1)
        #print("Lane 2")
        #print(self.lane2)
        L1 = np.ones(self.length, dtype=int);
        L2 = np.ones(self.length, dtype=int);
        c1 = np.transpose(np.nonzero(L1 > -1))
        c2 = np.transpose(np.nonzero(L2 > -1))
        for i in range (len(c1)):
            if self.lane1[c1[i]] > -1:
                L1[c1[i]] = 0
        for i in range (len(c2)):
            if self.lane2[c2[i]] > -1:
                L2[c2[i]] = 0
        print("Lane 1")
        print(L1)
        print("Lane 2")
        print(L2)

PT = Peachtree_2lane()
PT.display()
t = 2
for i in range(t):
    print("Time step:", i)
    PT.update()
    PT.display()
