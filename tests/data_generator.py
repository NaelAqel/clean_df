"""Support functions to generate random data for test"""

# import modules
import numpy as np
import pandas as pd
import string


def num_generator(type_, size) -> np.ndarray:
    """
    Generates a numpy array of numerical values that have distribution
    within `type_` value limits, also array will have a random number of
    outliers. Note that the output array will be float64 datatype, the
    function just produce array within `type_` limits.

    Parameters
    ----------
    type_ : numpy.dtype
        The type where data will be in its limitations (for example np.int8
        has values between -128 and 127). Values can be any (uint, int, float)
        types only.
    size : int
        The size of the generated array.

    Raises
    ------
    ValueError
        If `type_` is not a numerical type, accepted types are
        [`np.uint8`, `np.uint16`, `np.uint32`, `np.uint64`, `np.int8`,
        `np.int16`, `np.int32`, `np.int64`, `np.float16`, `np.float32`,
        `np.float64`]. If `size` is not a positive integer.

    Returns
    -------
    numpy.ndarray
        The generated numpy array.
    """
    # assign accepted types
    int_types = [np.uint8, np.uint16, np.uint32, np.uint64, np.int8, np.int16,
                 np.int32, np.int64]
    float_types = [np.float16, np.float32, np.float64]
    # assign min and max as the limits depending on the entered type
    if type_ in int_types:
        # if integer, use iinfo
        min, max = np.iinfo(type_).min, np.iinfo(type_).max
    elif type_ in float_types:
        # if float, use finfo
        min, max = np.finfo(type_).min, np.finfo(type_).max
    else:
        # otherwise, raise ValueError
        raise ValueError('Unaccepted entered datatype.')

    # check size value
    if (not isinstance(size, int)) or size < 1:
        raise ValueError("'size' should be a positive integer.")

    # to make sure of having outliers, we will have a normal distribution of
    # 90% of size with mean in the middle of values and std (mu) as 1/8 of
    # the full range, for the other 10% we will put 5% in lower range with
    # mean of min+std, last 5% is upper range with mean of max-mu.
    size_low = round(size*0.05)
    size_mid = round(size*0.9)
    # size_high will be the rest of size to avoid any error from using 'round'
    size_high = size - size_low - size_mid

    # assign mean and std (it will depend on min value)
    mean = max / 2 if min == 0 else 0
    mu = max / 8 if min == 0 else max / 4

    # assign the 3 normal distribution arrays using random function
    arr_low = np.random.normal(min+mu, mu/3, size_low)
    arr_mid = np.random.normal(mean, mu, size_mid)
    arr_high = np.random.normal(max-mu, mu/3, size_high)
    # concatenate all in one array
    arr = np.concatenate((arr_low, arr_mid, arr_high))

    # if the type is integer, round all values (convert to integers)
    if type_ in int_types:
        arr = np.round(arr)

    # to make sure we are within our limits, if anything out our limits
    # will be replaced with the limit values
    arr[np.where(arr > max)] = max
    arr[np.where(arr < min)] = min

    # return the array
    return arr


def str_generator(size, unique_num=0) -> np.ndarray:
    """
    Generate a numpy array of string values.

    Parameters
    ----------
    size : int
        The size of the generated array
    unique_num : int, optional
        The number of unique values in generated array, if not specified
        (i.e. 0) then number will be randomly selected within the function,
        defaults to 0

    Raises
    ------
    ValueError
        If `unique_num` is not 0 or positive integer.
    ValueError
        If `size` is not a positive integer.

    Returns
    -------
    numpy.ndarray
        The generated numpy array
    """
    # check unique_num value
    if (not isinstance(unique_num, int)) or unique_num < 0:
        raise ValueError("'unique_num' should be a positive integer or 0.")

    # check size value
    if (not isinstance(size, int)) or size < 1:
        raise ValueError("'size' should be a positive integer.")

    # make unique_num same size if its value is zero
    unique_num = size if unique_num == 0 else unique_num

    # generate a list of random strings, strings will have random length
    # between 1 and 10, the size of list will be unique_num
    str_array = [''.join(np.random.choice(
        [*string.ascii_letters], replace=True,
        size=np.random.randint(1, 10))) for _ in range(unique_num)]

    # generate random array by choosing 'size' number strings with replace
    # from str_array
    arr = np.random.choice(str_array, size=size, replace=True)

    # return the array
    return arr


def generate_df(size) -> pd.DataFrame:
    """
    This function will generate a dataframe with 'size' rows, with columns:
        1- `single_value`: which has one value `A`.
        2- `all_missing`: all `NaN`.
        3- `uint{x}': x in [8, 16, 32, 64], these columns contain random
            integers above zero, outliers, and missing values within the
            limits of uint{x}.
        4- `int{x}`: x in [8, 16, 32, 64], these columns contain random
            integers, outliers, and missing values within the limits of int{x}
        5- `float{x}`: x in [16, 32, 64], these columns contain random floats
            outliers, and missing values within the limits of float{x}.
        6- `date`: contains random dates.
        7- `time`: contains random times.
        8- `cat{x}`: 3 columns with random strings, the number of unique values
            in the column is between 2 and 5.
        9- `str{x}`: 3 columns with random strings.
    Some columns will have a random number of Missing values.

    Parameters
    ----------
    size : int
        The number of rows of generated dataframe

    Raises
    ------
    ValueError
        If `size` is not a positive integer.

    Returns
    -------
    pandas.DataFrame
        The generated dataframe.
    """
    # check size value
    if (not isinstance(size, int)) or size < 1:
        raise ValueError("'size' should be a positive integer.")

    # define dataframe df that will use for the test, it contains all cases
    df = pd.DataFrame({
        'single_value': ['A']*size,
        'all_missing': [np.nan]*size,
        'uint8': num_generator(np.uint8, size),
        'uint16': num_generator(np.uint16, size),
        'uint32': num_generator(np.uint32, size),
        'uint64': num_generator(np.uint64, size),
        'int8': num_generator(np.int8, size),
        'int16': num_generator(np.int16, size),
        'int32': num_generator(np.int32, size),
        'int64': num_generator(np.int64, size),
        'float16': num_generator(np.float16, size),
        'float32': num_generator(np.float32, size),
        'float64': num_generator(np.float64, size),
        'date': pd.date_range('2020-01-01', periods=size, freq='D'),
        'time': pd.timedelta_range('0:00:00', periods=size, freq='H'),
        'cat1': str_generator(size, unique_num=np.random.randint(2, 5)),
        'cat2': str_generator(size, unique_num=np.random.randint(2, 5)),
        'cat3': str_generator(size, unique_num=np.random.randint(2, 5)),
        'str1': str_generator(size),
        'str2': str_generator(size),
        'str3': str_generator(size)
        })

    # make random missing values in random 7 columns (exclude first two cols)
    for col in np.random.choice(df.columns[2:], size=7, replace=False):
        df.loc[np.random.choice(size, size=np.random.randint(1, size//10),
                                replace=False), col] = np.nan

    # repeate some columns and add to df
    df = pd.concat([df, df.iloc[np.random.choice(
        range(4), size=3, replace=True)]], ignore_index=True)

    # return dataframe
    return df
