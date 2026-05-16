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
def get_client_ip(request):
    """Takes request and extract client ip"""

    forwarded_for = request.headers.get('X-Forwarded-For')

    if forwarded_for:
        return forwarded_for.split(',')[0].strip()

    return request.remote_addr
