import logging
import re
from contextlib import contextmanager

import requests

from .services import BaseService

# from zeep import Client


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
        # self._register_soap_services()

        if username is not None and password is not None:
            self.login()

    def _register_rest_services(self):
        for cls in BaseService.__subclasses__():
            name = to_snake(cls.__name__.replace("Service", ""))
            service = cls(self.session, self.rest_url)
            setattr(self, name, service)

    # def _register_soap_services(self):
    #     self.soap = Client(f"{self.base_url}/webservice/Manager?WSDL").service

    # def __getattr__(self, name):
    #     import pdb;pdb.set_trace()
    #     return getattr(self.__soap.service, name)

    def login(self):
        session_id = self.authentication.login(self.username, self.password)
        self.session.params.update({"sID": session_id})

    def logout(self):
        self.authentication.logout()
        self.session.params.pop("sID", None)

    @contextmanager
    def as_tenant(self, tenant_name):
        root_session_id = self.session.params["sID"]
        session_id = self.authentication.tenant_login(tenant_name)
        self.session.params.update({"sID": session_id})

        yield self

        self.authentication.logout()
        self.session.params.update({"sID": root_session_id})

    def api_version(self):
        response = self.session.get(f"{self.rest_url}/apiVersion")
        return {"version": response.text}
