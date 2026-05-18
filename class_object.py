#  CLASS AND OBJECT

class Studentinfo:
    def __init__(self):
        self.roll = int(input("Enter Roll no : "))
        self.name = input("Enter name : ")
        
class Studentmarks:
    def __init__(self):
        self.m1 = int(input("Enter Subject-1 marks : "))
        self.m2 = int(input("Enter Subject-2 marks : "))
        self.m3 = int(input("Enter Subject-3 marks : "))
        
class Main:
    def __init__(self):
        n = int(input("Enter number of students : "))
        
        for i in range(n):
            print(f"\n=======Student {i+1}=======")
            
            s = Studentinfo()
            m = Studentmarks()
            
            g,a = self.calc_grade(s,m)
            print("\n==Student Details==\n")
            print("Roll No :", s.roll)
            print("Name :", s.name)
            print("Average :", a)
            print("Grade :", g)
            
    def calc_grade(self,s,m):
        avg = (m.m1 + m.m2 + m.m3)/3
            
        if avg > 100:
            grade = "Invalid Marks"
        elif 90 <= avg <= 100:
            grade = "A"
        elif 80 <= avg < 90:
            grade = "B"
        elif 60 <= avg < 80:
            grade = "C"
        elif 40 <= avg < 60:
            grade = "D"
        else:
            grade = "Fail"
        
        return grade,avg
            
    

obj = Main()

        
     

