import glob
from subprocess import Popen

config_files_count = len(glob.glob('configuration_files/*'))

all_servers = []

for i in range(config_files_count):
    all_servers.append(Popen(['python3.7', 'server.py', str(i+1)]))

for i in all_servers:
    i.wait()

