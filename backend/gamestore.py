import mysql.connector
from datetime import datetime

# Connect to MySQL database
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",  # Change this to your MySQL username
    password="mysqlbang777",  # Change this to your MySQL password
    database="game_store"
)
cursor = db.cursor()

# Function to login users or admins
def login(email, password, role):
    table = "users" if role == "user" else "admins"
    
    query = f"SELECT * FROM {table} WHERE email = %s AND password = %s"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    
    if user:
        print(f"\nLogin successful as {role}!")
        if role == "user":
            user_menu(user[1], user[2])  # Pass user name & email
        else:
            admin_menu()
    else:
        print("\nInvalid email or password. Please try again.")

# Function for users to view all games
def view_games():
    print("\nAvailable Games:\n")
    cursor.execute("SELECT id, name, price, category, year FROM games_list")
    games = cursor.fetchall()
    
    if games:
        for game in games:
            print(f"ID: {game[0]}, Name: {game[1]}, Price: ₹{game[2]}, Category: {game[3]}, Year: {game[4]}")
    else:
        print("No games found.")

# Function for users to buy games
def buy_game(user_name, email):
    view_games()
    game_ids = input("\nEnter Game IDs to buy (comma-separated): ").split(",")
    
    for game_id in game_ids:
        game_id = game_id.strip()

        # Check if game exists
        cursor.execute("SELECT name, price FROM games_list WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        if not game:
            print(f"\nGame ID {game_id} not found!")
            continue

        game_name, price = game

        # Check if user already owns the game
        cursor.execute("SELECT * FROM transactions WHERE email = %s AND game_id = %s", (email, game_id))
        existing = cursor.fetchone()
        if existing:
            print(f"\nYou already own '{game_name}'.")
            continue
        
        # Record the purchase in transactions table
        purchase_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO transactions (user_name, game_id, game_name, email, purchase_date) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (user_name, game_id, game_name, email, purchase_date))
        db.commit()

        print(f"\nSuccessfully purchased '{game_name}' for ₹{price}!")

# Function for users to view their purchased games
def my_library(user_name, email):
    print("\nYour Purchased Games:\n")
    cursor.execute("SELECT game_id, game_name, purchase_date FROM transactions WHERE email = %s", (email,))
    games = cursor.fetchall()
    
    if games:
        for game in games:
            print(f"Game ID: {game[0]}, Name: {game[1]}, Purchased on: {game[2]}")
    else:
        print("You haven't purchased any games yet!")

# Function for admins to add a game
def add_game():
    name = input("Enter game name: ")
    price = float(input("Enter price in INR: "))
    category = input("Enter category (comma-separated): ")
    year = int(input("Enter release year: "))

    query = "INSERT INTO games_list (name, price, category, year) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, price, category, year))
    db.commit()
    
    print(f"\nGame '{name}' added successfully!")

# Function for admins to remove a game
def remove_game():
    game_id = input("Enter Game ID to remove: ")
    query = "DELETE FROM games_list WHERE id = %s"
    
    cursor.execute(query, (game_id,))
    db.commit()
    
    print("\nGame removed successfully!")

# Function for admins to view all transactions
def view_transactions():
    print("\nTransactions:\n")
    cursor.execute("SELECT id, user_name, game_id, game_name, email, purchase_date FROM transactions")
    transactions = cursor.fetchall()
    
    if transactions:
        for txn in transactions:
            print(f"Transaction ID: {txn[0]}, User: {txn[1]}, Game ID: {txn[2]}, Game: {txn[3]}, Email: {txn[4]}, Date: {txn[5]}")
    else:
        print("No transactions found.")

# Admin menu with new option for viewing transactions
def admin_menu():
    while True:
        print("\nAdmin Panel")
        print("1. View Games")
        print("2. Add Game")
        print("3. Remove Game")
        print("4. View Transactions")
        print("5. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            view_games()
        elif choice == "2":
            add_game()
        elif choice == "3":
            remove_game()
        elif choice == "4":
            view_transactions()
        elif choice == "5":
            print("Logging out...")
            break
        else:
            print("Invalid choice! Try again.")

# User menu
def user_menu(user_name, email):
    while True:
        print("\nUser Panel")
        print("1. View Games")
        print("2. Buy Games")
        print("3. My Library")
        print("4. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            view_games()
        elif choice == "2":
            buy_game(user_name, email)
        elif choice == "3":
            my_library(user_name, email)
        elif choice == "4":
            print("Logging out...")
            break
        else:
            print("Invalid choice! Try again.")

# Main login interface
if __name__ == "__main__":
    role = input("Login as (user/admin): ").strip().lower()
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()

    login(email, password, role)

db.close()
