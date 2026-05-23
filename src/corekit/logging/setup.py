#   -----------------------------------------------------------------------------
#  Copyright (c) 2026. Vincent Corriveau (vincent.corriveau89@gmail.com)
#
#  Licensed under the MIT License. You may obtain a copy of the License at
#  https://opensource.org/licenses/MIT
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  -----------------------------------------------------------------------------
import os
import logging
from logging.config import dictConfig
from corekit.logging import TrailFilter, ConsoleFormatter, ISOJsonFormatter

def setup_logging(service_name, log_level='INFO'):
    log_level = getattr(logging, log_level.upper())

    # Prevent werkzeug and sqlalchemy.engine to talk to much
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(log_level + 10)

    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,

        'filters': {
            'context': {
                '()': TrailFilter,
                'service_name': service_name
            }
        },

        'formatters': {
            'console': {
                '()': ConsoleFormatter,
                'format': (
                    '[%(asctime)s] '
                    '[%(levelname)-8s] '
                    '[%(service)s] '
                    '[%(trail_id)-36s] '
                    '%(name)-30s - %(message)s'
                )
            },
            'json': {
                '()': ISOJsonFormatter,
                'fmt': (
                    '%(asctime)s '
                    '%(levelname)s '
                    '%(service)s '
                    '%(trail_id)s '
                    '%(name)s '
                    '%(message)s '
                )
            }
        },

        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': os.getenv('LOG_FORMAT', 'json'),
                'filters': ['context'],
            }
        },

        'root': {
            'level': log_level,
            'handlers': ['console']
        }
    })