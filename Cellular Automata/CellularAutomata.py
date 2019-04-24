#To use just change the time steps in the third to last line and run.


import numpy as np
import random 
import time


# In[173]:


class Peachtree:
    def __init__(self, t):
        self.t = t
        
        self.interarrival = 23
        self.Int1 = Peachtree10_11()
        self.Int2 = Peachtree11_12()
        self.Int3 = Peachtree12_13()
        self.Int4 = Peachtree13_14()
        
    def update(self):
        start = time.time()
        for t in range(self.t):
            if t%self.interarrival == 0:
#                 print(t)
                cars_out1 = self.Int1.update(t, np.array([np.round(random.random()/2).astype(int)+1, 0, (random.random()*5)]))
#                 print([np.round(random.random()/2).astype(int)+1, 0, (random.random()*5)])
            else:
                cars_out1 = self.Int1.update(t, np.array([0,0,0]))
            cars_out2 = self.Int2.update(t, cars_out1)
            cars_out3 = self.Int3.update(t, cars_out2)
            self.Int4.update(t, cars_out3)
            cars_out1 = np.empty((3,1), dtype=int)
            cars_out2 = np.empty((3,1), dtype=int)    
            cars_out3 = np.empty((3,1), dtype=int)
            
        print(time.time()-start)

    
        


# In[174]:


class Peachtree10_11:
    #Two Lanes, Straight Traffic with no left turn
    
    def __init__(self):
        self.length = np.round(404/16).astype(int) #length of road, split Peachtree into cells of 16ft(average car length)
        
        #Some needed variables
#         self.density = self.cars/(2*self.length);
        self.max_velocity = 50
        
        #Add traffic light timings
        self.g = 41.5
        self.y = 3.5 + self.g
        self.r = 55.5 + self.y
        self.lt = 100.5
        
        #Create 2 lane system & intersections
        self.lane1 = -np.ones(self.length, dtype=int)
        self.lane2 = -np.ones(self.length, dtype=int)
        
        self.lane1[0] = 25
        self.lane2[0] = 30
#         print((self.lane1>-1).sum() + (self.lane2>-1).sum())
#         print(self.lane1)
#         print(self.lane2)
#         print("update")
        
    def update(self, t, cars_in): 
        vmax = self.max_velocity
        cars_out = np.array([0,1,1]) # [lane#, loc, speed]
        c = 0 #count of cars exiting intersection
#         print(cars_in)
        #add cars from previous intersection
        if cars_in.ndim > 0:
            if cars_in[0] == 1:
                self.lane1[int(cars_in[1])] = cars_in[2]
            elif cars_in[0] == 2:
                self.lane2[int(cars_in[1])] = cars_in[2]
                    
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
            if i == len(locs1)-1:
                next_loc = loc
            else:
                next_loc = locs1[i+1]    
            
            gap = next_loc - loc
            if len(locs2) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs2>loc) - loc
                gapoback = loc - np.argmax(locs2>loc) - 1
            
            if gap >= self.lane1[loc] + 3:
                break #gap < l (T1)
                
            if self.lane2[loc] > -1 or gapo <= self.lane1[loc] + 3:
                break #gapo > l0 (T2)
                
            if gapoback-1 <= 30:
                break #gapoback > loback (T3) backwards causality
            
            if  random.random() >.4:
                break #randomness (T4)
                
#             print("lane1to2")
            #made it this far, then changing to lane 2
            self.lane2[loc] = self.lane1[loc]
            self.lane1[loc] = -1
            locs1 = np.delete(locs1,i);
            locs2 = np.insert(locs2,np.argmax(locs2 > i), i)
        
              
        #Repeat for Lane 2 to lane 1
        for i in range(len(locs2)):
            loc = locs2[i]
            if i == len(locs2)-1:
                next_loc = loc
            else:
                next_loc = locs2[i+1]    
            
            gap = next_loc - loc
            if len(locs1) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs1>loc) - loc
                gapoback = loc - np.argmax(locs1>loc) - 1
            
            if gap >= self.lane2[loc] + 3:
                break #gap < l (T1)
                
            if self.lane1[loc] > -1 or gapo <= self.lane2[loc] + 3:
                break #gapo > l0 (T2)
                
            if gapoback-1 <= 30:
                break #gapoback > loback (T3) backwards causality
                
            if  random.random() >.4:
                break #randomness (T4)
                
#             print("lane2to1")
            #made it this far, then changing to lane 2
            self.lane1[loc] = self.lane2[loc]
            self.lane2[loc] = -1
            locs2 = np.delete(locs2,i);
            locs1 = np.insert(locs1,np.argmax(locs1 > i), i)
        
        #single lane car movements in each lane now
        
        #lane 1
        for i in range(len(locs1)):
            loc = locs1[i]
            if i == len(locs1)-1:
                next_loc = self.length-1
            else:
                next_loc = locs1[i+1]  
            
            v = self.lane1[loc]
            
            gap = next_loc - loc
            
            #add traffic signal changes  for intersections,
            signal = (t*.5) % self.lt
            if signal >= self.y and signal < self.r-1 and loc >= self.length-4: #in yellow light slow down phase
                if v > 15:
                    v = v-10
