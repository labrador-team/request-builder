from json import JSONDecodeError
from typing import Dict, Any, Callable
from typing_extensions import Self

from requests import Response


class RequestBuilder(object):
    def __init__(self, path: str, **kwargs):
        self._path: str = path
        self._kwargs: Dict[str, Any] = kwargs

    def __getitem__(self, item: str) -> Self:
        return self.__class__(f'{self._path}/{item}', **self._kwargs)

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

    def __call__(self, json_data=None, *, files=None, auth=None, headers=None,
                 data=None, timeout=None, stream=None, cookies=None, **params):
        new_kwargs: Dict[str, Any] = dict(self._kwargs)

        # Handle data
        if json_data:
            new_kwargs.pop('data', None)
            new_kwargs['json'] = json_data
        elif data:
            new_kwargs.pop('json', None)
            new_kwargs['data'] = data

        # Handle additives
        for key, value in [('files', files), ('headers', headers), ('cookies', cookies), ('params', params)]:
            new_value = new_kwargs.pop(key, {})
            new_value.update(value)
            if new_value:
                new_kwargs[key] = new_value

        # Handle everything else
        for key, value in [('auth', auth), ('timeout', timeout), ('stream', stream)]:
            if value:
                new_kwargs[key] = value

        return self.__class__(self._path, **new_kwargs)

    def __truediv__(self, other: Callable) -> Response:
        return other(self._path, **self._kwargs)

    def __rtruediv__(self, other: Callable) -> Response:
        return self / other

    def __floordiv__(self, other: Callable):
        response = self / other
        if response.ok:
            try:
                return response.json()
            except JSONDecodeError:
                return response.content.decode(response.encoding)
        else:
            response.raise_for_status()

    def __rfloordiv__(self, other: Callable):
        return self // other

    def __repr__(self):
        parameters = ", ".join(f"{key}={value!r}" for key, value in self._kwargs.items())
        return f'<{self.__class__.__name__}[{self._path}]({parameters})>'

    def __str__(self):
        return repr(self)
