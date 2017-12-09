

def epc(array, distance=5):
    """
    Calculates percentage change between 2 elements between give space distance
    close: price numpy.ndarray
    distance: space distance check
    """

    dataset_size = array.size
    if dataset_size < distance-1:
        print('Error in ropc.py: passed not enough data! Required: ' + str(distance) +
              ' passed: ' + str(dataset_size))
        return None

    return (array[-1]*100.0 / array[-distance]) - 100.0



