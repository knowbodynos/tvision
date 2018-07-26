from time import gmtime


SECONDS_IN_DAY = 86400


def utc_seconds_now():
    """Convert current UTC time to total seconds past midnight."""
    utc_time_struct = gmtime()
    utc_minutes = 60 * utc_time_struct.tm_hour + utc_time_struct.tm_min
    utc_seconds = 60 * utc_minutes + utc_time_struct.tm_sec
    return utc_seconds


def utc_seconds_timestamp(utc_timestamp):
    """Convert given UTC time to total seconds past midnight."""
    hours, minutes = [int(field) for field in utc_timestamp.split(':')]
    utc_minutes = 60 * hours + minutes
    utc_seconds = 60 * utc_minutes
    return utc_seconds


def max_socket_timeout(config, step_num, timeout_buffer=30):
    """Given time-sorted configuration array and current step,
    determine maximum time until next step padded by timeout_buffer."""
    if step_num < len(config) - 1:
        # If some steps remain in the day, compute time until next step, padded by timeout_buffer
        return utc_seconds_timestamp(config[step_num + 1]['time']) - utc_seconds_now() - timeout_buffer
    else:
        # If no steps remain in the day, compute time until first step of following day, padded by timeout_buffer
        return SECONDS_IN_DAY + utc_seconds_timestamp(config[0]['time']) - utc_seconds_now() - timeout_buffer