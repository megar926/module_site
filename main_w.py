from waitress import serve
import main

serve(main.app, host = "192.168.1.99", port=8080, threads = 10)
