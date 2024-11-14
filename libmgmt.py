import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error

"""
Steps to set up MySQL database:

1. Install MySQL Server and MySQL Workbench
2. Open MySQL Workbench and connect to your local server
3. Create a new database by running:
   CREATE DATABASE library_management;
   USE library_management;

4. Create required tables:
   
   CREATE TABLE students (
       student_id INT AUTO_INCREMENT PRIMARY KEY,
       name VARCHAR(100) NOT NULL,
       email VARCHAR(100),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   CREATE TABLE books (
       book_id INT AUTO_INCREMENT PRIMARY KEY, 
       title VARCHAR(200) NOT NULL,
       category VARCHAR(50),
       status ENUM('available', 'issued') DEFAULT 'available',
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       INDEX idx_title (title),
       INDEX idx_status (status)
   );

   CREATE TABLE transactions (
       transaction_id INT AUTO_INCREMENT PRIMARY KEY,
       book_id INT,
       student_id INT,
       issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       due_date TIMESTAMP,
       return_date TIMESTAMP NULL,
       penalty_amount DECIMAL(10,2) DEFAULT 0.00,
       FOREIGN KEY (book_id) REFERENCES books(book_id),
       FOREIGN KEY (student_id) REFERENCES students(student_id),
       INDEX idx_book_student (book_id, student_id)
   );

   CREATE TABLE reviews (
       review_id INT AUTO_INCREMENT PRIMARY KEY,
       book_id INT,
       student_id INT,
       review_text TEXT,
       rating INT CHECK (rating BETWEEN 1 AND 5),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (book_id) REFERENCES books(book_id),
       FOREIGN KEY (student_id) REFERENCES students(student_id)
   );

5. Insert sample books:
   INSERT INTO books (title, category) VALUES
   ('Compiler Design', 'Computer Science'),
   ('DBMS Notes', 'Computer Science'),
   ('Data Science', 'Data & AI'),
   ('Machine Learning', 'Data & AI'),
   ('COA', 'General'),
   ('CSS', 'General'),
   ('COI', 'General'),
   ('UHV', 'General'),
   ('Python', 'Programming'),
   ('Operating System', 'Computer Science'),
   ('Automata', 'Programming');
"""

