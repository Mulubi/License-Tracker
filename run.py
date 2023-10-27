import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from tkinter import ttk, Toplevel, simpledialog, messagebox
from ttkbootstrap.dialogs import Messagebox
from PIL import ImageTk, Image
import sqlite3
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Global variables
nurse_data_file = 'nurse_license_data.db'
nurses = []

# Connect to the database
conn = sqlite3.connect("nurse_license_data.db")
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

    c.execute("SELECT *, oid FROM nurse_data")
    records = c.fetchall()

    conn.close()

    nurse_list = []
    for record in records:
        nurse_data = {
            "name": record[0],
            "license_issue_date": record[1],
            "oid": record[2]
        }
        nurse_list.append(nurse_data)

    return nurse_list

# Function to calculate days until expiration
def calculate_days_until_expiration(nurses):
    updated_nurses = []

    for nurse in nurses:
        try:
            issue_date = datetime.datetime.strptime(nurse['license_issue_date'], "%Y-%m-%d").date()
            expiration_date = issue_date + datetime.timedelta(days=365)
            days_until_expiration = (expiration_date - datetime.date.today()).days
            updated_nurse = {'name': nurse['name'], 'license_issue_date': nurse['license_issue_date'], 'oid': nurse['oid'], 'days_until_expiration': days_until_expiration}
            updated_nurses.append(updated_nurse)
        except ValueError:
            updated_nurse = {'name': nurse['name'], 'license_issue_date': nurse['license_issue_date'], 'oid': nurse['oid'], 'days_until_expiration': -1}
            updated_nurses.append(updated_nurse)

    return updated_nurses

# Function to add a nurse to the database
def add_nurse():
    nurse_name = name_entry.get()
    issue_date = license_issue_date_entry.get()

    if nurse_name and issue_date:
        conn = sqlite3.connect(nurse_data_file)
        c = conn.cursor()

        c.execute("INSERT INTO nurse_data VALUES (?, ?)", (nurse_name, issue_date))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Nurse {nurse_name} has been added successfully.")
        name_entry.delete(0, tk.END)
        license_issue_date_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Missing Information", "Please provide a nurse name and the license issue date.")


# Declare nurse_list_window outside any function
nurse_list_window = None

def delete_nurse(nurses, nurse_name):
    return [nurse for nurse in nurses if nurse['name'] != nurse_name]

