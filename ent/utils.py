from datetime import datetime
import os
import re


def to_datetime(value: str) -> datetime:
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')


def to_float(value: str) -> float:
    if not value:
        return None
    return float(value)


def to_int(value: str) -> int:
    if not value:
        return None
    try:
        float_value = float(value)
        if float_value.is_integer():
            return int(float_value)
        else:
            raise ValueError("Input value is a float")
    except ValueError:
        return int(value)


def log(msg):
    print(msg)


def get_stock_name(file_path: str):
    stock_name = os.path.basename(file_path).split('_')[0]

    if not re.match(r'^[A-Z]+$', stock_name):
        raise ValueError(f"Invalid stock name: {stock_name}")

    return stock_name


def generate_file_path(final_folder_name: str) -> str:
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, final_folder_name)
