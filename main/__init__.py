import subprocess

port = 8080
env = "dev"
subprocess.Popen(f"python ipv4_server.py {port} {env}", shell=True)
subprocess.Popen(f"python ipv6_server.py {port} {env}", shell=True)
