#!/usr/bin/env python
# coding: utf-8

# In[49]:


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
        
        lane1_state = -np.ones(self.length, dtype=int)
        lane2_state = -np.ones(self.length, dtype=int)
        
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
        
        #single lane car movements in each lane now
        
        #lane 1
        for i in range(len(locs1)):
            loc = locs1[i]
            print((i+1) % len(locs1))
            print(locs1)
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
            
            
        #repeat for lane 2
        
    def display(self):
        print("Lane 1")
        print(self.lane1)
        print("Lane 2")
        print(self.lane2)


# In[50]:


PT = Peachtree_2lane()
t = 2
for i in range(t):
    PT.update()
    PT.display()


# In[ ]:




