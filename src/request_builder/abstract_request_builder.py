import itertools
from abc import ABCMeta, abstractmethod
from http.cookiejar import CookieJar
from typing import Dict, Any, Callable, Union, Generic, TypeVar, Tuple, IO
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

import requests
from requests import Response
from requests.auth import AuthBase

TIn = TypeVar('TIn')
TOut = TypeVar('TOut')


class AbstractRequestBuilder(Generic[TIn, TOut], metaclass=ABCMeta):
    def __init__(self,
                 path: str,
                 suppress_errors: bool = False,
                 *,
                 cert: Union[str, Tuple[str, str]] = None,
                 auth: AuthBase = None,
                 allow_redirects: bool = None,
                 verify: bool = None,
                 proxies: Dict[str, str] = None,
                 **kwargs: Any):
        self._path: str = path
        if cert:
            kwargs['cert'] = cert
        if auth:
            kwargs['auth'] = auth
        if allow_redirects is not None:
            kwargs['allow_redirects'] = allow_redirects
        if verify is not None:
            kwargs['verify'] = verify
        if proxies:
            kwargs['proxies'] = proxies
        self._kwargs: Dict[str, Any] = kwargs
        self._suppress_errors: bool = suppress_errors

    def __getitem__(self, item: str) -> Self:
        return self.__class__(f'{self._path}/{item}',
                              suppress_errors=self._suppress_errors,
                              **self._kwargs)

    def __getattr__(self, item: str) -> Self:
        if item.startswith('_'):
            return super().__getattribute__(item)
        return self[item]

    def __setattr__(self, key: str, value: Any):
        if key.startswith('_'):
            return super().__setattr__(key, value)
        elif key == 'path':
            self._path = value
        else:
            self._kwargs[key] = value

    @abstractmethod
    def _process_input_data(self, data: TIn) -> Dict[str, Any]:
        """
        Process new data for the request and return new kwargs
        :param data: The new data for the request. Type can vary.
        :return: A dictionary to assimilate into the kwargs for the request. (Ex.: {'data': <new_data>})
        """
        pass

    def __call__(self,
                 data: TIn = None,
                 *,
                 files: Dict[str, Union[IO, Tuple[str, IO], Tuple[str, IO, str], Tuple[str, IO, str, Dict[str, str]]]] = None,
                 auth: AuthBase = None,
                 headers: Dict[str, str] = None,
                 timeout: Union[float, Tuple[float, float]] = None,
                 stream: bool = None,
                 cookies: Union[CookieJar, Dict[str, Any]] = None,
                 **params: Any) -> Self:
        new_kwargs: Dict[str, Any] = dict(self._kwargs)

        # Handle data
        new_kwargs.update(self._process_input_data(data))

        # Handle cookies
        new_value = new_kwargs.pop('cookies', None)
        if new_value is None:
            new_value = cookies
        elif isinstance(new_value, dict) and isinstance(cookies, dict):
            new_value.update(cookies)
        elif isinstance(new_value, dict) and isinstance(cookies, CookieJar):
            for cookie in cookies:
                new_value[cookie.name] = cookie.value
        elif isinstance(new_value, CookieJar) and isinstance(cookies, dict):
            for cookie in new_value:
                cookies[cookie.name] = cookie.value
            new_value = cookies
        elif isinstance(new_value, CookieJar) and isinstance(cookies, CookieJar):
            new_value = {
                cookie.name: cookie.value
                for cookie in itertools.chain(new_value, cookies)
            }
        else:
            new_value = cookies

        if new_value:
            new_kwargs['cookies'] = new_value

        # Handle additives
        for key, value in [('files', files), ('headers', headers), ('params', params)]:
            new_value = new_kwargs.pop(key, {})
            new_value.update(value or {})
            if new_value:
                new_kwargs[key] = new_value

        # Handle everything else
        for key, value in [('auth', auth), ('timeout', timeout), ('stream', stream)]:
            if value is not None:
                new_kwargs[key] = value

        return self.__class__(self._path, suppress_errors=self._suppress_errors, **new_kwargs)

    def __truediv__(self, other: Union[Callable, str]) -> Response:
        if callable(other):
            return other(self._path, **self._kwargs)
        else:
            return requests.request(other, self._path, **self._kwargs)

    def __rtruediv__(self, other: Union[Callable, str]) -> Response:
        return self / other

    @abstractmethod
    def _process_response(self, response: Response) -> TOut:
        return

    def __floordiv__(self, other: Union[Callable, str]) -> TOut:
        response = self / other
        return self._process_response(response)

    def __rfloordiv__(self, other: Union[Callable, str]) -> TOut:
        return self // other

    def __repr__(self) -> str:
        parameters = ", ".join(f"{key}={value!r}" for key, value in self._kwargs.items())
        return f'<{self.__class__.__name__}[{self._path}]({parameters})>'

    def __str__(self) -> str:
        return repr(self)
