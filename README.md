# Elevator-Scheduling-

# Ideas
To effectively and efficiently break down the problem and offer solutions to reduce the queuing time for the elevators and save energy! --> reduce the number of stops as acceleration/deceleration take a lot of extra time.

# Simulation
Assumptions --> 20 residents each floor, 24 floors in total (5/F~28/F). 3 elevators (lifts), each has a capacity of 12 people and 900kg. Piecewise linear approximation of elevator travel time.

# Algorithm
Dividing the three elevators so that each one of them goes to no. of floors = total no. of floors/ no. of elevators = 24/3 = 8 alternatively.
So, 
1st elevator = 5, 8, 11, 14, 17, 20, 23, 26.
2nd elevator = 6, 9, 12, 15, 18, 21, 24, 27.
3rd elevator = 7, 10, 13, 16, 19, 22, 25, 28.

Diving the three elevators into lower, middle and upper floors each going to total no. of 8 floors.
So, 
1st elevator = 5, 6, 7, 8, 9, 10, 11, 12.
2nd elevator = 13, 14, 15, 16, 17, 18, 19, 20.
3rd elevator = 21, 22, 23, 24, 25, 26, 27, 28.

# Results:
efficiency: 25% reduction in time taken for the queue of residents to reach their rooms. fairness: as all floors are divided equally and in equal number. so, you are expected to have to wait the same amount of time as your neighbor. feasibility: forming three queues instead of one queue.

# Conclusion and What's Next
Can be extended to going down and then eventually everyday usage.

# Built With
python
