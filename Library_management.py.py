from datetime import datetime, timedelta

class Library:
    def __init__(self, listOfBooks):
        self.books = {book: {'status': 'available', 'borrower': None, 'due_date': None, 'history': []} for book in listOfBooks}
        self.penalty_rate = 1 

    def display_AvailableBooks(self):
        print("Books Present in this library are: ")
        for book, details in self.books.items():
            if details['status'] == 'available':
                print(f"-> {book}")

    def borrowBook(self, bookName, student_name):
        if bookName in self.books and self.books[bookName]['status'] == 'available':
            due_date = datetime.now() + timedelta(days=7)
            transaction = {'borrower': student_name, 'issued_date': datetime.now(), 'return_date': None}
            self.books[bookName]['status'] = 'issued'
            self.books[bookName]['borrower'] = student_name
            self.books[bookName]['due_date'] = due_date
            self.books[bookName]['history'].append(transaction)
            print(f"You have been issued {bookName}. Please keep it safe and return it by {due_date.strftime('%Y-%m-%d')}")
            return True
        else:
            print("Sorry, This book is either not available or already issued by someone. Please wait until it is available.")
            return False

    def returnBook(self, bookName):
        if bookName in self.books and self.books[bookName]['status'] == 'issued':
            due_date = self.books[bookName]['due_date']
            returned_date = datetime.now()
            days_late = max(0, (returned_date - due_date).days)
            penalty_charge = days_late * self.penalty_rate
            self.books[bookName]['status'] = 'available'
            self.books[bookName]['borrower'] = None
            self.books[bookName]['due_date'] = None
            self.books[bookName]['history'][-1]['return_date'] = returned_date
            print(f"Thanks for returning this book. Hope you enjoyed reading it!")
            if days_late > 0:
                print(f"You are {days_late} days late. Penalty charge: Rs. {penalty_charge}")
        else:
            print("Invalid book or it is not issued. Please check the book name.")

    def displayTransactionHistory(self, bookName):
        if bookName in self.books:
            print(f"Transaction history for {bookName}:")
            for transaction in self.books[bookName]['history']:
                print(f"Borrower: {transaction['borrower']}, Issued Date: {transaction['issued_date'].strftime('%Y-%m-%d')}, Return Date: {transaction['return_date']}")
        else:
            print("Invalid book name.")

class Student:
    def __init__(self, name):
        self.name = name

    def requestBook(self):
        book = input("Enter the name of the book which you want to borrow: ")
        return book

    def returnBook(self):
        book = input("Enter the name of the book which you want to return: ")
        return book

if __name__ == "__main__":
    centralLibrary = Library(["Compiler Design", "DBMS Notes", "Data Science", "Machine Learning","COA","CSS","COI","UHV","Python","Operating System","Automata"])
    student_name = input("Enter your name: ")
    student = Student(student_name)

    while True:
        WelcomeMsg = ''' \n
        =====Welcome to the library====
        Please Choose an Option:
        1. List of all Books
        2. Request a Book
        3. Return A Book
        4. Transaction History
        5. Exit the Library.
        '''
        print(WelcomeMsg)
        choice = int(input("Enter your choice: "))

        if choice == 1:
            centralLibrary.display_AvailableBooks()
        elif choice == 2:
            book_to_borrow = student.requestBook()
            centralLibrary.borrowBook(book_to_borrow, student.name)
        elif choice == 3:
            book_to_return = student.returnBook()
            centralLibrary.returnBook(book_to_return)
        elif choice == 4:
            book_to_check_history = input("Enter the name of the book to check transaction history: ")
            centralLibrary.displayTransactionHistory(book_to_check_history)
        elif choice == 5:
            print("Thanks for visiting our Library.")
            exit()
        else:
            print("Invalid Choice!!")
