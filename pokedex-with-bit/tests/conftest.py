import pytest
# TODO: Use Jina module once the Jina version is updated to at least 1.2.0
# from jina.excepts import NoAvailablePortError


@pytest.fixture(scope='function', autouse=True)
def patched_random_port(mocker):
    used_ports = set()
    from jina.helper import random_port

    def _random_port():

        for _ in range(10):
            _port = random_port()

            if _port is not None and _port not in used_ports:
                used_ports.add(_port)
                return _port
        raise RuntimeError('No port is available')

    mocker.patch('jina.helper.random_port', new_callable=lambda: _random_port)
