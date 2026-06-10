import socket
import sqlite3
import os
import sys


HOST = "0.0.0.0"
PORT = 8000
DB = "users.db"


"""
    
    
    Demonstration of a command line authentication mechanism

    User connects -> enters name and password -> gets let in and sees information about their account
    

    Application < - > Database
        Users Table: 
            user_id
            username
            first name
            last name
            email
            age 

        Passwords Table
            password_id
            user_id ------------------> Users.user_id
            password

"""


def create_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    fname TEXT NOT NULL,
                    lname TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    age INTEGER
                );
            """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS passwords (
                    password_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    password TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            """)
    except sqlite3.Error as error:
        print("An error occurred: ", error)
    
    finally:
        conn.close()


def seed_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        users = [
            ("jdoe", "John", "Doe", "jdoe@example.com", 25),
            ("asmith", "Alice", "Smith", "asmith@example.com", 30),
            ("bwilson", "Bob", "Wilson", "bwilson@example.com", 22),
            ("cjones", "Carol", "Jones", "cjones@example.com", 28),
            ("dlee", "David", "Lee", "dlee@example.com", 35)
        ]

        cursor.executemany("""
            INSERT INTO users (
                username,
                fname,
                lname,
                email,
                age
            ) VALUES (?, ?, ?, ?, ?)
        """, users)

        passwords = [
            (1, "password123"),
            (2, "qwerty456"),
            (3, "hunter2"),
            (4, "letmein"),
            (5, "secretpass")
        ]

        cursor.executemany("""
            INSERT INTO passwords (
                user_id,
                password
            ) VALUES (?, ?)
        """, passwords)

        conn.commit()

    except sqlite3.Error as error:
        print("An error occurred:", error)

    finally:
        conn.close()


def login(username, password):
    # first get the user from the users table
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    results = cursor.fetchall()[0]

    if results is None:
        conn.close()
        return False
    if results: # user exists, now need to get the password
        user_id = results[0]
        cursor.execute("SELECT password FROM passwords WHERE user_id = ?", (user_id,))
        db_password = cursor.fetchone()[0]
        # print(db_password)

        conn.close()
        
        if password == db_password:
            print("Correct login, letting you in")
            return True
        else:
            print("Incorrect login, get out")
            return False
        

def get_user(username):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_info = cursor.fetchall()[0]

        if user_info is None:
            return None

        return user_info
    
    except sqlite3.Error as error:
        print("An error occurred:", error)

    finally:
        conn.close()



def main():
    create_db()
    print("DB created")
    seed_db()
    print("Users created")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            print("Authentication Demonstration Running")

            conn, addr = s.accept()

            with conn:
                print(f"Connection from {addr}")

                conn.sendall(b"Username: ")
                username = conn.recv(1024).decode().strip()
                
                conn.sendall(b"Password: ")
                password = conn.recv(1024).decode().strip()

                if login(username, password):
                    user_info = get_user(username)

                    response = f"""
                        User ID: {user_info[0]}
                        Username: {user_info[1]}
                        First Name: {user_info[2]}
                        Last Name: {user_info[3]}
                        Email: {user_info[4]}
                        Age: {user_info[5]}
                    """

                    conn.sendall(response.encode())
                else:
                    conn.sendall(b"Login failed.\n")
    except KeyboardInterrupt:

    # Adding authentication mechanisms here
        print("Deleting users and database now")
        
        if os.path.exists(DB):
            os.remove(DB)
            print("Database deleted")
        else:
            print("Database already deleted")
        
        sys.exit(0)


if __name__=="__main__":
    main()