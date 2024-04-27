from typing import Any, Dict, Tuple

from request_builder.abstract_request_builder import AbstractRequestBuilder

ECHO_ENDPOINT_URL = 'https://echo.free.beeceptor.com'
XML_ENDPOINT_URL = 'https://httpbin.org/xml'


def echo_function(*args, **kwargs):
    return args, kwargs


class MockRequestBuilder(AbstractRequestBuilder):
    def _process_input_data(self, data: Any) -> Dict[str, Any]:
        return {'input_data': data}

    def _process_response(self, response: Tuple[Tuple[Any], Dict[str, Any]]) -> Tuple[int, int]:
        args, kwargs = response
        return len(args), len(kwargs)
