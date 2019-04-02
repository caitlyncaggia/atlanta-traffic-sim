from numpy import genfromtxt
import numpy as np
# import pyglet...

# get data from CSV file
my_data = genfromtxt('NGSIM-Data/trajectories.csv', delimiter=',')
ts = 1 # Timestep (seconds)
# print(my_data)

a = np.shape(my_data)
lenDat = a[0]
print(a)


# Sort data by order of 0th column
sorted = my_data[my_data[:, 0].argsort()]

numFrames = my_data[1,2]

for x in range(0,int(lenDat)):
    # For each frame number,
    # Display car ID's for each entry in .csv
    print(my_data[x,0])
         #   find all cars in that frame.
         #   plot them in animation using pyglet
    # print(sorted[x,0])


print(lenDat)
