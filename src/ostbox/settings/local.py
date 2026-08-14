from .base import *

DEBUG = True

TASKS = {
    'default': {
        'BACKEND': 'django.core.tasks.backends.immediate.ImmediateBackend',
    }
}