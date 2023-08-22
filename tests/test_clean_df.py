"""Tests for `clean_df` package.
"""

# import modules
import pytest
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from PIL import Image
from skimage.metrics import structural_similarity
from clean_df.clean_df import CleanDataFrame
from tests.data_generator import generate_df
from tests.report_generator import report_generator


class TestCleanDataFrame:
    """
    This class will test :class:`CleanDataFrame` from `clean_df` package.
    """
    def setup_class(self):
        # fix numpy seed to 0, so everytime will generate the same dataframe
        np.random.seed(0)
        # initialize df to use in all tests
        self.df = generate_df(100)
        # initialize the true (expected) values
        self.duplicate_inds = np.array([1, 2, 100, 101, 102])
        self.cols_to_optimize = {
            'uint8': np.uint8, 'uint16': np.uint16, 'uint32': np.uint32,
            'uint64': np.uint64, 'int8': np.int8, 'int16': np.int16,
            'int32': np.int32, 'int64': np.int64, 'float16': np.float16,
            'float32': np.float32}
        self.cat_cols = {'cat1': ['SLscfDLKQ', 'lX'],
                         'cat2': ['fHCUMX', 'bcqclFkuK'],
                         'cat3': ['PfqAFgzlr', 'thYMdEL']}
        self.outliers = {
            'uint32': [6, 5, 11, 10.68], 'int32': [5, 5, 10, 9.71],
            'float16': [4, 5, 9, 8.74], 'float64': [3, 6, 9, 8.74],
            'uint16': [6, 2, 8, 7.77], 'int64': [6, 2, 8, 7.77],
            'float32': [8, 0, 8, 7.77], 'uint64': [1, 5, 6, 5.83],
            'int8': [4, 0, 4, 3.88], 'uint8': [0, 2, 2, 1.94],
            'int16': [0, 1, 1, 0.97]}
        self.missing_cols = {
            'cat3': [9, 8.74], 'int32': [8, 7.77], 'uint32': [6, 5.83],
            'str2': [6, 5.83], 'uint8': [4, 3.88], 'date': [3, 2.91],
            'int16': [2, 1.94]}
        self.num_cols = np.array([
            f'uint{x}' for x in [8, 16, 32, 64]] + [
                f'int{x}' for x in [8, 16, 32, 64]] + [f'float{x}' for x
                                                       in [16, 32, 64]])

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

    def test_before_cleaning(self, capsys):
        # We will check attributes, report and plots before any optimization
        # check all attributes using attributes_checking method
        self.attributes_checking()

        df_duplicated = self.df.iloc[[1, 2, 100, 101, 102]]

        # captrue report
        self.cdf.report(show_matrix=False, show_heat=False)
        captured = capsys.readouterr()

        # generate expected report
        expected = report_generator(
            len_duplicate=5, len_df=103, df_duplicate=df_duplicated,
            cat_cols=self.cat_cols, cols_to_optimize=self.cols_to_optimize,
            outliers=self.outliers, missing_cols=self.missing_cols)

        # Assert captured and expected
        assert captured.out == expected

        # check both report plots
        self.plots_checking(test_stage='before_cleaning', show_matrix=True)
        self.plots_checking(test_stage='before_cleaning', show_heat=True)

    def test_clean_method_with_false_drop_nan(self, capsys):
        # We will check attributes, report & plots after clean False drop_nan
        self.cdf.clean(min_missing_ratio=0.085, drop_nan=False)

        # first, we will update expected values attributes
        self.duplicate_inds = np.array([])
        self.cat_cols = {'cat1': ['SLscfDLKQ', 'lX'],
                         'cat2': ['fHCUMX', 'bcqclFkuK']}
        self.outliers = {
            'uint32': [5, 5, 10, 10], 'float16': [4, 5, 9, 9],
            'int32': [3, 5, 8, 8], 'uint64': [2, 5, 7, 7],
            'float64': [1, 6, 7, 7], 'float32': [5, 1, 6, 6],
            'uint16': [3, 2, 5, 5], 'int64': [3, 2, 5, 5],
            'int8': [3, 0, 3, 3], 'uint8': [0, 2, 2, 2],
            'int16': [0, 1, 1, 1]}
        self.missing_cols = {
            'int32': [8, 8], 'str2': [6, 6], 'uint32': [4, 4],
            'uint8': [3, 3], 'date': [3, 3], 'int16': [2, 2]}

        # check all attributes using attributes_checking method
        self.attributes_checking()

        # captrue report
        self.cdf.report(show_matrix=False, show_heat=False)
        captured = capsys.readouterr()

        # generate expected report
        expected = report_generator(
            is_duplicate=False, cols_to_optimize=self.cols_to_optimize,
            cat_cols=self.cat_cols, outliers=self.outliers,
            missing_cols=self.missing_cols)

        # Assert captured and expected
        assert captured.out == expected

        # check both report plots
        self.plots_checking(test_stage='after_cleaning_false_drop_nan',
                            show_matrix=True)
        self.plots_checking(test_stage='after_cleaning_false_drop_nan',
                            show_heat=True)

    def test_clean_method_with_true_drop_nan(self, capsys):
        # We will check attributes, report & plots after clean True drop_nan
        self.cdf.clean(min_missing_ratio=0.085)

        # first, we will update expected values attributes
        self.duplicate_inds = np.array([])
        self.cat_cols = {'cat1': ['SLscfDLKQ', 'lX'],
                         'cat2': ['fHCUMX', 'bcqclFkuK']}
        self.outliers = {
            'uint32': [4, 4, 8, 10.13], 'uint64': [4, 4, 8, 10.13],
            'int8': [4, 2, 6, 7.59], 'int32': [2, 4, 6, 7.59],
            'float16': [2, 4, 6, 7.59], 'float64': [0, 5, 5, 6.33],
            'uint8': [0, 4, 4, 5.06], 'float32': [3, 1, 4, 5.06],
            'uint16': [1, 2, 3, 3.8], 'int64': [1, 2, 3, 3.8],
            'int16': [0, 1, 1, 1.27]}
        self.missing_cols = {}

        # check all attributes using attributes_checking method
        self.attributes_checking()

        # captrue report
        self.cdf.report(show_matrix=False, show_heat=False)
        captured = capsys.readouterr()

        # generate expected report
        expected = report_generator(
            is_duplicate=False, cols_to_optimize=self.cols_to_optimize,
            cat_cols=self.cat_cols, outliers=self.outliers, is_missing=False)

        # Assert captured and expected
        assert captured.out == expected

    def test_optimize_method(self, capsys):
        # We will check attributes, report & plots after optimize method
        self.cdf.optimize()

        # first, we will update expected values attributes
        self.duplicate_inds = np.array([])
        self.cols_to_optimize = {}
        self.cat_cols = {}
        self.outliers = {
            'uint32': [4, 4, 8, 10.13], 'uint64': [4, 4, 8, 10.13],
            'int8': [4, 2, 6, 7.59], 'int32': [2, 4, 6, 7.59],
            'float16': [2, 4, 6, 7.59], 'float64': [0, 5, 5, 6.33],
            'uint8': [0, 4, 4, 5.06], 'float32': [3, 1, 4, 5.06],
            'uint16': [1, 2, 3, 3.8], 'int64': [1, 2, 3, 3.8],
            'int16': [0, 1, 1, 1.27]}
        self.missing_cols = {}

        # check all attributes using attributes_checking method
        self.attributes_checking()

        # captrue report
        self.cdf.report(show_matrix=False, show_heat=False)
        captured = capsys.readouterr()

        # generate expected report
        expected = report_generator(
            is_duplicate=False, is_num_opt=False, is_cat_opt=False,
            outliers=self.outliers, is_missing=False)

        # Assert captured and expected
        assert captured.out == expected

    def attributes_checking(self):
        # This method will check all public attributes
        # assert df
        pd.testing.assert_frame_equal(self.df, self.cdf.df)

        # assert max_num_cat
        assert self.cdf.max_num_cat == 5

        # assert duplicate_inds
        assert all(self.cdf.duplicate_inds == self.duplicate_inds)

        # assert cols_to_optimize
        assert self.cdf.cols_to_optimize == self.cols_to_optimize

        # assert cat_cols
        # check the keys are equal
        assert sorted([*self.cdf.cat_cols.keys()]) == sorted(
            [*self.cat_cols.keys()])
        # check values
        for col in self.cat_cols.keys():
            assert all(np.sort(self.cdf.cat_cols[col]
                               ) == np.sort(self.cat_cols[col]))

        # assert outliers
        # check the keys are equal
        assert sorted([*self.cdf.outliers.keys()]) == sorted(
            [*self.outliers.keys()])
        # check values
        for col in self.outliers.keys():
            assert all(self.cdf.outliers[col] == self.outliers[col])

        # assert missing_cols
        # check the keys are equal
        assert sorted([*self.missing_cols.keys()]) == sorted(
            [*self.cdf.missing_cols.keys()])
        # check values
        for col in self.missing_cols.keys():
            assert all(self.cdf.missing_cols[col] == self.missing_cols[col])

        # assert num_cols
        assert all(np.sort(self.cdf.num_cols) == np.sort(self.num_cols))

    def plots_checking(self, test_stage, show_matrix=False, show_heat=False):
        # save the current directory
        main_script_dir = os.path.dirname(__file__)

        # generate and save captured plot from report
        self.cdf.report(show_matrix=show_matrix, show_heat=show_heat)
        plt.savefig(os.path.join(main_script_dir, 'img/captured.png'),
                    bbox_inches='tight')

        # prepare the relative links
        plot_to_test = 'matrix' if show_matrix else 'heat'
        rel_path = f'img/{test_stage}_{plot_to_test}.png'

        # load both images as numpy gray scale arrays
        captured = np.array(Image.open(
            os.path.join(main_script_dir, 'img/captured.png')).convert('L'))

        expected = np.array(Image.open(os.path.join(main_script_dir, rel_path)
                                       ).convert('L'))

        # assert that the two photos are the same (we will give some small
        # tolerence due to structural_similarity propeties)
        assert structural_similarity(captured, expected) >= 0.995
