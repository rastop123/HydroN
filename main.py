from WaterSNetwork import *

a = ((0, 15, 35, 120, 300, 1000, 60, 870, 85, 900, 550), (0, -90, 0, 5.5, 2, 0.6, 2, 3, 1, 1, 1), (0, 8, 10, 10))

netw = WaterSNetwork(2300, 3.5, 4.5, 20, *a)

netw.all_calc()