## Chat App (Django + Channels)

**Real-time individual chat application** built with **Django (MVT)** and **Django Channels (WebSocket)**.

### Features
- **Custom user model** with `email`, `username`, `password`, `is_online`, `last_seen`
- **Authentication**: register, login, logout, login-required protection
- **User list** showing all users except self with **online indicator**
- **Private 1-to-1 chat** between users
- **Real-time messaging** via WebSockets (Django Channels)
- **Message persistence** in SQLite database
- **Chat history** loads on open
- **Read status**: `✓` (sent), `✓✓` (read)
- Auto-scroll to latest message

### Requirements
- Python 3.12+
- Redis server running locally on `redis://127.0.0.1:6379` (for Channels layer)

### Installation

```bash
cd C:\Users\91920\Music\Chatapp
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Make sure Redis is running (on Windows you can use WSL/ Docker or a native port).

### Database & Migrations

```bash
venv\Scripts\activate
python manage.py makemigrations accounts chat
python manage.py migrate
python manage.py createsuperuser
```

### Run the Development Server

```bash
venv\Scripts\activate
python manage.py runserver
```

Then open `http://127.0.0.1:8000/` in your browser.

### Usage
- Register two users (or use the admin to create them).
- Log in as one user.
- Visit the **Users** page, click another user to open a private chat.
- Open another browser/incognito window and log in as the second user to test real-time chat.

