import sys
import json

import httpx

DEBUG = False

class meraki_api:

    def __init__(self, APIKEY: str):
        self.APIKEY = APIKEY
        self.session = {}
        self.login(self.APIKEY)

    def login(self, APIKEY: str):
        """
        Login to Meraki
        """
        self.base_url_str = "https://api.meraki.com/api/v1/"
        self.login_data = {"X-Cisco-Meraki-API-Key": self.APIKEY}
        login_url = self.base_url_str + "organizations"

        # creat httpx session
        sess = httpx.Client() # (verify=False) if certificate is not trusted

        login_response = sess.get(url=login_url, headers=self.login_data)

        if login_response.status_code != 200:
            print("Login Failed.")
            if DEBUG:
                print(login_response)
                print(login_url)
                print(self.login_data)
            sys.exit(0)

        self.session[self.APIKEY] = sess

    def get_request(self, mount_point: str) -> dict:
        """
        GET request
        """
        url = self.base_url_str + mount_point
        if DEBUG:
            print(url)
        response = self.session[self.APIKEY].get(url, headers=self.login_data)

        if response.status_code != 200:
            print("Error")
            if DEBUG:
                print(response)
                print(url)
                print(self.login_data)
            sys.exit(0)

        data = response.text
        return json.loads(data)

    def async_get(self, mountpoint: str):
        pass

    def async_post(self, mount_point: str, payload: dict):
        pass

    def post_request(self, mount_point: str, payload: dict) -> str:
        """
        POST request
        """
        url = self.base_url_str + mount_point
        payload = json.dumps(payload)
        headers = {"X-Cisco-Meraki-API-Key": self.APIKEY, "Content-Type": "application/json"}

        if DEBUG:
            print(url)

        response = self.session[self.APIKEY].post(
            url=url, data=payload, headers=headers
        )
        if response.status_code == 201:
            return "Success"
        else:
            return response


    def get_organizations(self) -> dict:
        return self.get_request("organizations")

    def get_networks(self, ORGID: str) -> dict:
        return self.get_request(f"organizations/{ORGID}/networks")

    def get_switch_ports_status(self, serial: str) -> dict:
        return self.get_request(f"devices/{serial}/switch/ports/statuses")
    
    def get_switch_ports_config(self, serial: str, port: str = "") -> dict:
        url = f"devices/{serial}/switch/ports/{port}" # all ports, or specific port if given
        return self.get_request(url)


class async_meraki_api:

    async def __init__(self, APIKEY: str):
        self.APIKEY = APIKEY
        self.session = {}
        self.login(self.APIKEY)

    async def login(self, APIKEY: str):
        """
        Login to Meraki
        """
        self.base_url_str = "https://api.meraki.com/api/v1/"
        self.login_data = {"X-Cisco-Meraki-API-Key": self.APIKEY}
        login_url = self.base_url_str + "organizations"

        # creat httpx session
        sess = httpx.AsyncClient() # (verify=False) if certificate is not trusted

        login_response = sess.get(url=login_url, headers=self.login_data)

        if login_response.status_code != 200:
            print("Login Failed.")
            if DEBUG:
                print(login_response)
                print(login_url)
                print(self.login_data)
            sys.exit(0)

        self.session[self.APIKEY] = sess

    async def get_request(self, mount_point: str) -> dict:
        """
        GET request
        """
        url = self.base_url_str + mount_point
        if DEBUG:
            print(url)
        response = self.session[self.APIKEY].get(url, headers=self.login_data)

        if response.status_code != 200:
            print("Error")
            if DEBUG:
                print(response)
                print(url)
                print(self.login_data)
            sys.exit(0)

        data = response.text
        return json.loads(data)

    async def async_get(self, mountpoint: str):
        pass

    async def async_post(self, mount_point: str, payload: dict):
        pass

    async def post_request(self, mount_point: str, payload: dict) -> str:
        """
        POST request
        """
        url = self.base_url_str + mount_point
        payload = json.dumps(payload)
        headers = {"X-Cisco-Meraki-API-Key": self.APIKEY, "Content-Type": "application/json"}

        if DEBUG:
            print(url)

        response = self.session[self.APIKEY].post(
            url=url, data=payload, headers=headers
        )
        if response.status_code == 201:
            return "Success"
        else:
            return response


    async def get_organizations(self) -> dict:
        return self.get_request("organizations")

    async def get_networks(self, ORGID: str) -> dict:
        return self.get_request(f"organizations/{ORGID}/networks")

    async def get_switch_ports_status(self, serial: str) -> dict:
        return self.get_request(f"devices/{serial}/switch/ports/statuses")
    
    async def get_switch_ports_config(self, serial: str, port: str = "") -> dict:
        url = f"devices/{serial}/switch/ports/{port}" # all ports, or specific port if given
        return self.get_request(url)
