from json import JSONDecodeError
from typing import Any, Dict, Union

from requests import Response

from .abstract_request_builder import AbstractRequestBuilder


class JSONRequestBuilder(AbstractRequestBuilder[Union[dict, list], Union[dict, list]]):
    def _process_input_data(self, data: Any) -> Dict[str, Any]:
        return {'json': data}

    def _process_response(self, response: Response) -> Union[Any, bytes]:
        if not self._suppress_errors:
            response.raise_for_status()
        try:
            return response.json()
        except JSONDecodeError:
            if self._suppress_errors:
                return response.text
            else:
                raise
