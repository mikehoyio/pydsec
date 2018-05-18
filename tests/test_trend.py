from unittest.mock import MagicMock, patch

from pydsec import Trend


@patch("pydsec.pydsec.requests.Session.get")
def test_Trend_api_version(mocked_get):
    """Tests an API call to get REST API version"""
    mocked_get.return_value = MagicMock(status_code="200", text="3")
    client = Trend("https://example.co.uk")

    result = client.api_version()

    mocked_get.assert_called_with("https://example.co.uk/rest/apiVersion")
    assert isinstance(result, dict)
    assert result["version"] == "3"


@patch("pydsec.pydsec.requests.Session.post")
def test_Trend_login(mocked_post):
    """Tests instantiating Trend results in login"""
    mocked_post.return_value = MagicMock(status_code="200", text="123456789")
    client = Trend("https://example.co.uk", "username", "password")

    result = client.session.params

    mocked_post.assert_called_with(
        "https://example.co.uk/rest/authentication/login",
        json={"dsCredentials": {"userName": "username", "password": "password"}},
    )
    assert "sID" in result
    assert result["sID"] == "123456789"
    assert isinstance(result["sID"], str)


@patch("pydsec.pydsec.requests.Session.delete")
@patch("pydsec.pydsec.requests.Session.post")
def test_Trend_logout(mocked_post, mocked_delete):
    """Tests an API call to logout"""
    mocked_post.return_value = MagicMock(status_code="200", text="123456789")
    mocked_delete.return_value = MagicMock(status_code="200", text="OK")
    client = Trend("https://example.co.uk", "username", "password")

    client.logout()
    result = client.session.params

    mocked_delete.assert_called_with("https://example.co.uk/rest/authentication/logout")
    assert "sID" not in result


@patch("pydsec.pydsec.requests.Session.delete")
@patch("pydsec.pydsec.requests.Session.get")
@patch("pydsec.pydsec.requests.Session.post")
def test_Trend_tenant_login(mocked_post, mocked_get, mocked_delete):
    """Tests an API call to login as a tenant"""
    mocked_post.return_value = MagicMock(status_code="200", text="123456789")
    mocked_get.return_value = MagicMock(status_code="200", text="123456789-tenant")
    mocked_delete.return_value = MagicMock(status_code="200", text="OK")
    client = Trend("https://example.co.uk", "username", "password")

    with client.as_tenant("tenant_name") as t_client:
        result = t_client.session.params
        assert result["sID"] == "123456789-tenant"

    mocked_get.assert_called_with(
        "https://example.co.uk/rest/authentication/signinastenant/name/tenant_name"
    )
    assert result["sID"] == "123456789"
