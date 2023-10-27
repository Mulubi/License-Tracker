import tkinter as tk
from tkinter import messagebox, ttk, Toplevel, simpledialog
from PIL import ImageTk,Image
import sqlite3
import datetime
# from main import read_nurse_data, calculate_days_until_expiration, send_email_notification

# Global variable for nurse data
nurse_data_file = 'nurse_license_data.db'


# Connect to the database
conn = sqlite3.connect(nurse_data_file)
c = conn.cursor()

# Create the table if it doesn't exist
c.execute("""
    CREATE TABLE IF NOT EXISTS nurse_data (
        name TEXT,
        license_issue_date DATE
    )
""")

# Commit the changes and close the connection
conn.commit()
conn.close()

# Function to read nurse data from the database
def read_nurse_data():
    conn = sqlite3.connect(nurse_data_file)
    c = conn.cursor()

    c.execute("SELECT * FROM nurse_data")
    records = c.fetchall()

    conn.close()
    return []

def calculate_days_until_expiration(nurses):
    updated_nurses = []

    for nurse in nurses:
        try:
            issue_date = datetime.datetime.strptime(nurse[1], "%Y-%m-%d").date()
            expiration_date = issue_date + datetime.timedelta(days=365)
            days_until_expiration = (expiration_date - datetime.date.today()).days
            updated_nurse = list(nurse) # Convert the tuple to list
            updated_nurse.append(days_until_expiration)
            updated_nurses.append(updated_nurse)
        except ValueError:
            updated_nurse.append(nurse + (-1,)) # Append -1 for invalid dates

    return updated_nurses

# Function to handle the "Add Nurse" button click event
def add_nurse():
    global nurse_name
    global issue_date
    nurse_name = name_entry.get()
    issue_date = license_issue_date_entry.get()
    if nurse_name and issue_date:
        # Connect to a database
        conn = sqlite3.connect(nurse_data_file)

        # Create a cursor
        c = conn.cursor()

        #  Insert into Table
        c.execute("""INSERT INTO nurse_data VALUES (:name_entry, :license_issue_date_entry)""",
                {
                    'name_entry': name_entry.get(),
                    'license_issue_date_entry': license_issue_date_entry.get()
                })
        # Commit Database changes
        conn.commit()

        # Close Database connection
        conn.close()

        messagebox.showinfo("Success", f"Nurse {nurse_name} has been added successfully.")
        # nurse_names.append(nurse_name)
        # nurse_combobox['values'] = nurse_names # Update the combobox values
        # refresh_treeview()
    else:
        messagebox.showwarning("Missing Information", "Please provide a nurse name and the date their license was issued.")
    
    # Clear input fields
    name_entry.delete(0, tk.END)
    license_issue_date_entry.delete(0, tk.END)

# Function to handle the "View Nurses" button click event
def view_nurses():
    # Read the nurse data from the database
    nurses = read_nurse_data()

    # Calculate the days until expiration for each nurse
    updated_nurses = calculate_days_until_expiration(nurses)

    # Perform actions to view nurse information
    global nurse_list_window
    nurse_list_window = Toplevel(window)
    nurse_list_window.title("List of Nurses")

    # Nurse List Treeview
    nurse_tree = ttk.Treeview(nurse_list_window, columns=("Name", "License Issue Date", "Days Until Expiration", "Edit", "Delete"))
    nurse_tree.heading("#1", text="Name")
    nurse_tree.heading("#2", text="License Issue Date")
    nurse_tree.heading("#3", text="Days Until Expiration")
    nurse_tree.heading("#4", text="Edit")
    nurse_tree.heading("#5", text="Delete")
    nurse_tree.pack()

    # Connect to a database
    conn = sqlite3.connect("nurse_data.db")

    # Create a cursor
    c = conn.cursor()

    # Query the database
    c.execute("""SELECT *, oid FROM nurse_data""")
    records = c.fetchall()
    # print(records)
    # print(updated_nurses)


    for nurse in updated_nurses:
        nurse_name = nurse[0]
        issue_date = nurse[1]
        days_until_expiration = nurse[2] if nurse[2] >= 0 else "N/A"
        nurse_tree.insert("", "end", values=(nurse_name, issue_date, days_until_expiration, "Edit", "Delete"))

    # # Handle double click event on treeview item
    # def on_item_double_click(event):
    #     item = nurse_tree.selection()[0]
    #     column = nurse_tree.identify_column(event.x)

    #     if column == "#4":
    #         edit_nurse(item)
    #     elif column == "#5":
    #         delete_nurse(item)

    # nurse_tree.bind("<Double-1>", on_item_double_click)

    # Nurse List Buttons
    edit_button = tk.Button(nurse_list_window, text="Edit Nurse", command=edit_nurse)
    edit_button.pack(pady=5)

    delete_button = tk.Button(nurse_list_window, text="Delete Nurse", command=delete_nurse)
    delete_button.pack(pady=5)

    

    # list_nurses = ''
    # for record in records:
    #     list_nurses += str(record[2]) + " " + str(record[0]) + "\n"
    
    # view_nurses_label = tk.Label(window, text=list_nurses)
    # view_nurses_label.grid(row=9, column=0, columnspan=2)


