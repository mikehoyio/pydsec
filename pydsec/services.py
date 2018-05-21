import logging
import xml.etree.ElementTree as ET
from urllib.parse import quote

from requests.exceptions import ConnectionError, HTTPError, Timeout

from .exceptions import InternalServerError, Unavailable

log = logging.getLogger()


class BaseService:

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.url = f"{self.base_url}/rest/{self.service_path}"

    def make_request(self, method, url, *args, **kwargs):
        try:
            func = getattr(self.session, method)
            endpoint = f"{self.url}/{url}"
            log.info(f"Calling: {endpoint}")
            response = func(endpoint, *args, **kwargs)
        except (ConnectionError, Timeout) as e:
            log.exception("Connection Error")
            raise Unavailable() from e

        response.raise_for_status()

        return response


class AuthenticationService(BaseService):
    service_path = "authentication"

    def login(self, username, password):
        try:
            response = self.make_request(
                "post",
                "login",
                json={"dsCredentials": {"userName": username, "password": password}},
            )
        except HTTPError as e:
            log.exception("Login failed")
            raise InternalServerError() from e

        return response.text

    def tenant_login(self, tenant_name):
        try:
            tenant_name = quote(tenant_name, safe="")
            response = self.make_request("get", f"signinastenant/name/{tenant_name}")
        except HTTPError as e:
            log.exception("Tenant Login failed")
            raise InternalServerError() from e

        return response.text

    def logout(self):
        try:
            self.make_request("delete", "logout")
        except HTTPError as e:
            log.exception("Logout failed")
            raise InternalServerError() from e


class CloudAccountsService(BaseService):
    service_path = "cloudaccounts"

    def cloud_accounts_by_name(self, name):
        return self.cloud_accounts(name)

    def cloud_accounts(self, url=""):
        try:
            response = self.make_request(
                "get", url, headers={"Accept": "application/json"}
            )
        except HTTPError as e:
            log.exception("Cloud accounts failed")
            raise InternalServerError() from e

        return response.json()


class TenantsService(BaseService):
    service_path = "tenants"

    def tenants_by_name(self, name):
        return self.tenants(f"name/{name}")

    def tenants_by_id(self, id):
        return self.tenants(f"id/{id}")

    def tenants(self, url=""):
        try:
            response = self.make_request("get", url)
        except HTTPError as e:
            log.exception("Tenants failed")
            raise InternalServerError() from e

        # Having to do this because trend will not return json
        tree = ET.fromstring(response.text)
        tenants = [{t.tag: t.text for t in tenant} for tenant in tree]

        return {"tenantListing": {"tenants": tenants}}
