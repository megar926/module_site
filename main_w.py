from waitress import serve
import main
import configparser

config = configparser.ConfigParser()
config.read("/home/alex/Документы/myprojects/module_site/config_linux.ini")
ip = config["SERVER_DATA"]["ip"]
port = config["SERVER_DATA"]["port"]
serve(main.app, host = ip, port=port, threads = 1)