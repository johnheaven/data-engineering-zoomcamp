#!/usr/bin/env python
# coding: utf-8

import os
import argparse

from time import time

import pandas as pd
from sqlalchemy import create_engine

def main(params):
    username = params.pg_username
    password = params.pg_password
    host = params.pg_host 
    port = params.pg_port 
    db = params.pg_db
    table_name = params.pg_table_name
    url = params.data_url
    datecols = params.datecols.split(',') if params.datecols else None

    df_iter = pd.read_csv(url, iterator=True, chunksize=100000)

    df = next(df_iter)

    # cast date columns if they exist
    if datecols:
        for datecol in datecols:
            if datecol in df.columns:
                df[datecol] = pd.to_datetime(df[datecol])


    engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{db}')
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    df.to_sql(name=table_name, con=engine, if_exists='append')

    while True: 
        try:
            t_start = time()
            
            df = next(df_iter)

            if datecols:
                for datecol in datecols:
                    if datecol in df.columns:
                        df[datecol] = pd.to_datetime(df[datecol])
                
            df.to_sql(name=table_name, con=engine, if_exists='append')

            t_end = time()

            print('inserted another chunk, took %.3f second' % (t_end - t_start))

        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break

if __name__ == '__main__':
    import logging

    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--pg_username', required=False, help='user name for postgres')
    parser.add_argument('--pg_password', required=False, help='password for postgres')
    parser.add_argument('--pg_host', required=False, help='host for postgres')
    parser.add_argument('--pg_port', required=False, help='port for postgres')
    parser.add_argument('--pg_db', required=False, help='database name for postgres')
    parser.add_argument('--pg_table_name', required=False, help='name of the table where we will write the results to')
    parser.add_argument('--data_url', required=False, help='url of the csv file')
    parser.add_argument('--datecols', required=False, help='columns to attempt to convert to date. separate multiple values with comma')

    cl_args = vars(parser.parse_args())

    # argument tuples in format (name:str, required: bool)
    db_arg_names = (('pg_username', True), ('pg_password', True), ('pg_host', True), ('pg_port', True), ('pg_db', True), ('pg_table_name', True), ('data_url', True), ('datecols', False))
    from collections import namedtuple
    import os
    Args = namedtuple('args', (arg_name for arg_name, _ in db_arg_names))
    db_arg_values = []
    for arg_name, arg_required in db_arg_names:
        # try to get command-line argument
        if cl_args.get(arg_name, None):
            db_arg_values.append(cl_args[arg_name])
        elif arg_name.upper() in os.environ.keys():
        # try to get environment variable
            db_arg_values.append(os.environ[arg_name.upper()])
        elif not arg_name and arg_required:
        # if this parameter is required, then raise an error
            raise ValueError(f'Argument {arg_name} required as command line argument or {arg_name.upper()} as environment variable.')
    
    args = Args(*db_arg_values)
    main(args)
        
        
        
