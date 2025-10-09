import os

while True:
    username = os.getenv('USER', 'user')
    hostname = os.uname().nodename if hasattr(os, 'uname') else 'localhost'
    a = input(f"{username}@{hostname}:~$ ")
    b = a.split()
    if a == 'exit':
        break
    if len(b) == 0:
        continue
    if b[0] == "ls" or b[0] == "cd":
        print(a)