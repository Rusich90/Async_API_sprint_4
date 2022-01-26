LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'custom_formatter': {
            'format': '%(levelname)-10s %(name)-10s [%(asctime)s] : %(message)s'
        }
    },

    'handlers': {
        'console_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'custom_formatter',
        },

    },
    'loggers': {
        'my_logger': {
            'handlers': ['console_handler'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
