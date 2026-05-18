# n = int(input("Enter number of lines : "))

# f = open("L5.txt","w")
# print("Enter data : ")

# for i in range(n):
#     line = input()
#     f.write(line + "\n")

# f.close()

# f = open("L5.txt","r")

# data = f.read()
# f.seek(0)
# read_lines = f.readlines()

# print("\nFile Data : \n")
# print(data)

# lines = data.split("\n")
# if lines[-1] == "":
#     lines.pop()
    
# linec = len(lines)

# wordc = len(data.split())

# char_space = len(data)
# char_nospace = len(data.replace(" ",""))

# print(f"Number of lines : {linec}")
# print(f"Number of words : {wordc}")
# print(f"Number of characters with space : {char_space}")
# print(f"Number of character without space : {char_nospace}")

# f.close() 

# oword = input("Enter word to replace :")
# replacement = input("Enter replacement word : ")

# with open("dummyl5.txt","w+") as f:
#     reversed_lines = read_lines[::-1]
    
#     for rl in reversed_lines:
#         f.write(rl)
    
#     f.seek(0)
#     dummy_read = f.readlines()
#     print("Reversed lines : ")
#     for dr in dummy_read:
#         print(dr)
    
#     f.seek(0)    
#     data = f.read()
#     data = data.replace(oword,replacement)
#     f.seek(0)
#     f.write(data)
    
#     f.seek(0)
#     dummy_read = f.readlines()
#     print("updated lines : ")
#     for dr in dummy_read:
#         print(dr)
   
#=============================================
# TASK 

def write_data(n):
    student = []
    
    info = open("StudentInfo.txt","w")
    marksf = open("StudentMarks.txt","w")
    af = open("Agrade.txt", "w")
    bf = open("Bgrade.txt", "w")
    cf = open("Cgrade.txt", "w")
    
    for i in range(n):
        print(f"====Student {i+1}====")
        roll = int(input("Enter Roll No. : "))
        name = input("Enter Name : ") 
        info.write(f"{roll}-{name}\n")
    
        print(f"Enter marks-->")
        m1 = int(input("Subject 1 : "))
        m2 = int(input("Subject 2 : "))
        m3 = int(input("Subject 3 : "))
           
        marksf.write(f"{roll}-{m1}-{m2}-{m3}\n")
            
        avg = (m1+m2+m3) / 3
        data = f"{roll}-{name}-{str(avg)}\n"
        
        if avg >= 80:
            af.write(data)
        elif avg >= 60:
            bf.write(data)

        elif avg >= 40:
            cf.write(data)    
    
    info.close()
    marksf.close()
    af.close()
    bf.close()
    cf.close()

n = int(input("Enter number of students : "))

write_data(n)

print("\nData Stored Successfully")

   