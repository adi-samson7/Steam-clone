# 🎮 Steam Clone - Game Store CRUD Website

A Steam-inspired game store web application built using **FastAPI**, **MySQL**, **HTML**, **CSS**, and **JavaScript**.

This project simulates a digital game marketplace where users can browse games, add them to cart, purchase them, and manage their profiles. It also includes an admin dashboard for managing games and viewing transactions.

<img width="1894" height="898" alt="Screenshot1 (155)" src="https://github.com/user-attachments/assets/abdf3bbf-2fd5-46f3-bc29-dd2c7b48be77" />


---

## 🚀 Features

### 👤 User Features
- User registration and login
- Session-based authentication using `sessionStorage`
- Browse all available games
- Filter games by category
- Add games to cart
- Prevent duplicate cart entries
- Purchase games using dummy payment methods
- Prevent duplicate purchases of already-owned games
- View purchased games in personal library
- Update profile information
- View transaction history

---

### 🛠 Admin Features
- Admin registration and login
- Add new games
- Update existing games
- Delete games
- View all users
- View all admins
- View transactions linked to their games

---

## 🧰 Tech Stack

### Backend
- FastAPI
- MySQL
- mysql-connector-python
- Pydantic
- Jinja2
- Python-dotenv

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla)

---

## 📂 Project Structure

```bash
STEAM-CLONE/
│── .env
│── .gitignore
│── requirements.txt
│
├── backend/
│   ├── backend.py
│   ├── gamestore.py
│   ├── __init__.py
│
├── statics/
│   ├── images/
│   ├── login.js
│   ├── script.js
│   ├── style.css
│   ├── log_styles.css
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── index.html
│   ├── store.html
│   ├── cart.html
│   ├── payment.html
│   ├── order-confirmation.html
│   ├── profile.html
│   ├── admin.html
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/steam-clone-fastapi.git
cd steam-clone-fastapi
```

---

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create `.env` file

Create a `.env` file in the root directory:

```env
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=game_store
```

---

### 5. Start MySQL server

Make sure MySQL is running and create:

```sql
game_store
```

Database should contain these tables:

- users
- admins
- games_list
- transactions

---

### 6. Run the server

```bash
uvicorn backend.backend:app --reload
```

Server runs at:

```text
http://127.0.0.1:8000
```

---
## Screenshots
<img width="1920" height="895" alt="Screenshot1 (156)" src="https://github.com/user-attachments/assets/7681461c-8fdc-4413-8a17-1fcef0a1a856" />
<img width="1902" height="898" alt="Screenshot1 (157)" src="https://github.com/user-attachments/assets/7f6c076e-6dc9-4482-827e-cb47ffb4b143" />
<img width="1920" height="895" alt="Screenshot1 (160)" src="https://github.com/user-attachments/assets/e7477524-ab4f-4c46-b62c-8b9dffbc30f3" />
<img width="1920" height="891" alt="Screenshot1 (162)" src="https://github.com/user-attachments/assets/36c7ec43-e9a8-453d-b34a-7ed4df6e1813" />

## 📡 API Endpoints

### Authentication
- `POST /login`
- `POST /register`
- `POST /register_admin`

### Games
- `GET /games`
- `GET /games/{category}`
- `POST /games`
- `PUT /games/{game_id}`
- `DELETE /games/{game_id}`

### Profile
- `GET /api/profile`
- `PUT /api/profile`

### Transactions
- `GET /api/transactions`
- `POST /api/transactions`
- `GET /api/admin_transactions`

### Library
- `GET /api/user-library`

---

## 🔐 Security Note

Sensitive credentials are stored using `.env` and are excluded from GitHub via `.gitignore`.

---

## 📌 Future Improvements

- Password hashing with bcrypt
- JWT authentication
- Wishlist feature
- Search functionality
- Better admin analytics dashboard
- Cloud deployment (Render / Railway / AWS)

---

## 👨‍💻 Author

Built by **Aditya Samson**  
