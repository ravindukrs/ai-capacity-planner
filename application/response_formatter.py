import math
import numbers

def formatter(tps, concurrency=None):

    #Round up TPS
    tps = math.ceil(tps * 100.0) / 100.0
    if tps<1:
        tps = 1;

    #Calcuate Latency
    if not isinstance(concurrency, numbers.Number):
        return tps
    else:
        #Calculate Latency with Little's Law
        latency = concurrency/tps*1000;
        latency = math.ceil(latency * 100.0) / 100.0
        return tps, latency


def json_value_validator(scenario=None, concurrency=None, message_size=None, sample_count=None, type="point_pred"):

    is_valid = True

    if type == "point_pred" or type == "max_tps":

        if not isinstance(message_size, numbers.Number):
            is_valid = is_valid * False;

        if scenario != "Passthrough" and scenario != "Transformation":
            is_valid = is_valid * False;

        if message_size < 1 or message_size > 102400:
            is_valid = is_valid * False;

    if type == "point_pred":
        if not isinstance(concurrency, numbers.Number):
            is_valid = is_valid * False;

        if concurrency < 1 or concurrency > 100000:
            is_valid = is_valid * False;

    if type == "sampling_check":
        if not isinstance(sample_count, numbers.Number):
            is_valid = is_valid * False;

        if not sample_count >= 1:
            is_valid = is_valid * False;

    return is_valid





