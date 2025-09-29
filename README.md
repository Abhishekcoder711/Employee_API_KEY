# 🚀 Employee API KEY (Flask + MongoDB Atlas)

A robust and secure RESTful API built with **Flask** and **MongoDB Atlas** for managing employee records. This API uses **API Key Authentication** for all sensitive operations, making it production-ready.


## ✨ Features

* **Secure CRUD Operations:** Complete set of Create, Read, Update, and Delete operations for employee data.
* **API Key Authentication:** All endpoints (except key generation) are secured and require a valid API Key in the header.
* **MongoDB Atlas:** Uses a cloud-hosted NoSQL database for flexible data storage.
* **Gunicorn:** Deployed with Gunicorn for reliable and scalable production performance.


🔗 Live API Endpoint

You can access the live, deployed API here:

**Base URL:** 'https://employee-api-key.onrender.com'

---


⚙️ Local Installation & Setup
Follow these steps to set up the project locally for development:

1. ## Create and Activate Virtual Environment
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate


2. ## ⬇️ Install Dependencies
---->> pip install -r requirements.txt


3. ## 🚀 Environment Variables
Create a file named .env in the root directory and add your MongoDB Atlas connection string. This keeps your credentials secure (since .env is already in .gitignore).

--->> MONGO_URI="YOUR_MONGO_DB_STRING"


4. ## 🎊 Run the Application
Start the Flask application using the development server: python app.py


🔒 API Authentication (Crucial)
--->> Before using any employee endpoint, you must first generate an API key.

1. ## Generate API Key (POST /generate_key):-
--URL	https: //employee-api-key.onrender.com/generate_key
--Method:	POST
--Body (JSON):	{"name": "Your Name", "days_valid": 30}

---->>Success	Returns a unique api_key and its expiration date.<<----

2. ## Using the API Key
--> Header Key: X-API-KEY
--> Header Value: {Your Generated Key}


💡 API Endpoints Reference
            Endpoints 	        |   Method   |          Description            
--------------------------------------------------------------------------------------
/generate_key                   |    POST    |   Get new API_KEY and valid for 30 days.
/employees                      |	   POST	   |   Adds a new employee record(s)
/employees                      |    GET     |   Retrieves all employee records.
/employees/<int:employee_id>	  |    GET	   |   Retrieves an employee by ID.	
/employees/<int:employee_id>    |	   PUT	   |   Updates an employee's details.	
/employees/<int:employee_id>	  |   DELETE   |   Deletes an employee record.	

