import requests
import logging
from hashlib import md5
from enum import Enum
import webbrowser
from typing import Callable

logger = logging.getLogger(__file__)


class Permission(Enum):
    """
    read – gives the ability to read task, contact, group and list details and contents.
    write – gives the ability to add and modify task, contact, group and list details and contents (also allows you to read).
    delete – gives the ability to delete tasks, contacts, groups and lists (also allows you to read and write).
    """
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'


class RTMMethod(Enum):
    """
    https://www.rememberthemilk.com/services/api/methods.rtm
    """
    TASKS__GET_LIST = 'rtm.tasks.getList'
    AUTH__GET_TOKEN = 'rtm.auth.getToken'


class RTMClient:
    HOST = 'https://api.rememberthemilk.com'
    AUTH = f'{HOST}/services/auth/'
    REST = f'{HOST}/services/rest/'
    FORMAT = 'json'
    API_VERSION = 2

    def __init__(self, api_key: str, secret: str) -> None:
        self.api_key = api_key
        self.secret = secret
        self.token = ''


    def _calculate_signature(self, params: dict[str, str]) -> str:
        """https://www.rememberthemilk.com/services/api/authentication.rtm"""
        params_sorted = sorted(params.items(), key=lambda item: item[0])
        params_concat = "".join(f'{key}{val}' for key, val in params_sorted)
        token = f'{self.secret}{params_concat}'
        hash = md5(token.encode('utf-8'))
        return hash.hexdigest()


    def _get_frob(self, permission: Permission):
        """https://www.rememberthemilk.com/services/api/authentication.rtm"""
        params = dict(
            api_key=self.api_key,
            perm=permission,
        )
        params['api_sig'] = self._calculate_signature(params)

        url = requests.Request('GET', self.AUTH, params=params).prepare().url
        logger.debug('Called auth:\n%s', url)
        webbrowser.open(url)


    def _get_token(self, frob: str) -> str:
        """https://www.rememberthemilk.com/services/api/methods/rtm.auth.getToken.rtm"""
        body = self._get(
            method=RTMMethod.AUTH__GET_TOKEN,
            arguments=dict(frob=frob),
            token=False,
        )
        return body['token']


    def _get(self, method: RTMMethod, arguments: dict, token=True) -> dict:
        """https://www.rememberthemilk.com/services/api/request.rest.rtm"""
        params = dict(
            method=method.value,
            api_key=self.api_key,
            format=self.FORMAT,
            v=self.API_VERSION,
            **arguments,
        )
        if token:
            params['auth_token'] = self.token

        params['api_sig'] = self._calculate_signature(params)
        
        resp = requests.get(self.REST, params=params)
        logger.debug('Called method %s got:\n%s', method, resp.text)

        resp.raise_for_status()
        
        return resp.json()


    def authenticate(self, prompt: Callable[[], str]):
        """"""
        # TODO check token
        self._get_frob(Permission.DELETE)
        frob = prompt()
        self.token = self._get_token(frob)


    def get(self, method: RTMMethod, arguments: None | dict) -> dict:
        if not arguments:
            arguments = {}
        body = self._get(
            method=method,
            arguments=arguments,
        )
        return body
