from datetime import datetime


def convert_to_datetime(param_value):
    return datetime.strptime(
        param_value.replace("T", " ").replace("+00:00", ""),
        "%Y-%m-%d %H:%M:%S",
    )
