#!/usr/bin/env python3

my_integer = 10
print('Hello World!',my_integer)

string = "My name is Raghavendra"
str_len = len(string)
print("String length is ",str_len)

#multiplication
string1 = "One "
string2 = string1 * 3
print(string2)

#floating point formating

number=1.5876

print("The result is {:2.3f}".format(number))
print(f"The result is {number:2.3f}")


##Lists and their methods

my_list=["one","two","three"]
fruits=["apple","banana","pineapple"]
numbers=["2","1","5","4","3","fame","ca3t","ca2t","zebra","cat","2.2"]
my_list.append("four")             ## Adds "four" to end of the list
my_list.clear()                    ## Removes all the elements of the list
my_list1 = my_list.copy()          ## Returns the copy of the list, if you make changes to the second list, it wont effect the first list
count = my_list.count("three")     ## Returns number of times three is present in the list
my_list.extend(fruits)             ## Appends the elements of fruits to my_list
index=fruits.index("banana")       ## Returns of the first index whose element matches three, its a error if the index does not matches with nothing
fruits.insert(1,"strawberry")      ## Adds strawberry at index 1, if there is no index 1 then it adds to the last element in the list
fruits.pop(1)                      ## Pops the element 1 from the list, if the element does not exist, its a error
fruits.remove("banana")            ## Removes the first element which matches banana
fruits.reverse()                   ## Reverses the elements in the list
numbers.sort()                     ## Sorts the list, first numerically, then alphabetically

last_element=numbers[-1]           ## Get the last element of numbers
list_slicing=numbers[-1:-3:-1]     ## Get the last three element of numbers

#print(f"the last element is {list_slicing}")

#print(f"the sorted nubmer is {numbers}")

#my_list=["one","two","three","three"]
#print(f'The count is {my_list.index("three")}')

#my_list.insert(1,"two1")
#print(f"The string is {my_list}")

#my_list.append("four")
#print(f"The string is {my_list}")

#non_list=[]
#print(non_list)


##Dictonaries and their methods

fruits={'apple':2.999,'banana':1.587,'strawberry':5.999}
cars={"bmw":3,"benz":5,"audi":10}
x = ['key1', 'key2', 'key3']
y = ['1','2']
fruits.clear()                         ## Clear the elements of the dictonary
fruits_copy = fruits.copy()            ## Returns of the copy of fruits
thisdict = dict.fromkeys(x, y)         ## Returns a dictonary with keys set by x and all the keys set to y
car_value = cars.get("benz")           ## Returns the value of specified key
car_items = cars.items()               ## Returns a list which is tuple of key and value, does not support indexing, it can be used in for loop
car_keys = cars.keys()                 ## Retruns a list containing all the keys, can be used in for loop
cars.pop("benz")                       ## Removes key benz from the dictonary along with the value
cars.popitem()                         ## Removes the last inserted key value pair
x1 = cars.setdefault("maruthi","20")   ## Returns the value of maruthi if exists, else it returns 20 and adds the key maruthi to cars with value 20
cars.update({"lamborgini":40})         ## Adds the given key/value pair to the dictonary
x1 = cars.values()                     ## Returns a list of values in the dictonary car


print(cars)

fruits.update({'pineapple':6.678})
fruit_name='pineapple'
print(f"The price of {fruit_name} is {fruits[fruit_name]:1.2f}")



##FILE I/O Methods

f = open("file.txt","r")      # r = read mode,
                              # w = write mode
                              # r+ = read/write mode
                              # w+ = write/read mode
                              # a = append mode
f1 = open("file1.txt","w")
f2 = open("file.txt","r")
f.close()                         # Closes the file handle
file_num = f1.fileno()            # Returns the file number from OS perspective
file_contents = f2.read()         # Returns the entire contents of the file in one line
file_readable = f2.readable()     # Returns if the file is readable
file_line = f2.readline()         # Returns on line of the file
file_all_lines = f2.readlines()   # Returns all the lines of the file
f2.seek(1)                        # moves the cursor of the f2 to the 2 character in the file, 0 returns to the first character
file_seekable = f2.seekable()     # Returns of the file is seekable or not
current_position = f2.tell()      # Returns the current position of cursor in the file
f1.truncate(2)                    # Truncates the file to two bytes
f1.write("Write this line\n")     # writes a specified string to the file
f1.writelines(x)                  # writes a list to the file, note that it wont add the \n

f2.seek(2)
print(f2.tell())


f1.close()
f2.close()


## IF ELIF and ELSE statements

num = 10

if (num <= 2):
	print("Num is less than or equal 2")
	print("Num is less than or equal 2")
elif ((num > 2) and (num <=5)):
	print("Num is greater than 2")
	print("Num is less than or equal 5")
