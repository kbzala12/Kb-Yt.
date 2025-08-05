from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "<h2>👋 Welcome to Kingyt YouTube Promo WebApp!</h2><p>✅ This Flask app is running on Replit or Render!</p>"

# 🔹 Future: You can add video code submission, coin update, etc.

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # 🔥 Works on both Replit & Render
    app.run(host='0.0.0.0', port=port)