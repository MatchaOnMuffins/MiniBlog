import sqlite3
import hashlib
import traceback
import datetime

# Create table users if it doesn't exist
query = '''
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT)'''

# Create table posts if it doesn't exist
posts = '''
CREATE TABLE IF NOT EXISTS posts(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT, 
 content TEXT, 
author_id,
FOREIGN KEY(author_id) REFERENCES users(id)
) '''

# Create table comments if it doesn't exist
comments = '''
CREATE TABLE IF NOT EXISTS comments(
id INTEGER PRIMARY KEY AUTOINCREMENT,
post_id INTEGER,
author_id INTEGER,
content TEXT,
FOREIGN KEY(post_id) REFERENCES posts(id),
FOREIGN KEY(author_id) REFERENCES users(id)
)'''

# Initialize connection to database and create table if they don't exist
con = sqlite3.connect('users.db')
cur = con.cursor()
cur.execute(posts)
cur.execute(query)
cur.execute(comments)
con.commit()

# Login status
login_status = False

# Currently logged-in user
login_user = ''

# Currently logged-in user id
login_user_id = 0


# Register a new user

def register():
    print('Please enter a username:')
    username = input()
    # Check if username already exists
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cur.fetchone()
    if user:
        print('Username already exists. Please try again.\n')
        register()
    if username == '':
        print('Username cannot be empty. Please try again.')
        register()
    elif len(username) > 20:
        print('Username cannot be longer than 20 characters. Please try again.')
        register()
    # check if password matches
    while True:
        password = input('Please enter a password:')
        password_again = input('Please enter the password again:')
        if password == password_again:
            break
        else:
            print('Passwords do not match. Please try again.')
            continue

    return username, password


# Saves new user to database


def save_user():
    username, password = register()
    # Calculate password hash
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    # Insert new user into database
    cur.execute("INSERT INTO users(username, password) VALUES(?, ?)", (username, password_hash))
    con.commit()
    print('You have successfully registered!')


def login():
    # Declare global variables
    global login_status
    global login_user
    global login_user_id
    print('Please enter your username:')
    username = input()
    print('Please enter your password:')
    password = input()

    # Calculate password hash

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Check if username and password match
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password_hash))
    user = cur.fetchone()
    # print(user)
    if user:
        print('You have successfully logged in!')
        print("==========================================================")
        login_status = True
        login_user = username
        login_user_id = user[0]

    else:
        print('Wrong username or password. Please try again.')
        print("==========================================================")


