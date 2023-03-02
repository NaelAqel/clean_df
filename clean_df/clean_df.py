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
    This class is used to clean and optimize a pandas dataframe for further
    analysis.

    Attributes
    ----------
    df : pandas.DataFrame
        The dataframe to be cleaned and optimized or after cleaning and
        optimization.
    max_num_cat : int
        The maximum number of unique values in a column for it to be
        considered categorical.
    unique_val_cols : list of str, readonly
        List of the columns which have a unique value.
    duplicate_inds : list of int, readonly
        List of the indices of duplicated rows.
    cols_to_optimize : dict, readonly
        A dictionary of all numerical columns that can be memory optimized, it
        will be {column name: optimized data type}.
    outliers : dict, readonly
        A dictionary for outliers details in a list as {column name: outlier
        details} format, the list has:
            - The number of lower outliers
            - The number of upper outliers
            - The total number of outliers
            - The percentage of the total values that are outliers
    missing_cols : dict, readonly
        A dictionary for missing details in a list as {column name: missing
        details} format, the list has:
            - The total number of missing values
            - The percentage of the total values that are missing
    cat_cols : dict, readonly
        A dictionary for columns that can convert to categiorical type as
        {column name: list of unique values} format.
    num_cols : list of str, readonly
        List of numerical columns.

    Methods
    -------
    __init__(self, df, max_num_cat=10) -> None:
        Constructor for CleanDataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe to be cleaned and optimized.
        max_num_cat : int, optional
            The maximum number of unique values in a column for it to be
            considered categorical, defaults to 10.
    report(self, show_matrix=True, show_heat=True, matrix_kws={}, \
        heat_kws={}) -> None:
        Generate a summary report of the dataset, including:
            1. Columns with unique value report.
            2. Duplicated rows report.
            3. Columns' Datatype to optimize memory report.
            4. Columns to convert to categorical report.
            5. Outliers report.
            6. Missing values report.
        Each report will have a text message, then show a dataframe or plots
        if applicable.

        Parameters
        ----------
        show_matrix : bool, optional
            A flag to control whether to show the missing value matrix plot
            or not, defaults to True.
        heat_matrix : bool, optional
            A flag to control whether to show the missing value heatmap plot
            or not, defaults to True.
        matrix_kws : dict, optional
            Keyword arguments passed to the missing value matrix plot,
            defaults to {}.
        heat_kws : dict, optional
            Keyword arguments passed to the missing value heatmap plot,
            defaults to {}.

        Raises
        ------
        TypeError
            If any parameter has the wrong type.
    clean(self, min_missing_ratio=0.05, drop_nan=True, drop_kws={}, \
        drop_duplicates_kws={}) -> None:
        Drops columns with a high ratio of missing values and duplicate rows.

        Parameters
        ----------
        min_missing_ratio : float, optional
            The minimum ratio of missing values for columns to drop. Value
            should be between 0 and 1. Defaults to 0.05.
        drop_nan : bool, optional
            A flag to decide whether to drop any rows that contain missing
            values after dropping the columns with above `min_missing_ratio`
            missing values. Defaults to True.
        drop_kws : dict, optional
            Keyword arguments passed to the `drop()` function. Defaults to {}.
        drop_duplicates_kws : dict, optional
            Keyword arguments passed to the `drop_duplicates()` function.
            Defaults to {}.

        Raises
        ------
        TypeError
            If `drop_nan` is not boolean, or if `drop_kws` or
            `drop_duplicates_kws` have the wrong types.
        ValueError
            If `min_missing_ratio` is not between 0 and 1, or if `drop_kws`
            or `drop_duplicates_kws` have a key `inplace`.
    optimize(self) -> None:
        Optimizes the dataframe by converting columns to the desired data type
        and converting categorical columns to 'category' data type. Note that
        numerical columns should not contain missing values.

        Raises
        ------
        Warning
            If any numerical column contains missing values.
    """
    def __init__(self, df, max_num_cat=10) -> None:
        """
        Constructor for CleanDataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe to be cleaned and optimized.
        max_num_cat : int, optional
            The maximum number of unique values in a column for it to be
            considered categorical, defaults to 10.
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
        """
        Get the value of df.

        Returns
        -------
        pandas.DataFrame
            The value of df.
        """
        return self._df

    @df.setter
    def df(self, value) -> None:
        """
        Set the value of df.

        Parameters
        ----------
        value : pandas.DataFrame
            The new value of df.
        """
        self._df = value
        self._update()

    # add this setter to update all attributes if we change column names
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'df' or name in self._df.columns:
            self._update()

    @property
    def max_num_cat(self) -> int:
        """
        Get the value of max_num_cat.

        Returns
        -------
        int
            The value of max_num_cat.
        """
        return self._max_num_cat

    @max_num_cat.setter
    def max_num_cat(self, value) -> None:
        """
        Set the value of max_num_cat.

        Parameters
        ----------
        value : int
            The new value of max_num_cat.
        """
        self._max_num_cat = value
        self._update()

    # all other attributes will have are read-only, so only have getter
    @property
    def unique_val_cols(self) -> list:
        """
        Get the value of unique_val_cols.

        Returns
        -------
        list
            The value of unique_val_cols.
        """
        return self._unique_val_cols

    @property
    def duplicate_inds(self) -> list:
        """
        Get the value of duplicate_inds.

        Returns
        -------
        list
            The value of duplicate_inds.
        """
        return self._duplicate_inds

    @property
    def cols_to_optimize(self) -> dict:
        """
        Get the value of cols_to_optimize.

        Returns
        -------
        dict
            The value of cols_to_optimize.
        """
        return self._cols_to_optimize

    @property
    def outliers(self) -> dict:
        """
        Get the value of outliers.

        Returns
        -------
        dict
            The value of outliers.
        """
        return self._outliers

    @property
    def missing_cols(self) -> dict:
        """
        Get the value of missing_cols.

        Returns
        -------
        dict
            The value of missing_cols.
        """
        return self._missing_cols

    @property
    def cat_cols(self) -> list:
        """
        Get the value of cat_cols.

        Returns
        -------
        list
            The value of cat_cols.
        """
        return self._cat_cols

    @property
    def num_cols(self) -> list:
        """
        Get the value of num_cols.

        Returns
        -------
        list
            The value of num_cols.
        """
        return self._num_cols

    def _update(self) -> None:
        """
        Set or update all attributes for the CleanDataFrame class.

        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe to be cleaned and optimized.
        max_num_cat : int
            The maximum number of unique values in a column for it to be
            considered categorical.

        Raises
        ------
        TypeError
            If `df` is not a pandas dataframe.
        ValueError
            If `max_num_cat` is not a positive integer.
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
        self._cat_cols = {col: [*np.unique(self._df_dict[col])]
                          for col in cols_without_cat if (
            self._df[col].dtype == 'O') and len(
            set(self._df_dict[col])) <= self._max_num_cat}
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
        """
        Generate a summary report of the dataset, including:
            1. Columns with unique value report.
            2. Duplicated rows report.
            3. Columns' Datatype to optimize memory report.
            4. Columns to convert to categorical report.
            5. Outliers report.
            6. Missing values report.
        Each report will have a text message, then show a dataframe or plots
        if applicable.

        Parameters
        ----------
        show_matrix : bool, optional
            A flag to control whether to show the missing value matrix plot
            or not, defaults to True.
        heat_matrix : bool, optional
            A flag to control whether to show the missing value heatmap plot
            or not, defaults to True.
        matrix_kws : dict, optional
            Keyword arguments passed to the missing value matrix plot,
            defaults to {}.
        heat_kws : dict, optional
            Keyword arguments passed to the missing value heatmap plot,
            defaults to {}.

        Raises
        ------
        TypeError
            If any parameter has the wrong type.
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
        report_optimize, data_optimize = self._optimization_report()
        # print optimization columns report
        print(report_optimize)
        # print data if applicable
        if data_optimize is not None:
            display(data_optimize)
        print('\n')

        # ~~~~~~ Categorical Columns Report ~~~~~~
        print(' Categorical Columns '.center(79, '='))
        # call reporting function
        report_cat, data_cat = self._cat_report()
        # print categorical columns report
        print(report_cat)
        # print data if applicable
        if data_cat is not None:
            display(data_cat)
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
        """
        Drops columns with a high ratio of missing values and duplicate rows.

        Parameters
        ----------
        min_missing_ratio : float, optional
            The minimum ratio of missing values for columns to drop. Value
            should be between 0 and 1. Defaults to 0.05.
        drop_nan : bool, optional
            A flag to decide whether to drop any rows that contain missing
            values after dropping the columns with above `min_missing_ratio`
            missing values. Defaults to True.
        drop_kws : dict, optional
            Keyword arguments passed to the `drop()` function. Defaults to {}.
        drop_duplicates_kws : dict, optional
            Keyword arguments passed to the `drop_duplicates()` function.
            Defaults to {}.

        Raises
        ------
        TypeError
            If `drop_nan` is not boolean, or if `drop_kws` or
            `drop_duplicates_kws` have the wrong types.
        ValueError
            If `min_missing_ratio` is not between 0 and 1, or if `drop_kws`
            or `drop_duplicates_kws` have a key `inplace`.
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
            # update all related attributes
            self._unique_val_cols = []
            self._used_cols = list(set(self._used_cols).difference(set(
                dropped_cols)))
            # to make sure that _used_cols is the same df order
            self._used_cols = [col for col in self._df.columns
                               if col in self._used_cols]
            self._num_cols = list(set(self._num_cols).difference(set(
                dropped_cols)))
            for col in dropped_cols:
                self._df_dict.pop(col, None)
                self._cat_cols.pop(col, None)
                self._cols_to_optimize.pop(col, None)
                self._outliers.pop(col, None)
                self._missing_cols.pop(col, None)

        # if there are duplicated rows, drop them and update attribute
        if df_copy.duplicated().sum() > 0:
            df_copy.drop_duplicates(inplace=True, **drop_duplicates_kws)
            # update related attributes
            self._duplicate_inds = [*df_copy[df_copy.duplicated(keep=False)
                                             ].index]
            self._outliers = {
                col: iqr(self._df[col].values) for col in self._num_cols
                if iqr(self._df[col].values) is not None}

        # if drop_nan is True, drop any row with nans
        if drop_nan:
            df_copy.dropna(inplace=True)
            # clear _missing_cols
            self._missing_cols = {}

        # update df attribute
        self._df = df_copy

    def optimize(self) -> None:
        """
        Optimizes the dataframe by converting columns to the desired data type
        and converting categorical columns to 'category' data type. Note that
        numerical columns should not contain missing values.

        Raises
        ------
        Warning
            If any numerical column contains missing values.
        """
        if self._cols_to_optimize != {} or len(self._cat_cols) > 0:
            # if there are columns to optimize, convert them to the optimized
            # data types, after copyting our dataframe
            df_copy = self._df.copy()
            cols_to_optimize = [*self._cols_to_optimize.keys()]
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
                    self._cols_to_optimize.pop(col)

            # if there are categorical columns, covert them to df_copy
            if len(self._cat_cols.keys()) > 0:
                # convert to categorical
                for col in [*self._cat_cols.keys()]:
                    df_copy[col] = df_copy[col].astype('category')
                    # update _cat_cols by removing col
                    self._cat_cols.pop(col)
            # now we will update df attribute
            self._df = df_copy

    def _unique_val_report(self) -> str:
        """
        Reports the columns with unique values.

        Returns
        -------
        str
            A string contains a `header` which explaining the report
            purpose and a `body` that show the details (as per the
            availability of unique value columns)
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
        """
        Reports the duplicated rows.

        Returns
        -------
        msg: str
            A string contains a `header` which explaining the report purpose
            and a `body` that show the details (as per the availability of
            duplicated rows).
        data: pandas.DataFrame or None
            A dataframe of duplicated rows, or None if no duplicated rows.
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

    def _optimization_report(self) -> Tuple[str, Optional[pd.DataFrame]]:
        """
        Reports the columns that can change datatypes for optimization.

        Returns
        -------
        msg: str
            A string contains a `header` which explaining the report purpose
            and a `body` that show the details (as per the availability of
            numerical columns to optimize).
        data: pandas.DataFrame or None
            A dataframe of columns optimization datatype details, or None if
            no columns to optimize.
        """
        # define report header
        header = '- Checking datatypes to optimize memory ... '

        # Checking if we have numeraical columns to optimize
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
        else:
            body = 'No columns to optimize.'
            data = None

        # collect the msg from header and body
        msg = header + body
        # return the optimization report
        return msg, data

    def _cat_report(self) -> Tuple[str, Optional[pd.DataFrame]]:
        """
        Reports the columns that can change to categorical for optimization.

        Returns
        -------
        msg: str
            A string contains a `header` which explaining the report purpose
            and a `body` that show the details (as per the availability of
            categorical columns to optimize).
        data: pandas.DataFrame or None
            A dataframe of categorical columns with its unique values, or None
            if no columns to be converted.
        """
        # define report header
        header = '- Checking columns that can convert to categorical ... '

        # Checking if we have string columns to convert
        if self._cat_cols != {}:
            # assign body
            body = '\nThese columns can be converted to categorical:'
            # convert cat_cols to dataframe and assign to data
            cat_cols_dict = {col: ', '.join(self._cat_cols[col])
                             for col in self._cat_cols.keys()}
            data = pd.DataFrame.from_dict(cat_cols_dict, orient='index',
                                          columns=['unique_values'])
        else:
            body = 'No columns to optimize.'
            data = None

        # collect the msg from header and body
        msg = header + body
        # return the optimization report
        return msg, data

    def _outliers_report(self) -> Tuple[str, Optional[pd.DataFrame]]:
        """
        Reports the outliers in columns.

        Returns
        -------
        msg: str
            A string contains a `header` which explaining the report purpose
            and a `body` that show the details (as per the availability of
            outliers in columns).
        data: pandas.DataFrame or None
            A dataframe of outlier details in columns, or None if no outliers.
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
        """
        Reports the missing values with matrix and heat plot details.

        Parameters
        ----------
        show_matrix : bool
            A flag to control whether to show the missing value matrix plot or
            not.
        show_heat : bool
            A flag to control whether to show the missing value heatmap plot
            or not.
        matrix_kws : dict
            Keyword arguments passed to the missing value matrix plot.
        heat_kws : dict
            Keyword arguments passed to the missing value heatmap plot.

        Returns
        -------
        msg : str
            A string contains a `header` which explaining the report purpose
            and a `body` that show the details (as per the availability of
            missing values)
        data : pandasd.DataFrame or None
            A dataframe of missing values details, or None if no missings
        matrix : plt.Axes or None
            A Matrix plot (from `missingno` backage) if there are missing
            values and show_matrix is True, or None otherwise
        heat : plt.Axes or None
            A Heat plot (from `missingno` backage) if there are missing
            values and show_heat is True, or None otherwise.

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
