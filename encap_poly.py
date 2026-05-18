# ===============================================
# ENCAPSULATION AND POLYMORPHISM

class MaximumLimitException(Exception):
    pass

class MaximumTransactionException(Exception):
    pass

class hdfc:
    def __init__(self):
        self.__balance = 100000
        self.__max_limit = 20000
        self.__max_transactions = 3
        self.__transaction_count = 0
        
    def withdraw(self,amount):
        
        if self.__transaction_count >= self.__max_transactions: 
            raise MaximumTransactionException(f"HDFC Bank : Transaction Limit Exceeded ({self.__max_transactions} transactions)")
        
        if amount > self.__max_limit:
            raise MaximumLimitException(f"HDFC Bank : Withdrawal amount exceeds maximum limit of {self.__max_limit} rupees")
        
        if amount > self.__balance:
            raise MaximumLimitException(f"HDFC Bank : Insufficient balance. Available balance : {self.__balance} rupees")
        
        self.__balance -= amount
        self.__transaction_count += 1
        print(f"HDFC Bank : Successfully withdraw {amount} rupees")
        
    def get_balance(self):
        return self.__balance
    
    def get_transaction_count(self):
        return self.__transaction_count

class axis:
    def __init__(self):
        self.__balance = 150000
        self.__max_limit = 30000
        self.__max_transactions = 5
        self.__transaction_count = 0
    
    def withdraw(self,amount):
        if self.__transaction_count >= self.__max_transactions:
            raise MaximumTransactionException(f"AXIS Bank : Transaction Limit Exceeded ({self.__max_transactions} transactions)")
        
        if amount > self.__max_limit:
            raise MaximumLimitException(f"AXIS Bank : Withdrawal amount exceeds maximum limit of {self.__max_limit} rupees")
        
        if amount > self.__balance:
            raise MaximumLimitException(f"HDFC Bank : Insufficient balance. Available balance : {self.__balance} rupees")
        
        self.__balance -= amount
        self.__transaction_count += 1
        print(f"AXIS Bank : Successfully withdraw {amount} rupees")
        print(f"Remaining Balance : {self.__balance} rupees")
        
    def get_balance(self):
        return self.__balance
    
    def get_transaction_count(self):
        return self.__transaction_count

class atm:
    def __init__(self):
        self.hdfc = hdfc()
        self.axis = axis()
        
    def start(self):
        ch = input("Choose the bank (HDFC/AXIS) : ").lower()
        
        if ch not in ["hdfc","axis"]:
            print("Invalid bank choice : ")
            return
        
        bank = self.hdfc if ch == "hdfc" else self.axis
        
        while True:
            try:
                amount = int(input("Enter the amount to withdraw : "))
                
                if amount <= 0:
                    print("Please enter valid\n")
                    continue
                
                bank.withdraw(amount)
                
                next_transaction = input("Do you want to perform another action? (yes/no) : ").lower()
                
                if next_transaction != "yes":
                    print(f"Thank you for using {ch} ATM. Goodbye!")
                    break
                print()
                
            except MaximumLimitException as e:
                print(f"Error : {e}\n")
                break
            except MaximumTransactionException as e:
                print(f"Error : {e}\n")
                break
            except ValueError :
                print("Please enter a valid number\n")
            
if __name__ == "__main__":
    atm = atm()
    atm.start()