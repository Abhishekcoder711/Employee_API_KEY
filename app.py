from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv 
import secrets
import hashlib
from functools import wraps
from datetime import datetime, timedelta, timezone 
import os

# Load environment variables from .env file (for local development)
load_dotenv() 

# ---------------- MongoDB Config ----------------

# MONGO_URI ab .env file ya Render ke Environment Variable se load hoga
MONGO_URI = os.getenv("MONGO_URI") 
DB_NAME = "employee_api"

# Check karein agar MONGO_URI set nahi hai
if not MONGO_URI:
    print("❌ Critical Error: MONGO_URI environment variable is not set. Check your .env or Render settings.")
    # Agar local chala rahe hain aur MONGO_URI set nahi hai, toh app fail ho jayega.

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    employees_collection = db["employees"]
    api_keys_collection = db["api_keys"]
    # Ek simple check ki connection successful hai ya nahi
    client.admin.command('ping') 
    print(f"✅ MongoDB connected and ping successful to database: {DB_NAME}")
except Exception as e:
    print(f"❌ MongoDB connection error. Check your MONGO_URI: {e}")
    # Connection error ke bawajood, Flask app chalu rahega
    
app = Flask(__name__)

# ---------------- Utils ----------------
def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def serialize_doc(doc):
    if doc:
        # '_id' ko string mein badalna zaroori hai JSON ke liye
        doc['id'] = str(doc.pop('_id'))
        # Datetime objects ko ISO format mein badalna
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
    return doc

def create_api_key(name: str, days_valid: int = 30):
    raw_key = secrets.token_urlsafe(32)
    h = hash_key(raw_key)
    
    # Timezone-aware datetime objects for consistency
    created = datetime.now(timezone.utc)
    expires = created + timedelta(days=days_valid)
    
    key_doc = {
        "name": name,
        "key_hash": h,
        "created_at": created,
        "expires_at": expires,
        "revoked": False
    }
    
    api_keys_collection.insert_one(key_doc)
    
    return raw_key, created, expires

def validate_key(raw_key: str):
    if not raw_key:
        return False, "No key provided"
        
    h = hash_key(raw_key)
    
    key_doc = api_keys_collection.find_one({"key_hash": h})
    
    if not key_doc:
        return False, "Invalid key"
        
    if key_doc.get("revoked"):
        return False, "Key revoked"
        
    expires_at = key_doc.get("expires_at")
    
    # FIX for "can't compare offset-naive and offset-aware datetimes"
    # Ensure expires_at is timezone-aware (UTC) before comparison
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    # Timezone-aware comparison
    if expires_at and datetime.now(timezone.utc) > expires_at:
        return False, "Key expired"
        
    return True, serialize_doc(key_doc)

def require_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Key extraction logic to support both "ApiKey <key>" and "X-API-KEY"
        auth = request.headers.get("Authorization", "")
        raw_key = None
        if auth.startswith("ApiKey "):
            raw_key = auth.split(" ", 1)[1].strip()
        else:
            raw_key = request.headers.get("X-API-KEY") or request.args.get("api_key")
            
        valid, info = validate_key(raw_key)
        
        if not valid:
            return jsonify({"error": "Unauthorized", "reason": info}), 401
            
        request.api_key_info = info
        return f(*args, **kwargs)
    return wrapper

# ---------------- Routes ----------------
@app.route("/")
def index():
    return {"msg": "Employee API with MongoDB. Use /generate_key first."}

@app.route("/generate_key", methods=["POST"])
def route_generate_key():
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name", "client")
    days = int(data.get("days_valid", 30))
    raw, created, expires = create_api_key(name, days)
    return {
        "api_key": raw,
        "created_at": created.isoformat(),
        "expires_at": expires.isoformat(),
        "note": "Save this key now. It will not be shown again."
    }