# Function to view nurses
def view_nurses():
    records = read_nurse_data()
    print(records)
    updated_nurses = calculate_days_until_expiration(records)

    global nurse_list_window
    # Create a new nurse_list_window or destroy the existing one
    if nurse_list_window is not None and nurse_list_window.winfo_exists():
        nurse_list_window.destroy()

    nurse_list_window = Toplevel(window)
    nurse_list_window.title("List of Nurses")

    frame = tb.Frame(nurse_list_window)
    frame.pack()

    nurse_list_window_frame = tb.LabelFrame(frame, bootstyle="primary")
    nurse_list_window_frame.grid(row=0, column=0, sticky="news", padx=10, pady=10)


    nurse_tree = tb.Treeview(nurse_list_window_frame, bootstyle="danger", columns=("ID", "Name", "License Issue Date", "Days Until Expiration"))
    nurse_tree.heading("#1", text="ID")
    nurse_tree.heading("#2", text="Name")
    nurse_tree.heading("#3", text="License Issue Date")
    nurse_tree.heading("#4", text="Status")

    # hb = tb.Scrollbar(nurse_list_window_frame, orient="horizontal")
    # hb.configure(command=nurse_tree.xview)
    # nurse_tree.configure(xscrollcommand=hb.set)
    # hb.pack(fill=X, side=BOTTOM)

    vb = tb.Scrollbar(nurse_list_window_frame, orient="vertical")
    vb.configure(command=nurse_tree.yview)
    nurse_tree.configure(yscrollcommand=vb.set)
    vb.pack(fill=Y, side=RIGHT)

    nurse_tree.pack(pady=25, padx=25)

    # Function to refresh the Treeview with the latest data
    def refresh_treeview():
        nurse_tree.delete(*nurse_tree.get_children())  # Clear existing data
        view_nurses()  # Fetch and display the latest data


    for nurse in updated_nurses:
        Id = nurse['oid']
        nurse_name = nurse['name']
        issue_date = nurse['license_issue_date']
        days_until_expiration = nurse['days_until_expiration']

        if days_until_expiration < 0:
            expiration_status = "EXPIRED"
        elif days_until_expiration > 60:
            expiration_status = "GOOD"
        else:
            expiration_status = f"{days_until_expiration} days remaining"
        nurse_tree.insert("", "end", values=(Id, nurse_name, issue_date, expiration_status))

    def delete_selected_nurse(nurse_tree, nurses):
        selected_nurse = nurse_tree.focus()
        if not selected_nurse:
            messagebox.showerror("Error", "Please select a nurse to delete from the list.")
            refresh_treeview()
            return
            

        nurse_values = nurse_tree.item(selected_nurse)['values']
        print(nurse_values)
        oid = nurse_values[0]
        nurse_name = nurse_values[1]

        response = messagebox.askyesno("Delete Nurse", f"Delete {nurse_name}?")
        if response:
            delete_nurse(nurses, nurse_name)
            nurse_tree.delete(selected_nurse)
            # calculate_days_until_expiration(nurses)
            

            conn = sqlite3.connect(nurse_data_file)
            c = conn.cursor()

        
            del_query="DELETE FROM nurse_data WHERE oid=?"
            sel_nurse=(oid,)

            print(f"Deleting nurse with OID: {oid}")

            c.execute(del_query,sel_nurse)
            conn.commit()
            conn.close()

            print("Nurse data deleted from the database")

        
            messagebox.showinfo("Success", "Nurse data has been deleted")
            refresh_treeview()

    def update_selected_nurse(nurse_tree):
        current_item = nurse_tree.focus()
        if not current_item:
            messagebox.showerror("Error", "Please select a nurse to update from the list.")
            refresh_treeview()
            return

        nurse_values = nurse_tree.item(current_item, "values")
        print(nurse_values)

        update_window = tb.Toplevel(window)
        update_window.title("Update Nurse Information")

        frame = tb.Frame(update_window)
        frame.pack()

        nurse_info_frame = tb.LabelFrame(frame, text="Nurse Information", bootstyle="primary")
        nurse_info_frame.grid(row=0, column=0, sticky="news", padx=20, pady=20)

        name_label = tb.Label(nurse_info_frame, text="Nurse Name")
        name_label.grid(row=0, column=0)
        license_issue_date_label = tb.Label(nurse_info_frame, text="License Issue Date")
        license_issue_date_label.grid(row=0, column=1)

        name_entry = tb.Entry(nurse_info_frame, bootstyle="primary")
        name_entry.grid(row=1, column=0)
        license_issue_date_entry = tb.Entry(nurse_info_frame, bootstyle="primary")
        # license_issue_date_entry.insert(0, "YYYY-MM-DD")
        license_issue_date_entry.grid(row=1, column=1)

        for widget in nurse_info_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)

        name_entry.insert(0, nurse_values[1])
        license_issue_date_entry.insert(0, nurse_values[2])

        def update_nurse():
            nurse_name = name_entry.get()
            issue_date = license_issue_date_entry.get()

            if nurse_name and issue_date:
                conn = sqlite3.connect(nurse_data_file)
                c = conn.cursor()

                # c.execute("INSERT INTO nurse_data VALUES (?, ?)", (nurse_name, issue_date))
                c.execute("UPDATE nurse_data SET name=?, license_issue_date=? WHERE oid=?", (nurse_name, issue_date, nurse_values[0]))

                conn.commit()
                conn.close()

                messagebox.showinfo("Success", f"Nurse {nurse_name}'s details have been updated successfully.")
                name_entry.delete(0, tk.END)
                license_issue_date_entry.delete(0, tk.END)
                nurse_info_frame.destroy()
            else:
                messagebox.showerror("Error", "Please fill in all fields.")

        save_button = tb.Button(nurse_info_frame, text="Save Update", bootstyle="primary", command=update_nurse)
        save_button.grid(row=2, column=0)
        cancel_button = tb.Button(nurse_info_frame, text="Cancel", bootstyle="danger", command=update_window.destroy)
        cancel_button.grid(row=2, column=1)


    # Create the Refresh button
    refresh_button = tb.Button(nurse_list_window, text="Refresh", bootstyle="primary", command=refresh_treeview)
    refresh_button.pack(pady=10)

    update_button = tb.Button(nurse_list_window, text="Update Nurse", bootstyle="warning", command=lambda: update_selected_nurse(nurse_tree))
    update_button.pack(pady=10)

    delete_button = tb.Button(nurse_list_window, text="Delete Nurse", bootstyle="danger", command=lambda: delete_selected_nurse(nurse_tree, nurses))
    delete_button.pack(pady=10)

