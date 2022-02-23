import threading
import time
from datetime import datetime

def thread_function(name):
    count = 0
    while(count < 5):
        print(f"{datetime.now().strftime('%H:%M:%S')} thread{name} count : {count}")
        time.sleep(2+name)
        count +=1

thread_list = []
for i in range(0,3):
    t = threading.Thread(target=thread_function,args=(i,))
    thread_list.append(t)
    t.start()

for t in thread_list:
    t.join()

print(f"{datetime.now().strftime('%H:%M:%S')} Exiting the main function")