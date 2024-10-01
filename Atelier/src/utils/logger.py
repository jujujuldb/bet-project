import logging
import os
from logging.handlers import TimedRotatingFileHandler

def setup_logging(config):
    """Set up logging configuration with log rotation."""
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file = os.path.join(log_directory, config['file'])

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config['level']))

    # File handler with rotation
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=30,  # Keep logs for 30 days
        encoding='utf-8'
    )
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(getattr(logging, config['level']))
    root_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    logging.info("Logging setup completed with log rotation.")

    return file_handler, console_handler  # Return handlers for potential manual flushing