def main():
    # declare global variables
    global login_status
    global login_user
    global login_user_id
    print('Welcome to the blogging system!')
    print('Please select an option:')
    print('1. Register')
    print('2. Login')
    print('3. Exit')
    print('4. View all posts')
    # if user is logged in, show the following options
    if login_status:
        print('5. View profile')
        print('6. Write a post')
        print('7. Logout')
        print('8. Change password')

    # Prompt user to select an option
    print('Please enter your choice:')
    choice = input()
    if choice == '1':
        # Register a new user
        if login_status:
            # if user is logged in, cannot register again
            print('You are already logged in. Please logout first.')
            main()
        else:
            # if user is not logged in, register a new user
            save_user()
            main()
    elif choice == '2':
        # Login
        if login_status:
            # if user is logged in, cannot login again
            print('You are already logged in!')
            main()
        else:
            # if user is not logged in, login
            login()
            if login_status:
                print("Logged in as: ", login_user)
                print("==========================================================")
            main()
    elif choice == '3':
        # Exit
        print('Goodbye!')
        exit()
    elif choice == '4':
        # View all posts
        view_posts()
    elif choice == '5':
        # list all posts and comments of the user
        if login_status:
            # if user is logged in, list all posts and comments of the user
            cur.execute("SELECT * FROM posts WHERE author_id=?", (login_user_id,))
            posts_from_db = cur.fetchall()
            print("==========================================================")
            print("Posts:")
            print("==========================================================")
            for post in posts_from_db:
                print("Title:", post[1][0:100])
                print("Content: ", post[2][:200])
                print("=====================")
            print("==========================================================")
            print('Comments:')
            print("==========================================================")
            cur.execute("SELECT * FROM comments WHERE author_id=?", (login_user_id,))
            comments_from_db = cur.fetchall()
            for comment in comments_from_db:
                post = cur.execute("SELECT * FROM posts WHERE id=?", (comment[1],)).fetchone()
                print("Content:", comment[3][0:100])
                print('Comment on post:', post[1])
                print("=====================")
            print("==========================================================")
            # Ask user if they want to delete a post or a comment
            print('Would you like to delete a post or comment? (y/n)')
            choice = input()
            if choice == 'y':
                print('what would you like to delete?')
                print('1. Post')
                print('2. Comment')
                print('3. Cancel')
                choice = input('Choose an option:')
                if choice == '1':
                    # delete a post
                    print("==========================================================")
                    print('Which post would you like to delete?')
                    print("==========================================================")
                    # list all posts of the user
                    cur.execute("SELECT * FROM posts WHERE author_id=?", (login_user_id,))
                    posts_from_db = cur.fetchall()
                    for post in posts_from_db:
                        print("ID:", post[0])
                        print("=========")
                        print("Title:", post[1][0:100])
                        print("==========================================================")
                    choice = input('Enter the ID of the post you would like to delete:')
                    try:
                        # delete the post if it exists
                        cur.execute("SELECT * FROM posts WHERE id=?", (choice,))
                        post = cur.fetchone()
                        if post:
                            cur.execute("DELETE FROM comments WHERE post_id=?", (choice,))
                            cur.execute("DELETE FROM posts WHERE id=? AND author_id=?", (choice, login_user_id))
                            con.commit()
                            print("==========================================================")
                            print('Post deleted!')
                            print("==========================================================")
                        else:
                            # if post does not exist, print error message
                            print("==========================================================")
                            print('Post not found!')
                            print("==========================================================")
                    except sqlite3.Error as e:
                        print(e)
                        print("==========================================================")
                        print('Error deleting post.')
                        print("==========================================================")
                    main()
                elif choice == '2':
                    # Delete a comment
                    print("==========================================================")
                    print('Which comment would you like to delete?')
                    print("==========================================================")
                    # list all comments of the user
                    cur.execute("SELECT * FROM comments WHERE author_id=?", (login_user_id,))
                    comments_from_db = cur.fetchall()
                    for comment in comments_from_db:
                        post = cur.execute("SELECT * FROM posts WHERE id=?", (comment[1],)).fetchone()
                        print("ID:", comment[0])
                        print("Content:", comment[3][0:100])
                        print('Comment on post:', post[1])
                        print("==========================================================")
                    choice = input('Enter the ID of the comment you would like to delete:')
                    try:
                        # delete the comment if it exists
                        cur.execute("SELECT * FROM comments WHERE id=?", (choice,))
                        if cur.fetchone():
                            cur.execute("DELETE FROM comments WHERE id=?", (choice,))
                            con.commit()
                            print("==========================================================")
                            print('Comment deleted!')
                            print("==========================================================")
                        else:
                            # if comment does not exist, print error message
                            print("==========================================================")
                            print('Comment does not exist.')
                            print("==========================================================")
                    except sqlite3.Error as e:
                        print(e)
                        print('Error deleting comment.')
                    main()
                elif choice == '3':
                    # Cancel
                    main()
                else:
                    # if user enters an invalid option, print error message
                    print('Invalid option. Please try again.')
                    main()
                main()

            main()
        else:
            # if user not logged in, print error message
            print("==========================================================")
            print('You must be logged in to view your profile.')
            print("==========================================================")
            main()
    elif choice == '6':
        # Write a post
        if login_status:
            # if user is logged in, ask user for post title and content
            print("====================Write A Blog=========================")
            print('Please enter a title:')
            title = input()
            print("==========================================================")
            print('Please enter the content:')
            content = input()
            print("==========================================================")
            # insert the post into the database
            cur.execute("INSERT INTO posts(title, content, author_id) VALUES(?, ?, ?)", (title, content, login_user_id))
            con.commit()

            print('Post successfully created!')
            print("==========================================================")
            main()
        else:
            # if user not logged in, print error message
            print("==========================================================")
            print('You must be logged in to write a post.')
            print("==========================================================")
            main()
    elif choice == '7':
        # Log out
        if login_status:
            # if user is logged in, log out
            print("==========================================================")
            print('You have successfully logged out.')
            print("==========================================================")
            # set login_status to False
            login_status = False

            # set current logged-in user to None
            login_user = ''
            # set current logged-in user ID to 0
            login_user_id = 0
            main()
        else:
            # if user not logged in, print error message
            print("==========================================================")
            print('You are not logged in.')
            print("==========================================================")
            main()
    elif choice == '8':
        # change password
        if login_status:
            # if user is logged in, ask user for old password and new password
            print("==========================================================")
            current_password = input('Please enter your current password:')
            # check if current password is correct
            cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                        (login_user, hashlib.sha256(current_password.encode()).hexdigest()))
            user = cur.fetchone()
            if user:
                new_password = input('Please enter your new password:')
                new_password_again = input('Please enter your new password again:')
                # if new password and new password again are the same, update the password in the database
                if new_password == new_password_again:
                    cur.execute("UPDATE users SET password=? WHERE username=?",
                                (hashlib.sha256(new_password.encode()).hexdigest(), login_user))
                    con.commit()
                    print("==========================================================")
                    print('Password successfully changed!\n')
                    print("==========================================================")
                    main()
                else:
                    # if new password and new password again are not the same, print error message
                    print("==========================================================")
                    print('Passwords do not match. Please try again.')
                    print("==========================================================")
                    main()
            else:
                # if current password is incorrect, print error message
                print("==========================================================")
                print('Wrong password. Please try again.')
                print("==========================================================")
                main()
        else:
            # if user not logged in, print error message
            print("==========================================================")
            print('You must be logged in to change your password.')
            print("==========================================================")
            main()
    else:
        # if user enters an invalid option, print error message
        print('Invalid choice. Please try again.')
        main()


