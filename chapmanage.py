import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkinter import PhotoImage
import hashlib
import smtplib
from email.mime.text import MIMEText
import sys
import os
from PIL import Image, ImageTk


# Function to create the tables with fee-related columns
def create_tables(cursor, connection):
    # Create StudentsCoursesRegistraions table with PhoneNumber
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS StudentsCoursesRegistraions (
        StudentID INTEGER PRIMARY KEY,
        StudentName TEXT,
        PhoneNumber TEXT)''')

    # Create Fees table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Fees (
        StudentID INTEGER PRIMARY KEY,
        TotalFee REAL,
        FeePaid REAL,
        FeeDue REAL,
        FOREIGN KEY (StudentID) REFERENCES StudentsCoursesRegistraions(StudentID))''')

    # Add the PhoneNumber column if it doesn't already exist
    cursor.execute("PRAGMA table_info(StudentsCoursesRegistraions);")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "PhoneNumber" not in columns:
        cursor.execute("ALTER TABLE StudentsCoursesRegistraions ADD COLUMN PhoneNumber TEXT;")
    
    connection.commit()
# Function to create tables with user and student information
def create_tables(cursor, connection):
    # Create Users table for login
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        Username TEXT PRIMARY KEY,
        Password TEXT
    )''')

    # Create StudentsCoursesRegistraions table with PhoneNumber
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS StudentsCoursesRegistraions (
        StudentID INTEGER PRIMARY KEY,
        StudentName TEXT,
        PhoneNumber TEXT)''')

    # Create Fees table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Fees (
        StudentID INTEGER PRIMARY KEY,
        TotalFee REAL,
        FeePaid REAL,
        FeeDue REAL,
        FOREIGN KEY (StudentID) REFERENCES StudentsCoursesRegistraions(StudentID))''')

    connection.commit()

# Function to create a default user with hashed password if not already present
def create_default_user(cursor, connection):
    cursor.execute("SELECT * FROM Users WHERE Username = ?", ('admin',))
    user = cursor.fetchone()

    if not user:
        # Create a default username and password (hashed)
        password = 'admin123'  # Default password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO Users (Username, Password) VALUES (?, ?)", ('admin', hashed_password))
        connection.commit()

# Function to check login credentials
def check_login(cursor, connection, username, password):
    cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
    user = cursor.fetchone()

    if user:
        stored_password = user[1]  # Password from database
        hashed_input_password = hashlib.sha256(password.encode()).hexdigest()

        if stored_password == hashed_input_password:
            return True
        else:
            messagebox.showerror("Login Failed", "Incorrect Password")
            return False
    else:
        messagebox.showerror("Login Failed", "User does not exist")
        return False

# Function to send password reset email
def send_password_reset_email(user_email, new_password):
    from_email = "mohasule410@gmail.com"  # Your email
    to_email = user_email
    subject = "Password Reset"
    body = f"Your new password is: {new_password}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Upgrade the connection to TLS
            server.login(from_email, os.getenv('Moha,7315'))  # Use environment variable for password

            # Send email
            server.sendmail(from_email, to_email, msg.as_string())
            messagebox.showinfo("Password Reset", "Password reset email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        messagebox.showerror("Authentication Error", "Failed to authenticate. Please check your email/password or app password.")
        print("Authentication failed. Check your email/password or App Password.")
    except smtplib.SMTPConnectError:
        messagebox.showerror("Connection Error", "Failed to connect to the mail server. Check your internet connection or server settings.")
        print("Failed to connect to the SMTP server. Check your internet or server settings.")
    except Exception as e:
        messagebox.showerror("Error", f"Error sending email: {e}")
        print(f"An error occurred: {e}")


# Function to create login window
def create_login_window(cursor, connection):
    # Create the main window
    login_window = tk.Tk()
    login_window.title("Login")

    # Set window size to cover the entire screen
    login_window.geometry(f"{login_window.winfo_screenwidth()}x{login_window.winfo_screenheight()}+0+0")
    login_window.configure(bg='blue')  # Set background color to blue

    # Create a Canvas widget to display the background image
    canvas = tk.Canvas(login_window, width=login_window.winfo_screenwidth(), height=login_window.winfo_screenheight())
    canvas.pack(fill=tk.BOTH, expand=True)  # This allows the canvas to expand with the window

    # Load the background image using PIL
    if getattr(sys, 'frozen', False):
        image_path = os.path.join(sys._MEIPASS, 'bac.png')
    else:
        image_path = 'bac.png'
    bg_image = Image.open(image_path)

    # Convert the image to a PhotoImage object that tkinter can work with
    def update_background_image(event=None):
        width = event.width
        height = event.height

        # Resize the image to match the current window size
        resized_image = bg_image.resize((width, height), Image.Resampling.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
        bg_photo = ImageTk.PhotoImage(resized_image)

        # Update canvas size
        canvas.config(width=width, height=height)

        # Display the image on the canvas
        canvas.create_image(0, 0, anchor='nw', image=bg_photo)
        canvas.image = bg_photo  # Keep a reference to avoid garbage collection

    # Bind the resize event to update the background image when the window is resized
    login_window.bind('<Configure>', update_background_image)

    # Create a frame to hold the login widgets and center it
    frame = tk.Frame(login_window, bg='white', bd=10)
    frame.place(relx=0.5, rely=0.5, anchor='center')  # Position the frame at the center of the window

    # Create the username label and entry
    username_label = tk.Label(frame, text="Username:", bg='white', font=("Arial", 12))
    username_label.pack(pady=10)
    username_entry = tk.Entry(frame, font=("Arial", 12))
    username_entry.pack(pady=5)

    # Create the password label and entry
    password_label = tk.Label(frame, text="Password:", bg='white', font=("Arial", 12))
    password_label.pack(pady=10)
    password_entry = tk.Entry(frame, show="*", font=("Arial", 12))
    password_entry.pack(pady=5)

    # Function to handle login logic
    def on_login():
        username = username_entry.get()
        password = password_entry.get()

        if username and password:
            if check_login(cursor, connection, username, password):
                login_window.destroy()  # Close the login window
                setup_gui(cursor, connection)  # Proceed to the main system after successful login
            else:
                messagebox.showerror("Login Failed", "Incorrect Username or Password")
        else:
            messagebox.showerror("Input Error", "Please provide both Username and Password")

    # Create the login button
    login_button = tk.Button(frame, text="Login", command=on_login, font=("Arial", 12), bg='blue', fg='white')
    login_button.pack(pady=20)

    # Password Reset Option
    def reset_password():
        reset_window = tk.Toplevel()
        reset_window.title("Reset Password")
        reset_window.geometry("300x150")  # Set a fixed size for the reset window

        email_label = tk.Label(reset_window, text="Enter your email:", font=("Arial", 12))
        email_label.pack(pady=10)
        email_entry = tk.Entry(reset_window, font=("Arial", 12))
        email_entry.pack(pady=5)

        def on_reset():
            email = email_entry.get()
            if email:
                # Generate a new password and send it via email
                new_password = 'newpassword123'  # Example new password
                send_password_reset_email(email, new_password)
                reset_window.destroy()
            else:
                messagebox.showerror("Input Error", "Please provide an email address")

        reset_button = tk.Button(reset_window, text="Reset Password", command=on_reset, font=("Arial", 12))
        reset_button.pack(pady=20)

    # Password reset button
    reset_button = tk.Button(frame, text="Reset Password", command=reset_password, font=("Arial", 12), bg='red', fg='white')
    reset_button.pack(pady=5)

    # Run the window
    login_window.mainloop()

# Function to add student to the database with fee data
def add_student_to_db(student_id, student_name, phone_number, cursor, connection):
    cursor.execute("INSERT INTO StudentsCoursesRegistraions (StudentID, StudentName, PhoneNumber) VALUES (?, ?, ?)", 
                   (student_id, student_name, phone_number))
    connection.commit()

    # Insert initial fee data (all set to 0 initially)
    cursor.execute("INSERT INTO Fees (StudentID, TotalFee, FeePaid, FeeDue) VALUES (?, ?, ?, ?)", 
                   (student_id, 0.0, 0.0, 0.0))
    connection.commit()

# Function to update student in the database
def update_student_in_db(student_id, student_name, phone_number, cursor, connection):
    cursor.execute("UPDATE StudentsCoursesRegistraions SET StudentName = ?, PhoneNumber = ? WHERE StudentID = ?", 
                   (student_name, phone_number, student_id))
    connection.commit()

# Function to delete student from the database
def delete_student_from_db(student_id, cursor, connection):
    cursor.execute("DELETE FROM StudentsCoursesRegistraions WHERE StudentID = ?", (student_id,))
    connection.commit()

    cursor.execute("DELETE FROM Fees WHERE StudentID = ?", (student_id,))
    connection.commit()

# Function to load student data into the treeview
def load_students(treeview, cursor, search_query=""):
    # Clear the existing data in the treeview
    for row in treeview.get_children():
        treeview.delete(row)

    # Modify the SQL query based on the search query
    if search_query:
        query = '''
            SELECT s.StudentID, s.StudentName, s.PhoneNumber, f.TotalFee, f.FeePaid, f.FeeDue
            FROM StudentsCoursesRegistraions s
            JOIN Fees f ON s.StudentID = f.StudentID
            WHERE s.StudentName LIKE ? OR s.StudentID LIKE ? OR f.FeePaid LIKE ? OR f.FeeDue LIKE ? OR s.PhoneNumber LIKE ?
        '''
        search_term = f"%{search_query}%"
        cursor.execute(query, (search_term, search_term, search_term, search_term, search_term))
    else:
        query = '''
            SELECT s.StudentID, s.StudentName, s.PhoneNumber, f.TotalFee, f.FeePaid, f.FeeDue
            FROM StudentsCoursesRegistraions s
            JOIN Fees f ON s.StudentID = f.StudentID
        '''
        cursor.execute(query)

    students = cursor.fetchall()

    for student in students:
        treeview.insert("", "end", values=student)

# Function for handling updating student
def open_update_student_window(cursor, connection, treeview):
    update_window = tk.Toplevel()
    update_window.title("update Student")

    student_id_label = tk.Label(update_window, text="Student ID/birth.c. NO:")
    student_id_label.pack(pady=10)
    student_id_entry = tk.Entry(update_window)
    student_id_entry.pack(pady=5)

    student_name_label = tk.Label(update_window, text="new Student Name:")
    student_name_label.pack(pady=10)
    student_name_entry = tk.Entry(update_window)
    student_name_entry.pack(pady=5)

    phone_number_label = tk.Label(update_window, text="new Phone Number:")
    phone_number_label.pack(pady=10)
    phone_number_entry = tk.Entry(update_window)
    phone_number_entry.pack(pady=5)

    def on_update_student():
        student_id = student_id_entry.get()
        new_name = student_name_entry.get()
        new_phone_number = phone_number_entry.get()

        if student_id and new_name and new_phone_number:
            try:
                update_student_in_db(student_id, new_name, new_phone_number, cursor, connection)
                load_students(treeview, cursor)
                update_window.destroy()
                messagebox.showinfo("Success", "Student Updated Successfully!")
            except Exception as e:
                print("Error updating student:", e)
        else:
            messagebox.showerror("Input Error", "Please provide both Student ID and New Name.")

    update_button = tk.Button(update_window, text="update Student", command=on_update_student)
    update_button.pack(pady=20)

# Function for handling deleting a student
def open_delete_student_window(cursor, connection, treeview):
    delete_window = tk.Toplevel()
    delete_window.title("Delete Student")

    student_id_label = tk.Label(delete_window, text="Student ID/birth.c. NO:")
    student_id_label.pack(pady=10)
    student_id_entry = tk.Entry(delete_window)
    student_id_entry.pack(pady=5)

    def on_delete_student():
        student_id = student_id_entry.get()

        if student_id:
            try:
                cursor.execute("SELECT * FROM StudentsCoursesRegistraions WHERE StudentID = ?", (student_id,))
                student = cursor.fetchone()

                if student:
                    delete_student_from_db(student_id, cursor, connection)
                    load_students(treeview, cursor)
                    delete_window.destroy()
                    messagebox.showinfo("Success", "Student Deleted Successfully!")
                else:
                    messagebox.showerror("Error", "Student not found.")
            except Exception as e:
                print("Error deleting student:", e)
        else:
            messagebox.showerror("Input Error", "Please provide a Student ID.")

    delete_button = tk.Button(delete_window, text="Delete Student", command=on_delete_student)
    delete_button.pack(pady=20)

# Function to handle fee payment
def fee_payment(cursor, connection, treeview, student_id_payment_entry, amount_paid_entry):
    student_id = student_id_payment_entry.get()
    amount_paid = amount_paid_entry.get()

    if student_id and amount_paid:
        try:
            amount_paid = float(amount_paid)
            cursor.execute("SELECT FeeDue, FeePaid FROM Fees WHERE StudentID = ?", (student_id,))
            fee_data = cursor.fetchone()

            if fee_data:
                fee_due = fee_data[0]
                fee_paid = fee_data[1]
                if amount_paid <= fee_due:
                    new_fee_due = fee_due - amount_paid
                    new_fee_paid = fee_paid + amount_paid
                    cursor.execute("UPDATE Fees SET FeeDue = ?, FeePaid = ? WHERE StudentID = ?", 
                                   (new_fee_due, new_fee_paid, student_id))
                    connection.commit()

                    load_students(treeview, cursor)
                    student_id_payment_entry.delete(0, tk.END)
                    amount_paid_entry.delete(0, tk.END)
                    messagebox.showinfo("Success", "Fee Payment Successful!")
                else:
                    messagebox.showerror("Payment Error", "Amount paid exceeds fee due.")
            else:
                messagebox.showerror("Student Error", "Student not found.")
        except Exception as e:
            print("Error during fee payment:", e)
    else:
        messagebox.showerror("Input Error", "Please provide both Student ID and Amount Paid.")

# Function for handling adding a student
def open_add_student_window(cursor, connection, treeview):
    add_window = tk.Toplevel()
    add_window.title("Add Student")

    student_id_label = tk.Label(add_window, text="Student ID/birth.c. NO:")
    student_id_label.pack(pady=10)
    student_id_entry = tk.Entry(add_window)
    student_id_entry.pack(pady=5)

    student_name_label = tk.Label(add_window, text="Student Name:")
    student_name_label.pack(pady=10)
    student_name_entry = tk.Entry(add_window)
    student_name_entry.pack(pady=5)

    phone_number_label = tk.Label(add_window, text="Phone Number:")
    phone_number_label.pack(pady=10)
    phone_number_entry = tk.Entry(add_window)
    phone_number_entry.pack(pady=5)

    def on_add_student():
        student_id = student_id_entry.get()
        student_name = student_name_entry.get()
        phone_number = phone_number_entry.get()

        if student_id and student_name and phone_number:
            try:
                add_student_to_db(student_id, student_name, phone_number, cursor, connection)
                load_students(treeview, cursor)
                add_window.destroy()
            except Exception as e:
                print("Error adding student:", e)
        else:
            messagebox.showerror("Input Error", "Please provide Student ID, Name, and Phone Number.")

    add_button = tk.Button(add_window, text="Add Student", command=on_add_student)
    add_button.pack(pady=20)

# Function for handling fee management
def open_fee_management_window(cursor, connection, treeview):
    fee_window = tk.Toplevel()
    fee_window.title("Fee Management")

    student_id_label = tk.Label(fee_window, text="Student ID/birth.c. NO:")
    student_id_label.pack(pady=10)
    student_id_entry = tk.Entry(fee_window)
    student_id_entry.pack(pady=5)

    fee_label = tk.Label(fee_window, text="Fee Amount:")
    fee_label.pack(pady=10)
    fee_entry = tk.Entry(fee_window)
    fee_entry.pack(pady=5)

    def on_manage_fee():
        student_id = student_id_entry.get()
        fee = fee_entry.get()

        if student_id and fee:
            try:
                fee = float(fee)
                cursor.execute("UPDATE Fees SET TotalFee = ?, FeeDue = ? WHERE StudentID = ?", 
                               (fee, fee, student_id))
                connection.commit()

                load_students(treeview, cursor)
                fee_window.destroy()
            except Exception as e:
                print("Error managing fees:", e)
        else:
            messagebox.showerror("Input Error", "Please provide both Student ID and Fee.")

    fee_button = tk.Button(fee_window, text="Assign Fee", command=on_manage_fee)
    fee_button.pack(pady=20)

# Function for handling fee payment
def open_fee_payment_window(cursor, connection, treeview):
    payment_window = tk.Toplevel()
    payment_window.title("Fee Payment")

    student_id_payment_label = tk.Label(payment_window, text="Student ID/birth.c. NO:")
    student_id_payment_label.pack(pady=10)
    student_id_payment_entry = tk.Entry(payment_window)
    student_id_payment_entry.pack(pady=5)

    amount_paid_label = tk.Label(payment_window, text="Amount Paid:")
    amount_paid_label.pack(pady=10)
    amount_paid_entry = tk.Entry(payment_window)
    amount_paid_entry.pack(pady=5)

    def on_fee_payment():
        fee_payment(cursor, connection, treeview, student_id_payment_entry, amount_paid_entry)
        payment_window.destroy()

    payment_button = tk.Button(payment_window, text="Make Payment", command=on_fee_payment)
    payment_button.pack(pady=20)


# Function to create the main system GUI after login
def setup_gui(cursor, connection):
    root = tk.Tk()
    root.configure(bg='#f2f2f2')  # Lighter background color
    root.title("Student Management System")

    # Maximize the window
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f"{width}x{height}+0+0")  # Maximizes the window on start

    # Create top frame for title and logo
    top_frame = tk.Frame(root, bg="#4a90e2")  # Light blue background for the header
    top_frame.pack(side="top", fill="x", pady=10)

    # Add title with new font and color
    title_label = tk.Label(top_frame, text="STUDENT MANAGEMENT SYSTEM", font=("Arial", 40, "bold"), fg="white")
    title_label.pack(side="left", padx=20)

    try:
        logo_image = PhotoImage(file="shot.png")  # Adjust path as needed
        logo_image = logo_image.subsample(2, 3) 
        logo_label = tk.Label(top_frame, image=logo_image)
        logo_label.image = logo_image  # Keep a reference to avoid garbage collection
        logo_label.pack(side="right", padx=10)
    except Exception as e:
        print("Logo loading failed:", e)

    # Create frames for buttons and Treeview
    left_frame = tk.Frame(root, bg="#3a9c56", width=300, height=400)  # Green background for buttons
    left_frame.pack(side="left", padx=10, pady=10)

    right_frame = tk.Frame(root, bg="#f8f8f8", width=500, height=400)  # Light gray for right content area
    right_frame.pack(side="right", padx=10, pady=10)

    # Create Search bar with styled input and button
    search_label = tk.Label(right_frame, text="Search Student:", font=("Arial", 12), bg="#f8f8f8")
    search_label.pack(pady=10)

    search_entry = tk.Entry(right_frame, font=("Arial", 12))
    search_entry.pack(pady=5)

    def on_search():
        search_query = search_entry.get()
        load_students(treeview, cursor, search_query)

    search_button = tk.Button(right_frame, text="Search", font=("Arial", 12), bg="#4a90e2", fg="white", command=on_search)
    search_button.pack(pady=10)

    # Create Treeview for displaying student data including fee details
    global treeview  # Declare treeview as global to access inside other functions
    treeview = ttk.Treeview(right_frame, columns=("StudentID", "StudentName", "PhoneNumber", "TotalFee", "FeePaid", "FeeDue"), show="headings")
    treeview.heading("StudentID", text="Student ID/birth NO")
    treeview.heading("StudentName", text="Student Name")
    treeview.heading("PhoneNumber", text="Phone Number")  # Added PhoneNumber column
    treeview.heading("TotalFee", text="Total Fee")
    treeview.heading("FeePaid", text="Fee Paid")
    treeview.heading("FeeDue", text="Fee Due")
    treeview.pack(fill="both", expand=True)

    # Load students initially
    load_students(treeview, cursor)

    # Create buttons on the left side with enhanced styling
    add_student_button = tk.Button(left_frame, bg="#4a90e2", text="Add Student", font=("Arial", 12, "bold"), fg="white", 
                                   command=lambda: open_add_student_window(cursor, connection, treeview))
    add_student_button.pack(pady=5)

    update_student_button = tk.Button(left_frame, bg="#4a90e2", text="Update Student", font=("Arial", 12, "bold"), fg="white",
                                   command=lambda: open_update_student_window(cursor, connection, treeview))
    update_student_button.pack(pady=5)

    delete_student_button = tk.Button(left_frame, bg="#e94e77", text="Delete Student", font=("Arial", 12, "bold"), fg="white", 
                                      command=lambda: open_delete_student_window(cursor, connection, treeview))
    delete_student_button.pack(pady=5)

    fee_management_button = tk.Button(left_frame, bg="#4a90e2", text="Fee Management", font=("Arial", 12, "bold"), fg="white",
                                      command=lambda: open_fee_management_window(cursor, connection, treeview))
    fee_management_button.pack(pady=5)

    fee_payment_button = tk.Button(left_frame, bg="#4a90e2", text="Fee Payment", font=("Arial", 12, "bold"), fg="white", 
                                   command=lambda: open_fee_payment_window(cursor, connection, treeview))
    fee_payment_button.pack(pady=5)

    root.mainloop()

def main():
    connection = sqlite3.connect("school.db")
    cursor = connection.cursor()

    # Create the necessary tables
    create_tables(cursor, connection)
    create_default_user(cursor, connection)  # Add default user

    # Start the GUI by opening the login page
    create_login_window(cursor, connection)

if __name__ == "__main__":
    main()

