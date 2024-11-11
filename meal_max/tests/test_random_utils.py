import pytest
import requests
from meal_max.utils.random_utils import get_random


RANDOM_NUMBER = 0.42  # Example random number returned by the API


@pytest.fixture
def mock_random_org(mocker):
    """Patch requests.get call to simulate a response from random.org."""
    mock_response = mocker.Mock()
    mock_response.text = f"{RANDOM_NUMBER:.2f}"  # Mock response as a string
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


def test_get_random(mock_random_org):
    """Test retrieving a random decimal number from random.org."""
    result = get_random()

    # Assert that the result is the mocked random number
    assert (
        result == RANDOM_NUMBER
    ), f"Expected random number {RANDOM_NUMBER}, but got {result}"

    # Ensure that the correct URL was called
    requests.get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5,
    )


def test_get_random_in_range(mock_random_org):
    """Test that the random number is within the expected range (0 to 1)."""
    result = get_random()
    assert (
        0 <= result <= 1
    ), f"Expected random number to be within range [0, 1], but got {result}"


def test_get_random_request_failure(mocker):
    """Simulate a request failure."""
    mocker.patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Connection error"),
    )

    with pytest.raises(
        RuntimeError, match="Request to random.org failed: Connection error"
    ):
        get_random()


def test_get_random_timeout(mocker):
    """Simulate a timeout."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()


def test_get_random_invalid_response(mock_random_org):
    """Simulate an invalid response (non-float)."""
    mock_random_org.text = "invalid_response"

    with pytest.raises(
        ValueError, match="Invalid response from random.org: invalid_response"
    ):
        get_random()
