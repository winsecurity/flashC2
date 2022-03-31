import threading 
import time

def testing():
    print("This line gets executed by {}".format(threading.current_thread().name))
    time.sleep(2)

THREADS = []

for i in range(0,5):
    t = threading.Thread(target=testing)
    THREADS.append(t)

    t.start()
    

