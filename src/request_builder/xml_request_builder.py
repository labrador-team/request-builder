from typing import Any, Dict, Union
from xml.etree.ElementTree import Element as XMLElement, fromstring as xml_loads, \
    tostring as xml_dumps, ParseError as XMLParseError

from requests import Response

from .abstract_request_builder import AbstractRequestBuilder


class XMLRequestBuilder(AbstractRequestBuilder[XMLElement, XMLElement]):
    def _process_input_data(self, data: XMLElement) -> Dict[str, Any]:
        return {'data': xml_dumps(data)}

    def _process_response(self, response: Response) -> Union[XMLElement, bytes]:
        if not self._suppress_errors:
            response.raise_for_status()
        try:
            return xml_loads(response.content)
        except XMLParseError:
            if self._suppress_errors:
                return response.content
            else:
                raise
