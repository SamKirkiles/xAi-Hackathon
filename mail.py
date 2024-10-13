import schedule
import sqlite3
import time
from datetime import datetime, timedelta
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import decode_header
import grok

conn = sqlite3.connect('your_database.db')
cursor = conn.cursor()
#conn.close()

def create_db():
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS users (
        userID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        x_username TEXT
    )
    '''
    cursor.execute(create_table_sql)
    conn.commit()

def create_db_feedback():
    create_feedback_sql = '''
    CREATE TABLE IF NOT EXISTS user_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        feedback TEXT,
        feedback_date DATE NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(userID),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    '''
    cursor.execute(create_feedback_sql)
    conn.commit()

def create_db_products():
    create_products_sql = '''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        quality_rating INTEGER CHECK (quality_rating BETWEEN 0 AND 10),
        subjective_rating TEXT
    )
    '''
    cursor.execute(create_products_sql)
    conn.commit()

def add_user(full_name, email, x_username):
    user_data = (full_name, email, x_username)
    insert_user_sql = '''
    INSERT INTO users (name, email, x_username)
    VALUES (?, ?, ?)
    '''
    cursor.execute(insert_user_sql, user_data)
    conn.commit()

def add_product(product_id, product_name, quality_rating, subjective_rating):
    insert_product_sql = '''
    INSERT OR REPLACE INTO products (product_id, product_name, quality_rating, subjective_rating)
    VALUES (?, ?, ?, ?)
    '''
    cursor.execute(insert_product_sql, (product_id, product_name, quality_rating, subjective_rating))
    conn.commit()

def add_feedback(user_id, product_id, feedback, feedback_date):
    insert_feedback_sql = '''
    INSERT INTO user_feedback (user_id, product_id, feedback, feedback_date)
    VALUES (?, ?, ?, ?)
    '''
    cursor.execute(insert_feedback_sql, (user_id, product_id, feedback, feedback_date))
    conn.commit()

def get_users():
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def get_products():
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def get_feedback():
    cursor.execute("SELECT * FROM user_feedback")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def send_email(sender_email, sender_password, receiver_email, subject, body):
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email
    body_text = MIMEText(body, 'plain')
    message.attach(body_text)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                return body
    else:
        return msg.get_payload(decode=True).decode()
    
def unread_emails():
    imap_server = 'imap.gmail.com'
    email_address = "versonium@gmail.com"
    #delete this after!!!!!!!!!!!!!!!!!!!
    password = ""
    mail = imaplib.IMAP4_SSL(imap_server)
    try:
        mail.login(email_address, password)
        mail.select('inbox')
        _, message_numbers = mail.search(None, 'UNSEEN')
        if message_numbers[0]:
            for num in message_numbers[0].split():
                resp, msg = mail.fetch(num, '(RFC822)')
                for response in msg:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        subject, encoding = decode_header(msg['Subject'])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or 'utf-8')
                        from_, encoding = decode_header(msg.get('From', ''))[0]
                        if isinstance(from_, bytes):
                            from_ = from_.decode(encoding or 'utf-8')
                        
                        body = get_email_body(msg)

                        add_review(body)

                        start_ = "Here is the customer response you received. Either create a response message or if you think that the conversation should finish reply to me with the word done"
                        message_to_grok = "{}: Subject: {} From: {} Body: {}. Whatever you respond with, will be sent so don't include stuff like [Your Name]".format(start_, subject, from_, body)
                        grok_response = grok.send_grok_message(message_to_grok)
                        if grok_response != "done":
                            send_email(email_address, password, from_, subject, grok_response)
        else:
            print("No unread emails found.")
        pass
    finally:
        mail.logout()

def add_review(body):
    message_to_grok = "Based on this customer response: {}. Give me these fields user_id, product_id, feedback, feedback_date in that order separated by commas".format(body)
    grok_response = grok.send_grok_message(message_to_grok)
    inputs = grok_response.split(',')
    print("inputs: {}".format(inputs))
    add_feedback(inputs[0], inputs[1], inputs[2], inputs[3])
    get_feedback()

def monthly_email():
    sender_email = "versonium@gmail.com"
    sender_password = ""
    subject = "Your Experience With Our Products"
    cursor.execute("SELECT userID, name, email FROM users")
    users = cursor.fetchall()
    for user in users:
        user_id, customer_full_name, receiver_email = user
        if receiver_email == "maxbrsk77@gmail.com":
            body = f'''Hi {customer_full_name},
            We're always looking to improve our products and services. 
            Could you share your thoughts on the products you've bought from us? 
            What has been going well and what can we improve on?
            Your feedback helps us serve you better. Thanks for your time!'''
            try:
                send_email(sender_email, sender_password, receiver_email, subject, body)
                print(f"Email sent to {receiver_email}")
            except Exception as e:
                print(f"Failed to send email to {receiver_email}: {e}")

def check_if_12th():
    print(datetime.now().day)
    if datetime.now().day == 12:
        monthly_email()

def print_current_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"Current time: {current_time}")

def schedule_jobs():
    '''
    create_db()
    create_db_feedback()
    create_db_products()
    add_user("Alan B", "maxbrsk77@gmail.com", "alan45")
    add_user("Alex Josh", "ajosh@gmail.com", "alex_josh_1989")
    add_user("Noah Klein", "noah_klein@example.com", "noah_k_1992")
    add_user("Isabella Lopez", "isabella_lopez@email.com", "isabel_l_1987")
    add_user("Ethan Young", "ethan_young@company.com", "ethan_y_1978")
    add_user("Sophia Reed", "sophia_reed@mail.com", "sophia_r_1995")
    add_user("Lucas Brown", "lucas_brown@domain.com", "lucas_b_1985")
    add_user("Ava Green", "ava_green@service.com", "ava_g_1990")
    add_user("Liam Carter", "liam_carter@site.com", "liam_c_1980")
    add_user("Mia White", "mia_white@web.com", "mia_w_1993")
    add_user("James Turner", "james_turner@network.com", "james_t_1976")
    add_user("Ella Harris", "ella_harris@mail.net", "ella_h_1988")
    add_user("Oliver Scott", "oliver_scott@corp.com", "oliver_s_1982")
    add_user("Grace Lee", "grace_lee@domain.org", "grace_l_1991")
    add_product(1, "headphones", 7.8, "This product is usually breaking after 2 months of use. Other users are happy with the long lasting battery life.")
    add_product(2, "smartwatch", 8.5, "The fitness tracking is top-notch, but some users report issues with the touch screen responsiveness.")
    add_product(3, "laptop", 9.2, "High performance and excellent battery life, though it's quite heavy for a portable device.")
    add_product(4, "bluetooth speaker", 7.0, "Great sound quality for its size, but the Bluetooth connection can be finicky at times.")
    add_product(5, "e-reader", 8.8, "Perfect for avid readers with a long battery life, but the screen can glare in bright sunlight.")
    '''

    #schedule.every().month.on(12).at("00:00").do(monthly_email)
    #schedule.every().day.at("16:42").do(check_if_12th)
    schedule.every().minute.at(":00").do(unread_emails)
    schedule.every().minute.at(":00").do(check_if_12th)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_jobs()
