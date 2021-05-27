import datetime as dt
import pandas as pd
import csv
import os
import json
from faker import Faker
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

default_args = {
    "owner": "cesar",
    "start_date": dt.datetime(2021, 5, 26),
    "retries": 1,
    "retry_delay": dt.timedelta(minutes=5),
    "max_active_runs": 1,
    "depend_on_past": False,
    'schedule_interval': '@hourly'
}

root=os.getenv("PWD")


def create_csv():
    output = open(f"{root}/data.csv", 'w')
    fake = Faker()
    header = ['name', 'age', 'street', 'city', 'state', 'zip', 'lng', 'lat']
    writer = csv.writer(output)
    writer.writerow(header)
    for r in range(2000):
        writer.writerow([fake.name(), fake.random_int(min=18, max=80, step=1),
                         fake.street_address(), fake.city(), fake.state(),
                         fake.zipcode(), fake.longitude(), fake.latitude()])
    output.close()


def csv_to_json():
    df = pd.read_csv(f"{root}/data.csv")
    for i,r in df.iterrows():
        print(r['name'])
    df.to_json(f"{root}/fromAirflow.json",
               orient="records")


def read_json():
    with open(f"{root}/fromAirflow.json", "r") as f:
        data = json.load(f)

    print(data)


with DAG(dag_id="mycsvdag",
         default_args=default_args,
         ) as dag:
    print_starting = BashOperator(
        task_id="starting",
        bash_command='echo "I am reading the CSV now..."'
    )

    create_csv = PythonOperator(
        task_id="create_csv",
        python_callable=create_csv
    )

    convert_csv_to_json = PythonOperator(
        task_id="convert_csv_to_json",
        python_callable=csv_to_json
    )

    read_json = PythonOperator(
        task_id="read_json",
        python_callable=read_json
    )


print_starting >> create_csv >> convert_csv_to_json >> read_json