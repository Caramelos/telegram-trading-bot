import os
port = int(os.environ.get("PORT", 8080))

# Update the webhook server to use PORT environment variable
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)