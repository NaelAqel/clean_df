"""This module contains the CleanDataFrame class, which is used to clean the
data in a Pandas DataFrame.
"""

# import modules
import pandas as pd
import numpy as np
import re
import missingno as msno
from IPython.display import display
from typing import Optional, Tuple
import matplotlib.pyplot as plt
import warnings
# import functions from utils.py
from .utils import optimize_num, iqr
# show all values in columns
pd.set_option('display.max_colwidth', None)


class CleanDataFrame:
    """
    CleanDataFrame
    ==============

    This class is used to clean and optimize a pandas dataframe for further
    analysis.

    :ivar df: The dataframe to be cleaned and optimized or after cleaning and
        optimization
    :vartype df: pandas.Dataframe
    :ivar max_num_cat: The maximum number of unique values in a column for it
        to be considered categorical
    :vartype max_num_cat: int
    :ivar unique_val_cols: List of the columns which have a unique value
    :vartype unique_val_cols: list
    :ivar duplicate_inds: List of the indices of duplicated rows
    :vartype duplicate_inds: list
    :ivar cols_to_optimize: A dictionary of all numerical columns that can be
        memory optimized, it will be {column name: optimized data type}
    :vartype cols_to_optimize: dict
    :ivar outliers: A dictionary for outliers details (list of four values) as
        {column name: outlier details} format, outliers details list have:
            - The number of lower outliers
            - The number of upper outliers
            - The total number of outliers
            - The percentage of the total number of values that are outliers
    :vartype outliers: dict
    :ivar missing_cols: A dictionary for missing details (list of two values)
        as {column name: missing details} format, missing details list have:
            - The total number of missing values
            - The percentage of the total number of values that are missing
    :vartype missing_cols: dict
    :ivar cat_cols: List of columns that can be converted to categorical type
    :vartype cat_cols: list
    :ivar num_cols: List of numerical columns
    :vartype num_cols: list
    """
    def __init__(self, df, max_num_cat=10) -> None:
        """Constructor for CleanDataFrame

        :param df: The dataframe to be cleaned and optimized
        :type df: pandas.Dataframe
        :param max_num_cat: The maximum number of unique values in a column
            for it to be considered categorical, default to 10
        :type max_num_cat: int, optional
        """
        # save df, and max_num_cat
        self._df = df
        self._max_num_cat = max_num_cat
        # set the other attributes
        self._update()

    # Only df and max_num_cat attributes can be changes from outside
    # (we will put both getter and setter methods for them).
    @property
    def df(self) -> pd.DataFrame:
        """Gets the value of df.

        :return: The value of df
        :rtype: pandas.Dataframe
        """
        return self._df

    @df.setter
    def df(self, value) -> None:
        """Sets the value of df.

        :param value: The new value of df
        :type value: int
        """
        self._df = value
        self._update()

    @property
    def max_num_cat(self) -> int:
        """Gets the value of max_num_cat.

        :return: The value of max_num_cat
        :rtype: int
        """
        return self._max_num_cat

    @max_num_cat.setter
    def max_num_cat(self, value) -> None:
        """Sets the value of max_num_cat.

        :param value: The new value of max_num_cat
        :type value: int
        """
        self._max_num_cat = value
        self._update()

    # all other attributes will have are read-only, so only have getter
    @property
    def unique_val_cols(self) -> list:
        """Gets the value of unique_val_cols.

        :return: The value of unique_val_cols
        :rtype: list
        """
        return self._unique_val_cols

    @property
    def duplicate_inds(self) -> list:
        """Gets the value of duplicate_inds.

        :return: The value of duplicate_inds
        :rtype: list
        """
        return self._duplicate_inds

    @property
    def cols_to_optimize(self) -> dict:
        """Gets the value of cols_to_optimize.

        :return: The value of cols_to_optimize
        :rtype: dict
        """
        return self._cols_to_optimize

    @property
    def outliers(self) -> dict:
        """Gets the value of outliers.

        :return: The value of outliers
        :rtype: dict
        """
        return self._outliers

    @property
    def missing_cols(self) -> dict:
        """Gets the value of missing_cols.

        :return: The value of missing_cols
        :rtype: dict
        """
        return self._missing_cols

    @property
    def cat_cols(self) -> list:
        """Gets the value of cat_cols.

        :return: The value of cat_cols
        :rtype: list
        """
        return self._cat_cols

    @property
    def num_cols(self) -> list:
        """Gets the value of num_cols.

        :return: The value of num_cols
        :rtype: list
        """
        return self._num_cols

    def _update(self) -> None:
        """Sets or updates all attributes for `CleanDataFrame` class.

        :raises TypeError: If `df` is not a pandas dataframe
        :raises ValueError: If `max_num_cat` is not a positive integer
        """
        # check that parameters are correct types and values
        if not isinstance(self._df, pd.DataFrame):
            raise TypeError("'df' should be a pandas DataFrame.")
        if (not isinstance(self._max_num_cat, int)) or self._max_num_cat < 0:
            raise ValueError("'max_num_cat' should be a positive integer.")

        # Convert dataframe to dictionary after removing all missing
        self._df_dict = {col: self._df[col].replace(
            'nan', np.nan).dropna().values for col in self._df.columns}

        # ~~~~~ Unique value columns ~~~~~
        self._unique_val_cols = [
            col for col in self._df.columns
            if len(np.unique(self._df_dict[col])) <= 1]
        # remove unique_val_cols from df columns and save them in _used_cols
        self._used_cols = list(set(self._df.columns).difference(
            set(self._unique_val_cols)))
        # to make sure that _used_cols have the same order of columns
        self._used_cols = [col for col in self._df.columns
                           if col in self._used_cols]
        # list if dataframe has columns with type 'category', to exclude it
        # as numpy can not deal with category datatype
        cols_cat_type = [col for col in self._used_cols
                         if self.df[col].dtype == 'category']
        # exclude cols_cat_type columns from _used_cols
        cols_without_cat = list(set(self._used_cols).difference(
            set(cols_cat_type)))
        # list all columns that can be categorical
        self._cat_cols = [col for col in cols_without_cat if (
            self._df[col].dtype == 'O') and len(
                set(self._df_dict[col])) <= self._max_num_cat]
        # list numerical columns that are not in unique_val_cols (note: numpy
        # considered datatime as numerical, so we exclude it datatime)
        self._num_cols = [col for col in cols_without_cat if np.issubdtype(
            self._df_dict[col].dtype.name, np.number) and not np.issubdtype(
                self._df_dict[col].dtype.name, '<m8[ns]')]

        # ~~~~~ Duplicated Rows ~~~~~
        self._duplicate_inds = [*self._df[self._df.duplicated(keep=False)
                                          ].index]

        # ~~~~~ Optimization of Columns ~~~~~
        self._cols_to_optimize = {
            col: optimize_num(self._df_dict[col]) for col in self._num_cols
            if optimize_num(self._df_dict[col]) is not None}

        # ~~~~~ Outliers ~~~~~
        self._outliers = {
            col: iqr(self._df[col].values) for col in self._num_cols
            if iqr(self._df[col].values) is not None}

        # ~~~~~ Missing Values ~~~~~
        self._missing_cols = {
            col: [self._df[col].replace('nan', np.nan).isna().sum(),
                  round(self._df[col].replace('nan', np.nan).isna().sum(
                      ) * 100 / len(self._df), 2)] for col in self._used_cols
            if self._df[col].replace('nan', np.nan).isna().sum() > 0}

    def report(self, show_matrix=True, show_heat=True, matrix_kws={},
               heat_kws={}) -> None:
        """Reports summary of the dataset, it includes:
            1. Columns with unique value report.
            2. Duplicated rows report.
            3. Columns' Datatype to optimize memory report.
            4. Outliers report.
            5. Missing values report.
        Each report will have a text massage, then show dataframe or plots
        if applicable.

        :param show_matrix: A flag to control whether to show the missing
            value matrix plot or not , defaults to True
        :type show_matrix: bool, optional
        :param heat_matrix: A flag to control whether to show the missing
            value heatmap plot or not , defaults to True
        :type heat_matrix: bool, optional
        :param matrix_kws: Keyword arguments passed to the missing value
            matrix plot, defaults to {}
        :type matrix_kws: dict, optional
        :param heat_kws: Keyword arguments passed to the missing value
            heatmap plot, defaults to {}
        :type heat_kws: dict, optional
        :raises TypeError: If any parameter has wrong type
        """
        # check parameters' type
        if (not isinstance(show_matrix, bool)) \
                or (not isinstance(show_heat, bool)):
            raise TypeError(
                "'show_heat' and 'show_matrix' should be boolean.")

        if (not isinstance(matrix_kws, dict)) \
                or (not isinstance(heat_kws, dict)):
            raise TypeError(
                "'matrix_kws' and 'heat_kws' should be a dictionary.")

        # ~~~~~~ Unique Value Columns Report ~~~~~~
        # print section header
        print(' Unique Value Columns '.center(79, '='))
        # call reporting function
        report_unique = self._unique_val_report()
        # print report
        print(report_unique, '\n')

        # ~~~~~~ Duplicated Rows Report ~~~~~~
        # print section header
        print(' Duplicated Rows '.center(79, '='))
        # call reporting function
        report_duplicated, data_duplicated = self._duplicated_report()
        # print report
        print(report_duplicated)
        # print data if applicable
        if data_duplicated is not None:
            display(data_duplicated)
        print('\n')

        # ~~~~~~ Optimization Columns Report ~~~~~~
        # print section header
        print(' Optimization Columns '.center(79, '='))
        # call reporting function
        report_num, report_cat, data_num = self._optimization_report()
        # print numerical columns report
        print(report_num)
        # print data if applicable
        if data_num is not None:
            display(data_num)
        # print categorical report if applicable
        if report_cat is not None:
            print(report_cat)
        print('\n')

        # ~~~~~~ Outliers Report ~~~~~~
        # print section header
        print(' Outliers '.center(79, '='))
        # call reporting function
        report_outliers, data_outliers = self._outliers_report()
        # print report
        print(report_outliers)
        # print data if applicable
        if data_outliers is not None:
            display(data_outliers)
        print('\n')

        # ~~~~~~ Missing Values Report ~~~~~~
        # print section header
        print(' Missing Values '.center(79, '='))
        # call reporting function
        report_missing, data_missing, matrix, heat = self._missing_report(
            show_matrix, show_heat, matrix_kws, heat_kws)
        # print report
        print(report_missing)
        # print date if applicable
        if data_missing is not None:
            display(data_missing)
            # plot matrix if applicable
            if matrix is not None:
                display(matrix)
            # plot heat if applicable
            if heat is not None:
                display(heat)

    def clean(self, min_missing_ratio=0.05, drop_nan=True, drop_kws={},
              drop_duplicates_kws={}) -> None:
        """This function drops columns that have a high ratio of missing
        values and duplicate rows in the dataframe

        :param min_missing_ratio: The minimum ratio of missing values for
            columns to drop, value should be between 0 and 1, defaults to 0.05
        :type min_missing_ratio: float, optional
        :param drop_nan: A flag to deceide wither drop any rows that contain
            missing values after dropping the columns which have above than
            `min_missing_ratio` missing values, defaults to True
        :type drop_nan: bool, optional
        :param drop_kws: Keyword arguments passed to `drop()` function,
            defaults to {}
        :type drop_kws: dict, optional
        :param drop_duplicates_kws: Keyword arguments passed to
            `drop_duplicates()` function, defaults to {}
        :type drop_duplicates_kws: dict, optional
        :raises TypeError: If `drop_nan` is not boolean
        :raises TypeError: If `drop_kws` or `drop_duplicates_kws` have wrong
            types
        :raises ValueError: If `min_missing_ratio` is not between 0 and 1
        :raises ValueError: If `drop_kws` or `drop_duplicates_kws` have a key
            `inplace`
        """
        # check if drop_nan is not boolean
        if not isinstance(drop_nan, bool):
            raise TypeError("'drop_nan' should be boolean.")
        # check the type of drop_kws or drop_duplicates_kws
        if (not isinstance(drop_kws, dict)) \
                or (not isinstance(drop_duplicates_kws, dict)):
            raise TypeError(
                "'drop_kws' and 'drop_duplicates_kws' should be dictionary.")

        # check min_missing_ratio value
        if min_missing_ratio > 1 or min_missing_ratio < 0 \
                or (not isinstance(min_missing_ratio, float)):
            raise ValueError("'min_missing_ratio' should be between 0 and 1.")

        # check if inplace in drop_kws or drop_duplicates_kws
        if 'inplace' in drop_kws.keys() or ('inplace'
                                            in drop_duplicates_kws.keys()):
            raise ValueError("'drop_kws' and 'drop_duplicates_kws' can not \
                have 'inplace' value, this function will automatically \
                    inplace them. So please delete 'inplace' key.")

        # define dropped_cols which are the columns to drop (unique_val_cols &
        # missing columns with missing values ratio above min_missing_ratio)
        dropped_cols = self._unique_val_cols + [
            col for col in self._missing_cols.keys()
            if self._missing_cols[col][1] >= 100 * min_missing_ratio]

        # copy dataframe to make the process
        df_copy = self._df.copy()
        # if there are columns to drop, drop them and update attributes
        if len(dropped_cols) > 0:
            df_copy.drop(columns=dropped_cols, inplace=True, **drop_kws)

        # if there are duplicated rows, drop them and update attribute
        if df_copy.duplicated().sum() > 0:
            df_copy.drop_duplicates(inplace=True, **drop_duplicates_kws)

        # if drop_nan is True, drop any row with nans
        if drop_nan:
            df_copy.dropna(inplace=True)

        # update df attribute
        self.df = df_copy

    def optimize(self) -> None:
        """This function optimizes the dataframe by converting columns to the
        desired data type and converting categorical columns to 'category'
        data type. Note that numerical columns should be free from missings.

        .. warnings also:: if any numerical column contain missing values
        """
        if self._cols_to_optimize != {} or len(self._cat_cols) > 0:
            # if there are columns to optimize, convert them to the optimized
            # data types, after copyting our dataframe
            df_copy = self._df.copy()
            cols_to_optimize = self._cols_to_optimize.keys()
            if len(cols_to_optimize) > 0:
                # check if columns have missings
                num_cols_missing = [
                    col for col in cols_to_optimize if df_copy[
                        col].isna().sum() > 0]
                # raise warning if there are missing columns
                if len(num_cols_missing) > 0:
                    warnings.warn(f'{num_cols_missing} contains missing '
                                  f'values, it will not be optimized.',
                                  UserWarning)
                    # update cols_to_optimize (remove num_cols_missing)
                    cols_to_optimize = list(set(cols_to_optimize).difference(
                        set(num_cols_missing)))
                # optimize inside df_copy
                for col in cols_to_optimize:
                    df_copy[col] = df_copy[col].values.astype(
                        self._cols_to_optimize[col])
            # if there are categorical columns, covert them to df_copy
            if len(self._cat_cols) > 0:
                # convert to categorical
                for col in self._cat_cols:
                    df_copy[col] = df_copy[col].astype('category')
            # now we will update df attribute
            self.df = df_copy

    def _unique_val_report(self) -> str:
        """Reports the columns with unique values.

        :returns: A string contains a `header` which explaining the report
            purpose and a `body` that show the details (as per the
            availability of unique value columns)
        :rtype: str
        """
        # define report header
        header = '- Checking if any column has a unique value ... '

        # check if there are columns with unique values to put in report body
        if len(self._unique_val_cols) > 0:
            body = f'\nThese columns has one value: {self._unique_val_cols}'
        else:
            body = 'No columns founded.'

        # return the unique values full report
        return header + body

    def _duplicated_report(self) -> Tuple[str, Optional[pd.DataFrame]]:
        """Reports the duplicated rows.

        :return: A tuple containing:
            - A string contains a `header` which explaining the report purpose
                and a `body` that show the details (as per the availability of
                duplicated rows)
            - A dataframe of duplicated rows, or None if no duplicated rows
        :rtype: tuple
        """
        # define report header
        header = '- Checking if data frame has duplicated rows ... '

        # check duplication to put in report body
        if len(self._duplicate_inds) > 0:
            body = (
                f'\nThe dataset has {len(self._duplicate_inds)} duplicated'
                f''' rows, which is {round(len(self._duplicate_inds
                )*100 / len(self._df), 2)}% from the dataset, duplicated '''
                'rows are:')
            data = self._df[self._df.duplicated(keep=False)]
        else:
            body = 'No duplications.'
            data = None

        # collect the msg from header and body
        msg = header + body
        # return the duplicated full report
        return msg, data

    def _optimization_report(self) -> Tuple[str, Optional[str],
                                            Optional[pd.DataFrame]]:
        """Reports the columns that can change datatypes for optimization.

        :return: A tuple containing:
            - A string contains a `header` which explaining the report purpose
                and a `body` that show the details (as per the availability of
                categorical columns to optimize)
            - A string contains details about columns that can be categorical,
                or None if no columns
            - A dataframe of columns optimization datatype details, or None if
                no columns to optimize
        :rtype: tuple
        """
        # define report header
        header = '- Checking datatypes to optimize memory ... '
        # assain data, msg_cat as None
        data, msg_cat = None, None

        # Checking if we have numeraical columns to optimize
        # Or columns that can be categorical
        if (self._cols_to_optimize != {}) | (len(self._cat_cols) > 0):
            # check if there are columns to optimize to put in body
            if self._cols_to_optimize != {}:
                # assign body
                body = '\nThese numarical columns can be down graded:'
                # convert data types as
                # {data type: list of columns that can convert to this type}
                optimize_dict = {
                    re.findall('\\.(\\w*)', str(to_type))[0]: ', '.join(
                        [col for col in self._cols_to_optimize.keys()
                         if self._cols_to_optimize[col] == to_type])
                    for to_type in set(self._cols_to_optimize.values())}
                # convert optimize_dict to dataframe and assign to data
                data = pd.DataFrame.from_dict(
                    optimize_dict, orient='index', columns=['columns'])
            if len(self._cat_cols) > 0:
                # if there are columns can be categorical, assign msg_cat
                msg_cat = ('\nThese columns can be converted to categorical:'
                           f' {self._cat_cols}.')
        else:
            # if no optimization, we will change msg, so when return, this
            # message will appear
            body = 'No columns to optimize.'

        # collect the msg from header and body
        msg = header + body
        # return the optimization full report
        return msg, msg_cat, data

    def _outliers_report(self) -> Tuple[str, Optional[pd.DataFrame]]:
        """Reports the outliers in columns.

        :returns: A tuple containing:
            - A string contains a `header` which explaining the report purpose
                and a `body` that show the details (as per the availability of
                outliers in columns)
            - A dataframe of outlier details in columns, or None if no
                outliers
        :rtype: tuple
        """
        # define report header
        header = '- Checking for outliers ... '

        # check outliers for report body
        if self._outliers != {}:
            body = '\nOutliers are:'
            # assign outliers in descending order dataframe
            data = pd.DataFrame.from_dict(
                self._outliers, orient='index', columns=[
                    'outliers_lower', 'outliers_upper', 'outliers_total',
                    'outliers_percentage']
                ).sort_values('outliers_total', ascending=False)
        else:
            body = 'No outliers.'
            data = None

        # collect the msg from header and body
        msg = header + body
        # return the outliers full report
        return msg, data

    def _missing_report(self, show_matrix, show_heat, matrix_kws, heat_kws)\
        -> Tuple[str, Optional[pd.DataFrame], Optional[plt.Axes],
                 Optional[plt.Axes]]:
        """Report the missing values with matrix and heat plot details.

        :param show_matrix: A flag to control whether to show the missing
            value matrix plot or not
        :type show_matrix: bool
        :param show_heat: A flag to control whether to show the missing value
            heatmap plot or not
        :type show_heat: bool
        :param matrix_kws: Keyword arguments passed to the missing value
            matrix plot
        :type matrix_kws: dict
        :param heat_kws: Keyword arguments passed to the missing value heatmap
            plot
        :type heat_kws: dict
        :return: A tuple containing:
            - A string contains a `header` which explaining the report purpose
                and a `body` that show the details (as per the availability of
                missing values)
            - A dataframe of missing values details, or None if no missings
            - A Matrix plot (from `missingno` backage) if there are missing
                values and show_matrix is True, or None otherwise
            - A Heat plot (from `missingno` backage) if there are missing
                values and show_heat is True, or None otherwise
        :rtype: tuple
        """
        # define report header
        header = '- Checking for missing values ... '
        # assaign data, matrix, heat as None
        data, matrix, heat = None, None, None

        # check missing values for body report
        if self._missing_cols != {}:
            # assign body value
            body = '\nMissing details are:'
            # select only columns with missing values to df
            df = self._df[self._missing_cols.keys()]
            # convert missing_cols to dataframe and show them
            data = pd.DataFrame.from_dict(
                self._missing_cols, orient='index', columns=[
                    'missing_counts', 'missing_percentage']).sort_values(
                'missing_counts', ascending=False)

            # if show_matrix is True, save matrix plot in matrix
            if show_matrix:
                sort_by = data.index[0]
                matrix = msno.matrix(df.sort_values(sort_by), **matrix_kws)

            # if show_heat is True, save heat plot in heat
            if show_heat:
                heat = msno.heatmap(df, **heat_kws)
        else:
            body = 'No missing values.'

        # collect the msg from header and body
        msg = header + body
        # return the missing full report
        return msg, data, matrix, heat
