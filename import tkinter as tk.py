import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import sqlite3
import hashlib
import smtplib
from email.mime.text import MIMEText
import os
from PIL import Image, ImageTk

# ==================== Database Setup Functions ====================

def create_tables(cursor, connection):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            Username TEXT PRIMARY KEY,
            Password TEXT
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS StudentsCoursesRegistraions (
            StudentID INTEGER PRIMARY KEY,
            StudentName TEXT,
            PhoneNumber TEXT
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Fees (
            StudentID INTEGER PRIMARY KEY,
            TotalFee REAL,
            FeePaid REAL,
            FeeDue REAL,
            FOREIGN KEY (StudentID) REFERENCES StudentsCoursesRegistraions(StudentID)
        )''')
    connection.commit()

def create_default_user(cursor, connection):
    cursor.execute("SELECT * FROM Users WHERE Username = ?", ('admin',))
    if not cursor.fetchone():
        default_password = 'admin123'
        hashed = hashlib.sha256(default_password.encode()).hexdigest()
        cursor.execute("INSERT INTO Users (Username, Password) VALUES (?, ?)", ('admin', hashed))
        connection.commit()

# ==================== Utility Functions ====================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(cursor, connection, username, password):
    cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
    user = cursor.fetchone()
    if user and user[1] == hash_password(password):
        return True
    messagebox.showerror("Login Failed", "Invalid credentials.")
    return False

def send_password_reset_email(email, new_password):
    from_email = "your_email@example.com"
    subject = "Password Reset"
    body = f"Your new password is: {new_password}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, os.getenv('EMAIL_PASSWORD'))
            server.sendmail(from_email, email, msg.as_string())
            messagebox.showinfo("Success", "Password reset email sent.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {e}")

# ==================== Student CRUD Functions ====================

def add_student_to_db(student_id, student_name, phone_number, cursor, connection):
    cursor.execute("INSERT INTO StudentsCoursesRegistraions (StudentID, StudentName, PhoneNumber) VALUES (?, ?, ?)",
                   (student_id, student_name, phone_number))
    cursor.execute("INSERT INTO Fees (StudentID, TotalFee, FeePaid, FeeDue) VALUES (?, ?, ?, ?)",
                   (student_id, 0.0, 0.0, 0.0))
    connection.commit()

def update_student_in_db(student_id, name, phone, cursor, connection):
    cursor.execute("UPDATE StudentsCoursesRegistraions SET StudentName = ?, PhoneNumber = ? WHERE StudentID = ?",
                   (name, phone, student_id))
    connection.commit()

def delete_student_from_db(student_id, cursor, connection):
    cursor.execute("DELETE FROM Fees WHERE StudentID = ?", (student_id,))
    cursor.execute("DELETE FROM StudentsCoursesRegistraions WHERE StudentID = ?", (student_id,))
    connection.commit()

def load_students(treeview, cursor, search_query=None):
    for row in treeview.get_children():
        treeview.delete(row)

    if search_query:
        query = '''
            SELECT s.StudentID, s.StudentName, s.PhoneNumber, f.TotalFee, f.FeePaid, f.FeeDue
            FROM StudentsCoursesRegistraions s
            JOIN Fees f ON s.StudentID = f.StudentID
            WHERE s.StudentName LIKE ? OR s.StudentID LIKE ? OR s.PhoneNumber LIKE ?
        '''
        term = f"%{search_query}%"
        cursor.execute(query, (term, term, term))
    else:
        query = '''
            SELECT s.StudentID, s.StudentName, s.PhoneNumber, f.TotalFee, f.FeePaid, f.FeeDue
            FROM StudentsCoursesRegistraions s
            JOIN Fees f ON s.StudentID = f.StudentID
        '''
        cursor.execute(query)

    for student in cursor.fetchall():
        treeview.insert("", "end", values=student)

# ==================== Login Window ====================

def create_login_window(cursor, connection):
    login_window = tk.Tk()
    login_window.title("Login")
    # Make the window full screen
    login_window.attributes("-fullscreen", True)

    # === Create canvas to hold background image ===
    canvas = tk.Canvas(login_window, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    # === Load the background image ===
    bg_image = Image.open("/home/mohack/Pictures/Screenshots/bac.png")

    def update_background_image(event=None):
        # Get actual window size
        width = login_window.winfo_width()
        height = login_window.winfo_height()

        if width < 100 or height < 100:
            return  # Skip small initial sizes

        # Resize and convert image
        resized_image = bg_image.resize((width, height), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(resized_image)

        # Draw image on canvas with a tag
        canvas.delete("bg")
        canvas.create_image(0, 0, anchor='nw', image=bg_photo, tags="bg")
        canvas.image = bg_photo  # Prevent garbage collection

    # Bind the resize event to update the background
    login_window.bind('<Configure>', update_background_image)

    # === Create login frame (after canvas) ===
    frame = tk.Frame(login_window, bg="grey", padx=20, pady=20)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    # Bring login frame above canvas
    frame.tkraise()
#######
    frame = tk.Frame(login_window,bg='pink', padx=20, pady=20)
    frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame in the full screen

    tk.Label(frame, text="Username:", bg="white", font=("Arial", 14)).pack(pady=5)
    username_entry = tk.Entry(frame, font=("Arial", 12))
    username_entry.pack()

    tk.Label(frame, text="Password:", bg="white", font=("Arial", 14)).pack(pady=5)
    password_entry = tk.Entry(frame, show="*", font=("Arial", 12))
    password_entry.pack()

    def attempt_login(event=None):  # event=None allows binding and button to use same function
        username = username_entry.get()
        password = password_entry.get()
        if check_login(cursor, connection, username, password):
            login_window.destroy()
            setup_gui(cursor, connection)

    login_button = tk.Button(frame, text="Login", command=attempt_login, bg="blue", fg="white", font=("Arial", 12))
    login_button.pack(pady=10)

    def reset_password():
        reset_win = tk.Toplevel(login_window)
        reset_win.title("Reset Password")
        tk.Label(reset_win, text="Enter your email:").pack()
        email_entry = tk.Entry(reset_win)
        email_entry.pack()

        def send_reset():
            email = email_entry.get()
            new_pass = "newpassword123"
            send_password_reset_email(email, new_pass)
            reset_win.destroy()

        tk.Button(reset_win, text="Send Reset", command=send_reset).pack()

    tk.Button(frame, text="Forgot Password?", command=reset_password, bg="red", fg="white", font=("Arial", 12)).pack(pady=5)

    # Bind Enter key (Return) to the login function
    login_window.bind("<Return>", attempt_login)

    # Allow exiting full screen with ESC key
    login_window.bind("<Escape>", lambda e: login_window.attributes("-fullscreen", False))

    login_window.mainloop()


# ========= End of SECTION 1 =========

# ==================== Student and Fee Management Windows ====================

def open_add_student_window(cursor, connection, treeview):
    window = tk.Toplevel()
    window.title("Add Student")

    tk.Label(window, text="Student ID:").pack()
    id_entry = tk.Entry(window)
    id_entry.pack()

    tk.Label(window, text="Student Name:").pack()
    name_entry = tk.Entry(window)
    name_entry.pack()

    tk.Label(window, text="Phone Number:").pack()
    phone_entry = tk.Entry(window)
    phone_entry.pack()

    def submit():
        try:
            add_student_to_db(id_entry.get(), name_entry.get(), phone_entry.get(), cursor, connection)
            load_students(treeview, cursor)
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    window.bind("<Return>", lambda event: submit())
    tk.Button(window, text="Add", command=submit).pack(pady=10)

def open_update_student_window(cursor, connection, treeview):
    window = tk.Toplevel()
    window.title("Update Student")

    tk.Label(window, text="Student ID:").pack()
    id_entry = tk.Entry(window)
    id_entry.pack()

    tk.Label(window, text="New Name:").pack()
    name_entry = tk.Entry(window)
    name_entry.pack()

    tk.Label(window, text="New Phone:").pack()
    phone_entry = tk.Entry(window)
    phone_entry.pack()

    def submit():
        update_student_in_db(id_entry.get(), name_entry.get(), phone_entry.get(), cursor, connection)
        load_students(treeview, cursor)
        window.destroy()

    window.bind("<Return>", lambda event: submit())
    tk.Button(window, text="Update", command=submit).pack(pady=10)

def open_delete_student_window(cursor, connection, treeview):
    window = tk.Toplevel()
    window.title("Delete Student")

    tk.Label(window, text="Student ID:").pack()
    id_entry = tk.Entry(window)
    id_entry.pack()

    def submit():
        delete_student_from_db(id_entry.get(), cursor, connection)
        load_students(treeview, cursor)
        window.destroy()

    window.bind("<Return>", lambda event: submit())
    tk.Button(window, text="Delete", command=submit).pack(pady=10)

def open_fee_management_window(cursor, connection, treeview):
    window = tk.Toplevel()
    window.title("Assign Fee")

    tk.Label(window, text="Student ID:").pack()
    id_entry = tk.Entry(window)
    id_entry.pack()

    tk.Label(window, text="Fee Amount:").pack()
    fee_entry = tk.Entry(window)
    fee_entry.pack()

    def submit():
        try:
            fee = float(fee_entry.get())
            cursor.execute("UPDATE Fees SET TotalFee=?, FeeDue=? WHERE StudentID=?", (fee, fee, id_entry.get()))
            connection.commit()
            load_students(treeview, cursor)
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    window.bind("<Return>", lambda event: submit())
    tk.Button(window, text="Assign", command=submit).pack(pady=10)

def open_fee_payment_window(cursor, connection, treeview):
    window = tk.Toplevel()
    window.title("Pay Fee")

    tk.Label(window, text="Student ID:").pack()
    id_entry = tk.Entry(window)
    id_entry.pack()

    tk.Label(window, text="Amount Paid:").pack()
    amount_entry = tk.Entry(window)
    amount_entry.pack()

    def submit():
        try:
            student_id = id_entry.get()
            amount_paid = float(amount_entry.get())
            cursor.execute("SELECT FeePaid, FeeDue FROM Fees WHERE StudentID=?", (student_id,))
            record = cursor.fetchone()

            if record:
                new_paid = record[0] + amount_paid
                new_due = record[1] - amount_paid
                if new_due < 0:
                    messagebox.showerror("Error", "Overpayment is not allowed.")
                    return

                cursor.execute("UPDATE Fees SET FeePaid=?, FeeDue=? WHERE StudentID=?", (new_paid, new_due, student_id))
                connection.commit()
                load_students(treeview, cursor)
                window.destroy()
            else:
                messagebox.showerror("Error", "Student not found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    window.bind("<Return>", lambda event: submit())
    tk.Button(window, text="Submit Payment", command=submit).pack(pady=10)

# ==================== Main Application GUI ====================

def setup_gui(cursor, connection):
    root = tk.Tk()
    root.title("Student Management System")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0") 
    root.configure(bg="white")

    # Treeview
    tree_frame = tk.Frame(root)
    tree_frame.pack(side="right", fill="both", expand=True)

    columns = ("StudentID", "StudentName", "PhoneNumber", "TotalFee", "FeePaid", "FeeDue")
    treeview = ttk.Treeview(tree_frame, columns=columns, show="headings")

    for col in columns:
        treeview.heading(col, text=col)
        treeview.column(col, anchor="center")

    treeview.pack(fill="both", expand=True)
    load_students(treeview, cursor)

    # Sidebar Menu
    side_frame = tk.Frame(root, bg="#e0f0f0", padx=20, pady=20)
    side_frame.pack(side="left", fill="y")

    tk.Label(side_frame, text="Actions", font=("Arial", 16, "bold"), bg="#e0f0f0").pack(pady=10)

    tk.Button(side_frame, text="Add Student", command=lambda: open_add_student_window(cursor, connection, treeview)).pack(pady=5)
    tk.Button(side_frame, text="Update Student", command=lambda: open_update_student_window(cursor, connection, treeview)).pack(pady=5)
    tk.Button(side_frame, text="Delete Student", command=lambda: open_delete_student_window(cursor, connection, treeview)).pack(pady=5)
    tk.Button(side_frame, text="Assign Fee", command=lambda: open_fee_management_window(cursor, connection, treeview)).pack(pady=5)
    tk.Button(side_frame, text="Pay Fee", command=lambda: open_fee_payment_window(cursor, connection, treeview)).pack(pady=5)

    # Search
    tk.Label(side_frame, text="Search", bg="#e0f0f0").pack(pady=10)
    search_entry = tk.Entry(side_frame)
    search_entry.pack()

    def do_search():
        load_students(treeview, cursor, search_entry.get())

    search_entry.bind("<Return>", lambda event: do_search())
    tk.Button(side_frame, text="Search", command=do_search).pack(pady=5)

    root.mainloop()

# ==================== Main ====================

def main():
    connection = sqlite3.connect("school.db")
    cursor = connection.cursor()
    create_tables(cursor, connection)
    create_default_user(cursor, connection)
    create_login_window(cursor, connection)

if __name__ == "__main__":
    main()
