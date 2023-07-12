#!/usr/bin/env python3
from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host="192.168.0.10") #host app on local network
    #app.run(debug=True)