# Function to send email notification
def send_email_notification(nurse_data, target_email, cc_emails):
    sender_email = "" # Put the email address of your preferred sender
    sender_password = "" # Update with the right password
    smtp_server = "smtp.zoho.com" # Update with your preferred SMTP server

    subject = "NURSING LICENSE LIST REMINDER"

    # Construct the email message with nurse data
    message = f"Dear , \n\nI trust you are well. Kindly note the following nurse(s) license expire soon: \n\n"
    nurse_number = 0

    for nurse in nurse_data:
        days_until_expiration = nurse.get("days_until_expiration", -1)

        if days_until_expiration in range(0, 60):
            nurse_number += 1
            message += f"{nurse_number}. {nurse['name']}'s license will expire in {days_until_expiration} days.\n"

    # Add a closing message and signature
    message += f"\nKindly send them emails for renewal before the expiry dates. Thank you\n\nKind regards,\n\nHead of Nursing."

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

# Function to handle the "Send Email Reminder" button
def email_reminder():
    emailor = tb.Window(themename="lumen")
    # emailor = tk.Tk()
    emailor.title("Send Email Reminder")
    emailor.geometry("600x200")

    frame = tb.Frame(emailor)
    frame.pack()

    email_info_frame = tb.LabelFrame(frame, text="Fill in the email details: ", bootstyle="primary")
    email_info_frame.grid(row=0, column=0, sticky="news", padx=10, pady=10)
    
    target_email_label = tk.Label(email_info_frame, text="Sending To: ")
    target_email_label.grid(row=0, column=0)
    
    cc_label = tk.Label(email_info_frame, text="CC: ")
    cc_label.grid(row=1, column=0)

    target_email_label2 = tk.Label(email_info_frame, text="", width=25)
    target_email_label2.grid(row=0, column=1)
    
    cc_entry = tk.Entry(email_info_frame, width=30)
    cc_entry.grid(row=1, column=1)
    
    send_email_button = tk.Button(email_info_frame, text="Send", command=lambda: send_email_notification_wrapper(cc_entry))
    send_email_button.grid(row=1, column=2)

    for widget in email_info_frame.winfo_children():
        widget.grid_configure(padx=20, pady=20)

# Function to send email notification wrapper
def send_email_notification_wrapper(cc_entry):
    nurses = read_nurse_data()
    updated_nurses = calculate_days_until_expiration(nurses)

    target_email = ""  # Set target email here
    cc_emails = cc_entry.get()

    if any(0 <= nurse['days_until_expiration'] < 60 for nurse in updated_nurses):
        send_email_notification(updated_nurses, target_email, cc_emails)

# Create the main application window
window = tb.Window(themename="lumen")

# window = tk.Tk()
window.title("Nurse Licens")
window.iconbitmap('images/index.ico')
window.iconbitmap(default='images/index.ico')


frame = tb.Frame(window)
frame.pack()

nurse_info_frame = tb.LabelFrame(frame, text="Nurse Information", bootstyle="primary")
nurse_info_frame.grid(row=0, column=0, padx=20, pady=20)

name_label = tb.Label(nurse_info_frame, text="Nurse Name")
name_label.grid(row=0, column=0)
license_issue_date_label = tb.Label(nurse_info_frame, text="License Issue Date")
license_issue_date_label.grid(row=0, column=1)

name_entry = tb.Entry(nurse_info_frame, bootstyle="primary")
name_entry.grid(row=1, column=0)
license_issue_date_entry = tb.Entry(nurse_info_frame, bootstyle="primary")
license_issue_date_entry.insert(0, "YYYY-MM-DD")
license_issue_date_entry.grid(row=1, column=1)

add_button = tb.Button(nurse_info_frame, text="Add Nurse", command=add_nurse)
add_button.grid(row=1, column=2)

for widget in nurse_info_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

view_nurses_frame = tb.LabelFrame(frame, bootstyle="primary")
view_nurses_frame.grid(row=1, column=0, sticky="news", padx=20, pady=20)

view_button = tb.Button(view_nurses_frame, text="View Nurses Here", bootstyle="primary", command=view_nurses)
view_button.grid(row=0, column=0, sticky="news", pady=20, padx=20)

for widget in view_nurses_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

email_button = tb.Button(frame, text="Send email reminder here", bootstyle="primary, outline", command=email_reminder)
email_button.grid(row=3, column=0, sticky="news", padx=20, pady=10)

window.mainloop()