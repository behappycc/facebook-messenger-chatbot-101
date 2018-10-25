import argparse

from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}
    
    def post(self):
        json_data = request.get_json()
        data = {
          "message": f"hello {json_data['name']}!"
        }
        return data

api.add_resource(HelloWorld, '/')

def main():
    parser = argparse.ArgumentParser(description='Messenger Bot Server')
    parser.add_argument(
        '-p', type=int, help='listening port for Messenger Bot Server', default=8000)
    args = parser.parse_args()
    port = args.p
    app.run(port=port, debug=True)

if __name__ == "__main__":
    main()