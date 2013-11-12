import math

MAX = 7.682212795973759

def compute( x_tmp, y_tmp ):
    y_tmp = y_tmp * 10 # normalizing to cartesian coordinate system
    base = ((30*y_tmp) - (25*x_tmp)) / 61.
    height = ((-1*(216*y_tmp)) + (180*x_tmp)) / 366.
    distance = math.sqrt( pow( base, 2 ) + pow( height, 2 ) )
    weight = 1 - ( distance / MAX )
    return weight
