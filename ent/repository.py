import pandas as pd
from sqlalchemy import create_engine


class Repository:

    def __init__(self, username: str, password: str, db: str):
        self.engine = create_engine(f'postgresql+psycopg2://{username}:{password}@0.0.0.0:5432/{db}')

    def save_pandas_df(self, table_name: str, df: pd.DataFrame, if_exists='append', index=False) -> None:
        df.to_sql(table_name, self.engine, if_exists=if_exists, index=index)
