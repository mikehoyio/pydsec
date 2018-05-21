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


xml = """<?xml version="1.0" encoding="UTF-8"?>
<tenantListing>
   <tenants>
      <tenantID>21</tenantID>
   </tenants>
   <tenants>
      <tenantID>41</tenantID>
   </tenants>
</tenantListing>"""


@patch("pydsec.services.BaseService.make_request")
def test_tenants(mocked_request):
    """Tests an API call to list tenants"""
    mocked_request.return_value = MagicMock(status_code="200", text=xml)

    client = TenantsService(None, "https://example.co.uk")
    response = client.tenants()

    mocked_request.assert_called_with("get", "")
    assert (
        response
        == {"tenantListing": {"tenants": [{"tenantID": "21"}, {"tenantID": "41"}]}}
    )
