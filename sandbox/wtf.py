import os

os.chdir('Customer Export')

df = []

with open('11-23.csv', 'r') as f:
    lis = []
    li = ''
    for line in f:
        if not line.startswith('\n'):
            li += line.strip()
        else:
            lis.append(li)
            df.append(lis)
            lis = []
            li = ''

            
for line in df:
    print(line)