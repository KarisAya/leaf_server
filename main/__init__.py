import subprocess

subprocess.Popen("python -m http.server 12345 --directory ./src/", shell=True)
subprocess.Popen("python ipv4_server.py", shell=True)
subprocess.Popen("python ipv6_server.py", shell=True)
