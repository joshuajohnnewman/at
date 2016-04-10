import os


def get_data_path(file_name):
    return os.path.join(os.environ['TRADING_DATA'], file_name)