#                     print("yellow slow")
            if signal >= self.r-1 and loc >= self.length-4: #in red light stop phase
                if v > 15:
                    v = v/3 
#                     print("red stop")
                else:
                    v = 0
#                     print("red stop")
            if signal < self.g and v < 15 and loc >= self.length-4:
                v = v + 5
#                 print("speed up after red")
            else:
                if v < vmax and gap > v:
                    v = v+3 #(S1)
#                     print("speed up")

                if v > gap:
                    v = gap-1 #(s2)
#                     print(gap, "slow down")

                if v > 0 and random.random() < .4:
                    v = v-2; #(S3)
#                     print("random slow")
                    
            if loc+v < self.length:
                lane1_update[loc+v] = v
#                 print("new pos", loc+v)
            else:
                if c == 0:
                    cars_out = np.array([1, loc+v-self.length+1, v])
                else:
                    cars_out= np.vstack((cars_out,[1, loc+v-self.length+1, v])) 
                c= c+1
#                 print("exit")
            
            
        #repeat for lane 2
        for i in range(len(locs2)):
            loc = locs2[i]
            if i == len(locs2)-1:
                next_loc = self.length-1
            else:
                next_loc = locs2[i+1] 
            
            v = self.lane2[loc]
            gap = next_loc - loc
            
             #add traffic signal changes  for intersections,
            signal = (t*.5) % self.lt
            if signal >= self.y and signal < self.r-1 and loc >= self.length-4: #in yellow light slow down phase
                if v > 15:
                    v = v-10
#                     print("yellow slow")
            if signal >= self.r-1 and loc >= self.length-4: #in red light stop phase
                if v > 15:
                    v = v/3 
#                     print("red stop")
                else:
                    v = 0
#                     print("red stop")
            if signal < self.g and v < 15 and loc >= self.length-4:
                v = v + 5
#                 print("speed up after red")
            else:
                if v < vmax and gap > v:
                    v = v+3 #(S1)
#                     print("speed up")

                if v > gap:
                    v = gap-1 #(s2)
#                     print(gap, "slow down")

                if v > 0 and random.random() < .4:
                    v = v-2; #(S3)
#                     print("random slow")
                
            if loc+v < self.length:
                lane2_update[loc+v] = v
#                 print("new pos", loc+v)
            else:
                if c == 0:
                    cars_out = np.array([2, loc+v-self.length+1, v])
                else:
                    cars_out= np.vstack((cars_out,[2, loc+v-self.length+1, v])) 
                c = c+1
#                 print("exit")
            
        self.lane1 = lane1_update
        self.lane2 = lane2_update
#         plt.plot(t,(self.lane1>-1).sum() + (self.lane2>-1).sum())
#         print("carsleft1", (self.lane1>-1).sum() + (self.lane2>-1).sum())
#         print(self.lane1)
#         print(self.lane2)
        return(cars_out)


# In[175]:


class Peachtree11_12:
    #Two Lanes with Third left turn lane mid way
    
    def __init__(self):
        self.length = np.round(399/16).astype(int) #length of road, split Peachtree into cells of 16ft(average car length)
        self.length2 = np.round(264/16).astype(int)
        
        #Some needed variables
#         self.density = self.cars/(2*self.length);
        self.max_velocity = 50
        
        #Add traffic light timings
        self.g = 60
        self.y = 3.5 + self.g
        self.r = 35.5 + self.y
        self.lt = 99
        
        #Create 2 lane system & intersections
        self.lane1 = -np.ones(self.length, dtype=int)
        self.lane2 = -np.ones(self.length, dtype=int)
        self.lane3 = -np.ones(self.length, dtype=int) #Left turn only lane
        
        #Adding Cars
        
    def update(self, t, cars_in): 
        vmax = self.max_velocity
        cars_out = np.array([0,1,1]) # [lane#, loc, speed]
        c = 0 #count of cars exiting intersection
        
        #add cars from previous intersection
#         print("size", cars_in.shape)
#         print(cars_in)
        for i in range(len(cars_in)):
            if cars_in.ndim == 1:
                if cars_in[0] == 1:
                    self.lane1[cars_in[1]] = cars_in[2]
                elif cars_in[0] == 2:
                    self.lane2[cars_in[1]] = cars_in[2]
            elif cars_in.ndim > 1:
                if cars_in[i][0] == 1:
                    self.lane1[cars_in[i][1]] = cars_in[i][2]
                elif cars_in[i][0] == 2:
                    self.lane2[cars_in[i][1]] = cars_in[i][2]
        
        #for single lane movement update
        lane1_update = -np.ones(self.length, dtype=int)
        lane2_update = -np.ones(self.length, dtype=int)
        lane3_update = -np.ones(self.length, dtype=int)
        
        #Subset1: Check exchange of vehicles between lanes, currently implementing symmetric, will change to stochastic
        
        #current car locations
        locs1 = np.transpose(np.nonzero(self.lane1 > -1))
        locs2 = np.transpose(np.nonzero(self.lane2 > -1))
        locs3 = np.transpose(np.nonzero(self.lane3 > -1))
        
        #Change from lane 1 to lane 2
        for i in range(len(locs1)):
            loc = locs1[i]
            if i == len(locs1)-1:
                next_loc = loc
            else:
                next_loc = locs1[i+1]     
            
            gap = next_loc - loc
            if len(locs2) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs2>loc) - loc
                gapoback = loc - np.argmax(locs2>loc) - 1
            
            if gap >= self.lane1[loc] + 3:
                break #gap < l (T1)
                
            if self.lane2[loc] > -1 or gapo <= self.lane1[loc] + 3:
                break #gapo > l0 (T2)
                
            if gapoback-2 <= 30:
                break #gapoback > vmax (T3) backwards causality
            
            if  random.random() >.4:
                break #randomness (T4)
