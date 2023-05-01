import logging
import sys

# file logger
#file_handler = FileHandler('/path/to/file.log')
#file_handler.setLevel(logging.DEBUG)
#file_handler.setFormatter(formatter)
#logger.addHandler(file_handler)
#logger.removeHandler(logger.handlers[0]) # remove old handler outputting through stdout



# def setup_logger():
#     # Create logger
#     logger = logging.getLogger(__name__)
#     logger.setLevel(logging.INFO) # only equal or higher than this level will be logged

#     # Create console handler and set level to debug
#     console_handler = logging.StreamHandler(sys.stdout)
#     console_handler.setLevel(logging.INFO) # only equal or higher than this level will be logged

#     # Create formatter
#     formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s')

#     # Add formatter to console handler
#     console_handler.setFormatter(formatter)

#     # Add console handler to logger
#     logger.addHandler(console_handler)

#     return logger



import logging.config
import os

def setup_logger():
    log_file_path = os.path.join(os.path.dirname(__file__), 'logs', 'app.log')
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '{asctime} {levelname} {filename}:{lineno} - {message}',
                'style': '{'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': 'DEBUG',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_file_path,
                'formatter': 'default',
                'level': 'INFO',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
            },
        },
        'loggers': {
            __name__: {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
            f'{__name__}.console': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            f'{__name__}.file': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': False,
            },
            f'{__name__}.{os.path.basename(__file__)}': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    })
    
    return logging.getLogger(f'{__name__}.{os.path.basename(__file__)}')
