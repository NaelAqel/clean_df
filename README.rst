========
clean_df
========

.. image:: https://img.shields.io/pypi/v/clean_df.svg
        :target: https://pypi.python.org/pypi/clean_df

.. image:: https://github.com/NaelAqel/clean_df/actions/workflows/test.yml/badge.svg
   :target: https://github.com/NaelAqel/clean_df/actions/workflows/test.yml

.. image:: https://readthedocs.org/projects/clean-df/badge/?version=latest
        :target: https://clean-df.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/pypi/l/clean_df.svg
   :target: https://github.com/NaelAqel/clean_df/blob/main/LICENSE  
  
  
  
Python module to report, clean, and optimize **Pandas Dataframes** effectively.

**Full Documentation** `Here`_.

.. _Here: https://naelaqel.com/clean_df/
  
Description and Features
------------------------
The first step of any data analysis project is to check and clean the data, in this module I implemented a very effiecint code that can:  

* Automatically drop columns that have a unique value (these columns are useless, so it will be dropped).
* Report your **Pandas DataFrame** to decide for actions, this report will show:  

  #. Duplicated rows report.
  #. Columns’ Datatype to optimize memory report.
  #. Columns to convert to categorical report.
  #. Outliers report.
  #. Missing values report.


* Clean the dataframe by dropping columns that have a high ratio of missing values, rows with missing values, and duplicated rows in the dataframe.

* Optimize the dataframe by converting columns to the desired data type and converting categorical columns to 'category' data type.

Installation
------------
To install ``clean_df``, run this command in your terminal:: 

    $ pip install clean_df

For more information on installation details for this project, please see the ``docs/installation.rst`` file.


    
Usage
-----
This module is very easy to use, for a full detailed example please see the ``docs/usage.rst`` file.

Importing the module
^^^^^^^^^^^^^^^^^^^^
::

        from clean_df import CleanDataFrame   

Defining the class
^^^^^^^^^^^^^^^^^^
Pass your pandas dataframe to ``CleanDataFrame`` class::

        cdf = CleanDataFrame(
                df=df,             # the dataframe to be cleaned
                max_num_cat=5      # maximum number of unique values in a column to be 
                )                  # converted to categorical datatype, default is 5

Reporting
^^^^^^^^^
Call ``report`` method to see a full report about the dataframe (duplications, columns to optimize its data types, categorical columns, outliers, and missing values::

        cdf.report(
                show_matrix=True,   # show matrix missing values (from missingno package), default is True
                show_heat=True,     # show heat missing values (from missingno package), default is True
                matrix_kws={},      # if need to pass any arguments to matrix plot, default is {}
                heat_kws={}         # if need to pass any arguments to heat plot, default is {}
                )

Cleaning
^^^^^^^^
Call ``clean`` method to drop high number of missing value columns, duplicated rows, and rows with missing values::

        cdf.clean(
                min_missing_ratio=0.05,    # the minimum ratio of missing values to drop a column, default is 0.05
                drop_nan=True              # if True, drop the rows with missing values after dropping columns 
                                           # with missingsa above min_missing_ratio
                drop_kws={},               # if need to pass any arguments to pd.DataFrame.drop(), default is {}
                drop_duplicates_kws={}     # same drop_kws, but for drop_duplicates function
                )

Optimizing
^^^^^^^^^^
Call ``optimize`` method to optimize the dataframe by changing columns' data types based on its values for maximum memory savings::

        cdf.optimize()


Accessing the Cleaned Data DataFrame
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

        cdf.df 


  
Contributing
------------
See the ``CONTRIBUTING.rst`` for contribution details. Feel free to contact me for any subject through my:  

* `Email`_
* `LinkedIn`_
* `WhatsApp`_

Also, you are welcomed to visit my personal `blog`_ .

.. _Email: mailto:dev@naelaqel.com
.. _LinkedIn: https://www.linkedin.com/in/naelaqel1
.. _WhatsApp: https://wa.me/962796780232
.. _blog: https://naelaqel.com

   

License
-------
Free software: MIT license.

    

Documentation
-------------
* The full documentation is hosted on my `website`_, and on `ReadTheDocs`_.
* The source code is available in `GitHub`_.

.. _website: https://naelaqel.com/clean_df/
.. _ReadTheDocs: https://clean_df.readthedocs.io
.. _GitHub: https://github.com/naelaqel/clean_df

    
    
Credits
-------
* This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.  
* Here are `additional`_ resources I got a lot from them.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`additional`: https://naelaqel.com/resources/