#             print("lane1to2")
            #made it this far, then changing to lane 2
            self.lane2[loc] = self.lane1[loc]
            self.lane1[loc] = -1
            locs1 = np.delete(locs1,i);
            locs2 = np.insert(locs2,np.argmax(locs2 > i), i)
            
        #Change from lane 1 to lane 3
        for i in range(len(locs1)):
            loc = locs1[i]
            if loc >= self.length2:
                if i == len(locs1)-1:
                    next_loc = loc
                else:
                    next_loc = locs1[i+1]     

                gap = next_loc - loc
                if len(locs3) == 0:
                    gapo = self.length - 1 - loc
                    gapoback = loc 
                else:
                    gapo = np.argmax(locs3>loc) - loc
                    gapoback = loc - np.argmax(locs3>loc) - 1
                
                if  random.random() >.3:
                    break #randomness (T4), choosing to exit

                if gap >= self.lane1[loc] + 3:
                    break #gap < l (T1)

                if self.lane3[loc] > -1 or gapo <= self.lane1[loc] + 3:
                    break #gapo > l0 (T2)

                if gapoback-1 <= 30:
                    break #gapoback > vmax (T3) backwards causality

#                 print("lane1to3")
                #made it this far, then changing to lane 3
                self.lane3[loc] = self.lane1[loc]
                self.lane1[loc] = -1
                locs1 = np.delete(locs1,i);
                locs3 = np.insert(locs3,np.argmax(locs2 > i), i)
        
              
        #Repeat for Lane 2 to lane 1
        for i in range(len(locs2)):
            loc = locs2[i]
            if i == len(locs2)-1:
                next_loc = loc
            else:
                next_loc = locs2[i+1]    
            
            gap = next_loc - loc
#             print("HERE")
#             print("gap",gap)
#             print(loc)
#             print(len(locs1))
            if len(locs1) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs1>loc) - loc
                gapoback = loc - np.argmax(locs1>loc) - 1
            
            if gap >= self.lane2[loc] + 3:
                break #gap < l (T1)
                
            if self.lane1[loc] > -1 or gapo <= self.lane2[loc] + 3:
                break #gapo > l0 (T2)
                
            if gapoback-1 <= 30:
                break #gapoback > loback (T3) backwards causality
                
            if  random.random() >.4:
                break #randomness (T4)
                
#             print("lane2to1")
            #made it this far, then changing to lane 2
            self.lane1[loc] = self.lane2[loc]
            self.lane2[loc] = -1
            locs2 = np.delete(locs2,i);
            locs1 = np.insert(locs1,np.argmax(locs1 > i), i)
            
        #Repeat for Lane 3 to lane 1
        for i in range(len(locs3)):
            loc = locs3[i]
            if i == len(locs3)-1:
                next_loc = loc
            else:
                next_loc = locs3[i+1]    
            
            gap = next_loc - loc
            if len(locs1) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs1>loc) - loc
                gapoback = loc - np.argmax(locs1>loc) - 1
            
            if gap >= self.lane3[loc] + 3:
                break #gap < l (T1)
                
            if self.lane1[loc] > -1 or gapo <= self.lane3[loc] + 3:
                break #gapo > l0 (T2)
                
            if gapoback-1 <= 30:
                break #gapoback > loback (T3) backwards causality
                
            if  random.random() >.4:
                break #randomness (T4)
                
#             print("lane3to1")
            #made it this far, then changing to lane 2
            self.lane1[loc] = self.lane3[loc]
            self.lane3[loc] = -1
            locs3 = np.delete(locs3,i);
            locs1 = np.insert(locs1,np.argmax(locs1 > i), i)
        
        #single lane car movements in each lane now
        
        #lane 1
        for i in range(len(locs1)):
            loc = locs1[i]
            if i == len(locs1)-1:
                next_loc = self.length-1
            else:
                next_loc = locs1[i+1]  
            
            v = self.lane1[loc]
            
            gap = next_loc - loc
            
            #add traffic signal changes  for intersections,
            signal = (t*.5) % self.lt
            if signal >= self.y and signal < self.r-1 and loc >= self.length-4: #in yellow light slow down phase
                if v > 15:
                    v = v-10
