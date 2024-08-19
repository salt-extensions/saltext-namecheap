import pytest

pytestmark = [
    pytest.mark.requires_salt_modules("namecheap.example_function"),
]


@pytest.fixture
def namecheap(modules):
    return modules.namecheap


def test_replace_this_this_with_something_meaningful(namecheap):
    echo_str = "Echoed!"
    res = namecheap.example_function(echo_str)
    assert res == echo_str