# Function to delete a nurse
def delete_nurse(nurse_name):
    nurse_id = nurse_tree.item(selected_item)['values'][2]

    # Connect to a database
    conn = sqlite3.connect(nurse_data_file)

    # Create a cursor
    c = conn.cursor()

    c.execute("""DELETE FROM nurse_data WHERE oid=?""", (nurse_id,))

    # Commit Database changes
    conn.commit()

    # Close Database connection
    conn.close()

    nurse_tree.delete(selected_item)

    # Display success message
    messagebox.showinfo("Success", "{nurse_name} deleted successfully.")
    
    # Clear input fields
    delete_entry.delete(0, tk.END)


# def save_nurse():

#     conn = sqlite3.connect(nurse_data_file)
#     c = conn.cursor()
#     nurse_id = delete_entry.get()
#     c.execute("""
#     UPDATE nurse_data SET
#         name = :name_entry,
#         license_issue_date = :license_issue_date_entry,
#         email = :email_entry
#     WHERE oid = :oid
#     """,
#     {
#         'name_entry': name_entry_editor.get(),
#         'license_issue_date_entry': license_issue_date_entry_editor.get(),
#         'email_entry': email_entry_editor.get(),
#         'oid': nurse_id
#     })

#     # Commit the changes and close the connection
#     conn.commit()
#     conn.close()

#     editor.destroy()



#Function to edit a nurse record
def edit_nurse(selected_item):
    def save_nurse():
        updated_name = name_entry_editor.get()
        updated_issue_date = license_issue_date_entry_editor.get()

        # Connect to a database
        conn = sqlite3.connect(nurse_data_file)

        # Create a cursor
        c = conn.cursor()
        nurse_id = nurse_tree.item(selected_item)['values'][2]

        # Query the database
        c.execute("""UPDATE nurse_data SET name = ?, license_issue_date = ? WHERE oid = ?""",
                    (updated_name, updated_issue_date, nurse_id))
        
        conn.commit()
        conn.close()

        nurse_tree.item(selected_item, values=(updated_name, updated_issue_date, days_until_expiration, nurse_id))
        editor.destroy()

    global editor
    editor = tk.Toplevel(window)
    editor.title("Edit Nurse Details")
    editor.iconbitmap('hosp.ico')
    editor.geometry("400x400")
    
    selected_nurse = nurse_tree.item(selected_item)["values"]
    name_label_editor = tk.Label(editor, text="Nurse Name")
    name_label_editor.grid(row=0, column=0)
    name_entry_editor = tk.Entry(editor, width=30)
    name_entry_editor.insert(0, selectred_nurse[0])
    name_entry_editor.grid(row=0, column=1, padx=20)

    license_issue_date_label_editor = tk.Label(editor, text="License Issue Date")
    license_issue_date_label_editor.grid(row=1, column=0)
    license_issue_date_entry_editor = tk.Entry(editor, width=30)
    license_issue_date_entry.insert(0, selected_nurse[1])
    license_issue_date_entry_editor.grid(row=1, column=1)

    # Create buttons for saving and viewing nurse information
    save_button = tk.Button(editor, text="Save", command=save_nurse)
    save_button.grid(row=6, column=0, columnspan=2, pady=10, padx=10, ipadx=100)

    # # Create Global variables for the text box names
    # global name_entry_editor
    # global license_issue_date_entry_editor
    # global email_entry_editor

    # #  Create text boxes
    

    

    # email_entry_editor = tk.Entry(editor, width=30)
    # email_entry_editor.grid(row=2, column=1)

    # # Create text box labels
    

    

    # email_label_editor = tk.Label(editor, text="Email Address")
    # email_label_editor.grid(row=2, column=0)

    # # delete_label = tk.Label(editor, text="Enter ID: ")
    # # delete_label.grid(row=11, column=0)

    # # edit_label = tk.Label(editor, text="Enter ID: ")
    # # edit_label.grid(row=13, column=0)

    # for record in records:
    #     name_entry_editor.insert(0, record[0])
    #     license_issue_date_entry_editor.insert(1, record[1])
    #     email_entry_editor.insert(2, record[2])


    

    # view_button = tk.Button(editor, text="View Nurses", command=view_nurses)
    # view_button.grid(row=7, column=0, columnspan=2, pady=10, padx=10, ipadx=140)

    # delete_button = tk.Button(editor, text="Delete a nurse", command=delete_nurse)
    # delete_button.grid(row=12, column=0, columnspan=2, pady=10, padx=10, ipadx=120)

    # edit_button = tk.Button(editor, text="Select a Nurse", command=edit_nurse)
    # edit_button.grid(row=14, column=0, columnspan=2, pady=10, padx=10, ipadx=148)

    # # Create labels and entry fields for nurse information
    # name_label = tk.Label(editor, text="Nurse Name:")
    # name_label.pack()
    # name_entry = tk.Entry(editor)
    # name_entry.pack()

    # issue_date_label = tk.Label(editor, text="License Issue Date:")
    # issue_date_label.pack()
    # issue_date_entry = tk.Entry(editor)
    # issue_date_entry.pack()



    # # Button to Exit the program
    # exit_button = tk.Button(editor, text="Exit", command=editor.quit)
    # exit_button.grid(columnspan=2)



