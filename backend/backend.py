import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import mysql.connector
from datetime import datetime

app = FastAPI()

# Serve static files from /statics directory
app.mount("/statics", StaticFiles(directory="statics"), name="statics")

# Templates configuration: HTML templates are served from the "templates" directory.
templates = Jinja2Templates(directory="templates")

# Database Dependency Injection
def get_db():
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    try:
        yield db
    finally:
        db.close()

# ----- MODELS -----

# Login Request Model
class LoginRequest(BaseModel):
    email: str
    password: str
    role: str  # "user" or "admin"

# Pydantic models for order payload.
class GameTransaction(BaseModel):
    game_id: int
    game_name: str
    price: float

class Order(BaseModel):
    user_name: str
    email: str
    games: List[GameTransaction]

# Pydantic Models (Updated to include image_path and admin_id)
class GameBase(BaseModel):
    name: str
    price: float
    category: List[str]  # Accept list for multiple categories
    year: int
    image_path: str = ""
    admin_id: str = ""

# For updates, we no longer require an "id" in the JSON payload.
class GameUpdate(GameBase):
    pass

# ----- ROUTES FOR TEMPLATES -----

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Serves the login page
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register.html", response_class=HTMLResponse)
async def show_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/index.html", response_class=HTMLResponse)
async def show_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/store.html", response_class=HTMLResponse)
async def store(request: Request):
    return templates.TemplateResponse("store.html", {"request": request})

@app.get("/cart.html", response_class=HTMLResponse)
async def cart(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request})

@app.get("/payment.html", response_class=HTMLResponse)
async def show_payment_page(request: Request):
    return templates.TemplateResponse("payment.html", {"request": request})

@app.get("/order-confirmation.html", response_class=HTMLResponse)
async def show_order_confirmation(request: Request):
    return templates.TemplateResponse("order-confirmation.html", {"request": request})

@app.get("/admin.html", response_class=HTMLResponse)
async def show_admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

# New: Profile Page Endpoint
@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

# ----- API ENDPOINTS -----

