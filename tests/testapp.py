from burette import Burette, redirect, jinja2

app = Burette()


@app.route('/hoge/path')
def hogepath(req):
    q = req.params.get('q', [''])[0]
    return "<html><body>my first app: q = " + q + \
           "<form method='POST' action='/post'><input name=mytext type=text><input name='POST' type=submit></form>" + \
           "</body></html>"


@app.route('/empty')
def empty():
    return "<html><body>" \
           "<form method='POST' action='/post'><input name=mytext type=text><input name='POST' type=submit></form>" + \
           "</body></html>"


@app.route('/post', method='POST')
def post_route(request):
    return "<html><body> posted body = " + request.text + \
           "<form method='POST' action='/post'><input name=mytext type=text><input name='POST' type=submit></form>" + \
           "</body></html>"


@app.route('/json')
def give_me_json():
    return {'a': 'b', 'aa': [1, 2, 3]}


@app.route('/redirect')
def abc():
    return redirect('/empty')


@app.route('/jinja2')
def jinja():
    return jinja2('hoge.tpl', users=[{'url': 'http://www.yahoo.com', 'name': 'Yahoo'}, {'url': 'http://www.gmail.com', 'name': 'GMAIL'}], template_path='./tests/templates')


if __name__ == '__main__':
    app.run_local()