@app.route("/employees", methods=["GET"])
@require_api_key
def list_employees():
    rows = list(employees_collection.find({}))
    serialized_rows = [serialize_doc(row) for row in rows]
    return jsonify(serialized_rows)

@app.route("/employees", methods=["POST"])
@require_api_key
def create_employee():
    data = request.get_json(force=True, silent=True)
    
    if isinstance(data, list):
        employees_to_process = data
    elif isinstance(data, dict):
        employees_to_process = [data]
    else:
        return {"error": "Invalid data format. Expected JSON object or list."}, 400

    now = datetime.now(timezone.utc)
    
    documents_to_insert = []
    errors = []
    
    for emp_data in employees_to_process:
        name = emp_data.get("name")
        
        if not name:
            errors.append({"error": "name is required.", "data": emp_data})
            continue

        doc = {
            "name": name,
            "email": emp_data.get("email"),
            "position": emp_data.get("position"),
            "salary": emp_data.get("salary"),
            "created_at": now,
            "updated_at": now
        }
        documents_to_insert.append(doc)
    
    successful_inserts = 0
    if documents_to_insert:
        try:
            result = employees_collection.insert_many(documents_to_insert)
            successful_inserts = len(result.inserted_ids)
        except Exception as e:
            errors.append({"error": str(e)})

    if successful_inserts > 0 and not errors:
        return {"message": f"{successful_inserts} employee(s) added successfully."}, 201
    elif successful_inserts > 0 and errors:
        return jsonify({
            "message": f"Partially successful: {successful_inserts} added.",
            "errors": errors
        }), 207
    else:
        return jsonify({"error": "Failed to add any employees.", "errors": errors}), 400

@app.route("/employees/<emp_id>", methods=["GET"])
@require_api_key
def get_employee(emp_id):
    try:
        emp_obj_id = ObjectId(emp_id)
    except:
        return {"error": "Invalid ID format"}, 400
        
    row = employees_collection.find_one({"_id": emp_obj_id})
    
    if not row:
        return {"error": "Not found"}, 404
        
    return serialize_doc(row)

@app.route("/employees/<emp_id>", methods=["PUT"])
@require_api_key
def update_employee(emp_id):
    data = request.get_json(force=True, silent=True) or {}
    update_data = {}
    
    for col in ("name", "email", "position", "salary"):
        if col in data:
            update_data[col] = data[col]
            
    if not update_data:
        return {"error": "no fields to update"}, 400
        
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    try:
        emp_obj_id = ObjectId(emp_id)
    except:
        return {"error": "Invalid ID format"}, 400
        
    result = employees_collection.update_one(
        {"_id": emp_obj_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        return {"error": "Not found"}, 404
        
    row = employees_collection.find_one({"_id": emp_obj_id})
    return serialize_doc(row)

@app.route("/employees", methods=["DELETE"])
@require_api_key
def bulk_delete_employees():
    data = request.get_json(force=True, silent=True)
    
    if not isinstance(data, list):
        return {"error": "Expected a list of employee IDs in the request body."}, 400
        
    object_ids = []
    for id_str in data:
        try:
            object_ids.append(ObjectId(id_str))
        except:
            return {"error": f"Invalid ID format in list: {id_str}"}, 400

    if not object_ids:
        return {"error": "No valid employee IDs provided for deletion."}, 400
        
    result = employees_collection.delete_many({"_id": {"$in": object_ids}})
    deleted_count = result.deleted_count
    
    return {"status": "deleted", "deleted_count": deleted_count, "requested_ids_count": len(object_ids)}

@app.route("/employees/<emp_id>", methods=["DELETE"])
@require_api_key
def delete_employee_single(emp_id):
    try:
        emp_obj_id = ObjectId(emp_id)
    except:
        return {"error": "Invalid ID format"}, 400
        
    result = employees_collection.delete_one({"_id": emp_obj_id})
    
    if result.deleted_count == 0:
        return {"error": "Not found"}, 404
        
    return {"status": "deleted"}

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)