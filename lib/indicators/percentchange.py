import pandas as pd


def percent_change(df, n_size=1):
    """
    Calculates percentage change between n last elements
    df: input dataframe
    n_size: step size between intervals
    """
    if df.empty:
        print("PercentChange Error: got empty dataframe, returning 0.0")
        return 0.0

    df_rows = len(df.index)
    if df_rows < n_size:
        print("PercentChange Error: not enough elements in buffer,.returning 0.0")
        return 0.0

    el1 = df.tail(1).close.iloc[0]
    el2 = df.iloc[[df_rows - n_size - 1]].close.iloc[0]
    diff = el1 - el2
    percent = (diff*100)/el2
    return percent


