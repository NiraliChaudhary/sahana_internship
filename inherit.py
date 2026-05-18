import random

class Bankinfo:
    def __init__(self):
        self.fn = input("First name : ")
        self.ln = input("Last name :")
        self.gen = input("Gender : ")
        self.address = input("Address : ")
        
class Bankacc(Bankinfo):
    def __init__(self):
        super().__init__() #parent constructor
        self.anum = random.randint(1000000000000,9999999999999)
        self.amt = 0
        
class Saving(Bankacc):
    min_amt = 10000
    rate = 6
    
    def __init__(self):
        super().__init__()
    
    def validate(self):
        count = 0
        
        while count < 3:
            amount = int(input("Enter amount : "))
            
            if amount >= Saving.min_amt:
                self.amt = amount
                self.calc_interest()
                return
            else:
                print("Minimum amount should be 10000:(")
                count += 1
                
        print("\nChances Over :(")
        print("Program Terminated!!!")
        
    def calc_interest(self):
        self.month = int(input("Enter  months : "))
        self.interest = (self.amt * Saving.rate * self.month) / 100
        
        self.display()
        
    def display(self):
        print("\n===Saving Profile===")
        print(f"Account Holder : {self.fn} {self.ln}")
        print(f"Gender : {self.gen}") 
        print(f"Address : {self.address}") 
        print(f"Account No.  : {self.anum}") 
        print(f"Amount : {self.amt}") 
        print(f"Months : {self.month}") 
        print(f"Rate : {self.rate}") 
        print(f"Interest : {self.interest}") 

class Current(Bankacc):
    min_amt = 5000
    
    def __init__(self):
        super().__init__()
    
    def validate(self):
        count = 0
        
        while count < 3:
            amount = int(input("Enter amount : "))
            
            if amount >= Current.min_amt:
                self.amt = amount
                self.display()
                return
            else:
                print("Minimum amount should be 5000")
        
        print("\nThree chances over :(")
        print("Program terminated !!!")
        
    def display(self):
        print("\n===Current Profile===")
        print(f"Account Holder : {self.fn} {self.ln}")
        print(f"Gender : {self.gen}")
        print(f"Address : {self.address}")
        print(f"Account No. : {self.anum}")
        print(f"Amount : {self.amt}")
       
class Main:
    def __init__(self):
        choice = input("Select Account(Saving/Current)").lower()
        
        if choice == "saving":
            s = Saving()
            s.validate()
        elif choice == "current":
            c = Current()
            c.validate()
        else:
            print("Invalid Choice :(")            
            
m = Main()    