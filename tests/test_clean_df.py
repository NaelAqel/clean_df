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
    """
    This class will test :class:`CleanDataFrame` from `clean_df` package.
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

    def test_change_attributes(self):
        df1 = self.df.copy()
        cdf1 = CleanDataFrame(df1, max_num_cat=5)
        # check attribute values
        pd.testing.assert_frame_equal(df1, cdf1.df)
        assert cdf1.max_num_cat == 5

        def test_change_df(self):
            cdf1.df = df1.head(10)
            pd.testing.assert_frame_equal(df1.head(10), cdf1.df)

        def test_change_max_num_cat(self):
            cdf1.max_num_cat = 10
            assert cdf1.max_num_cat == 10

        def test_change_column_name(self):
            cdf1.df.columns = ['col_1'] + [*df1.columns[1:]]
            assert cdf1.df.columns[0] == 'col_1'

    def test_attributes_before_cleaning(self):
        # will check here all public attributes (before run any method)
        # assert df
        pd.testing.assert_frame_equal(self.df, self.cdf.df)

        # assert max_num_cat
        assert self.cdf.max_num_cat == 5

        # assert duplicate_inds
        assert all(self.cdf.duplicate_inds == [1, 2, 100, 101, 102])

        # assert cols_to_optimize
        assert self.cdf.cols_to_optimize == {
            'uint8': np.uint8, 'uint16': np.uint16, 'uint32': np.uint32,
            'uint64': np.uint64, 'int8': np.int8, 'int16': np.int16,
            'int32': np.int32, 'int64': np.int64, 'float16': np.float16,
            'float32': np.float32}

        # assert outliers
        true_vals = {'uint8': [0.0, 2.0, 2.0, 1.94],
                     'uint16': [6.0, 2.0, 8.0, 7.77],
                     'uint32': [6.0, 5.0, 11.0, 10.68],
                     'uint64': [1.0, 5.0, 6.0, 5.83],
                     'int8': [4.0, 0.0, 4.0, 3.88],
                     'int16': [0.0, 1.0, 1.0, 0.97],
                     'int32': [5.0, 5.0, 10.0, 9.71],
                     'int64': [6.0, 2.0, 8.0, 7.77],
                     'float16': [4.0, 5.0, 9.0, 8.74],
                     'float32': [8.0, 0.0, 8.0, 7.77],
                     'float64': [3.0, 6.0, 9.0, 8.74]}
        # check the keys are equal
        assert sorted([*true_vals.keys()]) == sorted(
            [*self.cdf.outliers.keys()])
        # check values
        for col in true_vals.keys():
            assert all(self.cdf.outliers[col] == true_vals[col])

        # assert missing_cols
        true_vals = {
            'uint8': [4, 3.88], 'uint32': [6, 5.83], 'int16': [2, 1.94],
            'int32': [8, 7.77], 'date': [3, 2.91], 'cat3': [9, 8.74],
            'str2': [6, 5.83]}
        # check the keys are equal
        assert sorted([*true_vals.keys()]) == sorted(
            [*self.cdf.missing_cols.keys()])
        # check values
        for col in true_vals.keys():
            assert all(self.cdf.missing_cols[col] == true_vals[col])

        # assert cat_cols
        true_vals = {'cat3': ['PfqAFgzlr', 'thYMdEL'],
                     'cat2': ['bcqclFkuK', 'fHCUMX'],
                     'cat1': ['SLscfDLKQ', 'lX']}
        # check the keys are equal
        assert sorted([*true_vals.keys()]) == sorted(
            [*self.cdf.cat_cols.keys()])
        # check values
        for col in true_vals.keys():
            assert all(np.sort(self.cdf.cat_cols[col]
                               ) == np.sort(true_vals[col]))

        # assert num_cols
        assert all(np.sort(self.cdf.num_cols) == np.sort(np.array([
            f'uint{x}' for x in [8, 16, 32, 64]] + [
                f'int{x}' for x in [8, 16, 32, 64]] + [f'float{x}' for x
                                                       in [16, 32, 64]])))

    def test_clean_method_with_false_drop_nan(self):
        self.cdf.clean(min_missing_ratio=0.085, drop_nan=False)
        # assert the attributes which has changed after cleaning
        # assert duplicate_inds
        assert len(self.cdf.duplicate_inds) == 0

        # assert cols_to_optimize
        assert self.cdf.cols_to_optimize == {
            'uint8': np.uint8, 'uint16': np.uint16, 'uint32': np.uint32,
            'uint64': np.uint64, 'int8': np.int8, 'int16': np.int16,
            'int32': np.int32, 'int64': np.int64, 'float16': np.float16,
            'float32': np.float32}

        # assert outliers
        true_vals = {'uint8': [0.0, 2.0, 2.0, 2.0],
                     'uint16': [3.0, 2.0, 5.0, 5.0],
                     'uint32': [5.0, 5.0, 10.0, 10.0],
                     'uint64': [2.0, 5.0, 7.0, 7.0],
                     'int8': [3.0, 0.0, 3.0, 3.0],
                     'int16': [0.0, 1.0, 1.0, 1.0],
                     'int32': [3.0, 5.0, 8.0, 8.0],
                     'int64': [3.0, 2.0, 5.0, 5.0],
                     'float16': [4.0, 5.0, 9.0, 9.0],
                     'float32': [5.0, 1.0, 6.0, 6.0],
                     'float64': [1.0, 6.0, 7.0, 7.0]}
        # check the keys are equal
        assert sorted([*true_vals.keys()]) == sorted(
            [*self.cdf.outliers.keys()])
        # check values
        for col in true_vals.keys():
            assert all(self.cdf.outliers[col] == true_vals[col])

        # assert missing_cols
        true_vals = {
            'uint8': [3, 3], 'uint32': [4, 4], 'int16': [2, 2],
            'int32': [8, 8], 'date': [3, 3], 'str2': [6, 6]}
        # check the keys are equal
        assert sorted([*true_vals.keys()]) == sorted(
            [*self.cdf.missing_cols.keys()])
        # check values
        for col in true_vals.keys():
            assert all(self.cdf.missing_cols[col] == true_vals[col])

        # assert cat_cols
        true_vals = {'cat2': ['bcqclFkuK', 'fHCUMX'],
                     'cat1': ['SLscfDLKQ', 'lX']}
        # check the keys are equal
        assert sorted([*true_vals.keys()]) == sorted(
            [*self.cdf.cat_cols.keys()])
        # check values
        for col in true_vals.keys():
            assert all(np.sort(self.cdf.cat_cols[col]
                               ) == np.sort(true_vals[col]))

        # assert num_cols
        assert all(np.sort(self.cdf.num_cols) == np.sort(np.array([
            f'uint{x}' for x in [8, 16, 32, 64]] + [
                f'int{x}' for x in [8, 16, 32, 64]] + [f'float{x}' for x
                                                       in [16, 32, 64]])))

    def test_clean_method_with_true_drop_nan(self):
        self.cdf.clean(min_missing_ratio=0.085)
        # assert the attributes which has changed after cleaning
        # assert duplicate_inds
        assert len(self.cdf.duplicate_inds) == 0

        # assert cols_to_optimize
        assert self.cdf.cols_to_optimize == {
            'uint8': np.uint8, 'uint16': np.uint16, 'uint32': np.uint32,
            'uint64': np.uint64, 'int8': np.int8, 'int16': np.int16,
            'int32': np.int32, 'int64': np.int64, 'float16': np.float16,
            'float32': np.float32}

        # assert outliers
        true_vals = {
            'uint8': [0, 4, 4, 5.06],  'uint16': [1, 2, 3, 3.8],
            'uint32': [4, 4, 8, 10.13], 'uint64': [4, 4, 8, 10.13],
            'int8': [4, 2, 6, 7.59], 'int16': [0, 1, 1, 1.27],
            'int32': [2, 4, 6, 7.59], 'int64': [1, 2, 3, 3.8],
            'float16': [2, 4, 6, 7.59], 'float32': [3, 1, 4, 5.06],
            'float64': [0, 5, 5, 6.33]}
        # check the keys are equal
        assert sorted([*true_vals.keys()]) == sorted(
            [*self.cdf.outliers.keys()])
        # check values
        for col in true_vals.keys():
            assert all(self.cdf.outliers[col] == true_vals[col])

        # assert missing_cols
        assert self.cdf.missing_cols == {}

        # assert cat_cols
        true_vals = {'cat2': ['bcqclFkuK', 'fHCUMX'],
                     'cat1': ['SLscfDLKQ', 'lX']}
        # check the keys are equal
        assert sorted([*true_vals.keys()]) == sorted(
            [*self.cdf.cat_cols.keys()])
        # check values
        for col in true_vals.keys():
            assert all(np.sort(self.cdf.cat_cols[col]
                               ) == np.sort(true_vals[col]))

        # assert num_cols
        assert all(np.sort(self.cdf.num_cols) == np.sort(np.array([
            f'uint{x}' for x in [8, 16, 32, 64]] + [
                f'int{x}' for x in [8, 16, 32, 64]] + [f'float{x}' for x
                                                       in [16, 32, 64]])))

    def test_optimize_method_after_call_clean_method(self):
        self.cdf.clean(min_missing_ratio=0.085)
        self.cdf.optimize()
        # assert the attributes which has changed after optimization
        # assert duplicate_inds
        assert len(self.cdf.duplicate_inds) == 0

        # assert cols_to_optimize
        assert self.cdf.cols_to_optimize == {}

        # assert outliers
        true_vals = {'uint8': [0.0, 4.0, 4.0, 5.06],
                     'uint16': [1.0, 2.0, 3.0, 3.8],
                     'uint32': [4.0, 4.0, 8.0, 10.13],
                     'uint64': [4.0, 4.0, 8.0, 10.13],
                     'int8': [4.0, 2.0, 6.0, 7.59],
                     'int16': [0.0, 1.0, 1.0, 1.27],
                     'int32': [2.0, 4.0, 6.0, 7.59],
                     'int64': [1.0, 2.0, 3.0, 3.8],
                     'float16': [2.0, 4.0, 6.0, 7.59],
                     'float32': [3.0, 1.0, 4.0, 5.06],
                     'float64': [0.0, 5.0, 5.0, 6.33]}
        # check the keys are equal
        assert sorted([*true_vals.keys()]) == sorted(
            [*self.cdf.outliers.keys()])
        # check values
        for col in true_vals.keys():
            assert all(self.cdf.outliers[col] == true_vals[col])

        # assert missing_cols
        assert self.cdf.missing_cols == {}

        # assert cat_cols
        assert self.cdf.cat_cols == {}

        # assert num_cols
        assert sorted(self.cdf.num_cols) == sorted([
            f'uint{x}' for x in [8, 16, 32, 64]] + [
                f'int{x}' for x in [8, 16, 32, 64]] + [f'float{x}' for x
                                                       in [16, 32, 64]])
