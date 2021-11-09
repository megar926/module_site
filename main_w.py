from waitress import serve
import main

serve(main, host = "192.168.1.10", port=8080, threads = 10)