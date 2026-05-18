# def fn(**std):
#     print(std)
#     print(type(std))
#     if std is not None:
#         for key,value in std.items():
#             print("%s = %s" %(key,value))
# fn(a='abc',b='def',n='nirali',age=15)

#=task3===================================
def word_rev(s):
    words = s.split()
    rev = words[::-1]
    result = " ".join(rev)
    print(f"Word wise reverse : {result}")
    
def interchange(s):
    result = ""
        
        
    for i in range(0,len(s)-1,2):
        result += s[i+1] + s[i]
        
    if len(s) % 2 != 0:
        result += s[-1]
        
    print(f"Two characters interchange : {result}")
        
s = input("Enter a string : ")
word_rev(s)
interchange(s)


#=task2===================================
def calculate(*lists):
    
    if len(lists) == 1:
        print("List = ",lists[0])
        
    elif len(lists) == 2:
        concat = lists[0] + lists[1]
        print("Concatenated List = ",concat)
        
        print("Maximun element : ",max(concat))
        print("Minimun element : ",min(concat))
        
    elif len(lists) == 3:
        concat = lists[0] + lists[1] + lists[2]
        
        print("Concatenated list = ",concat)
        
        total = sum(concat)
        print("Addition of all elements = ",total)
        
    else:
        concat = []
        
        for l in lists:
            concat.extend(l)
        print("Concatenated List : ",concat)
        
        square_l = list(map(lambda x: x*x,concat))
        
        print("Square List : ",square_l)
        
        odd_l = list(filter(lambda x:x%2 != 0,concat))
        
        print("Odd numbers : ",odd_l)    
        

n = input("Enter number of list : ")

all_list = []

for i in range(n):
    size = int(input(f"Enter number of elements for list {i+1} : "))
    
    temp = []
    
    for j in range(size):
        e = int(input("Enter element : "))
        temp.append(e)
        
    all_list.append(temp)

#if you want to use only single * in complete code ..then call func everytime after checking variable length
calculate(*all_list) 
        


    
