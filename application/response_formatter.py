import math
import numbers

def formatter(tps, concurrency=None):
    """
    Get predicted TPS and format the TPS.
    If concurrency is available, calculate Little's Law latency
    :param data: Concurrency and Message Size
    :return TPS(max tps) or TPS and Little's law Latency:
    """
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
    """
    Validate the JSON input.
    :param scenario: 'Passthrough' or 'Transformation'
    :param concurrency: Concurrency
    :param message_size: Message Size
    :param sample_count: Sample Count for Sampling Method
    :param type: point_pred or max_tps
    :return is_valid: Validity of JSON:
    """
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

        if concurrency < 1 or concurrency > 1000:
            is_valid = is_valid * False;

    if type == "sampling_check":
        if not isinstance(sample_count, numbers.Number):
            is_valid = is_valid * False;

        if not sample_count >= 1:
            is_valid = is_valid * False;

    return is_valid





