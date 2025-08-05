from flask import Flask, render_template

app = Flask(__name__)

# 🔓 Home Route
@app.route('/')
def home():
    return render_template('index.html')

# 🔐 Health Check for Render or Uptime
@app.route('/ping')
def ping():
    return "Bot is live ✅"

# 🟢 Main Run
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)