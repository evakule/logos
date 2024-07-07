import datetime
import os
from concurrent.futures import ProcessPoolExecutor

from ent.base_ds import BaseConfig
from ent.job import GroupByCorrelationPerStockJob
from ent.utils import generate_file_path


# TODO Add sma_window, type_vol, depth, coordinates_basis. Add dependency management. Split by packages.

def execute_job(config):
    job = GroupByCorrelationPerStockJob(config)
    job.execute()


def start_jobs():
    job_configs = []
    sd_folder_path = generate_file_path('source_data')
    files = os.listdir(sd_folder_path)
    for f in files:
        file_path = os.path.join(sd_folder_path, f)
        c = BaseConfig().builder() \
            .with_file_path(file_path) \
            .with_sma_window(3) \
            .with_type_vol(0.25) \
            .with_depth(20) \
            .with_coordinates_basis('close') \
            .with_stop_loss(0.5) \
            .build()
        job_configs.append(c)

    with ProcessPoolExecutor() as executor:
        executor.map(execute_job, job_configs)


if __name__ == '__main__':
    start = datetime.datetime.now()
    print(start)

    start_jobs()
    end = datetime.datetime.now()

    print((start - end).total_seconds())
