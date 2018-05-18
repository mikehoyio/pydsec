import logging
import xml.etree.ElementTree as ET
from urllib.parse import quote

from requests.exceptions import HTTPError

log = logging.getLogger()


class BaseService:

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    @property
    def url(self):
        return f"{self.base_url}/{self.service_path}"


class AuthenticationService(BaseService):
    service_path = "authentication"

    def login(self, username, password, primary, sso):
        if primary and sso:
            raise ValueError("Do not supply both arguments")

        url = f"{self.url}/login"
        if primary:
            url = f"{url}/primary"

        if sso:
            url = f"{url}/sso"

        payload = {"dsCredentials": {"userName": username, "password": password}}
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.text

        except HTTPError as e:
            log.exception("Login failed")

    def tenant_login(self, tenant_name):
        try:
            tenant_name = quote(tenant_name, safe="")
            response = self.session.get(f"{self.url}/signinastenant/name/{tenant_name}")
            response.raise_for_status()
            return response.text

        except HTTPError as e:
            log.exception("Login failed")

    def logout(self):
        try:
            response = self.session.delete(f"{self.url}/logout")
            response.raise_for_status()

        except HTTPError as e:
            log.exception("Logout failed")


class CloudAccountsService(BaseService):
    service_path = "cloudaccounts"

    def list_cloud_accounts(self, cloud_account=None):
        url = self.url
        if cloud_account:
            url = f"{url}/{cloud_account}"
        response = self.session.get(url, headers={"Accept": "application/json"})

        return response.json()


class TenantsService(BaseService):
    service_path = "tenants"

    def get(self, id=None, name=None):
        if name and id:
            raise ValueError("Do not supply both arguments")

        url = self.url
        if id:
            url = f"{url}/id/{id}"

        if name:
            url = f"{url}/name/{name}"
        response = self.session.get(url)

        # Having to do this because trend will not return json
        tree = ET.fromstring(response.text)
        tenants = [{t.tag: t.text for t in tenant} for tenant in tree]

        return {"tenantListing": {"tenants": tenants}}
