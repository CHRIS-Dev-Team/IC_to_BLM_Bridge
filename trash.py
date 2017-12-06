import time


def timer(func):
    def wrapper():
        t_start = time.time()
        func()
        t_end = time.time()
        print t_end - t_start

    return wrapper


def multiwith():
    with open("test1.txt", 'w') as f:
        f.write("Hello Hello Mirrabello \n")


@timer
def singleopen():
    f2 = open('test2.txt', 'w')
    for x in range(0, 100):
        f2.write("Hello Hello Mirrabello \n")
    f2.close()


@timer
def callmultiwith():
    for x in range(0, 100):
        multiwith()


callmultiwith()
singleopen()
