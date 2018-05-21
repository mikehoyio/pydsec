import logging
import re
from contextlib import contextmanager
from functools import wraps

import requests

from zeep import Client

from .services import BaseService

log = logging.getLogger()


def to_snake(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class Trend:

    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url
        self.rest_url = f"{base_url}/rest"
        self.username = username
        self.password = password
        self.session = requests.Session()
        self._register_rest_services()

        if username is not None and password is not None:
            self.login()

    def _register_rest_services(self):
        for cls in BaseService.__subclasses__():
            name = to_snake(cls.__name__.replace("Service", ""))
            service = cls(self.session, self.rest_url)
            setattr(self, name, service)

    @property
    def soap(self):
        if not hasattr(self, "_soap"):
            self._soap = SoapWrapper(self.base_url)
        self._soap.sid = self._sid
        return self._soap

    @property
    def _sid(self):
        return self.session.params["sID"]

    @_sid.setter
    def _sid(self, value):
        if value is None:
            self.session.params.pop("sID", None)
        else:
            self.session.params.update({"sID": value})

    def login(self):
        self._sid = self.authentication.login(self.username, self.password)

    def logout(self):
        self.authentication.logout()
        self._sid = None

    @contextmanager
    def as_tenant(self, tenant_name):
        root_session_id = self._sid
        self._sid = self.authentication.tenant_login(tenant_name)

        yield self

        self.authentication.logout()
        self._sid = root_session_id

    def api_version(self):
        response = self.session.get(f"{self.rest_url}/apiVersion")
        return {"version": response.text}


class SoapWrapper:

    def __init__(self, base_url):
        self._client = Client(f"{base_url}/webservice/Manager?WSDL")

    def __getattr__(self, attr):
        attr = getattr(self._client.service, attr)
        if not callable(attr):
            return attr

        @wraps(attr)
        def _wrapped(*args, **kwargs):
            defaults = {"sID": self.sid}
            defaults.update(kwargs)
            return attr(*args, **defaults)

        return _wrapped
