str = "this is string example"

#1
srev = str[::-1]
print(f"Reversed string : {srev}")

#2
words = str.split()
wrev = words[::-1]
result = " ".join(wrev)
print(f"Word wise reversed string : {result}")

#3
res =" "
for i in range(0,len(str)-1,2):
    res += str[i+1] + str[i]
    
if len(str) % 2 != 0:
    res += str[-1]

print(f"Interchanged character string : {res}")

#replacing only first 2 character
l = list(str)
i=0
j=3
l[i],l[j] = l[j],l[i]
result = " ".join(l)
print(result)

#4
w = str.split()
result = "*".join(w)
print(f"Splitting and joing : {result}")

#5
rep = str.replace("is","was")
print(f"Replaced string : {rep}")

#-->
sub = str[:7:]
sp = sub.split()
word = []

for i in sp:
    if i == "is":
        word.append("was")
    else:
        word.append(i)
result = " ".join(word)
print("Substring replacing only is to was : ",result)