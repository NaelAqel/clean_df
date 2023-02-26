"""Tests for `clean_df` package.
"""

# import modules
import pytest
from clean_df.clean_df import CleanDataFrame
from tests.data_generator import generate_df
import numpy as np
import pandas as pd
# fix numpy seed to 0
np.random.seed(0)


class TestCleanDataFrame:
    """This class will test :class:`CleanDataFrame` from `clean_df` package.
    """
    def setup_class(self):
        # initialize df to use in all tests
        self.df = generate_df(100)

    def setup_method(self, method):
        # intialize CleanDataFrame class to use in all tests
        self.cdf = CleanDataFrame(self.df, max_num_cat=5)

    def test_errors_and_warnings(self):
        def test_errors_init_method(self):
            # test for error when df is not a pandas Dataframe
            with pytest.raises(TypeError):
                CleanDataFrame(list(range(10)))
            # test for error when max_num_cat is not positive integer
            with pytest.raises(ValueError):
                CleanDataFrame(self.df, max_num_cat=-10)
            with pytest.raises(ValueError):
                CleanDataFrame(self.df, max_num_cat=10.5)

        def test_errors_report_method(self):
            # test for error when report parameters has wrong type
            with pytest.raises(TypeError):
                self.cdf.report(show_matrix=5)
            with pytest.raises(TypeError):
                self.cdf.report(show_heat=5)
            with pytest.raises(TypeError):
                self.cdf.report(matrix_kws=5)
            with pytest.raises(TypeError):
                self.cdf.report(heat_kws=5)

        def test_errors_clean_method(self):
            # test for error when clean parameters has wrong type
            with pytest.raises(TypeError):
                self.cdf.clean(drop_nan=5)
            with pytest.raises(TypeError):
                self.cdf.clean(drop_kws=5)
            with pytest.raises(TypeError):
                self.cdf.clean(drop_duplicates_kws=5)
            # test for error when clean parameters has wrong values
            with pytest.raises(ValueError):
                self.cdf.clean(min_missing_ratio=5)
            with pytest.raises(ValueError):
                self.cdf.clean(heat_kws={'inplace': True})
            with pytest.raises(ValueError):
                self.cdf.clean(drop_duplicates_kws={'inplace': True})

        def test_errors_change_read_only_attributes(self):
            with pytest.raises(AttributeError):
                self.cdf.unique_val_cols = 0
            with pytest.raises(AttributeError):
                self.cdf.duplicate_inds = 0
            with pytest.raises(AttributeError):
                self.cdf.cols_to_optimize = 0
            with pytest.raises(AttributeError):
                self.cdf.outliers = 0
            with pytest.raises(AttributeError):
                self.cdf.missing_cols = 0
            with pytest.raises(AttributeError):
                self.cdf.cat_cols = 0
            with pytest.raises(AttributeError):
                self.cdf.num_cols = 0

        def test_warning_missing_values_with_optimize_method(self):
            df1 = self.df.copy()
            cdf1 = CleanDataFrame(df1, max_num_cat=5)
            with pytest.warns(UserWarning):
                cdf1.optimize()

    def test_attributes_before_cleaning(self):
        # will check here all public attributes (before run any method)
        # assert df
        # assert pd.testing.assert_frame_equal(self.df, self.cdf.df)

        # assert max_num_cat
        assert self.cdf.max_num_cat == 5

        # assert unique_val_cols
        assert self.cdf.unique_val_cols == ['single_value', 'all_missing']

        # assert duplicate_inds
        assert self.cdf.duplicate_inds == [1, 2, 100, 101, 102]

        # assert cols_to_optimize
        assert self.cdf.cols_to_optimize == {
            'uint8': np.uint8, 'uint16': np.uint16, 'uint32': np.uint32,
            'uint64': np.uint64, 'int8': np.int8, 'int16': np.int16,
            'int32': np.int32, 'int64': np.int64, 'float16': np.float16,
            'float32': np.float32}

        # assert outliers
        assert self.cdf.outliers == {
            'uint8': [0, 2, 2, 1.94],  'uint16': [6, 2, 8, 7.77],
            'uint32': [6, 5, 11, 10.68], 'uint64': [1, 5, 6, 5.83],
            'int8': [4, 0, 4, 3.88], 'int16': [0, 1, 1, 0.97],
            'int32': [5, 5, 10, 9.71], 'int64': [6, 2, 8, 7.77],
            'float16': [4, 5, 9, 8.74], 'float32': [8, 0, 8, 7.77],
            'float64': [3, 6, 9, 8.74]}

        # assert missing_cols
        assert self.cdf.missing_cols == {
            'uint8': [4, 3.88], 'uint32': [6, 5.83], 'int16': [2, 1.94],
            'int32': [8, 7.77], 'date': [3, 2.91], 'cat3': [9, 8.74],
            'str2': [6, 5.83]}

        # assert cat_cols
        assert sorted(self.cdf.cat_cols) == ['cat1', 'cat2', 'cat3']

        # assert num_cols
        assert sorted(self.cdf.num_cols) == sorted([
            f'uint{x}' for x in [8, 16, 32, 64]] + [
                f'int{x}' for x in [8, 16, 32, 64]] + [f'float{x}' for x
                                                       in [16, 32, 64]])

    def test_clean_method(self):
        self.cdf.clean(min_missing_ratio=0.08)
        # assert the attributes which has changed after cleaning
        # assert unique_val_cols
        assert self.cdf.unique_val_cols == []

        # assert duplicate_inds
        assert self.cdf.duplicate_inds == []

        # assert cols_to_optimize
        assert self.cdf.cols_to_optimize == {
            'uint8': np.uint8, 'uint16': np.uint16, 'uint32': np.uint32,
            'uint64': np.uint64, 'int8': np.int8, 'int16': np.int16,
            'int32': np.int32, 'int64': np.int64, 'float16': np.float16,
            'float32': np.float32}

        # assert outliers
        assert self.cdf.outliers == {
            'uint8': [0, 4, 4, 5.06],  'uint16': [1, 2, 3, 3.8],
            'uint32': [4, 4, 8, 10.13], 'uint64': [4, 4, 8, 10.13],
            'int8': [4, 2, 6, 7.59], 'int16': [0, 1, 1, 1.27],
            'int32': [2, 4, 6, 7.59], 'int64': [1, 2, 3, 3.8],
            'float16': [2, 4, 6, 7.59], 'float32': [3, 1, 4, 5.06],
            'float64': [0, 5, 5, 6.33]}

        # assert missing_cols
        assert self.cdf.missing_cols == {}

        # assert cat_cols
        assert sorted(self.cdf.cat_cols) == ['cat1', 'cat2']

        # assert num_cols
        assert sorted(self.cdf.num_cols) == sorted([
            f'uint{x}' for x in [8, 16, 32, 64]] + [
                f'int{x}' for x in [8, 16, 32, 64]] + [f'float{x}' for x
                                                       in [16, 32, 64]])

    def test_optimize_method_after_call_clean_method(self):
        self.cdf.clean(min_missing_ratio=0.08)
        self.cdf.optimize()
        # assert the attributes which has changed after optimization
        # assert unique_val_cols
        assert self.cdf.unique_val_cols == []

        # assert duplicate_inds
        assert self.cdf.duplicate_inds == []

        # assert cols_to_optimize
        assert self.cdf.cols_to_optimize == {}

        # assert outliers
        assert self.cdf.outliers == {
            'uint8': [0, 4, 4, 5.06],  'uint16': [1, 2, 3, 3.8],
            'uint32': [4, 4, 8, 10.13], 'uint64': [4, 4, 8, 10.13],
            'int8': [4, 2, 6, 7.59], 'int16': [0, 1, 1, 1.27],
            'int32': [2, 4, 6, 7.59], 'int64': [1, 2, 3, 3.8],
            'float16': [2, 4, 6, 7.59], 'float32': [3, 1, 4, 5.06],
            'float64': [0, 5, 5, 6.33]}

        # assert missing_cols
        assert self.cdf.missing_cols == {}

        # assert cat_cols
        assert sorted(self.cdf.cat_cols) == []

        # assert num_cols
        assert sorted(self.cdf.num_cols) == sorted([
            f'uint{x}' for x in [8, 16, 32, 64]] + [
                f'int{x}' for x in [8, 16, 32, 64]] + [f'float{x}' for x
                                                       in [16, 32, 64]])
