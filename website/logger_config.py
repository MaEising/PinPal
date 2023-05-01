import logging
import sys
import logging.handlers
import os
import logging.config

# Define a function to set up the logger
def setup_logger():
    # Set the path for the log file
    log_file_path = os.path.join(os.path.dirname(__file__), 'logs', 'app.log')
    # Create the directories for the log file if they do not exist
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    # Configure the logger using a dictionary
    logging.config.dictConfig({
        # Set the logging version
        'version': 1,
        # Disable existing loggers
        'disable_existing_loggers': False,
        # Set the formatter for the logger
        'formatters': {
            'default': {
                'format': '{asctime} {levelname} {filename}:{lineno} - {message}',
                'style': '{'
            },
        },
        # Set the handlers for the logger
        'handlers': {
            # Handler for logging to the console
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': 'DEBUG',
            },
            # Handler for logging to a file
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_file_path,
                'formatter': 'default',
                'level': 'DEBUG',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
            },
        },
        # Set the loggers for the logger
        'loggers': {
            # Root logger
            __name__: {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
            # Logger for console handler
            f'{__name__}.console': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            # Logger for file handler
            f'{__name__}.file': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': False,
            },
            # Logger for current file with both console and file handlers
            # only this logger is currently in use
            f'{__name__}.{os.path.basename(__file__)}': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    })
    # Return the logger for the current file with both console and file handlers
    return logging.getLogger(f'{__name__}.{os.path.basename(__file__)}')
