from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Here\'s looking at you, kid!'


if __name__ == '__main__':
    app.run()
