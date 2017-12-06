import os
from datetime import datetime


def get_log_path():
    home_dir = os.getcwd()[:-7]
    cur_time = datetime.now()
    file_name = cur_time.strftime("%m-%d-%y_%H%M%S.txt")
    file_path = os.path.join(home_dir, "logs/", file_name)
    return file_path


def write_to_log(func):
    def wrapper(message, log):
        log.write(func(message))
    return wrapper


@write_to_log
def add_header(header):
    f_header = "{0}\n{1}\n{0}\n".format("-"*20, header)
    return f_header