def send_email_notification(nurse_data, target_email, cc_emails):
    sender_email = "it@3rdparkhospital.com" # Put the email address of your preferred sender
    sender_password = "16rnVgYYVcEN" # Update with the right password
    smtp_server = "smtp.zoho.com" # Update with your preferred SMTP server

    subject = "NURSE LICENSE EXPIRATION REMINDER"

    # Construct the email message with nurse data
    message = f"Dear Macroy, \n\nThe following nurses have licenses that will expire soon: \n\n"
    for nurse in nurse_data:
        days_until_expiration = nurse.get("days_until_expiration", -1)

        if days_until_expiration in range(0, 60):
            message += f"{nurse['name']}'s license will expire in {days_until_expiration} days.\n"

    # Add a closing message and signature
    message += f"\nKindly follow up to make sure this is renewed.\n\nBest regards,\nMiriam \nDirector of Nursing Services."

    # Construct the email
    email = MIMEMultipart()
    email['From'] = sender_email
    email['To'] = target_email
    email['Subject'] = subject

    # Add CC email addresses if available
    if cc_emails:
        email['Cc'] = ', '.join(cc_emails.split(","))

    email.attach(MIMEText(message, 'plain'))

    try:
        # Connect with the SMTP server to send the email
        with smtplib.SMTP(smtp_server, 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(email)
        messagebox.showinfo("Email Sent", "Email has been sent successfully!")

    except Expection as e:
        messagebox.showerror("Error", f"An error occurred while sending the email: {str(e)}")

def email_reminder():
    emailor = tk.Tk()
    emailor.title("Send Email Reminder")
    emailor.geometry("600x200")

    frame = tk.Frame(emailor)
    frame.pack()

    email_info_frame = tk.LabelFrame(frame, text="Fill in the email details: ")
    email_info_frame.grid(row=0, column=0, sticky="news", padx=10, pady=10)
    
    target_email_label = tk.Label(email_info_frame, text="Sending To: ")
    target_email_label.grid(row=0, column=0)
    
    cc_label = tk.Label(email_info_frame, text="CC: ")
    cc_label.grid(row=1, column=0)

    target_email_label2 = tk.Label(email_info_frame, text="hr@3rdparkhospital.com", width=25)
    target_email_label2.grid(row=0, column=1)
    
    # target_email_entry = tk.Entry(email_info_frame)
    # target_email_entry.grid(row=0, column=1)
    cc_entry = tk.Entry(email_info_frame, width=30)
    cc_entry.grid(row=1, column=1)
    # Create buttons for adding and viewing nurse information
    send_email_button = tk.Button(email_info_frame, text="Send", command=lambda: send_email_notification_wrapper(cc_entry))
    send_email_button.grid(row=1, column=2)

    for widget in email_info_frame.winfo_children():
        widget.grid_configure(padx=20, pady=20)
    
def send_email_notification_wrapper(cc_entry):
    # Read data
    nurses = read_nurse_data()

    calculate_days_until_expiration(nurses)

    # Email addresses
    target_email = "mulubiwarren@gmail.com"
    cc_emails = cc_entry.get()

    # Send email notification only if there are nurses with licenses expiring soon
    if any(0 <= nurse.get("days_until_expiration", -1) < 60 for nurse in nurses):
        send_email_notification(nurses, target_email, cc_emails)


    

# Create the main application window
window = tk.Tk()
window.title("Nurse License Tracker")
# window.geometry("400x600")
window.iconbitmap('images/index.ico')
window.iconbitmap(default='images/index.ico')

frame = tk.Frame(window)
frame.pack()

nurse_info_frame = tk.LabelFrame(frame, text="Nurse Information")
nurse_info_frame.grid(row=0, column=0, padx=20, pady=20)

name_label = tk.Label(nurse_info_frame, text="Nurse Name")
name_label.grid(row=0, column=0)
license_issue_date_label = tk.Label(nurse_info_frame, text="License Issue Date")
license_issue_date_label.grid(row=0, column=1)


name_entry = tk.Entry(nurse_info_frame)
name_entry.grid(row=1, column=0)
license_issue_date_entry = tk.Entry(nurse_info_frame)
license_issue_date_entry.grid(row=1, column=1)
# Create buttons for adding and viewing nurse information
add_button = tk.Button(nurse_info_frame, text="Add Nurse", command=add_nurse)
add_button.grid(row=1, column=2)


for widget in nurse_info_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)
# email_entry = tk.Entry(window, width=30)
# email_entry.grid(row=2, column=1)

