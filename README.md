# Request Builder
A utility for building requests with the `requests` library

## Key Features

- dot-notation for path expansions
- call-notation to add different parameters
- slash-notation to send request, using a `requests` function of a method string
- double-slash-notation for post-processing responses

## Examples

### Initialization

```python
from request_builder import RequestBuilder

rb = RequestBuilder('https://example.domain.com')
```

### Expanding the path

```python
# New path will be https://example.domain.com/path/to/endpoint
rb = rb.path.to.endpoint

# Overriding the existing path
rb.path = 'https://example.domain.com/path'
```

### Adding query parameters to request

```python
# Request will now send the two params added
rb = rb(param1='value1', param2='value2')

# Query params are additive, so you can add more and override existing values
rb = rb(param3='value3', param1='value4')  # params are now ?param1=value4&param2=value2&param3=value3

# You can override all params by setting them directly on the request builder
rb.params = {'param1': 'value2'}  # all existing params got overridden
```

### Adding other additive request parameters

**Note:** The same principal applies to the `files` parameter

```python
rb = rb(headers={'X-Custom-Header': 'some_value'})

# Like query params, headers are also additive
rb = rb(header={'X-Another-Custom-Header': 'some_other_value'})  # 2 headers are now present

# And like query params, headers can also be overridden entirely
rb.headers = {'X-Final-Custom-Header': 'another_value'}  # all existing headers got overridden
```

### Adding data to request

The type of data and the processing will depend on the type of request builder used.
The regular `RequestBuilder` expects data for the `data` parameter of `requests` functions,
The `JSONRequestsBuilder` expects a JSON-serializable object and will pass it to the `json`
parameter of `requests` functions. The `XMLRequestsBuilder` expects an XML element from the
XML python library (specifically, `xml.etree.ElementTree.Element`), which it will then
dump as bytes and send to the `data` parameter of the `requests` functions.

```python
rb = rb(b'Some data to send to the server')

# Setting the data again will override the existing data, as it is a non-additive parameter
rb = rb(b'Other data to send to the server')  # This overrides the previously set data

from request_builder import JSONRequestBuilder

jrb = JSONRequestBuilder('https://example.domain.com')
jrb = jrb({'some': 'json_data'})  # Will be passed to the `json` parameter
```

### Adding other non-additive request parameters

**Note:** The same principal applies to the `auth` and `stream` parameters

```python
rb = rb(timeout=3.0)

# Setting timeout again will override the previous one
rb = rb(timeout=(2.0, 1.0))
```

### Adding cookies

Cookies are a special case because `requests` accepts both dictionaries and `CookieJar` objects,
so handling them is a little more nuanced. Cookies are additive, and both types can be used
when setting them. If a `CookieJar` is set, adding cookies to it will convert the `CookieJar`
to a dictionary and add the new cookies (this will happen whether the added cookies are in the
form of a `CookieJar` or a dictionary), but as long as no cookies are added the `CookieJar` will
not change its type. If a dictionary is set, all added cookies, no matter what form, will be
added to a dictionary.

```python
rb = rb(cookies='<a_cookie_jar>')  # As long as cookies aren't added, the CookieJar will remain

# Adding other cookies will break the jar and create a dictionary with the cookies from the jar
# and the added cookies
rb = rb(cookies={'cookie1': 'cookie_value1'})

# A CookieJar can be added to another CookieJar or a dictionary, it will break the jar and add
# the cookies together
rb = rb(cookies='<another_cookie_jar>')
```

### Sending the request

To send the request to the server, slash-notation is used. A function can be used with the
`RequestBuilder` or an HTTP method. The returned data-type if a `requests.Response` object.

#### Using an HTTP method

```python
response = 'GET' / rb

# Also works the other way around!
response = rb / 'POST'
```

#### Using a custom function

```python
import requests

response = requests.get / rb

response = rb / requests.post
```

### Getting a processed response

The request builder can be used raw (with a single slash) or return a processed response, using
double-slash notation. Like the raw form, both HTTP method strings and custom functions can be used.
The return type will depend on the type of `RequestBuilder` used. The raw one will just return the
raw response bytes, the `JSONRequestBuilder` will return the output of calling the `json()` method
on the response, and `XMLRequestBuilder` will try to parse the response bytes as an XML element and
then return it (the return type will be `xml.etree.ElementTree.Element`).

```python
from request_builder import JSONRequestBuilder

rb = JSONRequestBuilder('https://example.domain.com')
response_json = 'GET' // rb

response_json = rb // 'GET'  # Also works!
```

#### Error suppression

Additionally, there is an option when initializing the builder to supress errors. By default, request
builders will raise an error for non-OK HTTP response codes and parsing issues, but if the suppression
option if turned on all errors will be suppressed and the following behaviour will be occurring:

- If the response code is not ok (so if `response.ok` is `False`), no error will be raised and the
  response data will be passed to processing.
- If the parsing fails, the raw response bytes will be returned instead.

```python
from request_builder import RequestBuilder

rb = RequestBuilder('https://example.domain.com', suppress_errors=True)  # All errors will be suppressed
```

## Parameter Reference

All parameters can be set through the initialization of the builder and setting attributes afterward,
but only some can be set through the `__call__` function. The breakdown is as follows:

### Additive parameters

- `params` (through kwargs in `__call__`)
- `headers`
- `files`
- `cookies`

### Non-additive-parameters

- `data` (1st positional argument in `__call__`)
- `auth`
- `timeout`
- `stream`

### Init-only parameters (not available to set through `__call__`)

- `cert`
- `allow_redirects`
- `verify`
- `proxies`

### RequestBuilder custom parameters

- `suppress_errors` (cannot be changed after initialization)