#                     print("yellow slow")
            if signal >= self.r-1 and loc >= self.length-4: #in red light stop phase
                if v > 15:
                    v = v/3 
#                     print("red stop")
                else:
                    v = 0
#                     print("red stop")
            if signal < self.g and v < 15 and loc >= self.length-4:
                v = v + 5
#                 print("speed up after red")
            else:
                if v < vmax and gap > v:
                    v = v+3 #(S1)
#                     print("speed up")

                if v > gap:
                    v = gap-1 #(s2)
#                     print(gap, "slow down")

                if v > 0 and random.random() < .4:
                    v = v-2; #(S3)
#                     print("random slow")
                    
            if loc+v < self.length:
                lane1_update[loc+v] = v
#                 print("new pos", loc+v)
            else:
                if c == 0:
                    cars_out = np.array([1, loc+v-self.length+1, v])
                else:
                    cars_out= np.vstack((cars_out,[1, loc+v-self.length+1, v])) 
                c= c+1
#                 print("exit")
            
            
        #repeat for lane 2
        for i in range(len(locs2)):
            loc = locs2[i]
            if i == len(locs2)-1:
                next_loc = self.length-1
            else:
                next_loc = locs2[i+1] 
            
            v = self.lane2[loc]
            gap = next_loc - loc
            
             #add traffic signal changes  for intersections,
            signal = (t*.5) % self.lt
            if signal >= self.y and signal < self.r-1 and loc >= self.length-4: #in yellow light slow down phase
                if v > 15:
                    v = v-10
#                     print("yellow slow")
            if signal >= self.r-1 and loc >= self.length-4: #in red light stop phase
                if v > 15:
                    v = v/3 
#                     print("red stop")
                else:
                    v = 0
#                     print("red stop")
            if signal < self.g and v < 15 and loc >= self.length-4:
                v = v + 5
#                 print("speed up after red")
            else:
                if v < vmax and gap > v:
                    v = v+3 #(S1)
#                     print("speed up")

                if v > gap:
                    v = gap-1 #(s2)
#                     print(gap, "slow down")

                if v > 0 and random.random() < .4:
                    v = v-2; #(S3)
#                     print("random slow")
                
            if loc+v < self.length:
                lane2_update[loc+v] = v
#                 print("new pos", loc+v)
            else:
                if c == 0:
                    cars_out = np.array([2, loc+v-self.length+1, v])
                else:
                    cars_out= np.vstack((cars_out,[2, loc+v-self.length+1, v])) 
                c = c+1
#                 print("exit")
            
        #lane 3
        for i in range(len(locs3)):
            loc = locs3[i]
            if loc >= self.length2:
                if i == len(locs3)-1:
                    next_loc = self.length-1
                else:
                    next_loc = locs3[i+1]   

                v = self.lane3[loc]
                gap = next_loc - loc

             #add traffic signal changes  for intersections,
            signal = (t*.5) % self.lt
            if signal >= self.y and signal < self.r-1 and loc >= self.length-4: #in yellow light slow down phase
                if v > 15:
                    v = v-10
#                     print("yellow slow")
            if signal >= self.r-1 and loc >= self.length-4: #in red light stop phase
                if v > 15:
                    v = v/3 
#                     print("red stop")
                else:
                    v = 0
#                     print("red stop")
            if signal < self.g and v < 15 and loc >= self.length-4:
                if v > 0:
                    v = v-1
#                 print("slow down to turn")
            else:
                if v < vmax and gap > v:
                    v = v+3 #(S1)
#                     print("speed up")

                if v > gap:
                    v = gap-1 #(s2)
#                     print(gap, "slow down")

                if v > 0 and random.random() < .4:
                    v = v-2; #(S3)
#                     print("random slow")
                
            if loc+v < self.length:
                lane3_update[loc+v] = v
#                 print("new pos", loc+v)
#             else:
#                 print("exit")
            
            
        self.lane1 = lane1_update
        self.lane2 = lane2_update
        self.lane3 = lane3_update
#         plt.plot(t,(self.lane1>-1).sum() + (self.lane2>-1).sum() + (self.lane3>-1).sum())
#         print(self.lane1)
#         print(self.lane2)
#         print("cars left2", (self.lane1>-1).sum() + (self.lane2>-1).sum() + (self.lane3>-1).sum())
        return cars_out


# In[176]:


class Peachtree12_13:
    #Two Lanes with Third left lane mid way, no signal and no left turns
    
    def __init__(self):
        self.length = np.round(340/16).astype(int) #length of road, split Peachtree into cells of 16ft(average car length)
        self.length2 = np.round(144/16).astype(int) #when left turn lane begins
        
        #Some needed variables
#         self.density = self.cars/(2*self.length);
        self.max_velocity = 50
        
        #Create 2 lane system & intersections
        self.lane1 = -np.ones(self.length, dtype=int)
        self.lane2 = -np.ones(self.length, dtype=int)
        self.lane3 = -np.ones(self.length, dtype=int) #Left turn only lane
        
        #Adding Cars
        
    def update(self, t, cars_in): 
        vmax = self.max_velocity
        cars_out = np.array([0,1,1]) # [lane#, loc, speed]
        c = 0 #count of cars exiting intersection
        
        #add cars from previous intersection
