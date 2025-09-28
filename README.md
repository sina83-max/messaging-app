# Messaging API

A production-ready messaging platform built with **FastAPI**, featuring secure JWT authentication, user profile management, messaging with delivery/read receipts, message filtering, and email notifications.  
The project is fully **Dockerized** and uses **PostgreSQL** as the database backend.

---

##  Features

- 🔐 **User Authentication**
  - Register and login with JWT tokens.
  - Manage user profiles (username, avatar).
- 💬 **Messaging**
  - Send and receive messages.
  - Random message generator API.
  - Message history with delivery/read receipts.
- 🔔 **Notifications**
  - In-app notifications.
  - Email notifications (via Gmail SMTP).
- 🔎 **Search & Filters**
  - Filter messages by:
    - Keyword
    - Sender ID
    - Date
    - Unread messages only

---

##  Tech Stack

- **Backend Framework:** FastAPI  
- **Database:** PostgreSQL  
- **ORM:** SQLAlchemy  
- **Authentication:** JWT (JSON Web Tokens)  
- **Notifications:** Email via SMTP (Gmail)  
- **Containerization:** Docker & Docker Compose  

---

## ⚙ Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/messaging-api.git
cd messaging-api
```
### 2. Create a .env file

Define environment variables inside .env file at the root: 
```bash
# Database
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/messaging_db

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (Gmail SMTP)
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_FROM=your_gmail@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```
For Gmail: enable 2FA and create an App Password to use here.

### 3. Run With Docker
```bash
docker-compose up --build
```
This will start:  
FastAPI app at http://localhost:8000  
PostgreSQL database on port 5432

---

### API Docs

Once the app is running, go to:

- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)

#### Example Endpoints

#### 🔐 Auth
- `POST /auth/register` → Register user  
- `POST /auth/login` → Login and get JWT  

#### 👤 User
- `GET /users/me` → Get current user  
- `PATCH /users/me/username` → Change username  

#### 💬 Messages
- `POST /messages/send` → Send a message  
- `GET /messages/` → List user messages  
- `GET /messages/random` → Get a random system-generated message  
- `GET /messages/filter` → Filter messages by query parameters  

#### 🔔 Notifications
- `GET /notifications` → View in-app notifications  
- (Emails are sent automatically on new message)
