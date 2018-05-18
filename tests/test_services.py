from unittest.mock import MagicMock, patch

from pydsec.services import CloudAccountsService, TenantsService


@patch("pydsec.services.BaseService.make_request")
def test_cloud_accounts(mocked_request):
    """Tests an API call to list cloud accounts"""
    mocked_request.return_value = MagicMock(
        status_code="200", json=MagicMock(return_value={"test": "json"})
    )

    client = CloudAccountsService(None, "https://example.co.uk")
    response = client.cloud_accounts()

    mocked_request.assert_called_with("get", "", headers={"Accept": "application/json"})
    assert response == {"test": "json"}


@patch("pydsec.services.BaseService.make_request")
def test_tenants(mocked_request):
    """Tests an API call to list tenants"""
    mocked_request.return_value = MagicMock(status_code="200", text="XML")

    client = TenantsService(None, "https://example.co.uk")
    response = client.tenants()

    mocked_request.assert_called_with("get", "")
    assert response == {"tenantListing": {"tenants": "tenants"}}
