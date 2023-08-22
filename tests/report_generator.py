"""Support function to test `report` method"""

# import modules
from tabulate import tabulate
import pandas as pd
import re


def report_generator(is_duplicate=True, len_duplicate=0, len_df=1,
                     df_duplicate=None, is_num_opt=True, cols_to_optimize={},
                     is_cat_opt=True, cat_cols={}, is_outlier=True,
                     outliers={}, is_missing=True, missing_cols={}) -> str:
    """
    Generate the report as when `report` method is called, the parameters
    are different situations inside CleanDataFrame class, the whole output
    will be collected into one string to use it inside pytest.

    Parameters
    ----------
    is_duplicate : bool, optional
        A flag to be used if the dataframe has duplications, its value will
        change the report. Defaults to True.
    len_duplicate: int, optional
        The number of duplicated rows in the dataframe. Defaults to 0.
    len_df : int, optional
        The number of rows in the dataframe. Defaults to 1.
    df_duplicate : pandas.DataFrame, optional
        A dataframe contains duplicated rows. Defaults to None.
    is_num_opt : bool, optional
        A flag to be used if the dataframe has numerical columns to be
        optimize, its value will change the report. Defaults to True.
    cols_to_optimize : dict, optional
        A dictionary of all numerical columns that can be memory optimized, it
        will be {column name: optimized data type}. Defaults to {}.
    is_cat_opt : bool, optional
        A flag to be used if the dataframe has columns that can convert to
        categorical, its value will change the report. Defaults to True.
    cat_cols : dict, optional
        A dictionary for columns that can convert to categiorical type as
        {column name: array of unique values} format. Defaults to {}.
    is_outlier : bool, optional
        A flag to be used if the dataframe has outliers, its value will change
        the report. Defaults to True.
    outliers : dict, optional
        A dictionary for outliers details in descinding order in an array as
        {column name: outlier details} format, the list has:
            - The number of lower outliers.
            - The number of upper outliers.
            - The total number of outliers.
            - The percentage of the total values that are outliers.
        Defaults to {}.
    is_missing : bool, optional
        A flag to be used if the dataframe has missing values, its value will
        change the report. Defaults to True.
    missing_cols : dict, optional
        A dictionary for missing details in descinding order in an array as
        {column name: missing details} format, the list has:
            - The total number of missing values.
            - The percentage of the total values that are missing.
        Defaults to {}.

    Raises
    ------
    TypeError
        If any of the parameters' types are wrong.
    ValueError
        If `len_duplicate` or `len_df` are not positive integers.
    """
    # check the data types, first assign the correct types
    params_type = {
         'is_duplicate': [isinstance(is_duplicate, bool), 'boolian'],
         'is_num_opt': [isinstance(is_num_opt, bool), 'boolian'],
         'is_cat_opt': [isinstance(is_cat_opt, bool), 'boolian'],
         'is_outlier': [isinstance(is_outlier, bool), 'boolian'],
         'is_missing': [isinstance(is_missing, bool), 'boolian'],
         'len_duplicate': [isinstance(len_duplicate, int), 'integer'],
         'len_df': [isinstance(len_df, int), 'integer'],
         'cols_to_optimize': [isinstance(cols_to_optimize, dict),
                              'dictionary'],
         'cat_cols': [isinstance(cat_cols, dict), 'dictionary'],
         'outliers': [isinstance(outliers, dict), 'dictionary'],
         'missing_cols': [isinstance(missing_cols, dict), 'dictionary'],
         'df_duplicate': [
             isinstance(df_duplicate, pd.DataFrame) or df_duplicate is None,
             'pandas dataframe']
         }

    # check the data types and raise TypeError if the type is wrong
    for param in params_type.keys():
        if not params_type[param][0]:
            raise TypeError(
                f'`{param}` should be `{params_type[param][1]} datatype.`')

    # check len_duplicate is a positive integer
    if len_duplicate < 0:
        raise ValueError('`len_duplicate` should be a positive number.')

    # check len_df is a positive integer
    if len_df < 0:
        raise ValueError('`len_df` should be a positive number.')

    # check the duplication
    if is_duplicate:
        # make the percentage of duplication and convert the duplicate
        # dataframe to tabulate form
        dup_percentage = round(len_duplicate*100 / len_df, 2)
        table = tabulate(df_duplicate, headers=df_duplicate.columns)

        # save the duplication report to duplicated
        duplicated = ('===============\nDuplicated Rows\n===============\n'
                      f'The dataset has {len_duplicate} duplicated rows, '
                      f'which is {dup_percentage}% from the dataset, '
                      f'duplicated rows are:\n\n{table} \n\n')
    else:
        # if no duplication, save report to duplicated
        duplicated = ('===============\nDuplicated Rows\n===============\n'
                      'No duplicated rows.\n\n')

    # check numbers to be optimized
    if is_num_opt:
        # convert data types as
        # {data type: list of columns that can convert to this type}
        num_opt_dict = {
            re.findall('\\.(\\w*)', str(to_type))[0]: [', '.join([
                col for col in cols_to_optimize.keys()
                if cols_to_optimize[col] == to_type]
                )] for to_type in set(cols_to_optimize.values())}
        # convert num_opt_dict to tabulate form
        table = tabulate(num_opt_dict.values(), showindex=num_opt_dict.keys(),
                         headers=['columns_to_convert'])
        # save the numaric optimization report to num_opt
        num_opt = ('==============================\nNumerical Columns '
                   'Optimization\n==============================\nThese '
                   f'numarical columns can be down graded:\n\n{table} \n\n')
    else:
        # if no optimized columns, save report to num_opt
        num_opt = ('==============================\nNumerical Columns '
                   'Optimization\n==============================\n'
                   'No numerical columns to optimize.\n\n')

    # check columns that can convert to categorical
    if is_cat_opt:
        # convert the values as a dictionary
        cat_opt_dict = {col: [', '.join(cat_cols[col])]
                        for col in cat_cols.keys()}
        # convert cat_opt_dict to tabulate form
        table = tabulate(cat_opt_dict.values(), showindex=cat_opt_dict.keys(),
                         headers=['unique_values'])
        # save the categorical optimization report to cat_opt
        cat_opt = ('================================\nCategorical Columns '
                   'Optimization\n================================\nThese '
                   f'columns can be converted to categorical:\n\n{table} \n\n'
                   )
    else:
        # if no optimized columns, save report to cat_opt
        cat_opt = ('================================\nCategorical Columns '
                   'Optimization\n================================\n'
                   'No columns to optimize.\n\n')

    # check outliers
    if is_outlier:
        # convert outliers to tabulate form
        table = tabulate(outliers.values(), showindex=outliers.keys(),
                         headers=['outliers_lower', 'outliers_upper',
                                  'outliers_total', 'outliers_percentage'])
        # save the outliers report to outlier
        outlier = ('========\nOutliers\n========\nOutliers are:\n\n'
                   f'{table} \n\n')
    else:
        # if no outliers, save report to outlier
        outlier = ('========\nOutliers\n========\nNo outliers.\n\n')

    # check missing values
    if is_missing:
        # convert missing_cols to tabulate form
        table = tabulate(missing_cols.values(), showindex=missing_cols.keys(),
                         headers=['missing_counts', 'missing_percentage'])
        # save the missing report to missing
        missing = ('==============\nMissing Values\n==============\n'
                   f'Missing details are:\n\n{table} \n\n')
    else:
        # if no missings, save report to missing
        missing = ('==============\nMissing Values\n==============\n'
                   'No missing values.\n\n')

    # collect the final report and return it
    return f'{duplicated}\n{num_opt}\n{cat_opt}\n{outlier}\n{missing}\n'
