"""Utility functions for clean_df.
"""

# import modules
import numpy as np
from typing import Optional


def optimize_num(arr) -> Optional[np.dtype]:
    """
    Optimize the data type of a numerical array.
    The function determines the optimal data type for the array based on the
    data type and minimum and maximum values of the elements in the array. If
    the optimized data type is not the same ``arr`` data type (``arr`` can be
    optimized), the function returns the optimized data type.

    Parameters
    ----------
    arr : numpy.ndarray
        A numerical numpy array.

    Raises
    ------
    TypeError
        If ``arr`` is not a numpy array.
    ValueError
        If ``arr`` is not a numerical numpy array or all values are NaN.

    Returns
    -------
    numpy.dtype or None
        The optimized data type for the array if the array can be optimized,
        or None if the array data type cannot be optimized.
    """
    # check if input is not an array
    if not isinstance(arr, np.ndarray):
        raise TypeError('Input must be a numpy array.')
    # check if array is not a numerical numpy array or all are NaNs
    if not np.issubdtype(arr.dtype, np.number) or np.isnan(arr).all():
        raise ValueError('Input must be a numerical numpy array with at \
            least one non-NaN value.')

    # if the array (non-nan) values are all integers
    if (arr[~np.isnan(arr)] % 1 == 0).all():
        # if all integers are non-negative, use unsigned int types
        if np.nanmin(arr) >= 0:
            types = np.array([np.uint8, np.uint16, np.uint32, np.uint64])
        else:
            # otherwise, use signed int types
            types = np.array([np.int8, np.int16, np.int32, np.int64])
        # save the min and max values for each data type
        mins = np.array([np.iinfo(x).min for x in types])
        maxs = np.array([np.iinfo(x).max for x in types])
    else:
        # if float type, use float types
        types = np.array([np.float16, np.float32, np.float64])
        # save the min and max values for each data type
        mins = np.array([np.finfo(x).min for x in types])
        maxs = np.array([np.finfo(x).max for x in types])

    # get the indecies of the data type is within limits
    upper_limits = np.where(np.nanmax(arr) <= maxs)[0]
    lower_limits = np.where(np.nanmin(arr) >= mins)[0]

    # if no values in upper or lower limits, then there is value in arr
    # outside integer limits, will check as if it is a float32 or 64 only
    if len(upper_limits) == 0 or len(lower_limits) == 0:
        types = np.array([np.float32, np.float64])
        # save the min and max values for each data type
        mins = np.array([np.finfo(x).min for x in types])
        maxs = np.array([np.finfo(x).max for x in types])
        # get the indecies of the data type is within limits
        upper_limits = np.where(np.nanmax(arr) <= maxs)[0]
        lower_limits = np.where(np.nanmin(arr) >= mins)[0]

    # now, the type index will be the maximum of the first value of lower
    # and first value of upper
    type_index = max(upper_limits[0], lower_limits[0])

    # return the data type if it's not the same arr data type
    if types[type_index] != arr.dtype:
        return types[type_index]


def iqr(arr) -> Optional[list]:
    """
    Calculates the interquartile range (IQR) of a numerical array.
    The IQR is calculated as the difference between the 75th percentile and
    the 25th percentile of the array, and any values outside of 1.5 times the
    IQR are considered outliers. The function returns the number of lower
    outliers, upper outliers, and total outliers, as well as the percentage of
    the total number of values that are outliers only if there are outliers in
    the array.

    Parameters
    ----------
    arr : numpy.ndarray
        A numerical numpy array.

    Raises
    ------
    TypeError
        If ``arr`` is not a numpy array.
    ValueError
        If ``arr`` is not a numerical numpy array or all values are NaN.

    Returns
    -------
    list or None
        A list containing:
            - int: The number of lower outliers
            - int: The number of upper outliers
            - int: The total number of outliers
            - float: The percentage of outliers to total values of array
        Or None if there are no outliers
    :rtype: list or None
    """
    # check if input is not an array
    if not isinstance(arr, np.ndarray):
        raise TypeError('Input must be a numpy array.')
    # check if array is not a numerical numpy array or all are NaNs
    if not np.issubdtype(arr.dtype, np.number) or np.isnan(arr).all():
        raise ValueError('Input must be a numerical numpy array with at \
            least one non-NaN value.')

    # save 1st and third quartile values
    arr_25, arr_75 = np.nanpercentile(arr, 25), np.nanpercentile(arr, 75)

    # define lower and upper fences
    lower_fence = len(np.where(arr < arr_25 - 1.5 * (arr_75 - arr_25))[0])
    upper_fence = len(np.where(arr > arr_75 + 1.5 * (arr_75 - arr_25))[0])

    # if there are outliers, return them as described in doc_string
    if lower_fence + upper_fence > 0:
        return [
            lower_fence,
            upper_fence,
            lower_fence + upper_fence,
            round((lower_fence + upper_fence) * 100 / len(arr), 2)
        ]
