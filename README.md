# Nurse License Tracker

The Nurse License Tracker is an application designed to track the licenses of nurses and provide timely notifications for upcoming license expirations. The purpose of the project is to streamline the process of managing nurse licenses and ensure that nurses remain compliant with licensing requirements.

## Features
- License Tracking: The application allows you to maintain a list of nurses along with their license information, including the issue date and expiration date.

- Automatic Notifications: The system automatically sends notifications to nurses as their license expiration dates approach. Notifications are sent via email or push notifications (configurable) to ensure that nurses are aware of upcoming expirations.

- Flexible Notification Schedule: The system provides flexibility in setting the notification schedule. You can configure the frequency and timing of notifications to align with your organization's requirements.

## Benefits
- Compliance: The Nurse License Tracker ensures that nurses maintain active and up-to-date licenses, promoting compliance with licensing regulations. By providing timely notifications, nurses are reminded to renew their licenses before they expire.

- Efficiency: The automated tracking and notification system saves time and effort by eliminating manual tracking and reminders. The system handles the tedious task of license management, allowing administrative staff to focus on other critical responsibilities.

- Convenience: Nurses receive notifications about upcoming license expirations, reducing the chances of missing renewal deadlines. The application keeps them informed and empowers them to take timely action to maintain their licensure.

- Accuracy: The application maintains an up-to-date record of license information, reducing the risk of human errors associated with manual tracking. This ensures that the information is accurate and reliable.

- Customization: The Nurse License Tracker provides customization options to suit your organization's needs. You can configure notification methods, schedules, and other settings to align with your specific requirements.

## Prerequisites

- Python 3.x installed on your system. You can download Python from the official website: https://www.python.org/downloads/

## Getting Started

1. Clone the repository or download the source code as a ZIP file.

2. Open a terminal or command prompt and navigate to the project directory.

3. (Optional) It's recommended to create a virtual environment to isolate the project dependencies. Run the following command to create a virtual environment:

   ```bash
   python3 -m venv env
   ```
4. Activate the virtual environment. Run the appropriate command based on your operating system:
      -For macOS/Linux:
       ```
       source env/bin/activate
       ```
       -For Windows:
       ```
       env\SCripts\activate
       ```
5. Install the project dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```
6. Set up your nurse data file in CSV format. The file should contain nurse details such as name, license issue date, and contact information. You can use the provided nurse_data.csv file as a template and modify it with your own data.
7. Configure the email or push notification settings in the code:
  - For email notifications:
    - Open the main.py file.
    - Update the sender_email, sender_password, and smtp_server variables with your email address, password, and SMTP server details.
  - For push notifications:
      - Open the main.py file.
      - Replace your_fcm_server_key with your actual FCM server key. You can obtain the server key from your Firebase project settings.
      - Update the notification details in the send_push_notification function, such as the notification title, body, icon, and click action.
8. Run the application by executing the following command in the terminal:
    ```
    python main.py
    ```
    The application will start tracking the licenses, checking for upcoming expirations, and sending notifications based on your configuration.
9. Keep the application running to ensure continuous license tracking and notifications. You can stop the application by pressing Ctrl + C in the terminal.
