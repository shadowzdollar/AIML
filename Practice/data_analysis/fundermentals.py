#data types
#integers
age = 25

#float

num = 49.9

#string

str = "Hello world"

#Booleans

is_student = True

#operators

#Arithmetic Operators**: `+`, `-`, `*`, `/`, `%`
#Assignment Operators**: `=`, `+=`, `-=`, `*=`, `/=`
#Comparison Operators**: `==`, `!=`, `<`, `>`, `<=`, `>=`

#examples of arthimetica operators

a = 40
b = 50

# Addition
sum_result = a + b

# Subtraction
diff_result = a - b

# Multiplication
mul_result = a * b

# Division
div_result = a / b

# Modulus (remainder)
mod_result = a % b



#control flows

if a > b:
    print("A is greater than B")
elif a == b:
    print("A is equal to B")
else:
    print("B is greater than A")

#for loops

numbers = [1, 2, 3, 4, 5]

for num in numbers:
    print(num)

#while loop

count = 0
while count < 5:
    print(count)
    count +=1

#functions
def greet(name):
    return f"Hello, {name}!"
print(greet("Alice"))


## list
fruits = ['Apple', 'Banana', 'cherry']

#adding an element to the end

fruits.append("date")

#removing fruit 

del fruits[1]

#Get length of the list

length = len(fruits)

#Dictionaries

person = {
    "name": "Alice",
    "age": 30,
    "city": "New york"
}

#access value by it's key

print(person["name"])

# Add or update a key-value pair
person["occupation"] = "Engineer"

### 8. Tuples
#Tuples are similar to lists but are immutable (cannot be changed once created). They are often used for fixed data

coordinates = (10, 20)

# Access elements by index
x, y = coordinates

### 9. Sets
#Sets are unordered collections of unique elements. They do not allow duplicate values.


unique_numbers = {1, 2, 3, 4, 5}

# Add an element
unique_numbers.add(6)

# Remove an element
unique_numbers.remove(3)


### 10. File Handling
#Python can read from and write to files using built-in functions like `open()`, `read()`, and `write()`.

#### Writing to a file

with open("example.txt", "w") as file:
    file.write("Hello, World!")


#### Reading from a file

with open("example.txt", "r") as file:
    content = file.read()
    print(content)

