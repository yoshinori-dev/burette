# Burette

A micro web framework for python3.

## HelloWorld

Here is an example of the HelloWorld.

```python

from burette import Burette

app = Burette()

@app.route('/hello/world')
def helloworld():
    return "Hello World!"

if __name__ == '__main__':
    app.run_local()

```

## Routing

Here are some routing examples.

```python

# /hello/Jack -> "Hello Jack"
@app.route('/hello/<yourname>')
def hello_path(request):
    return "Hello " + request.path_params.get('yourname')


# /hello?yourname=Ken -> "Hello Ken"
@app.route('/hello')
def hello_querystring(request):
    return "Hello " + request.params.get('yourname')
    

# POST and PUT
@app.route('/hello_post', method='POST')
def hello_post(request):
    return "Hello " + request.text

```

## Redirecting

```python
from burette import redirect

@app.route('/redirect')
def redirect_example():
    return redirect('/to/path')

```

## JSON

Sometimes you may want to return json to the client.
Just return a dictionary for that.

```python

@app.route('/json')
def get_json():
    return {'key': 'value'}

```

