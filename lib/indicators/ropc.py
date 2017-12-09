

def ropc(close, timeperiod=5):
    """
    Calculates percentage change between n last elements
    close: price numpy.ndarray
    timeperiod: size to check
    """

    dataset_size = close.size
    if dataset_size < timeperiod-1:
        print('Error in ropc.py: passed not enough data! Required: ' + str(timeperiod) +
              ' passed: ' + str(dataset_size))
        return None

    close_list = close.tolist()
    prev_value = None
    price_diff_sum = 0.0
    for value in close_list:
        if not prev_value:
            prev_value = value
            continue
        value_diff = value - prev_value
        perc_change = (value_diff*100/prev_value)
        price_diff_sum += perc_change

    return price_diff_sum


