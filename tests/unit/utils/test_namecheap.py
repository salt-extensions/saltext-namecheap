import pytest
from salt.modules import config

from saltext.namecheap.utils import namecheap


@pytest.fixture
def namecheap_opts():
    return {
        "namecheap.name": "foo",
        "namecheap.user": "bar",
        "namecheap.key": "hunter1",
        "namecheap.client_ip": "1.2.3.4",
        "namecheap.url": "http://name.cheap",
    }


@pytest.fixture
def configure_loader_modules(namecheap_opts):
    return {
        config: {
            "__opts__": namecheap_opts,
        }
    }


def test_get_opts(namecheap_opts):
    """
    Basic test to make the test suite pass
    """
    command = "namecheap.domains.dns.getlist"
    expected = {
        "ApiUser": namecheap_opts["namecheap.name"],
        "UserName": namecheap_opts["namecheap.user"],
        "ApiKey": namecheap_opts["namecheap.key"],
        "ClientIp": namecheap_opts["namecheap.client_ip"],
        "Command": command,
    }
    opts, url = namecheap.get_opts(config.option, command)
    assert opts == expected
    assert url == namecheap_opts["namecheap.url"]
