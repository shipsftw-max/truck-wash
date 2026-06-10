from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'مغسلة الشاحنات - شغالة 24 ساعة!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
