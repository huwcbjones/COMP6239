import logging

main_logger = logging.getLogger('main')

main_logger.setLevel(logging.INFO)

main_fmt = '%(asctime)s[%(levelname)-8s][%(threadName)s][%(module)s] %(funcName)s: %(message)s'
main_time_fmt = '[%m/%d/%Y %H:%M:%S]'

main_console_handler = logging.StreamHandler()
main_console_formatter = logging.Formatter(main_fmt, main_time_fmt)

main_console_handler.setFormatter(main_console_formatter)

main_logger.addHandler(main_console_handler)

debug = main_logger.debug
info = main_logger.info
warning = main_logger.warning
error = main_logger.error
fatal = main_logger.fatal
exception = main_logger.exception
log = main_logger.log