else:
	print("Num is greater than 5")
	print("Num is greater than 5")

if(cars.get("benz") == None):
	print("None")
else:
	print("yes")


## For loop examples

for i in range(0,5):
	print(f"The number is {i}")

temp_list = list(range(1,5))

for i in range(0,len(temp_list)):
	print(f"The list value is {temp_list[i]}")

for i in temp_list:
	print(i)

## Tuple can be unpacked in a loop
temp_dict = {"first":1,"second":2,"third":3}

for key,value in temp_dict.items():
	print(f"Key : {key} value : {value}")



## While loop
x=0
while(x<5):
	print(x)
	x+=1

## break keyword
x=0
while(x<5):
	if(x==2):
		break
	print(x)
	x+=1

## Continue keyword
x=0
while(x<5):
	if(x==2):
		x+=1
		continue
	print(x)
	x+=1

## pass keyword, simply does nothing. Used as placeholder
x="Sammy"
for letter in x:
	pass

## Enumerate is a generator which generate a list of tuples containing the index of the list

word = "My name is Adiga"
for index,letter in enumerate(word):
	print(f"The letter at index {index} is {letter}")

## Zip function zips the list togather

list1 = list(range(0,5))
list2 = ['a','b','c']
list3 = range(100,400,100)

for item in zip(list1,list2,list3):
	print(item)

## Random library

## shuffle : shuffles a list
from random import shuffle

list1 = list(range(0,5))
shuffle(list1)
print(list1)

## randint, give a random integer in a given range
from random import randint

randnum = randint(0,100)
print(f"The random number is {randnum}")

## in operator : using this you can find if something is in the list or not
list1 = list(range(0,50))
if (10 in list1):
	print("10 is in the list")
else:
	print("10 is not in the list")

dict1 = {'key1':1,'key2':2}
if ('key1' in dict1.keys()):
	print("key1 is in the dictonary")
else:
	print("key1 is not in the dictonary")


## list comprehension

even_number = [num**2 for num in range(0,10) if (num%2==0)]
print(even_number)

## Function *args and **kwargs
## *args creates a tuple of positional arguments
## **kwargs creates a dictonary of keyword arguments
## args and kwargs should be in order they have been declared
def func1(*args,**kwargs):
	print(args)
	print(kwargs)

func1(1,2,3,car1='audi',car2='benz')


## Lambda expression
## def func (x)
## return (x**2) can be written as
## lambda x:x**2
my_nums = list(range(0,10))
print(list(map(lambda x:x**2,my_nums)))

## MAP function = Performs a specified function on all the elements of a list.
## This can be used to reduce for loop, for example string manipulation on the lines of a file

def mul_num(a,b):
	return(a*b)


num1 = [1,2,3,4,5]
num2 = [1,2,3,4,5,6]

mapped_num=list(map(mul_num,num1,num2))
print(mapped_num)


## Filter Function = Use a function to decide whether to filter out certain elements of the list and
## Provides a reduced list

def num_gt_5(a):
	return(a>5)

num = [1,10,5,2,3,30]
print(num)
filtered_num = list(filter(num_gt_5,num))
print(filtered_num)


## reduce : This function used to reduce the list into just one element to say for example find the largest
## element of a list

def gt(a,b):
	if(a>b):
		return(a)
	else:
		return(b)

num = [1,4,3,5,2,7,1,4,5]
from functools import reduce
largest_num = reduce(gt,num)
print(largest_num)

a=['1']*10
print(a)

## Classes
class Circle():
	## Object parameters which cannot be changed like local params
	pi=3.14

	## First method the object called when the intstance is created
	def __init__(self,radius=1):
		## Object params which is defined when the object is created
		self.radius = radius
		self.area = self.pi * radius * radius

    ## Object methods. Always refer to self keyword to either bind to this class or
    ## using the parameters of this objects
	def calc_circumference(self):
		return(2*self.pi*self.radius)

	## Calling functions inside the current class
	def get_circumference(self):
		print(self.calc_circumference())


mycircle = Circle()

print(mycircle.radius)
print(mycircle.calc_circumference())
mycircle.get_circumference()

## Inheritence and Polymorphism

class Animal():
	## This is a base class which we dont intend to implement
	def __init__(self,name="None"):
		self.name = name

	def speak(self,num=1):
		raise NotImplementedError("This method needs to be implmented by sub class")

## Class inheriting the base class
class Dog(Animal):
	## Override the init method for Dog class
	def __init__(self,name="None",spots="False"):
		## Call the init method of the Animal Class
		Animal.__init__(self,name)
		self.spots = spots

	def speak(self,num=1):
		return(self.name+" says Woof! "+str(num)+" times" )

