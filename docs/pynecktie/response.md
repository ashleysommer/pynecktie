# Response

Use functions in `pynecktie.response` module to create responses.

## Plain Text

```python
from pynecktie import response


@app.route('/text')
def handle_request(request):
    return response.text('Hello world!')
```

## HTML

```python
from pynecktie import response


@app.route('/html')
def handle_request(request):
    return response.html('<p>Hello world!</p>')
```

## JSON


```python
from pynecktie import response


@app.route('/json')
def handle_request(request):
    return response.json({'message': 'Hello world!'})
```

## File

```python
from pynecktie import response


@app.route('/file')
async def handle_request(request):
    return await response.file('/srv/www/whatever.png')
```

## Streaming

```python
from pynecktie import response

@app.route("/streaming")
async def index(request):
    async def streaming_fn(response):
        response.write('foo')
        response.write('bar')
    return response.stream(streaming_fn, content_type='text/plain')
```

## File Streaming
For large files, a combination of File and Streaming above
```python
from pynecktie import response

@app.route('/big_file.png')
async def handle_request(request):
    return await response.file_stream('/srv/www/whatever.png')
```

## Redirect

```python
from pynecktie import response


@app.route('/redirect')
def handle_request(request):
    return response.redirect('/json')
```

## Raw

Response without encoding the body

```python
from pynecktie import response


@app.route('/raw')
def handle_request(request):
    return response.raw(b'raw data')
```

## Modify headers or status

To modify headers or status code, pass the `headers` or `status` argument to those functions:

```python
from pynecktie import response


@app.route('/json')
def handle_request(request):
    return response.json(
        {'message': 'Hello world!'},
        headers={'X-Served-By': 'pynecktie'},
        status=200
    )
```
