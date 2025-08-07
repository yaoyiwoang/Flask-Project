from flask import Flask

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def home_page():
    return 'This is my home page'

if __name__ == '__main__':
    app.run(port=8080)