# delete_entry = tk.Entry(window, width=30)
# delete_entry.grid(row=11, column=1)

# Create text box labels

view_nurses_frame = tk.LabelFrame(frame)
view_nurses_frame.grid(row=1, column=0, sticky="news", padx=20, pady=20)

view_button = tk.Button(view_nurses_frame, text="View Nurses Here", command=view_nurses)
view_button.grid(row=0, column=0, sticky="news", pady=20, padx=20)

for widget in view_nurses_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

notifications_frame = tk.LabelFrame(frame)
notifications_frame.grid(row=2, sticky="news", column=0, padx=20, pady=20)

email_button = tk.Button(frame, text="Send email reminder here", command=email_reminder)
email_button.grid(row=3, column=0, sticky="news", padx=20, pady=10)

# email_label = tk.Label(window, text="Email Address", font=('Arial', 18))
# email_label.grid(row=2, column=0)

# delete_label = tk.Label(window, text="Enter ID: ")
# delete_label.grid(row=11, column=0)

# edit_label = tk.Label(window, text="Enter ID: ")
# edit_label.grid(row=13, column=0)




# delete_button = tk.Button(window, text="Delete a nurse", command=delete_nurse)
# delete_button.grid(row=12, column=0, columnspan=2, pady=10, padx=10, ipadx=120)

# edit_button = tk.Button(window, text="Select a Nurse", command=edit_nurse)
# edit_button.grid(row=14, column=0, columnspan=2, pady=10, padx=10, ipadx=148)

# send_email_button = tk.Button(window, text="Selend an email", command=send_email_notification(nurse_data))
# send_email_button.grid(row=14, column=0, columnspan=2, pady=10, padx=10, ipadx=148)

# # Create labels and entry fields for nurse information
# name_label = tk.Label(window, text="Nurse Name:")
# name_label.pack()
# name_entry = tk.Entry(window)
# name_entry.pack()

# issue_date_label = tk.Label(window, text="License Issue Date:")
# issue_date_label.pack()
# issue_date_entry = tk.Entry(window)
# issue_date_entry.pack()



# Button to Exit the program
# exit_button = tk.Button(window, text="Exit", command=window.quit)
# exit_button.grid(columnspan=2)

# Run the main application loop
window.mainloop()