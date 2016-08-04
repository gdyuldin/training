import random
s = "/tmp/{0}".format(random.random())
while True:
    file = open(s, 'w+')