#         print("size", cars_in.shape)
#         print(cars_in)
        for i in range(len(cars_in)):
            if cars_in.ndim == 1:
                if cars_in[0] == 1:
                    self.lane1[cars_in[1]] = cars_in[2]
                elif cars_in[0] == 2:
                    self.lane2[cars_in[1]] = cars_in[2]
            elif cars_in.ndim > 1:
                if cars_in[i][0] == 1:
                    self.lane1[cars_in[i][1]] = cars_in[i][2]
                elif cars_in[i][0] == 2:
                    self.lane2[cars_in[i][1]] = cars_in[i][2]
        
        #for single lane movement update
        lane1_update = -np.ones(self.length, dtype=int)
        lane2_update = -np.ones(self.length, dtype=int)
        lane3_update = -np.ones(self.length, dtype=int)
        
        #Subset1: Check exchange of vehicles between lanes, currently implementing symmetric, will change to stochastic
        
        #current car locations
        locs1 = np.transpose(np.nonzero(self.lane1 > -1))
        locs2 = np.transpose(np.nonzero(self.lane2 > -1))
        locs3 = np.transpose(np.nonzero(self.lane3 > -1))
        
        #Change from lane 1 to lane 2
        for i in range(len(locs1)):
            loc = locs1[i]
            if i == len(locs1)-1:
                next_loc = loc
            else:
                next_loc = locs1[i+1]     
            
            gap = next_loc - loc
            if len(locs2) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs2>loc) - loc
                gapoback = loc - np.argmax(locs2>loc) - 1
            
            if gap >= self.lane1[loc] + 3:
                break #gap < l (T1)
                
            if self.lane2[loc] > -1 or gapo <= self.lane1[loc] + 3:
                break #gapo > l0 (T2)
                
            if gapoback-2 <= 30:
                break #gapoback > vmax (T3) backwards causality
            
            if  random.random() >.4:
                break #randomness (T4)
#             print("lane1to2")
            #made it this far, then changing to lane 2
            self.lane2[loc] = self.lane1[loc]
            self.lane1[loc] = -1
            locs1 = np.delete(locs1,i);
            locs2 = np.insert(locs2,np.argmax(locs2 > i), i)
            
        #Change from lane 1 to lane 3
        for i in range(len(locs1)):
            loc = locs1[i]
            if loc >= self.length2:
                if i == len(locs1)-1:
                    next_loc = loc
                else:
                    next_loc = locs1[i+1]     

                gap = next_loc - loc
                if len(locs3) == 0:
                    gapo = self.length - 1 - loc
                    gapoback = loc 
                else:
                    gapo = np.argmax(locs3>loc) - loc
                    gapoback = loc - np.argmax(locs3>loc) - 1
                
                if  random.random() >.4:
                    break #randomness (T4), choosing to exit

                if gap >= self.lane1[loc] + 3:
                    break #gap < l (T1)

                if self.lane3[loc] > -1 or gapo <= self.lane1[loc] + 3:
                    break #gapo > l0 (T2)

                if gapoback-1 <= 30:
                    break #gapoback > vmax (T3) backwards causality

#                 print("lane1to3")
                #made it this far, then changing to lane 3
                self.lane3[loc] = self.lane1[loc]
                self.lane1[loc] = -1
                locs1 = np.delete(locs1,i);
                locs3 = np.insert(locs3,np.argmax(locs2 > i), i)
        
              
        #Repeat for Lane 2 to lane 1
        for i in range(len(locs2)):
            loc = locs2[i]
            if i == len(locs2)-1:
                next_loc = loc
            else:
                next_loc = locs2[i+1]    
            
            gap = next_loc - loc
            if len(locs1) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs1>loc) - loc
                gapoback = loc - np.argmax(locs1>loc) - 1
            
            if gap >= self.lane2[loc] + 3:
                break #gap < l (T1)
                
            if self.lane1[loc] > -1 or gapo <= self.lane2[loc] + 3:
                break #gapo > l0 (T2)
                
            if gapoback-1 <= 30:
                break #gapoback > loback (T3) backwards causality
                
            if  random.random() >.4:
                break #randomness (T4)
                
#             print("lane2to1")
            #made it this far, then changing to lane 2
            self.lane1[loc] = self.lane2[loc]
            self.lane2[loc] = -1
            locs2 = np.delete(locs2,i);
            locs1 = np.insert(locs1,np.argmax(locs1 > i), i)
            
        #Repeat for Lane 3 to lane 1
        for i in range(len(locs3)):
            loc = locs3[i]
            if i == len(locs3)-1:
                next_loc = loc
            else:
                next_loc = locs3[i+1]    
            
            gap = next_loc - loc
            if len(locs1) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs1>loc) - loc
                gapoback = loc - np.argmax(locs1>loc) - 1
            
            if gap >= self.lane3[loc] + 3:
                break #gap < l (T1)
                
            if self.lane1[loc] > -1 or gapo <= self.lane3[loc] + 3:
                break #gapo > l0 (T2)
                
            if gapoback-1 <= 30:
                break #gapoback > loback (T3) backwards causality
                
            if  random.random() >.4:
                break #randomness (T4)
                
