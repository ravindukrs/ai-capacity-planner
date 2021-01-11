import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

file_handler = logging.FileHandler('programlogs.log')
file_handler.setFormatter(log_formatter)

logger.addHandler(file_handler)