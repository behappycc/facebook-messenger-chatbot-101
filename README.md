# Facebook Messenger Chatbot 101
## Setting
### Python 3.6
[Python 3.6](https://www.python.org/downloads/)

### ngrok
1. signup your ngrok account
https://ngrok.com/

2. Download ngrok  
[Windows](https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip)  
[Mac](https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip)  
[Linux](https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip) 

3. Connect your account
```
./ngrok authtoken <AUTH_TOKEN>
```

## Install
```
# Clone the repository
$ git clone https://github.com/behappycc/facebook-messenger-chatbot-101.git

# Go into the repository
$ cd facebook-messenger-chatbot-101

# Python3.6
$ sudo pip3 install -r requirements.txt
```

## Usage
```
./ngrok http <PORT_NUMBER>
python3 web_server.py -p <PORT_NUMBER>
```
