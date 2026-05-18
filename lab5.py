# student = {}
# n = int(input("Enter number of students : "))

# for i in range(n):
#     print(f"===Student {i+1}===")
#     roll = int(input("Roll No. : "))
#     name = input("Name : ")
#     marks = int(input("Marks : "))
    
#     student[roll] = {"Name" : name,"Marks" : marks}

# print("\nStudent Dictionary : \n")

# for key,value in student.items():
#     print(f"Roll No : {key}")
#     print("Name : ",value["Name"])
#     print(f"Marks : ", value["Marks"])
#     print()

#============================================
# l = []

# n = int(input("Enter number of elements : "))

# for i in range(n):
#     e = int(input("Enter element : "))
#     l.append(e)

# print(f"List : {l}")

# temp = [l[0]]
# all_seq = []

# for i in range(1,len(l)):
#     if l[i] > l[i-1]:
#         temp.append(l[i])
#     else:
#         all_seq.append(temp)
#         temp = [l[i]]

# all_seq.append(temp)

# print("\nIncreasing sequence : \n")
# for seq in all_seq:
#     print(seq)

# maxi = max(len(seq) for seq in all_seq)

# print("\nLongest Sequences : \n")
# for seq in all_seq:
#     if len(seq) == maxi:
#         print(seq)

#====================================
#TASK 1
# def str_op(str):
#     print(f"String List : {str}")
#     print("Reverse String : ")

#     for s in str:
#         print(s[::-1])
        
# def int_op(num):
#     print(f"\nInteger List : {num}")
#     print(f"Minimum Value : {min(num)}")
#     print(f"Maximum Value : {max(num)}")
    
# a = input("Enter values : ")
# data = a.split(" ")
# str = []
# num = []

# for i in data:
#     i = i.strip()
    
#     if i.isdigit():
#         num.append(int(i))
#     else:
#         str.append(i)
        
# int_op(num)
# str_op(str)


#====================================
#TASK 2

def grading(marks):
    if 90 <= marks <= 100:
        return "A"
    elif 80 <= marks < 90:
        return "B"
    elif 60 <= marks < 80:
        return "C"
    elif 40 <= marks < 60:
        return "D"
    else:
        return "Fail"
    
def input_data(student,n):
    for i in range(1,n+1):
        key = f"s{i}"
        
        print(f"\n===Student {i}===")
        roll = int(input("Roll No. : "))
        name = input("Name : ")
        marks = int(input("Marks : "))
        grade = grading(marks)
        # grade = None
        student[key] = {"roll" : roll,"name" : name,"marks" : marks,"grade" : grade}

def display(student):
    print("\nStudent Dictionary : \n")

    for key,value in student.items():
        print(key, " : ", value)


student = {}
n = int(input("Enter number of students : "))

input_data(student,n)
display(student)

