# 🚀 Employee API with API Key Authentication (Flask + MongoDB Atlas)

A **secure and production-ready RESTful API** built with **Flask** and **MongoDB Atlas** for managing employee records.  
The API is protected using **API Key Authentication** ensuring only authorized users can perform sensitive operations.  

---

## ✨ Features
- 🔐 **API Key Authentication** – Secure all endpoints (except key generation).  
- 🛠 **Full CRUD Operations** – Create, Read, Update, Delete employee records.  
- ☁️ **MongoDB Atlas Integration** – Cloud-hosted NoSQL database for flexible data storage.  
- 🚀 **Production Deployment** – Optimized with Gunicorn for scalability.  

---

## 🔗 Live API Endpoint
**Base URL:** 👉 [https://employee-api-key.onrender.com](https://employee-api-key.onrender.com)  

---

## ⚙️ Local Installation & Setup
Follow these steps to run the project locally for development:

### 1️⃣ Create & Activate Virtual Environment  
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
2️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
3️⃣ Configure Environment Variables
Create a .env file in the project root and add your MongoDB Atlas connection string:

bash
Copy code
MONGO_URI="YOUR_MONGO_DB_STRING"
4️⃣ Run the Application
bash
Copy code
python app.py
🔒 API Authentication
Before accessing employee endpoints, generate an API key.

1. Generate API Key
Endpoint:

http
Copy code
POST /generate_key
Request Body (JSON):

json
Copy code
{
  "name": "Your Name",
  "days_valid": 30
}
✅ Response (Success): Returns a unique api_key and its expiration date.

2. Using the API Key
Every request (except /generate_key) must include the API key in headers:

http
Copy code
X-API-KEY: your_generated_key
📖 API Endpoints Reference
Endpoint	Method	Description
/generate_key	POST	Generate a new API Key (valid for X days).
/employees	POST	Add a new employee record.
/employees	GET	Get all employee records.
/employees/<int:employee_id>	GET	Get details of a specific employee.
/employees/<int:employee_id>	PUT	Update employee details.
/employees/<int:employee_id>	DELETE	Delete an employee record.
