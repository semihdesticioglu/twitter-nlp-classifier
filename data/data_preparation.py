#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


# In[ ]:


def load_data(messages_filepath, categories_filepath):
    """
    Load Messages Data and Categories Data
    
    Arguments:
        messages_filepath -> Path to the CSV file containing messages
        categories_filepath -> Path to the CSV file containing categories
    Output:
        df -> A dataframe contains message and target categories
    """
    
    # load messages dataset
    messages = pd.read_csv(messages_filepath)

    # load categories dataset
    categories = pd.read_csv (categories_filepath)

    #merging datasets
    df = messages.merge(categories,on="id",how="left")
    
    # create a dataframe of the 36 individual category columns
    categories = pd.DataFrame(df.categories.str.split(";").tolist())

    # select the first row of the categories dataframe
    row = categories.iloc[0]
    
    # use this row to extract a list of new column names for categories.
    category_colnames = row.apply(lambda x: x[:-2])

    # rename the columns of `categories`
    categories.columns = category_colnames

    #Convert category values to just numbers
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str[-1:]
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)

    # drop the original categories column from `df`
    df.drop(["categories"],axis=1,inplace=True)

    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df,categories.reindex(df.index)],axis=1)

    return df


# In[ ]:


def clean_data(df):
    """
    Cleans Data and Drops Duplicates
    
    Arguments:
        df -> Dataframe contains messages and categories
    Outputs:
        df -> Cleaned dataframe after some cleaning processes
    """ 
    
    #dropping duplicates
    df2 = df.drop_duplicates()

    #dropping id duplicated rows
    df3 = df2.drop_duplicates(subset=["id"],keep="last")

    #changing some target rows which has value 2, turning to binary target structure
    df3.loc[df3.related == 2, 'related'] = 1
    return df3


# In[ ]:


def save_data(df, database_filepath):
    """
    Save Data to SQLite Database
    
    Arguments:
        df -> Dataframe contains messages and categories
        database_filename -> Path to SQLite destination database
    """
    
    engine = create_engine('sqlite:///'+ str(database_filepath))
    df.to_sql('messages', engine, index=False)    
    pass


# In[ ]:


def main():
    """
    Main function for data processing functions. There are three primary actions taken by this function:
        1) Load Messages Data with Target Categories
        2) Clean Dataframe Data
        3) Save Data to SQLite Database
    """    

    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        df = load_data(messages_filepath, categories_filepath)

        df = clean_data(df)

        save_data(df, database_filepath)

    else:
        print('Please provide the arguments correctly \n\nExample: python process_data.py '              'messages.csv categories.csv '              'messages.db')


if __name__ == '__main__':
    main()

