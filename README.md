# Hostel Late Entry and Exit Management System (HLEEMS)

A comprehensive, production-quality full-stack application built for managing student hostel access, permissions, and logs.

## 📌 Architecture
- **Frontend**: Vanilla HTML5, CSS3, JavaScript with Custom Glassmorphism UI
- **Backend**: Python 3 (Flask) RESTful API
- **Database**: MySQL (InnoDB) enforcing strict 3NF and referential integrity

## 🚀 Setup Instructions

### 1. Database Setup
1. Ensure you have a running MySQL server.
2. Login to MySQL and execute the schema:
   ```bash
   mysql -u root -p < database/schema.sql
   ```
3. Seed the sample users data:
   ```bash
   mysql -u root -p < database/seed.sql
   ```

### 2. Backend Setup
1. Navigate to the `backend` directory.
   ```bash
   cd backend
   ```
2. Create standard Python virtual environment (Optional but Recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Verify the `.env` settings (Default `root` with no password for MySQL). Adjust if needed.
5. Run the server:
   ```bash
   python app.py
   ```
   > The API will run on `http://localhost:5000`

### 3. Frontend Setup
The frontend uses pure Vanilla browser tech. You do not need to install `npm` modules.
1. Open up a local development server for the `frontend` folder (e.g., using `Live Server` extension in VSCode, or Python HTTP Server):
   ```bash
   cd frontend
   python -m http.server 8000
   ```
2. Navigate to `http://localhost:8000/index.html` in your browser.

## 👥 Sample Credentials (from `seed.sql`)
Password for all initial test users: **`password123`**
- **Admin**: `admin1`
- **Warden**: `wardena`
- **Student**: `student1`
