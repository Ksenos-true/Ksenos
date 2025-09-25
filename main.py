while True:
    a = input("username@hostname:~$")
    b = a.split()
    if a == 'exit':
        break
    if len(b) == 0:
        continue
    if b[0] == "ls":
        print(a)
    if b[0] == "cd":
        print(a)    
