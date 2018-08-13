# This module contains various utility functions, in particular functions to calculate consumption values

import sys
import pandas as pd

def calc_rates_dict(dict):
    # Create data frame from dict
    df = pd.DataFrame.from_dict(dict, orient='index', columns= ['price'])
    # Move index to new column 'lower_limit'
    df = df.reset_index()
    df = df.rename(columns= {'index' : 'lower_limit'})
    # Cast values in column 'lower_limit' to float64
    df['lower_limit'] = df['lower_limit'].astype('float64')
    # Prepare for creation of column 'upper_limit' by shifting 'lower_limit' one entry up
    thresholds_list = list(df['lower_limit'][1:])
    thresholds_list.append(sys.float_info.max)
    # Create new column 'upper_limit'
    df['upper_limit'] = pd.Series(thresholds_list)
    # Calculate maximum value per interval and cumulative value up to interval
    df['interval_value'] = df['price'] * (df['upper_limit'] - df['lower_limit'])
    df['cum_value'] = df['interval_value'].cumsum()
    # Shift cumulative values one entry down
    cum_value_list = list(df['cum_value'][0:-1])
    cum_value_list.insert(0,0)
    df['cum_value'] = pd.Series(cum_value_list)

    # return dataframe as dict
    return df.to_dict()

def calc_amount(dict, qty):
    # Convert dict to dataframe
    df = pd.DataFrame.from_dict(dict)
    # Only consider rate intervals with a lower_limit below the actually used quantity
    mask = df['lower_limit'] <= qty
    # Pick the last interval
    interval  = df[mask].iloc[-1]
    # Calculate value as cumulative value of previous interval plus the consumption value in the present interval
    value = interval['price'] * (qty - interval['lower_limit'] ) + interval['cum_value']
    return value

if __name__ == "__main__":
    import json
    s = '''
            {
        "lower_limit": {
            "0": 0.0,
            "1": 10235.0,
            "2": 51195.0,
            "3": 153595.0,
            "4": 511995.0
        },
        "price": {
            "0": 0.0733671,
            "1": 0.0699939,
            "2": 0.059031,
            "3": 0.042165,
            "4": 0.042165
        },
        "upper_limit": {
            "0": 10235.0,
            "1": 51195.0,
            "2": 153595.0,
            "3": 511995.0,
            "4": 1.7976931348623157e308
        },
        "interval_value": {
            "0": 750.9122685000001,
            "1": 2866.950144,
            "2": 6044.7744,
            "3": 15111.936,
            "4": 7.579973103146954e306
        },
        "cum_value": {
            "0": 0.0,
            "1": 750.9122685000001,
            "2": 3617.8624125,
            "3": 9662.6368125,
            "4": 24774.572812500002
        }
        }
        '''
    dict = json.loads(s)
    print("Result of calc_amount: ", calc_amount(dict, 0))


