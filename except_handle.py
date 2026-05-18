#SINGLE TRY WITH MULTI EXCEPT


# class Lib1:
#     def issue_book(self):
#         try:
#             books = ["Python","Java","C","C++"]
#             i = int(input("Enter book id : "))
#             print("Book : ",books[i])
            
#         except ValueError:
#             print("Enter integer id only...")
            
#         except IndexError :
#             print("Book not found...")
            
# b1 = Lib1()
# b1.issue_book()

#=======================================
#MULTI TRY WITH SINGLE EXCEPT

# class Lib2:
#     def details(self):
            
        # try:
        #     name  = input("\nEnter student name :")
        #     print("Student : ",name)
        
        # except:
        #     print("Student name error...")
        
        # try:
        #     days = int(input("Enter late days : "))
        #     fine = 100 / days
        #     print("Fine : ",fine)
            
        # except:
        #     print("Fine Error occured!")
          #------------------  
#         try:
            
#             try:
#                 name = input("Enter book name : ")
#                 print("Book ",name)
                
#             finally:
#                 pass
            
#             try:
#                 days = int(input("Enter days : "))
#                 fine = 100 / days
#                 print("Fine : ",fine)
                
#             finally:
#                 pass
            
#         except Exception as e:
#             print("Error : ",e)
            
# b1 = Lib2()
# b1.details()

#=======================================
#NESTED TRY WITH NESTED EXCEPT       

# class Lib3:
#     def fine(self):
#         try:
#             member = input("Enter member name : ")
            
#             if member.isdigit():
#                 raise Exception("Invalid name !")
            
#             try:
#                 days = int(input("Enter days : "))
#                 fine = 100 / days
#                 print("Fine : ",fine)
#             except ZeroDivisionError:
#                 print("Days cannot be zero!")
        
#         except Exception as e:
#             print("Member error! ",e)
            
# b = Lib3()
# b.fine()


#=======================================
#NESTED TRY WITH NESTED FINALLY

# class Lib4:
#     def fine(self):
#         try:
#             print("Library management started ...")
            
#             try:
#                 days = int(input("Enter days : "))
#                 fine = 100 / days
#                 print(f"Fine : {fine}")
#             except ZeroDivisionError:
#                 print("Days cannpt be zero")
#             finally:
#                 print("Inner finally===")
                
#         finally:
#             print("Library management ended ...")

# b = Lib4()
# b.fine()          
                  
#=======================================
#MULTI TRY WITH MULTI FINALLY AND EXCEPT

class Lib:

    def operations(self):

        try:

            books = ["Python", "Java"]

            i = int(input("Enter Book Index : "))

            print("Book :", books[i])

        except ValueError:

            print("Invalid Input")

        except IndexError:

            print("Book Not Found")

        finally:

            print("Book Section Completed")


        try:

            days = int(input("Enter Days : "))

            fine = 100 / days

            print("Fine :", fine)

        except ValueError:

            print("Invalid Days")

        except ZeroDivisionError:

            print("Days Cannot Be Zero")

        finally:

            print("Fine Section Completed")


b = Lib()

b.operations()