#             print("lane3to1")
            #made it this far, then changing to lane 2
            self.lane1[loc] = self.lane3[loc]
            self.lane3[loc] = -1
            locs3 = np.delete(locs3,i);
            locs1 = np.insert(locs1,np.argmax(locs1 > i), i)
           
        #single lane car movements in each lane now
        
        #lane 1
        for i in range(len(locs1)):
            loc = locs1[i]
            if i == len(locs1)-1:
                next_loc = self.length-1
            else:
                next_loc = locs1[i+1]  
            
            v = self.lane1[loc]
            
            gap = next_loc - loc
            
            #regular rules
            if v < vmax and gap > v:
                v = v+3 #(S1)
#                 print("speed up")

            elif v > gap:
                v = gap-1 #(s2)
#                 print(gap, "slow down")

            elif v > 0 and random.random() < .4:
                v = v-2; #(S3)
#                 print("random slow")
                    
            if loc+v < self.length:
                lane1_update[loc+v] = v
#                 print("new pos", loc+v)
            else:
                if c == 0:
                    cars_out = np.array([1, loc+v-self.length+1, v])
                else:
                    cars_out= np.vstack((cars_out,[1, loc+v-self.length+1, v])) 
                c= c+1
#                 print("exit")
            
            
        #repeat for lane 2
        for i in range(len(locs2)):
            loc = locs2[i]
            if i == len(locs2)-1:
                next_loc = self.length-1
            else:
                next_loc = locs2[i+1] 
            
            v = self.lane2[loc]
            gap = next_loc - loc
            
            #regular rules
            if v < vmax and gap > v:
                v = v+3 #(S1)
#                 print("speed up")

            elif v > gap:
                v = gap-1 #(s2)
#                 print(gap, "slow down")

            elif v > 0 and random.random() < .4:
                v = v-2; #(S3)
#                 print("random slow")
                
            elif loc+v < self.length:
                lane2_update[loc+v] = v
#                 print("new pos", loc+v)
            else:
                if c == 0:
                    cars_out = np.array([2, loc+v-self.length+1, v])
                else:
                    cars_out= np.vstack((cars_out,[2, loc+v-self.length+1, v])) 
                c = c+1
#                 print("exit")
            
        #lane 3
        for i in range(len(locs3)):
            loc = locs3[i]
            if loc >= self.length2:
                if i == len(locs3)-1:
                    next_loc = self.length-1
                else:
                    next_loc = locs3[i+1]   

                v = self.lane3[loc]
                gap = next_loc - loc
            
            #regular rules
            if v < vmax and gap > v:
                v = v+3 #(S1)
#                 print("speed up")

            elif v > gap:
                v = gap-1 #(s2)
#                 print(gap, "slow down")

            elif v > 0 and random.random() < .4:
                v = v-2; #(S3)
#                 print("random slow")
                
            elif loc+v < self.length:
                lane3_update[loc+v] = v
#                 print("new pos", loc+v)
            else:
                if c == 0:
                    cars_out = np.array([3, loc+v-self.length+1, v])
                else:
                    cars_out= np.vstack((cars_out,[3, loc+v-self.length+1, v])) 
                c= c+1
#                 print("exit")
            
            
        self.lane1 = lane1_update
        self.lane2 = lane2_update
        self.lane3 = lane3_update
#         plt.plot(t,(self.lane1>-1).sum() + (self.lane2>-1).sum())
#         print(self.lane1)
#         print(self.lane2)
#         print("cars left", (self.lane1>-1).sum() + (self.lane2>-1).sum() + (self.lane3>-1).sum())
#         print(cars_out)
        return cars_out


# In[177]:


class Peachtree13_14:
    #Two Lanes with Third left turn only lane 
    
    def __init__(self):
        self.length = np.round(314/16).astype(int) #length of road, split Peachtree into cells of 16ft(average car length)
        
        #Some needed variables
#         self.density = self.cars/(2*self.length);
        self.max_velocity = 50
        
        #Add traffic light timings
        self.g = 34.5
        self.y = 3.5 + self.g
        self.r = 46 + self.y
        self.lt = 84
        
        #Create 2 lane system & intersections
        self.lane1 = -np.ones(self.length, dtype=int)
        self.lane2 = -np.ones(self.length, dtype=int)
        self.lane3 = -np.ones(self.length, dtype=int) #Left turn only lane
        
        #Adding Cars
        
    def update(self, t, cars_in): 
        vmax = self.max_velocity
        
        #add cars from previous intersection