class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Create main container with scrollbar
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Add canvas and scrollbar
        self.canvas = tk.Canvas(self.main_container)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack scrollbar components
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Database connection
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",  # Replace with your MySQL username
                password="dheeraj036", # Replace with your MySQL password
                database="library_management"
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except Error as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {str(e)}")
            root.destroy()
            return

        self.student = None
        self.setup_login_screen()

    def setup_login_screen(self):
        self.login_frame = tk.Frame(self.scrollable_frame, bg="#f0f0f0")
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="Library Management System", 
                font=("Helvetica", 24, "bold"), bg="#f0f0f0").pack(pady=20)

        tk.Label(self.login_frame, text="Enter your name:", 
                font=("Helvetica", 12), bg="#f0f0f0").pack()

        self.name_entry = tk.Entry(self.login_frame, font=("Helvetica", 12))
        self.name_entry.pack(pady=10)

        tk.Label(self.login_frame, text="Email:", 
                font=("Helvetica", 12), bg="#f0f0f0").pack()
        self.email_entry = tk.Entry(self.login_frame, font=("Helvetica", 12))
        self.email_entry.pack(pady=10)

        tk.Button(self.login_frame, text="Login", command=self.login,
                 font=("Helvetica", 12), bg="#4CAF50", fg="white").pack(pady=10)

    def login(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if name and email:
            try:
                # Check if student exists or create new
                self.cursor.execute("SELECT student_id, name FROM students WHERE email = %s", (email,))
                student = self.cursor.fetchone()
                
                if not student:
                    self.cursor.execute(
                        "INSERT INTO students (name, email) VALUES (%s, %s)",
                        (name, email)
                    )
                    self.conn.commit()
                    student_id = self.cursor.lastrowid
                else:
                    student_id = student['student_id']
                
                self.student = {'id': student_id, 'name': name, 'email': email}
                self.login_frame.destroy()
                self.setup_main_screen()
            except Error as e:
                messagebox.showerror("Database Error", str(e))
        else:
            messagebox.showerror("Error", "Name and email cannot be empty")

    def setup_main_screen(self):
        # Main menu buttons
        button_frame = tk.Frame(self.scrollable_frame, bg="#f0f0f0")
        button_frame.pack(pady=20)

        buttons = [
            ("View Available Books", self.show_available_books),
            ("Borrow a Book", self.borrow_book),
            ("Return a Book", self.return_book),
            ("Transaction History", self.show_transaction_history),
            ("Search Books", self.search_books),
            ("Browse Categories", self.browse_categories),
            ("My Borrowed Books", self.show_my_books),
            ("Book Reviews", self.book_reviews),
            ("Exit", self.root.quit)
        ]

        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command,
                     font=("Helvetica", 12), width=20, bg="#2196F3", fg="white").pack(pady=5)

        self.display_frame = tk.Frame(self.scrollable_frame, bg="white")
        self.display_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

    def clear_display(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

    def show_available_books(self):
        self.clear_display()
        tree = ttk.Treeview(self.display_frame, columns=("Book", "Category"), show="headings")
        tree.heading("Book", text="Book Title")
        tree.heading("Category", text="Category")
        tree.pack(pady=10, fill=tk.BOTH, expand=True)

        try:
            self.cursor.execute(
                "SELECT title, category FROM books WHERE status = 'available'"
            )
            books = self.cursor.fetchall()
            for book in books:
                tree.insert("", tk.END, values=(book['title'], book['category']))
        except Error as e:
            messagebox.showerror("Database Error", str(e))

    def borrow_book(self):
        self.clear_display()
        frame = tk.Frame(self.display_frame, bg="white")
        frame.pack(pady=20)

        tk.Label(frame, text="Available Books:", font=("Helvetica", 12, "bold"), bg="white").pack()
        books_list = tk.Listbox(frame, font=("Helvetica", 11), width=40, height=8)
        books_list.pack(pady=10)
        
        try:
            self.cursor.execute(
                "SELECT title FROM books WHERE status = 'available'"
            )
            books = self.cursor.fetchall()
            for book in books:
                books_list.insert(tk.END, book['title'])
        except Error as e:
            messagebox.showerror("Database Error", str(e))

        tk.Label(frame, text="Enter book name:", font=("Helvetica", 12), bg="white").pack()
        book_entry = tk.Entry(frame, font=("Helvetica", 12))
        book_entry.pack(pady=10)

        def submit():
            book_name = book_entry.get().strip()
            try:
                # Start transaction
                self.cursor.execute("START TRANSACTION")
                
                # Get book details
                self.cursor.execute(
                    "SELECT book_id FROM books WHERE title = %s AND status = 'available'",
                    (book_name,)
                )
                book = self.cursor.fetchone()
                
                if book:
                    due_date = datetime.now() + timedelta(days=7)
                    
                    # Update book status
                    self.cursor.execute(
                        "UPDATE books SET status = 'issued' WHERE book_id = %s",
                        (book['book_id'],)
                    )
                    
                    # Create transaction record
                    self.cursor.execute(
                        """INSERT INTO transactions 
                           (book_id, student_id, due_date) 
                           VALUES (%s, %s, %s)""",
                        (book['book_id'], self.student['id'], due_date)
                    )
                    
                    self.conn.commit()
                    messagebox.showinfo("Success", f"Book '{book_name}' borrowed successfully!")
                    
                    # Update display
                    books_list.delete(0, tk.END)
                    self.cursor.execute(
                        "SELECT title FROM books WHERE status = 'available'"
                    )
                    available_books = self.cursor.fetchall()
                    for book in available_books:
                        books_list.insert(tk.END, book['title'])
                else:
                    messagebox.showerror("Error", "Book not available")
                    self.conn.rollback()
                
                book_entry.delete(0, tk.END)
            except Error as e:
                self.conn.rollback()
                messagebox.showerror("Database Error", str(e))

        tk.Button(frame, text="Borrow", command=submit,
                 font=("Helvetica", 12), bg="#4CAF50", fg="white").pack()

    def return_book(self):
        self.clear_display()
        frame = tk.Frame(self.display_frame, bg="white")
        frame.pack(pady=20)

        tk.Label(frame, text="Your Borrowed Books:", font=("Helvetica", 12, "bold"), bg="white").pack()
        books_list = tk.Listbox(frame, font=("Helvetica", 11), width=40, height=8)
        books_list.pack(pady=10)

        try:
            self.cursor.execute("""
                SELECT b.title 
                FROM books b
                JOIN transactions t ON b.book_id = t.book_id
                WHERE t.student_id = %s AND t.return_date IS NULL
                """, (self.student['id'],))
            books = self.cursor.fetchall()
            for book in books:
                books_list.insert(tk.END, book['title'])
        except Error as e:
            messagebox.showerror("Database Error", str(e))

        tk.Label(frame, text="Enter book name:", font=("Helvetica", 12), bg="white").pack()
        book_entry = tk.Entry(frame, font=("Helvetica", 12))
        book_entry.pack(pady=10)

        def submit():
            book_name = book_entry.get().strip()
            try:
                self.cursor.execute("START TRANSACTION")
                
                # Get transaction details
                self.cursor.execute("""
                    SELECT t.transaction_id, t.due_date, b.book_id
                    FROM transactions t
                    JOIN books b ON t.book_id = b.book_id
                    WHERE b.title = %s AND t.student_id = %s AND t.return_date IS NULL
                    """, (book_name, self.student['id']))
                transaction = self.cursor.fetchone()
                
                if transaction:
                    return_date = datetime.now()
                    days_late = max(0, (return_date - transaction['due_date']).days)
                    penalty = days_late * 1.0  # Rs. 1 per day
                    
                    # Update transaction
                    self.cursor.execute("""
                        UPDATE transactions 
                        SET return_date = %s, penalty_amount = %s
                        WHERE transaction_id = %s
                        """, (return_date, penalty, transaction['transaction_id']))
                    
                    # Update book status
                    self.cursor.execute("""
                        UPDATE books 
                        SET status = 'available'
                        WHERE book_id = %s
                        """, (transaction['book_id'],))
                    
                    self.conn.commit()
                    
                    msg = f"Book '{book_name}' returned successfully!"
                    if penalty > 0:
                        msg += f"\nLate return penalty: Rs. {penalty}"
                    messagebox.showinfo("Success", msg)
                    
                    # Update display
                    books_list.delete(0, tk.END)
                    self.cursor.execute("""
                        SELECT b.title 
                        FROM books b
                        JOIN transactions t ON b.book_id = t.book_id
                        WHERE t.student_id = %s AND t.return_date IS NULL
                        """, (self.student['id'],))
                    borrowed_books = self.cursor.fetchall()
                    for book in borrowed_books:
                        books_list.insert(tk.END, book['title'])
                else:
                    messagebox.showerror("Error", "You haven't borrowed this book")
                    self.conn.rollback()
                
                book_entry.delete(0, tk.END)
            except Error as e:
                self.conn.rollback()
                messagebox.showerror("Database Error", str(e))

        tk.Button(frame, text="Return", command=submit,
                 font=("Helvetica", 12), bg="#4CAF50", fg="white").pack()

    def show_transaction_history(self):
        self.clear_display()
        tree = ttk.Treeview(self.display_frame, columns=("Book", "Issue Date", "Due Date", "Return Date", "Penalty"), show="headings")
        tree.heading("Book", text="Book Title")
        tree.heading("Issue Date", text="Issue Date")
        tree.heading("Due Date", text="Due Date")
        tree.heading("Return Date", text="Return Date")
        tree.heading("Penalty", text="Penalty (Rs.)")
        tree.pack(pady=10, fill=tk.BOTH, expand=True)

        try:
            self.cursor.execute("""
                SELECT b.title, t.issued_date, t.due_date, t.return_date, t.penalty_amount
                FROM transactions t
                JOIN books b ON t.book_id = b.book_id
                WHERE t.student_id = %s
                ORDER BY t.issued_date DESC
                """, (self.student['id'],))
            transactions = self.cursor.fetchall()
            for t in transactions:
                return_date = t['return_date'].strftime('%Y-%m-%d') if t['return_date'] else "Not Returned"
                tree.insert("", tk.END, values=(
                    t['title'],
                    t['issued_date'].strftime('%Y-%m-%d'),
                    t['due_date'].strftime('%Y-%m-%d'),
                    return_date,
                    t['penalty_amount']
                ))
        except Error as e:
            messagebox.showerror("Database Error", str(e))

    def search_books(self):
        self.clear_display()
        frame = tk.Frame(self.display_frame, bg="white")
        frame.pack(pady=20)

        tk.Label(frame, text="Search Books", font=("Helvetica", 12, "bold"), bg="white").pack()
        search_entry = tk.Entry(frame, font=("Helvetica", 12))
        search_entry.pack(pady=10)

        tree = ttk.Treeview(frame, columns=("Book", "Category", "Status"), show="headings")
        tree.heading("Book", text="Book Title")
        tree.heading("Category", text="Category")
        tree.heading("Status", text="Status")
        tree.pack(pady=10, fill=tk.BOTH, expand=True)

        def search():
            for item in tree.get_children():
                tree.delete(item)
            search_term = f"%{search_entry.get().strip()}%"
            try:
                self.cursor.execute("""
                    SELECT title, category, status
                    FROM books
                    WHERE title LIKE %s OR category LIKE %s
                    """, (search_term, search_term))
                books = self.cursor.fetchall()
                for book in books:
                    tree.insert("", tk.END, values=(book['title'], book['category'], book['status']))
            except Error as e:
                messagebox.showerror("Database Error", str(e))

        tk.Button(frame, text="Search", command=search,
                 font=("Helvetica", 12), bg="#2196F3", fg="white").pack()

    def browse_categories(self):
        self.clear_display()
        frame = tk.Frame(self.display_frame, bg="white")
        frame.pack(pady=20)

        tk.Label(frame, text="Categories", font=("Helvetica", 12, "bold"), bg="white").pack()
        categories_list = tk.Listbox(frame, font=("Helvetica", 11), width=40, height=5)
        categories_list.pack(pady=10)

        tree = ttk.Treeview(frame, columns=("Book", "Status"), show="headings")
        tree.heading("Book", text="Book Title")
        tree.heading("Status", text="Status")
        tree.pack(pady=10, fill=tk.BOTH, expand=True)

        try:
            self.cursor.execute("SELECT DISTINCT category FROM books ORDER BY category")
            categories = self.cursor.fetchall()
            for category in categories:
                categories_list.insert(tk.END, category['category'])
        except Error as e:
            messagebox.showerror("Database Error", str(e))

        def show_books(event):
            for item in tree.get_children():
                tree.delete(item)
            selection = categories_list.curselection()
            if selection:
                category = categories_list.get(selection[0])
                try:
                    self.cursor.execute("""
                        SELECT title, status
                        FROM books
                        WHERE category = %s
                        """, (category,))
                    books = self.cursor.fetchall()
                    for book in books:
                        tree.insert("", tk.END, values=(book['title'], book['status']))
                except Error as e:
                    messagebox.showerror("Database Error", str(e))

        categories_list.bind('<<ListboxSelect>>', show_books)

    def show_my_books(self):
        self.clear_display()
        tree = ttk.Treeview(self.display_frame, columns=("Book", "Issue Date", "Due Date", "Days Left"), show="headings")
        tree.heading("Book", text="Book Title")
        tree.heading("Issue Date", text="Issue Date")
        tree.heading("Due Date", text="Due Date")
        tree.heading("Days Left", text="Days Left")
        tree.pack(pady=10, fill=tk.BOTH, expand=True)

        try:
            self.cursor.execute("""
                SELECT b.title, t.issued_date, t.due_date
                FROM transactions t
                JOIN books b ON t.book_id = b.book_id
                WHERE t.student_id = %s AND t.return_date IS NULL
                ORDER BY t.due_date
                """, (self.student['id'],))
            books = self.cursor.fetchall()
            for book in books:
                days_left = (book['due_date'] - datetime.now()).days
                tree.insert("", tk.END, values=(
                    book['title'],
                    book['issued_date'].strftime('%Y-%m-%d'),
                    book['due_date'].strftime('%Y-%m-%d'),
                    f"{days_left} days"
                ))
        except Error as e:
            messagebox.showerror("Database Error", str(e))

    def book_reviews(self):
        self.clear_display()
        frame = tk.Frame(self.display_frame, bg="white")
        frame.pack(pady=20)

        # Book selection
        tk.Label(frame, text="Select Book:", font=("Helvetica", 12, "bold"), bg="white").pack()
        books_list = ttk.Combobox(frame, font=("Helvetica", 11), width=40)
        books_list.pack(pady=10)

        # Reviews display
        reviews_frame = tk.Frame(frame, bg="white")
        reviews_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        try:
            self.cursor.execute("SELECT title FROM books ORDER BY title")
            books = self.cursor.fetchall()
            books_list['values'] = [book['title'] for book in books]
        except Error as e:
            messagebox.showerror("Database Error", str(e))

        def show_reviews(event=None):
            for widget in reviews_frame.winfo_children():
                widget.destroy()

            book_title = books_list.get()
            if not book_title:
                return

            try:
                self.cursor.execute("""
                    SELECT r.review_text, r.rating, s.name, r.created_at
                    FROM reviews r
                    JOIN books b ON r.book_id = b.book_id
                    JOIN students s ON r.student_id = s.student_id
                    WHERE b.title = %s
                    ORDER BY r.created_at DESC
                    """, (book_title,))
                reviews = self.cursor.fetchall()

                if reviews:
                    for review in reviews:
                        review_frame = tk.Frame(reviews_frame, bg="white", relief=tk.RIDGE, bd=1)
                        review_frame.pack(pady=5, padx=5, fill=tk.X)
                        
                        tk.Label(review_frame, text=f"Rating: {'★' * review['rating']}", 
                                bg="white", font=("Helvetica", 10)).pack(anchor=tk.W)
                        tk.Label(review_frame, text=f"By {review['name']} on {review['created_at'].strftime('%Y-%m-%d')}", 
                                bg="white", font=("Helvetica", 10, "italic")).pack(anchor=tk.W)
                        tk.Label(review_frame, text=review['review_text'], 
                                bg="white", font=("Helvetica", 11), wraplength=400).pack(anchor=tk.W, pady=5)
                else:
                    tk.Label(reviews_frame, text="No reviews yet", 
                            bg="white", font=("Helvetica", 11)).pack()

            except Error as e:
                messagebox.showerror("Database Error", str(e))

        books_list.bind('<<ComboboxSelected>>', show_reviews)

        # Add review section
        add_review_frame = tk.Frame(frame, bg="white")
        add_review_frame.pack(pady=20, fill=tk.X)

        tk.Label(add_review_frame, text="Add Your Review", 
                font=("Helvetica", 12, "bold"), bg="white").pack()
        
        rating_var = tk.StringVar(value="5")
        rating_frame = tk.Frame(add_review_frame, bg="white")
        rating_frame.pack(pady=5)
        
        for i in range(1, 6):
            tk.Radiobutton(rating_frame, text=str(i), variable=rating_var, 
                          value=str(i), bg="white").pack(side=tk.LEFT)

        review_text = tk.Text(add_review_frame, height=4, width=40, font=("Helvetica", 11))
        review_text.pack(pady=5)

        def submit_review():
            book_title = books_list.get()
            if not book_title:
                messagebox.showerror("Error", "Please select a book")
                return

            review = review_text.get("1.0", tk.END).strip()
            if not review:
                messagebox.showerror("Error", "Please write a review")
                return

            try:
                # Get book_id
                self.cursor.execute("SELECT book_id FROM books WHERE title = %s", (book_title,))
                book = self.cursor.fetchone()
                
                if book:
                    # Add review
                    self.cursor.execute("""
                        INSERT INTO reviews (book_id, student_id, review_text, rating)
                        VALUES (%s, %s, %s, %s)
                        """, (book['book_id'], self.student['id'], review, rating_var.get()))
                    self.conn.commit()
                    
                    messagebox.showinfo("Success", "Review submitted successfully!")
                    review_text.delete("1.0", tk.END)
                    show_reviews()
                else:
                    messagebox.showerror("Error", "Book not found")
            except Error as e:
                messagebox.showerror("Database Error", str(e))

        tk.Button(add_review_frame, text="Submit Review", command=submit_review,
                 font=("Helvetica", 12), bg="#4CAF50", fg="white").pack(pady=5)

    def __del__(self):
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryGUI(root)
    root.mainloop()