# API Endpoint: Fetch Current User Profile Information
@app.get("/api/profile")
def get_profile(email: str, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, username, email, phone FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    cursor.close()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

# API Endpoint: Update Current User Profile Information
class ProfileUpdateRequest(BaseModel):
    current_email: str
    username: str
    email: str
    phone: str = None

@app.put("/api/profile")
def update_profile(profile: ProfileUpdateRequest, db=Depends(get_db)):
    cursor = db.cursor()
    query = "UPDATE users SET username = %s, email = %s, phone = %s WHERE email = %s"
    try:
        cursor.execute(query, (profile.username, profile.email, profile.phone, profile.current_email))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        db.commit()
        return {"message": "Profile updated successfully"}
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()

# Login API
@app.post("/login")
async def login(data: LoginRequest, db=Depends(get_db)):
    if data.role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    table = "users" if data.role == "user" else "admins"
    query = f"SELECT username, email FROM {table} WHERE email = %s AND password = %s"
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, (data.email, data.password))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return {
            "message": "Login successful",
            "role": data.role,
            "email": user["email"],
            "username": user["username"],
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Fetch All Games
@app.get("/games")
def get_games(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM games_list")
    games = cursor.fetchall()
    cursor.close()
    return {"games": games}

# Fetch Games by Category
@app.get("/games/{category}")
def get_games_by_category(category: str, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM games_list WHERE LOWER(category) LIKE %s"
    cursor.execute(query, (f"%{category.lower()}%",))
    games = cursor.fetchall()
    cursor.close()
    return {"games": games}

# Fetch All Users (for Users & Admins page)
@app.get("/users")
def get_users(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    cursor.close()
    return {"users": users}

# Fetch All Admins (for Users & Admins page)
@app.get("/admins")
def get_admins(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT username FROM admins")
    admins = cursor.fetchall()
    cursor.close()
    return {"admins": admins}

# Fetch All Transactions (for Users)
@app.get("/api/transactions")
def get_transactions(username: str = "", db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    if username:
        query = "SELECT * FROM transactions WHERE user_name = %s ORDER BY purchase_date DESC"
        cursor.execute(query, (username,))
    else:
        query = "SELECT * FROM transactions ORDER BY purchase_date DESC"
        cursor.execute(query)
    transactions = cursor.fetchall()
    cursor.close()
    return {"transactions": transactions}

# API Endpoint: Fetch Admin's Transactions (for Admin Dashboard)
@app.get("/api/admin_transactions")
def get_admin_transactions(admin_id: str, username: str = "", db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    if username:
        query = """
            SELECT t.* FROM transactions t
            JOIN games_list g ON t.game_id = g.id
            WHERE g.admin_id = %s AND t.user_name = %s
            ORDER BY t.purchase_date DESC
        """
        cursor.execute(query, (admin_id, username))
    else:
        query = """
            SELECT t.* FROM transactions t
            JOIN games_list g ON t.game_id = g.id
            WHERE g.admin_id = %s
            ORDER BY t.purchase_date DESC
        """
        cursor.execute(query, (admin_id,))
    transactions = cursor.fetchall()
    cursor.close()
    return {"transactions": transactions}

# Helper function: Insert Order Directly into Transactions Table with admin_id
def insert_transaction(order: Order, db):
    try:
        cursor = db.cursor()
        fetch_admin_query = "SELECT admin_id FROM games_list WHERE id = %s"
        transaction_query = """
            INSERT INTO transactions (user_name, game_id, game_name, email, purchase_date, price, admin_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        for game in order.games:
            cursor.execute(fetch_admin_query, (game.game_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail=f"Game with ID {game.game_id} not found")
            admin_id = result[0]
            cursor.execute(
                transaction_query,
                (
                    order.user_name,
                    game.game_id,
                    game.game_name,
                    order.email,
                    datetime.now(),
                    game.price,
                    admin_id
                )
            )
        db.commit()
        cursor.close()
    except mysql.connector.Error as e:
        db.rollback()
        print("Database error:", e)
        raise HTTPException(status_code=500, detail="Database insertion error")

# Payment API (Saves Directly to Transactions Table)
@app.post("/api/transactions")
async def create_transaction(order: Order, db=Depends(get_db)):
    insert_transaction(order, db)
    return JSONResponse(content={"message": "Transaction recorded successfully!"}, status_code=201)

# Registration Request Model for Users
class RegisterRequest(BaseModel):
    username: str
    phone: str
    email: str
    password: str

# Registration API Endpoint with Proper Transaction Handling for Users
@app.post("/register")
async def register_user(data: RegisterRequest, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        db.start_transaction()
        cursor.execute(
            "INSERT INTO users (username, phone, email, password) VALUES (%s, %s, %s, %s)",
            (data.username, data.phone, data.email, data.password)
        )
        db.commit()
        return {"message": "Account created successfully!"}
    except mysql.connector.Error as err:
        db.rollback()
        if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
            error_message = str(err)
            if "username" in error_message:
                detail = "Username already exists. Please choose a different one."
            elif "email" in error_message:
                detail = "Email is already registered. Try logging in or use another email."
            elif "phone" in error_message:
                detail = "Phone number is already registered. Use a different number."
            else:
                detail = "A user with the provided details already exists."
            raise HTTPException(status_code=400, detail=detail)
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()

# Admin Registration Request Model
class RegisterAdminRequest(BaseModel):
    username: str
    email: str
    password: str

# Admin Registration API Endpoint
@app.post("/register_admin")
async def register_admin(data: RegisterAdminRequest, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        db.start_transaction()
        cursor.execute(
            "INSERT INTO admins (username, email, password) VALUES (%s, %s, %s)",
            (data.username, data.email, data.password)
        )
        db.commit()
        return {"message": "Admin account created successfully!"}
    except mysql.connector.Error as err:
        db.rollback()
        if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
            error_message = str(err)
            if "username" in error_message:
                detail = "Username already exists. Please choose a different one."
            elif "email" in error_message:
                detail = "Email is already registered. Try logging in or use another email."
            else:
                detail = "An admin with the provided details already exists."
            raise HTTPException(status_code=400, detail=detail)
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()

# Fetch User Library (for My Library page)
@app.get("/api/user-library")
def get_user_library(email: str, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT g.name AS game_name, g.image_path AS game_image_path
        FROM transactions t 
        JOIN games_list g ON t.game_id = g.id 
        WHERE t.email = %s
    """
    cursor.execute(query, (email,))
    library = cursor.fetchall()
    cursor.close()
    return {"library": library}

# Add a New Game (Updated to include image_path and admin_id)
@app.post("/games")
def add_game(game: GameBase, db=Depends(get_db)):
    cursor = db.cursor()
    category_str = ",".join(game.category)
    try:
        query = "INSERT INTO games_list (name, price, category, year, image_path, admin_id) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (game.name, game.price, category_str, game.year, game.image_path, game.admin_id))
        db.commit()
        return {"message": "Game added successfully!"}
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()

# Update Game Details (Updated to include image_path and admin_id)
@app.put("/games/{game_id}")
def update_game(game_id: int, game: GameUpdate, db=Depends(get_db)):
    cursor = db.cursor()
    category_str = ",".join(game.category)
    query = "UPDATE games_list SET name = %s, price = %s, category = %s, year = %s, image_path = %s, admin_id = %s WHERE id = %s"
    try:
        cursor.execute(query, (game.name, game.price, category_str, game.year, game.image_path, game.admin_id, game_id))
        db.commit()
        return {"message": "Game updated successfully!"}
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()

# Delete a Game
@app.delete("/games/{game_id}")
def delete_game(game_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    query = "DELETE FROM games_list WHERE id = %s"
    try:
        cursor.execute(query, (game_id,))
        db.commit()
        return {"message": "Game deleted successfully!"}
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()

# API Endpoint: Fetch Admin Profile (for Admin dashboard)
@app.get("/api/admin_profile")
def get_admin_profile(email: str, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, username, email FROM admins WHERE email = %s"
    cursor.execute(query, (email,))
    admin = cursor.fetchone()
    cursor.close()
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return {"admin": admin}

# Run Server: uvicorn backend.backend:app --reload