#         print("size", cars_in.shape)
#         print(cars_in)
        for i in range(len(cars_in)):
            if cars_in.ndim == 1:
                if cars_in[0] == 1:
                    self.lane1[cars_in[1]] = cars_in[2]
                elif cars_in[0] == 2:
                    self.lane2[cars_in[1]] = cars_in[2]
                elif cars_in[0] == 3:
                    self.lane3[cars_in[1]] = cars_in[2]
            elif cars_in.ndim > 1:
                if cars_in[i][0] == 1:
                    self.lane1[cars_in[i][1]] = cars_in[i][2]
                elif cars_in[i][0] == 2:
                    self.lane2[cars_in[i][1]] = cars_in[i][2]
                elif cars_in[i][0] == 3:
                    self.lane3[cars_in[i][1]] = cars_in[i][2]
        
        #for single lane movement update
        lane1_update = -np.ones(self.length, dtype=int)
        lane2_update = -np.ones(self.length, dtype=int)
        lane3_update = -np.ones(self.length, dtype=int)
        
        #Subset1: Check exchange of vehicles between lanes, currently implementing symmetric, will change to stochastic
        
        #current car locations
        locs1 = np.transpose(np.nonzero(self.lane1 > -1))
        locs2 = np.transpose(np.nonzero(self.lane2 > -1))
        locs3 = np.transpose(np.nonzero(self.lane3 > -1))
        
        #Change from lane 1 to lane 2
        for i in range(len(locs1)):
            loc = locs1[i]
            if i == len(locs1)-1:
                next_loc = loc
            else:
                next_loc = locs1[i+1]     
            
            gap = next_loc - loc
            if len(locs2) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs2>loc) - loc
                gapoback = loc - np.argmax(locs2>loc) - 1
            
            if gap >= self.lane1[loc] + 3:
                break #gap < l (T1)
                
            if self.lane2[loc] > -1 or gapo <= self.lane1[loc] + 3:
                break #gapo > l0 (T2)
                
            if gapoback-2 <= 30:
                break #gapoback > vmax (T3) backwards causality
            
            if  random.random() >.4:
                break #randomness (T4)
#             print("lane1to2")
            #made it this far, then changing to lane 2
            self.lane2[loc] = self.lane1[loc]
            self.lane1[loc] = -1
            locs1 = np.delete(locs1,i);
            locs2 = np.insert(locs2,np.argmax(locs2 > i), i)
            
        #Change from lane 1 to lane 3
        for i in range(len(locs1)):
            loc = locs1[i]
            if i == len(locs1)-1:
                next_loc = loc
            else:
                next_loc = locs1[i+1]     

            gap = next_loc - loc
            if len(locs3) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs3>loc) - loc
                gapoback = loc - np.argmax(locs3>loc) - 1

            if  random.random() >.3:
                break #randomness (T4), choosing to exit

            if gap >= self.lane1[loc] + 3:
                break #gap < l (T1)

            if self.lane3[loc] > -1 or gapo <= self.lane1[loc] + 3:
                break #gapo > l0 (T2)

            if gapoback-1 <= 30:
                break #gapoback > vmax (T3) backwards causality

#                 print("lane1to3")
            #made it this far, then changing to lane 3
            self.lane3[loc] = self.lane1[loc]
            self.lane1[loc] = -1
            locs1 = np.delete(locs1,i);
            locs3 = np.insert(locs3,np.argmax(locs2 > i), i)

              
        #Repeat for Lane 2 to lane 1
        for i in range(len(locs2)):
            loc = locs2[i]
            if i == len(locs2)-1:
                next_loc = loc
            else:
                next_loc = locs2[i+1]    
            
            gap = next_loc - loc
#             print("HERE")
#             print("gap",gap)
#             print(loc)
#             print(len(locs1))
            if len(locs1) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs1>loc) - loc
                gapoback = loc - np.argmax(locs1>loc) - 1
            
            if gap >= self.lane2[loc] + 3:
                break #gap < l (T1)
                
            if self.lane1[loc] > -1 or gapo <= self.lane2[loc] + 3:
                break #gapo > l0 (T2)
                
            if gapoback-1 <= 30:
                break #gapoback > loback (T3) backwards causality
                
            if  random.random() >.4:
                break #randomness (T4)
                
#             print("lane2to1")
            #made it this far, then changing to lane 2
            self.lane1[loc] = self.lane2[loc]
            self.lane2[loc] = -1
            locs2 = np.delete(locs2,i);
            locs1 = np.insert(locs1,np.argmax(locs1 > i), i)
            
        #Repeat for Lane 3 to lane 1
        for i in range(len(locs3)):
            loc = locs3[i]
            if i == len(locs3)-1:
                next_loc = loc
            else:
                next_loc = locs3[i+1]    
            
            gap = next_loc - loc
            if len(locs1) == 0:
                gapo = self.length - 1 - loc
                gapoback = loc 
            else:
                gapo = np.argmax(locs1>loc) - loc
                gapoback = loc - np.argmax(locs1>loc) - 1
            
            if gap >= self.lane3[loc] + 3:
                break #gap < l (T1)
                
            if self.lane1[loc] > -1 or gapo <= self.lane3[loc] + 3:
                break #gapo > l0 (T2)
                
            if gapoback-1 <= 30:
                break #gapoback > loback (T3) backwards causality
                
            if  random.random() >.4:
                break #randomness (T4)
                
