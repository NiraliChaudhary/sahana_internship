#1
# str = input("Enter string (a,b,c): ")
# if(str=="a"):
#     print("you have enter a")
# elif(str=="b"):
#     print("you have enter b")
# elif(str=="c"):
#     print("you have enter c")
# else:
#     print("Invalid character")

#2
# n = int(input("Enter a number : "))
# res=0

# if(n>0):
#     if(n%2==0):
#         res = n*1.5
        
#     else:
#         res = n+10
# else:
#     if(n%2==0):
#         res = n%1.5
#     else:
#         res = n-10
        
# print(res)

#3
# n = int(input("Enter a marks : "))

# if(n>=90 and n<=100):
#     print("A grade")
# elif(n>=80 and n<90):
#     print("B grade")
# elif(n>=60 and n<80):
#     print("C grade")
# elif(n>=40 and n<60):
#     print("D grade")
# elif(n<40):
#     print("Fail")
# else:
#     print("Invalid Marks")

#4
# r = int(input("Enter number of rows : "))

# num=1


# for i in range(1,r+1):
#     for j in range(i):
#         print(1,end=" ")
#     print()

# for i in range(1,r+1):
#     for j in range(i):
#         print(num,end=" ")
#         num += 1
#     print()
    
# for i in range(r,0,-1):
#     for j in range(i):
#         print("*",end=" ")
#     print()

# for i in range(1,r+1):
#     for j in range(r-i):
#         print(" ",end="")
#     for k in range(i):
#         print("*",end=" ")
#     print()
    
# for i in range(1,r+1):
#     for j in range(r-i):
#         print(" ",end="")
#     for k in range(i):
#         print("*",end=" ")
#     print()
# for i in range(r-1,0,-1):
#     for j in range(r-i):
#         print(" ",end="")
#     for k in range(i):
#         print("*",end=" ")
#     print()

#5
n = int(input("Enter a number : "))
fact = 1
i = 1

while i <= n:
    fact = fact * i
    i += 1
print("Factorial = ",fact)