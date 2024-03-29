"""This module contains the CleanDataFrame class, which is used to clean the
data in a Pandas DataFrame.
"""

# import modules
import pandas as pd
import numpy as np
import re
import missingno as msno
from IPython.display import display
from tabulate import tabulate
import warnings
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
    duplicate_inds : numpy ndarray, readonly
        Array of the indices of duplicated rows.
    cols_to_optimize : dict, readonly
        A dictionary of all numerical columns that can be memory optimized, it
        will be {column name: optimized data type}.
    outliers : dict, readonly
        A dictionary for outliers details in descinding order in an array as
        {column name: outlier details} format, the list has:
            - The number of lower outliers.
            - The number of upper outliers.
            - The total number of outliers.
            - The percentage of the total values that are outliers.
    missing_cols : dict, readonly
        A dictionary for missing details in descinding order in an array as
        {column name: missing details} format, the list has:
            - The total number of missing values.
            - The percentage of the total values that are missing.
    cat_cols : dict, readonly
        A dictionary for columns that can convert to categiorical type as
        {column name: array of unique values} format.
    num_cols : numpy ndarray of str, readonly
        Array of numerical columns.

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
            1. Duplicated rows report.
            2. Columns' Datatype to optimize memory report.
            3. Columns to convert to categorical report.
            4. Outliers report.
            5. Missing values report.

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
    def duplicate_inds(self) -> np.ndarray:
        """
        Get the value of duplicate_inds.

        Returns
        -------
        numpy ndarray
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
    def cat_cols(self) -> np.ndarray:
        """
        Get the value of cat_cols.

        Returns
        -------
        numpy ndarray
            The value of cat_cols.
        """
        return self._cat_cols

    @property
    def num_cols(self) -> np.ndarray:
        """
        Get the value of num_cols.

        Returns
        -------
        numpy ndarray
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

        # save columns (in its order) in _cols_order
        self._cols_order = np.array(self._df.columns)

        # ~~~~~ Unique value columns ~~~~~
        unique_val_cols = np.array([
            col for col in self._cols_order if self._df[col].nunique() <= 1])
        # if there are columns with only unique value, drop them and update
        # relevent attributes
        if len(unique_val_cols) > 0:
            print('Founded useless columns (with single value) ... ', end='')
            self._df.drop(columns=unique_val_cols, inplace=True)
            print(f"[{', '.join(unique_val_cols)}] columns dropped.\n")
            self._cols_order = np.setdiff1d(
                self._cols_order, unique_val_cols, assume_unique=True)

        # list if dataframe has columns with type 'category', to exclude it
        # as numpy can not deal with category datatype
        cols_without_cat = np.array(
            [col for col in self._cols_order
             if self._df[col].values.dtype != 'category'])
        # list all columns that can be categorical
        self._cat_cols = {col: pd.unique(self._df[col].dropna())
                          for col in cols_without_cat if (
            self._df[col].values.dtype == 'O') and len(
            set(self._df[col].values)) <= self._max_num_cat}
        # list numerical columns that are not in unique_val_cols (note: numpy
        # considered datatime as numerical, so we exclude it datatime)
        self._num_cols = np.array([
            col for col in cols_without_cat
            if np.issubdtype(self._df[col].values.dtype.name, np.number)
            and not np.issubdtype(self._df[col].values.dtype.name, '<m8[ns]')])

        # ~~~~~ Duplicated Rows ~~~~~
        self._duplicate_inds = self._df[self._df.duplicated(keep=False)
                                        ].index.values

        # ~~~~~ Optimization of Columns ~~~~~
        self._cols_to_optimize = {
            col: optimize_num(self._df[col].values) for col in self._num_cols
            if optimize_num(self._df[col].values) is not None}

        # ~~~~~ Outliers ~~~~~
        self._outliers = {
            col: iqr(self._df[col].values) for col in self._num_cols
            if iqr(self._df[col].values) is not None}
        # sort in desc order as per the number of outliers
        self._outliers = dict(
            sorted(self._outliers.items(), key=lambda item: item[1][2],
                   reverse=True))

        # ~~~~~ Missing Values ~~~~~
        self._missing_cols = {
                col: np.array([
                    pd.isna(self._df[col].values).sum(),
                    round(pd.isna(self._df[col].values).sum(
                    )*100 / len(self._df), 2)])
                for col in self._cols_order
                if pd.isna(self._df[col].values).sum() > 0}
        # sort in desc order as per the number of missing values
        self._missing_cols = dict(
            sorted(self._missing_cols.items(), key=lambda item: item[1][0],
                   reverse=True))

    def report(self, show_matrix=True, show_heat=True, matrix_kws={},
               heat_kws={}) -> None:
        """
        Generate a summary report of the dataset, including:
            1. Duplicated rows report.
            2. Columns' Datatype to optimize memory report.
            3. Columns to convert to categorical report.
            4. Outliers report.
            5. Missing values report.

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

        def header(title) -> str:
            """
            Print a formatted title as a header, it will print the title
            between two '=' lines which has the same length of title

            Parameters
            ----------
            title: str
                A string of the title needed to be formatted.

            Rises
            -----
            TypeError
                If `title` is not string.

            Returns
            -------
            str
                A string of formatted title.
            """
            # check 'title' data type
            if (not isinstance(title, str)):
                raise TypeError("'title' should be string.")

            # generate the upper and lower lines
            len_title = '='*len(title)
            # return formatted title
            return f'{len_title}\n{title}\n{len_title}'

        # ~~~~~ Duplicated Rows Report ~~~~~
        # print formatted header
        print(header('Duplicated Rows'))
        # Checking if we have duplications
        if len(self._duplicate_inds) > 0:
            # print a message showing number and percentage of duplications
            print(
                f'The dataset has {len(self._duplicate_inds)} duplicated'
                f''' rows, which is {round(len(self._duplicate_inds
                )*100 / len(self._df), 2)}% from the dataset, duplicated '''
                'rows are:\n')
            # print duplicated rows
            print(tabulate(self._df.iloc[self._duplicate_inds],
                           headers=self.df.columns), '\n\n')
        else:
            # if no duplications, show this message
            print('No duplicated rows.\n\n')

        # ~~~~~ Numerical Columns Optimization Report ~~~~~
        # print formatted header
        print(header('Numerical Columns Optimization'))
        # Checking if we have numeraical columns to optimize
        if self._cols_to_optimize != {}:
            print('These numarical columns can be down graded:\n')
            # convert data types as
            # {data type: list of columns that can convert to this type}
            optimize_dict = {
                re.findall('\\.(\\w*)', str(to_type))[0]: [', '.join(
                    [col for col in self._cols_to_optimize.keys()
                     if self._cols_to_optimize[col] == to_type])]
                for to_type in set(self._cols_to_optimize.values())}
            # print optimize_dict as a table
            print(tabulate(
                optimize_dict.values(), showindex=optimize_dict.keys(),
                headers=['columns_to_convert']), '\n\n')
        else:
            # if no columns to optimize, print this message
            print('No numerical columns to optimize.\n\n')

        # ~~~~~ Categorical Columns Optimization Report ~~~~~
        # print formatted header
        print(header('Categorical Columns Optimization'))
        # Checking if we have string columns to convert
        if self._cat_cols != {}:
            print('These columns can be converted to categorical:\n')
            # convert cat_cols to dataframe and assign to data
            cat_cols_dict = {col: [', '.join(self._cat_cols[col])]
                             for col in self._cat_cols.keys()}
            # print cat_cols_dict as a table
            print(tabulate(
                cat_cols_dict.values(), showindex=cat_cols_dict.keys(),
                headers=['unique_values']), '\n\n')
        else:
            # if no columns to optimize, print this message
            print('No columns to optimize.\n\n')

        # ~~~~~ Outliers Report ~~~~~
        # print formatted header
        print(header('Outliers'))
        # check outliers for report body
        if self._outliers != {}:
            print('Outliers are:\n')
            # print outliers as a table
            print(tabulate(
                self._outliers.values(), showindex=self._outliers.keys(),
                headers=['outliers_lower', 'outliers_upper',
                         'outliers_total', 'outliers_percentage']), '\n\n')
        else:
            # if no outliers, print this message
            print('No outliers.\n\n')

        # ~~~~~ Missing Values Report ~~~~~
        # print formatted header
        print(header('Missing Values'))
        # check missing values for body report
        if self._missing_cols != {}:
            print('Missing details are:\n')
            # print missing_cols as a table
            print(tabulate(self._missing_cols.values(),
                           headers=['missing_counts', 'missing_percentage'],
                           showindex=self._missing_cols.keys()), '\n\n')

            # if show_matrix is True, show matrix plot
            if show_matrix:
                display(msno.matrix(
                    self._df[self._missing_cols.keys()
                             ].sort_values([*self._missing_cols.keys()][0]
                                           ), **matrix_kws))

            # if show_heat is True, show heat plot
            if show_heat:
                display(msno.heatmap(self._df[self._missing_cols.keys()],
                                     **heat_kws))
        else:
            # if no missings, print this message
            print('No missing values.\n\n')

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
                or (not isinstance(min_missing_ratio, float)
                    and min_missing_ratio != 1):
            raise ValueError("'min_missing_ratio' should be between 0 and 1.")

        # check if inplace in drop_kws or drop_duplicates_kws
        if 'inplace' in drop_kws.keys() or ('inplace'
                                            in drop_duplicates_kws.keys()):
            raise ValueError("'drop_kws' and 'drop_duplicates_kws' can not \
                have 'inplace' value, this function will automatically \
                    inplace them. So please delete 'inplace' key.")

        # define dropped_cols which are the columns to drop (missing columns
        # with missing values ratio above min_missing_ratio)
        dropped_cols = np.array([
            col for col in self._missing_cols.keys()
            if self._missing_cols[col][1] >= 100 * min_missing_ratio])

        # if there are columns to drop, drop them and update attributes
        if len(dropped_cols) > 0:
            self._df.drop(columns=dropped_cols, inplace=True, **drop_kws)
            # update all related attributes
            # remove dropped_cols from _cols_order
            self._cols_order = np.setdiff1d(
                self._cols_order, dropped_cols, assume_unique=True)
            self._num_cols = np.setdiff1d(
                self._num_cols, dropped_cols, assume_unique=True)
            for col in dropped_cols:
                self._cat_cols.pop(col, None)
                self._cols_to_optimize.pop(col, None)
                self._outliers.pop(col, None)
                self._missing_cols.pop(col, None)

        # if there are duplicated rows, or dropnan is True
        if len(self._duplicate_inds) > 0 or drop_nan:
            # if there is duplicated rows, drop them
            if len(self._duplicate_inds) > 0:
                self._df.drop_duplicates(inplace=True, **drop_duplicates_kws)
                # update related attributes
                self._duplicate_inds = np.array([])
            # if drop_nan is True, drop any row with nans
            if drop_nan:
                self._df.dropna(inplace=True)
                # update related attributes _missing_cols
                self._missing_cols = {}
            # update related attributes
            self._outliers = {
                col: iqr(self._df[col].values) for col in self._num_cols
                if iqr(self._df[col].values) is not None}
            # sort in desc order as per the number of outliers
            self._outliers = dict(
                sorted(self._outliers.items(), key=lambda item: item[1][2],
                       reverse=True))

            self._missing_cols = {
                col: np.array([
                    pd.isna(self._df[col].values).sum(),
                    round(pd.isna(self._df[col].values).sum(
                    )*100 / len(self._df), 2)])
                for col in self._cols_order
                if pd.isna(self._df[col].values).sum() > 0}
            # sort in desc order as per the number of missing values
            self._missing_cols = dict(sorted(self._missing_cols.items(),
                                             key=lambda item: item[1][0],
                                             reverse=True))

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
            # if there are columns to optimize
            if len(self._cols_to_optimize.keys()) > 0:
                cols_to_optimize = np.array([*self._cols_to_optimize.keys()])
                # check if columns have missings
                num_cols_missing = np.array([
                    col for col in cols_to_optimize
                    if col in self._missing_cols.keys()])
                # raise warning if there are missing columns
                if len(num_cols_missing) > 0:
                    warnings.warn(f'{num_cols_missing} contains missing '
                                  f'values, it will not be optimized.',
                                  UserWarning)
                    # update cols_to_optimize (remove num_cols_missing)
                    cols_to_optimize = np.setdiff1d(
                        cols_to_optimize, num_cols_missing,
                        assume_unique=True)
                # optimize inside _df, _df_dict and update _cols_to_optimize
                for col in cols_to_optimize:
                    self._df[col] = self._df[col].astype(
                        self._cols_to_optimize[col])
                    self._cols_to_optimize.pop(col)

            # if there are categorical columns, covert them to df_copy
            if len(self._cat_cols.keys()) > 0:
                # convert to categorical
                for col in [*self._cat_cols.keys()]:
                    self._df[col] = self._df[col].astype('category')
                    # update _cat_cols by removing col
                    self._cat_cols.pop(col)