#             print("lane3to1")
            #made it this far, then changing to lane 2
            self.lane1[loc] = self.lane3[loc]
            self.lane3[loc] = -1
            locs3 = np.delete(locs3,i);
            locs1 = np.insert(locs1,np.argmax(locs1 > i), i)
        
        #single lane car movements in each lane now
        
        #lane 1
        for i in range(len(locs1)):
            loc = locs1[i]
            if i == len(locs1)-1:
                next_loc = self.length-1
            else:
                next_loc = locs1[i+1]  
            
            v = self.lane1[loc]
            
            gap = next_loc - loc
            
            #add traffic signal changes  for intersections,
            signal = (t*.5) % self.lt
            if signal >= self.y and signal < self.r-1 and loc >= self.length-4: #in yellow light slow down phase
                if v > 15:
                    v = v-10
#                     print("yellow slow")
            if signal >= self.r-1 and loc >= self.length-4: #in red light stop phase
                if v > 15:
                    v = v/3 
#                     print("red stop")
                else:
                    v = 0
#                     print("red stop")
            if signal < self.g and v < 15 and loc >= self.length-4:
                v = v + 5
#                 print("speed up after red")
            else:
                if v < vmax and gap > v:
                    v = v+3 #(S1)
#                     print("speed up")

                if v > gap:
                    v = gap-1 #(s2)
#                     print(gap, "slow down")

                if v > 0 and random.random() < .4:
                    v = v-2; #(S3)
#                     print("random slow")
                    
            if loc+v < self.length:
                lane1_update[loc+v] = v
#                 print("new pos", loc+v)
#             else:
#                 print("exit")
            
            
        #repeat for lane 2
        for i in range(len(locs2)):
            loc = locs2[i]
            if i == len(locs2)-1:
                next_loc = self.length-1
            else:
                next_loc = locs2[i+1] 
            
            v = self.lane2[loc]
            gap = next_loc - loc
            
             #add traffic signal changes  for intersections,
            signal = (t*.5) % self.lt
            if signal >= self.y and signal < self.r-1 and loc >= self.length-4: #in yellow light slow down phase
                if v > 15:
                    v = v-10
#                     print("yellow slow")
            if signal >= self.r-1 and loc >= self.length-4: #in red light stop phase
                if v > 15:
                    v = v/3 
#                     print("red stop")
                else:
                    v = 0
#                     print("red stop")
            if signal < self.g and v < 15 and loc >= self.length-4:
                v = v + 5
#                 print("speed up after red")
            else:
                if v < vmax and gap > v:
                    v = v+3 #(S1)
#                     print("speed up")

                if v > gap:
                    v = gap-1 #(s2)
#                     print(gap, "slow down")

                if v > 0 and random.random() < .4:
                    v = v-2; #(S3)
#                     print("random slow")
                
            if loc+v < self.length:
                lane2_update[loc+v] = v
#                 print("new pos", loc+v)
            else:
                if c == 0:
                    cars_out = np.array([2, loc+v-self.length+1, v])
#                 else:
#                 print("exit")
            
        #lane 3
        for i in range(len(locs3)):
            loc = locs3[i]
            if loc >= self.length2:
                if i == len(locs3)-1:
                    next_loc = self.length-1
                else:
                    next_loc = locs3[i+1]   

                v = self.lane3[loc]
                gap = next_loc - loc

             #add traffic signal changes  for intersections,
            signal = (t*.5) % self.lt
            if signal >= self.y and signal < self.r-1 and loc >= self.length-4: #in yellow light slow down phase
                if v > 15:
                    v = v-10
#                     print("yellow slow")
            if signal >= self.r-1 and loc >= self.length-4: #in red light stop phase
                if v > 15:
                    v = v/3 
#                     print("red stop")
                else:
                    v = 0
#                     print("red stop")
            if signal < self.g and v < 15 and loc >= self.length-4:
                if signal % 16 <= 9 + 3.5 and signal % 16 > 9: # yellow light
                    if v > 15:
                        v = v-10
                elif signal % 16 > 9+3.5:
                    if v > 15:
                        v = v/3
                    else:
                        v = 0
                else:
                    if v > 0:
                        v = v-1
#                 print("slow down to turn")
            else:
        
                if v < vmax and gap > v:
                    v = v+3 #(S1)
#                     print("speed up")

                if v > gap:
                    v = gap-1 #(s2)
#                     print(gap, "slow down")

                if v > 0 and random.random() < .4:
                    v = v-2; #(S3)
#                     print("random slow")
                
            if loc+v < self.length:
                lane3_update[loc+v] = v
#                 print("new pos", loc+v)
#             else:
#                 print("exit")
            
            
        self.lane1 = lane1_update
        self.lane2 = lane2_update
        self.lane3 = lane3_update
#         plt.plot(t,(self.lane1>-1).sum() + (self.lane2>-1).sum())
#         print(self.lane1)
#         print(self.lane2)
#         print("cars left4", (self.lane1>-1).sum() + (self.lane2>-1).sum() + (self.lane3>-1).sum())


t = 3000
PT = Peachtree(t)
PT.update()

