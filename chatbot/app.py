from flask import Flask, render_template, jsonify, request
import preprocessor as processor


app = Flask(__name__)

app.config['SECRET_KEY'] = 'enter-a-very-secretive-key-3479373'


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('main.html', **locals())



@app.route('/chat',methods=['GET','POST'])
#@app.route('/home',methods=['GET','POST'])
def home():
    return render_template('index.html')

@app.route("/get")
def chatbot():
    userText = request.args.get('msg')
    resp=processor.response(userText)
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)