class Cat(Animal):

	def speak(self,num=1):
		return(self.name+" says Meow! "+str(num)+" times" )

pets = [Dog("Sammy"),Cat("Felix")]

## Polymorphism, means that difference sub class can override the methods of the base class
## Here the list Pets need not be aware of the class, because both have the same method, but they behave differently
for i,pet in enumerate(pets):
	print(pet.speak(i))

## Special methods

class Book():
	def __init__(self,name="None",author="None",pages=0):
		self.name = name
		self.author = author
		self.pages = pages

	## This is the special function which is called when you type print an object
	def __str__(self):
		return(f"{self.name} by {self.author} rocks")

	## This is the special function which is called when you type len(object)
	def __len__(self):
		return self.pages

	def __del__(self):
		print("Book object has been deleted")

mybook = Book("Python","Raghu",100)
print(mybook)
print(len(mybook))


## Examples of packages and modules

from classpackage.carclasses import car

car1 = car()

print(car1)

car1.paint("yellow")
print(car1)


## Examples of try and exception
## Below, if any of the line catches an exception it goes to except block
while True:
	try:
		print("Testing try and except")
		x=int(input("Enter an integer"))
		print("Thank you")
		break
	except:
		print("Sorry you need to enter an integer")


####### DECORATORS #######

def new_decorator(origin_func):

	def decorator():
		print("Some extra functionality before")
		origin_func()
		print("Some extra functionality after")

	return(decorator)

@new_decorator
def origin_func():
	print("This is the origin_func")

## Since there is a @new_decorator above, it converts this line into
## new_decorator(origin_func)()
origin_func()

##### Generator ########
# Generator will create an entire list, instead it will
# Remember the previous value and work on it

def gen_fib(n):
	a = 1
	b = 1
	for x in range(n):
		yield a
		a,b = b,a+b

for i in gen_fib(5):
	print(i)


######## COUNTER
## This object creates a keyed list
## The key will the the unique values of the list
## Value will be count of those unique values in that list

from collections import Counter

s = "How many word are present in this sentence. Word is set of letters. There are 26 letters in English. English is an international language"
words = s.split()
print(Counter(words).most_common(2))



#### Argument parser
### command line arguments, gives the first command line argument
temp = sys.argv[1]


import argparse

#parser = argparse.ArgumentParser()
#parser.add_argument("file1", help="Absolute path of the file1",type=str)
#parser.add_argument("num", help="A integer number",type=int)
# In this case we only need to give -v with no arguments, then it will be either true or false
#parser.add_argument("-v", "--verbose", help="increase output verbosity",
#                    action="store_true")
#parser.add_argument("-n", "--num", type=int, choices=[0, 1, 2],
#                    help="increase output verbosity")
#args = parser.parse_args()

#print(f"{args.file1} {args.verbose}")


### Colored output
import sys

RED   = "\033[1;31m"
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
ORANGE = "\033[38;5:202m"
REVERSE = "\033[;7m"

sys.stdout.write(RED)
print(f"I am Good")


##Regular Expressions

import re
string = "I am a good good boy"
string2 = re.sub(r"(.*?)(good)(.*boy)",r"\1",string)
match = re.search(r'word:\w\w\w', string)
if match:
  print("yes")
print(string2)


## Datetime
import datetime
import time

time1 = datetime.datetime.now()
time.sleep(5)
time2 = datetime.datetime.now() - time1

print(f"{time2}")


## String Formatting

string1 = "Hello"
string2 = "World!!!"

print(f"{string1:^10}{string2:^10}")

string1 = "This      is       Hello      from     World"
list1 = string1.split(r"\s+")
list2 = re.split(r"\s+",string1)
print(list2)

###Stripping trailing \n
string1 = "This is hello \n"
print(string1)
print(string1.rstrip("\n"))



import logging
logging.basicConfig(filename='example.log',filemode="w",level=logging.DEBUG)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')

#### Running shell commands
import os

##Saves the output of the command to temp, waits for the command to finish
temp=os.popen(f"ls -lrt").readlines()

##Saves the status of the command into temp, waits for the command to finish
temp=os.system(f"ls -lrt")

import subprocess
##This function outputs the command output to a file
subprocess.call(f"ftrun mbist -batch -include cfg_mbist_signoff -include {cfg} -include cfg_disable_prove_cache -include cfg_mbist_background",stdout=out_file,shell=True)


####multi processing
import multiprocessing

def run_job(cmdline):
  os.system(f'bsub -I -o .temp -q PD -W 80:0 -R "select[rhe7 && os64]" {cmdline}')
##gives a process id for running a function run_job and args for them
pid=multiprocessing.Process(target=run_job,args=(cmdline,))
##starts the process
pid.start()

##Checks if a process is active yet
pid.is_alive()