def view_posts():
    # view all posts
    # 查看所有文章
    cur.execute("SELECT * FROM posts")
    posts_from_db = cur.fetchall()
    for post in posts_from_db:
        print("==========================================================")
        print("Post ID: ", post[0])
        print("=================")
        print("Title: ", post[1])
        cur.execute("SELECT * FROM users WHERE id=?", (post[3],))
        author_short = cur.fetchone()
        print("Author: ", author_short[1])
        print("Content: ", post[2][:200])
        print("==========================================================")

    # ask user if they want to view a specific post
    print("Do you want to see a post's details? (y/n)")
    choice = input()
    if choice == 'y':
        # if user wants to view a specific post, ask user for post ID
        print("Please enter the post ID:")
        post_id = input()
        try:
            # select a post with the given post ID
            cur.execute("SELECT * FROM posts WHERE id=?", (post_id,))
            post = cur.fetchone()
            print("==========================================================")
            print("Title: ", post[1])
            # get author's name from database using author ID
            cur.execute("SELECT * FROM users WHERE id=?", (post[3],))
            author_detail = cur.fetchone()
            print("Author: ", author_detail[1])
            print("======================")
            print("Content: ", post[2])
            # get comments from database using post ID
            cur.execute("SELECT * FROM comments WHERE post_id=?", (post_id,))
            comments_from_db = cur.fetchall()
            print()
            print("==========================================================")
            print("Comments:\n")
            for comment in comments_from_db:
                cur.execute("SELECT * FROM users WHERE id=?", (comment[2],))
                author = cur.fetchone()
                print("Author: ", author[1])
                print("Content: ", comment[3])
                print("==========================")
        except TypeError:
            # if post ID is invalid, print error message (TypeError indicates that the given post ID is not a valid id)
            print("==========================================================")
            print("Invalid post ID.")
            print("==========================================================")
            view_posts()
        except Exception as e:
            # Catch all other exceptions
            print("==========================================================")
            print(e)
            print('Error fetching posts.')
            print("==========================================================")
        if login_status:
            # if user is logged in, ask user if they want to comment on the post
            print("Do you want to comment on this post? (y/n)")
            choice = input()
            if choice == 'y':
                # if user wants to comment on the post, ask user for comment content
                print("Please enter your comment:")
                comment = input()
                try:
                    # insert comment into database
                    cur.execute("INSERT INTO comments(post_id, author_id, content) VALUES(?, ?, ?)",
                                (post_id, login_user_id, comment))
                    con.commit()
                    print("Comment successfully created!")
                    print("==========================================================")
                except sqlite3.Error as e:
                    # Catch all other sqlite3 exceptions
                    print("==========================================================")
                    print(e)
                    print('Error commenting on post.')
                    print("==========================================================")
                    view_posts()
                main()
            else:
                main()
        # Ask user if they want to view another post
        print("==========================================================")
        print("would you like to view another post? (y/n)")
        print("==========================================================")
        choice = input()
        if choice == 'y':
            # if user wants to view another post, call view_posts function again
            view_posts()
        else:
            # if user does not want to view another post, return to main menu
            main()
    elif choice == 'n':
        # if user does not want to view a specific post, return to main menu
        main()
    else:
        # if user enters invalid input, print error message and return to main menu
        print("==========================================================")
        print('Invalid choice. Please try again.')
        print("==========================================================")
        view_posts()
    main()


# sketchy method to stop program from throwing errors and closing
def anti_crash_main():
    try:
        # call main function
        main()
    except KeyboardInterrupt:
        # if user hits ctrl+c, print farewell message and exit program
        print("==========================================================")
        print('Goodbye!')
        con.close()
        exit()
    except Exception as e:
        # catch all other exceptions
        print(e)
        print('Error.')
        # log errors to a log file
        with open("exceptions.log", "a") as log:
            log.write("%s: Exception occurred:\n" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            traceback.print_exc(file=log)
        # restart program
        anti_crash_main()


if __name__ == "__main__":
    # call wrapper function to stop program from throwing errors and closing
    anti_crash_main()
