import logging

import requests
from requests.exceptions import HTTPError

log = logging.getLogger()


class TrendServiceREST:

    def __init__(self, base_url, username='', password='', login=True):
        self.rest_url = f"{base_url}/rest"
        self.username = username
        self.password = password
        self.session = requests.Session()

        if login:
            self._login()

    def _login(self):
        payload = {
            "dsCredentials": {
                "userName": self.username,
                "password": self.password,
            }
        }
        try:
            response = self.session.post(
                f"{self.rest_url}/authentication/login", json=payload
            )
            response.raise_for_status()

            self.session.params.update({"sID": response.text})
        except HTTPError as e:
            log.exception("Login failed")

    def logout(self):
        try:
            response = self.session.delete(
                f"{self.rest_url}/authentication/logout"
            )
            response.raise_for_status()

            if response.text == 'OK':
                self.session.params.pop("sID", None)
        except HTTPError as e:
            log.exception("Logout failed")

    def version(self):
        response = self.session.get(f"{self.rest_url}/apiVersion")
        return {"version": response.text}
