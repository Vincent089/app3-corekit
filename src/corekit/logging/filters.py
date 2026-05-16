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
import logging
from corekit.context import trail_id_var, user_id_var


class TrailFilter(logging.Filter):

    def __init__(self, service_name):
        super().__init__()
        self.service_name = service_name

    def filter(self, record):
        record.trail_id = trail_id_var.get()
        record.user_id = user_id_var.get()
        record.service = self.service_name

        return True
