from waitress import serve
import main
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
ip = config["SERVER_DATA"]["ip"]
port = config["SERVER_DATA"]["port"]
serve(main.app, host = ip, port=port, threads = 10)
