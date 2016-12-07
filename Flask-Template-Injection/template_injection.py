from flask import Flask, request, render_template_string, render_template

app = Flask(__name__)

# 127.0.0.1:5000/template-injection?name=Batman {{person.secret}}
# 127.0.0.1:5000/template-injection?name=Batman {{get_user_file(%22file/secret.txt%22)}}
@app.route('/template-injection')
def hello_ssti():
    person = {'name': "world", 'secret': "Potato is cool"}
    if request.args.get('name'):
        person['name'] = request.args.get('name')
    template = '''<h2>Hello %s!</h2>''' % person['name']
    print template
    return render_template_string(template, person=person)


# TODO
# 127.0.0.1:5000/protected?name=Batman.<script>alert("Hi")</script>
@app.route('/protected')
def hello_protected():
    person = {'name': "world", 'secret': "Potato is still cool"}
    if request.args.get('name'):
        person['name'] = request.args.get('name')
        print "NAME IS", person['name']
    template = '''<h2>Hello {{ person.name }}!</h2>'''
    # template = '''Hello {{ person.name }}'''
    print template
    return render_template_string(template, person=person)


# Note: document.title doesn't work in Chrome
# 127.0.0.1:5000/xss?name=Batman<script>document.title="No escaping here"</script>
# with | e no change in doc title
@app.route('/xss')
def xss():
    name = "world"
    template = 'hello.unsafe' # 'unsafe' file extension... totally legit.
    if request.args.get('name'):
        name = request.args.get('name')
    return render_template(template, name=name)


# TODO onmouseover doesn't work on URL
# http://127.0.0.1:5000/attribute-injection?name=test onmouseover="document.title='Potatos!'"
@app.route('/attribute-injection')
def attribute():
    template = '''<title>No Injection Allowed!</title>
        <a href={{ url_for('xss')}}?name={{ name | e }} onmouseover="document.title='Potatos!'">
        Click here for a welcome message</a>'''
    name = "world"
    if request.args.get('name'):
        name = request.args.get('name')
    return render_template_string(template, name=name)


###
# Private function if the user has local files.
###
def get_user_file(f_name):
    with open(f_name) as f:
        return f.readlines()

app.jinja_env.globals['get_user_file'] = get_user_file # Allows for use in Jinja2 templates

if __name__ == "__main__":
    app.run(debug=True)
