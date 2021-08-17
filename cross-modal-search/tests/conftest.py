"""Patch the birthday problem for random parts"""

import pytest


@pytest.fixture(scope='function', autouse=True)
def patched_random_port(mocker):
    used_ports = set()
    from jina.helper import random_port
    from jina.excepts import NoAvailablePortError

    def _random_port():

        for i in range(10):
            _port = random_port()

            if _port is not None and _port not in used_ports:
                used_ports.add(_port)
                return _port
        raise NoAvailablePortError

    mocker.patch('jina.helper.random_port', new_callable=lambda: _random_port)