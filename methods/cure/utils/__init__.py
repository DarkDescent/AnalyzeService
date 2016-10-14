def euclidean_distance_sqrt(a, b):
    """!
    @brief Calculate square Euclidian distance between vector a and b.
    
    @param[in] a (list): The first vector.
    @param[in] b (list): The second vector.
    
    @return (double) Square Euclidian distance between two vectors.
    
    """  
    
    if ( ((type(a) == float) and (type(b) == float)) or ((type(a) == int) and (type(b) == int)) ):
        return (a - b)**2.0
        
    dimension = len(a)
    # assert len(a) == len(b)
    
    distance = 0.0
    for i in range(0, dimension):
        distance += (a[i] - b[i])**2.0
        
    return distance

def euclidean_distance(a, b):
    """!
    @brief Calculate Euclidian distance between vector a and b.

    @param[in] a (list): The first vector.
    @param[in] b (list): The second vector.

    @return (double) Euclidian distance between two vectors.

    @note This function for calculation is faster then standard function in ~100 times!

    """

    distance = euclidean_distance_sqrt(a, b);
    return distance**(0.5);