from datetime import datetime
import airflow
from airflow import AirflowException
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow import DAG
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, BigInteger, String, Text


# Global variables that are set using environment varaiables
OTUS_TUTORIAL_DB_URL = os.getenv('OTUS_TUTORIAL_DB_URL')
OTUS_TUTORIAL_ROOT_PATH = os.getenv('OTUS_TUTORIAL_ROOT_PATH')

default_args = {
    "owner": "Airflow",
    "start_date": airflow.utils.dates.days_ago(1)
}


dag = DAG(
    dag_id='it_is_a_magic_dag',
    default_args=default_args,
    schedule_interval=None,
)


def load_files_into_db(ds, **kwargs):

    engine = create_engine(OTUS_TUTORIAL_DB_URL)

    with engine.connect() as conn:
        conn.execute("drop table if exists resp_view cascade")
        conn.execute("drop table if exists ch_id cascade")

        df_resp_view = pd.read_csv(os.path.join(OTUS_TUTORIAL_ROOT_PATH, "data", "resp_view.csv"), dtype=str)
        column_rename_dict = {old_column_name: old_column_name.lower() for old_column_name in df_resp_view.columns}
        df_resp_view.rename(columns=column_rename_dict, inplace=True)
        df_resp_view['mediapackageid'] = df_resp_view['mediapackageid'].fillna('1')
        df_resp_view.to_sql("resp_view", engine,
                            schema=None,
                            if_exists='replace',
                            index=False,
                            index_label=None,
                            chunksize=None,
                            dtype= {'subjectid': BigInteger,
                                    'viewingtime': BigInteger,
                                    'endviewingtime': BigInteger,
                                    'mediapackageid': BigInteger,
                                    'duration': Integer})

        df_ch_id = pd.read_csv(os.path.join(OTUS_TUTORIAL_ROOT_PATH, "data", "ch_id.csv"), dtype=str)
        column_rename_dict_2 = {old_column_name_2: old_column_name_2.lower() for old_column_name_2 in df_ch_id.columns}
        df_ch_id.rename(columns=column_rename_dict_2, inplace=True)
        df_ch_id.to_sql("ch_id", engine,
                                      schema=None,
                                      if_exists='replace',
                                      index=False,
                                      index_label=None,
                                      chunksize=None,
                                      dtype= {'channelname': Text,
                                              'mediapackageid': BigInteger})

    return 'Loaded files into the database'


task_load_files_into_db = PythonOperator(
    task_id='task_load_files_into_db',
    provide_context=True,
    python_callable=load_files_into_db,
    dag=dag,
)


task_transform_data_in_db = BashOperator(
    task_id='task_transform_data_in_db',
    bash_command='dbt run --project-dir {}'.format(os.path.join(OTUS_TUTORIAL_ROOT_PATH, 'dbt')),
    dag=dag)


task_test_data_in_db = BashOperator(
    task_id='task_test_data_in_db',
    bash_command='dbt test --project-dir {}'.format(os.path.join(OTUS_TUTORIAL_ROOT_PATH, 'dbt')),
    dag=dag)


# DAG dependencies
task_load_files_into_db >> task_transform_data_in_db
task_transform_data_in_db >> task_test_data_in_db