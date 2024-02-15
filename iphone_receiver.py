from flask import Flask, request

app = Flask(__name__)

@app.route('/text', methods=['POST'])
def receive_text():
    # Access the form data sent with the key "hey"
    text_value = request.get_json()
    input_command = text_value['command']
    print(text_value['command'])
    if text_value is None:
        return ' "command" not found in the form data', 400


    return input_command

if __name__ == '__main__':
    app.run(host='192.168.1.78', port=5000, debug=True)