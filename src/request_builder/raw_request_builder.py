from typing import Any, Dict, Union, List, IO

from requests import Response

from .abstract_request_builder import AbstractRequestBuilder


class RequestBuilder(AbstractRequestBuilder[Union[dict, List[tuple], str, bytes, IO], bytes]):
    def _process_input_data(self, data: Union[dict, List[tuple], str, bytes, IO]) -> Dict[str, Any]:
        return {'data': data}

    def _process_response(self, response: Response) -> bytes:
        if not self._suppress_errors:
            response.raise_for_status()
        return response.content
