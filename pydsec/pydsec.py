import logging
import re

import requests

from .services import BaseService

log = logging.getLogger()


def to_snake(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class TrendServiceREST:

    def __init__(self, base_url, username=None, password=None):
        self.rest_url = f"{base_url}/rest"
        self.username = username
        self.password = password
        self.session = requests.Session()
        self._register_services()

        if username is not None and password is not None:
            self.authentication.login(self.username, self.password)

    def _register_services(self):
        for cls in BaseService.__subclasses__():
            name = to_snake(cls.__name__.replace("Service", ""))
            service = cls(self.session, self.rest_url)
            setattr(self, name, service)

    # def __getattr__(self, name):
    #     return getattr(self.__authentication, name)

    def version(self):
        response = self.session.get(f"{self.rest_url}/apiVersion")
        return {"version": response.text}
