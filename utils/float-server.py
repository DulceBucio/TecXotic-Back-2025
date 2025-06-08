from flask import Flask, request

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    data = request.data.decode('utf-8')
    print(f"[DATA RECEIVED]\n{data}\n")

    with open("received_data.txt", "a") as f:
        f.write(data + "\n")

    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
