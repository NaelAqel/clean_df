"""Utilities test module. Asserts that functions are correct.
"""

# import modules
import numpy as np
from clean_df.utils import (optimize_num, iqr)
from tests.data_generator import num_generator
import pytest

# set the numpy seed to 0 to fix random functions outputs
np.random.seed(0)


class TestOptimizeNum:
    """
    This class is to test optimize_num function from utils.py
    """
    # first we will test all cases that cause errors
    def test_errors(self):
        # test for error when array is not numpy array
        with pytest.raises(TypeError):
            optimize_num(list(range(10)))

        # test for error when array is numpy non numarical
        with pytest.raises(ValueError):
            optimize_num(np.array(list(range(10))+['AA']))

        # test for error when array has nan values only
        with pytest.raises(ValueError):
            optimize_num(np.array([np.nan]*10))

    def test_uint(self):
        # test for optimization for uint8
        arr = num_generator(np.uint8, 100)
        # assert when not specifiy type for arr
        assert optimize_num(arr) == np.uint8
        # assert when arr is uint8 type
        assert optimize_num(arr.astype(np.uint8)) is None

        # test for optimization for uint16
        arr = num_generator(np.uint16, 100)
        # assert when not specifiy type for arr
        assert optimize_num(arr) == np.uint16
        # assert when arr is uint16 type
        assert optimize_num(arr.astype(np.uint16)) is None

        # test for optimization for uint32
        arr = num_generator(np.uint32, 100)
        # assert when not specifiy type for arr
        assert optimize_num(arr) == np.uint32
        # assert when arr is uint16 type
        assert optimize_num(arr.astype(np.uint32)) is None

        # test for optimization for uint64
        arr = num_generator(np.uint64, 100)
        # assert when not specifiy type for arr
        assert optimize_num(arr) == np.uint64
        # assert when arr is uint16 type
        assert optimize_num(arr.astype(np.uint64)) is None

    def test_int(self):
        # test for optimization for int8
        arr = num_generator(np.int8, 100)
        # assert when not specifiy type for arr
        assert optimize_num(arr) == np.int8
        # assert when arr is int8 type
        assert optimize_num(arr.astype(np.int8)) is None

        # test for optimization for int16
        arr = num_generator(np.int16, 100)
        # assert when not specifiy type for arr
        assert optimize_num(arr) == np.int16
        # assert when arr is int16 type
        assert optimize_num(arr.astype(np.int16)) is None

        # test for optimization for int32
        arr = num_generator(np.int32, 100)
        # assert when not specifiy type for arr
        assert optimize_num(arr) == np.int32
        # assert when arr is int32 type
        assert optimize_num(arr.astype(np.int32)) is None

        # test for optimization for int64
        arr = num_generator(np.int64, 100)
        # assert when not specifiy type for arr
        assert optimize_num(arr) == np.int64
        # assert when arr is int64 type
        assert optimize_num(arr.astype(np.int64)) is None

    def test_float(self):
        # test for optimization for float16
        arr = num_generator(np.float16, 100)
        # assert when not specifiy type for arr
        assert optimize_num(arr) == np.float16
        # assert when arr is float16 type
        assert optimize_num(arr.astype(np.float16)) is None

        # test for optimization for float32
        arr = num_generator(np.float32, 100)
        # assert when not specifiy type for arr
        assert optimize_num(arr) == np.float32
        # assert when arr is float32 type
        assert optimize_num(arr.astype(np.float32)) is None

        # test for optimization for float64
        arr = num_generator(np.float64, 100)
        # assert when not specifiy type for arr
        assert optimize_num(arr) is None


class TestIqr:
    """
    This class is to test iqr function from utils.py.
    """
    # first we will test all cases that cause errors
    def test_errors(self):
        # test for error when array is not numpy array
        with pytest.raises(TypeError):
            iqr(list(range(10)))

        # test for error when array is numpy non numarical
        with pytest.raises(ValueError):
            iqr(np.array(list(range(10))+['AA']))

        # test for error when array has nan values only
        with pytest.raises(ValueError):
            iqr(np.array([np.nan]*10))

    def test_with_outliers(self):
        # generate array with outliers
        arr_low = np.random.normal(0, 1, 9)
        arr_mid = np.random.normal(500, 1, 80)
        arr_high = np.random.normal(1000, 1, 11)
        # concatenate all in one array
        arr = np.concatenate((arr_low, arr_mid, arr_high))

        # arr will have 9 lower and 11 upper outlier, full arr size is 100
        assert all(iqr(arr) == [9, 11, 20, 20])

    def test_without_outliers(self):
        # take random uniform distribution array
        arr = np.random.uniform(0, 1, 100)
        assert iqr(arr) is None
