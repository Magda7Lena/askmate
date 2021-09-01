from datetime import datetime


def convert_time(unix_timestamp):
    converted_timestamp = datetime.fromtimestamp(unix_timestamp)
    return f"{converted_timestamp:%Y-%m-%d %H:%M:%S}"


def get_current_time():
    return datetime.now().isoformat(' ', 'seconds')


def string_data_to_int(data):
    for row in data:
        for key, value in row.items():
            try:
                row[key] = int(value)
            except ValueError:
                pass
    return data
