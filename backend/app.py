import requests
import pandas as pd
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from pymongo import MongoClient 

app = Flask(__name__)

#CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:4200",  # Allow local development (optional)
            "https://parthdarji9714.github.io/university-course-app"  # Allow your deployed GitHub Pages site
        ]
    }
}, supports_credentials=True)

# Configuration
#app.config["MONGO_URI"] = "mongodb+srv://parthdarji9714:Xxm1kBMQxh2EoAbc@cluster0.2pey1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
#mongo = PyMongo(app)

# Get MongoDB URI from environment variable
mongo_uri = os.getenv('MONGODB_URI')

# Ensure the URI includes ssl=True
mongo_uri += "?ssl=true&ssl_cert_reqs=CERT_NONE"

mongo = MongoClient(mongo_uri)

db = mongo.get_default_database()
# Function to download data
def download_data():
    url = "https://api.mockaroo.com/api/501b2790?count=100&key=8683a1c0"
    response = requests.get(url)
    with open("courses.csv", "wb") as file:
        file.write(response.content)
    return "courses.csv"

# Enhanced normalization function with correct column names
def normalize_data(file_path):
    df = pd.read_csv(file_path)
    
    # Convert column names to lowercase and replace spaces with underscores
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    
    # List of text fields to normalize, checking if they exist in the DataFrame
    text_fields = ['university', 'city', 'country', 'coursename', 'coursedescription', 'currency']
    existing_text_fields = [field for field in text_fields if field in df.columns]
    
    if existing_text_fields:
        # Strip leading/trailing spaces in text fields
        df[existing_text_fields] = df[existing_text_fields].apply(lambda x: x.str.strip())
        
        # Standardize text fields to title case (or lower case, depending on your needs)
        df[existing_text_fields] = df[existing_text_fields].apply(lambda x: x.str.title())
    
    # Convert date fields to datetime and handle invalid dates, if they exist
    date_fields = ['start_date', 'end_date']
    for field in date_fields:
        if field in df.columns:
            df[field] = pd.to_datetime(df[field], errors='coerce')
    
    # Remove rows where dates are missing or invalid
    if 'start_date' in df.columns and 'end_date' in df.columns:
        df.dropna(subset=['start_date', 'end_date'], inplace=True)
        # Ensure start_date is before end_date
        df = df[df['start_date'] <= df['end_date']]
    
    # Convert price to numeric, handling any non-numeric values
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        # Handle missing or invalid price
        df['price'].fillna(0, inplace=True)
    
    return df

# Function to check for data expiration and refresh if necessary
def check_and_refresh_data():
    # Check if the 'last_update' field exists in the database
    latest_record = mongo.db.courses.find_one(sort=[("last_update", -1)])
    
    if latest_record:
        last_update_time = latest_record.get('last_update')
        current_time = datetime.utcnow()
        
        # Check if the data is older than 10 minutes
        if last_update_time and current_time - last_update_time > timedelta(minutes=10):
            print("Data is expired. Refreshing...")
            mongo.db.courses.delete_many({})  # Clear old data
            refresh_data()  # Re-download, normalize, and store the data
    else:
        print("No data found. Downloading...")
        refresh_data()  # No data found, so download it

# Function to refresh data
def refresh_data():
    file_path = download_data()
    df = normalize_data(file_path)
    
    # Add 'last_update' timestamp to each record
    df['last_update'] = datetime.utcnow()
    
    # Insert normalized data into MongoDB
    mongo.db.courses.insert_many(df.to_dict('records'))

@app.route('/download-data', methods=['GET'])
def download_and_normalize():
    check_and_refresh_data()
    return jsonify({"msg": "Data checked and updated if necessary"}), 200


@app.route('/', methods=['GET'])
def get_courses():
    search_query = request.args.get('query', '').strip()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    # Construct the query for searching on specific text fields
    query_params = {}
    if search_query:
        text_fields = ['university', 'city', 'country', 'coursename', 'coursedescription']
        search_conditions = []
        for field in text_fields:
            search_conditions.append({field: {'$regex': search_query, '$options': 'i'}})  # Case-insensitive search
        query_params = {'$or': search_conditions}

    # MongoDB query with pagination
    courses = list(
        mongo.db.courses.find(query_params)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )

    # Convert ObjectId to string for JSON serialization
    for course in courses:
        course['_id'] = str(course['_id'])

    # Include total count for pagination purposes
    total_courses = mongo.db.courses.count_documents(query_params)

    # Check if no courses were found
    if total_courses == 0:
        return jsonify({"error": "No courses found matching the criteria"}), 404

    response = {
        'total_courses': total_courses,
        'page': page,
        'page_size': page_size,
        'courses': courses
    }

    return jsonify(response), 200

#@app.route('/api/courses/<course_id>', methods=['PUT'])
@app.route('/<course_id>', methods=['PUT'])
def update_course_by_id(course_id):
    if not request.json:
        return jsonify({"error": "Invalid input, JSON required"}), 400

    updated_data = request.json

    # Remove fields that are not allowed to be updated
    protected_fields = ['coursename', 'country', 'city', 'university']
    for field in protected_fields:
        if field in updated_data:
            del updated_data[field]

    # Attempt to update the course with the remaining fields
    result = mongo.db.courses.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": updated_data}
    )

    if result.matched_count:
        return jsonify({"success": "Course updated successfully"}), 200
    else:
        return jsonify({"error": "Course not found"}), 404

#@app.route('/api/courses/<course_id>', methods=['DELETE'])
@app.route('/<course_id>', methods=['DELETE'])
def delete_course_by_id(course_id):
    try:
        # Convert the course_id to an ObjectId
        course_object_id = ObjectId(course_id)
    except:
        return jsonify({"error": "Invalid course ID"}), 400

    # Attempt to delete the course by its _id
    result = mongo.db.courses.delete_one({"_id": course_object_id})
    if result.deleted_count:
        return jsonify({"success": "Course deleted successfully"}), 200
    else:
        return jsonify({"error": "Course not found"}), 404

# @app.route('/api/courses', methods=['POST'])
# def create_course():
#     if not request.json:
#         return jsonify({"error": "Invalid input, JSON required"}), 400

#     new_course = request.json

#     # Validate required fields
#     required_fields = ['university', 'city', 'country', 'coursename', 'coursedescription', 'start_date', 'end_date', 'price']
#     for field in required_fields:
#         if field not in new_course:
#             return jsonify({"error": f"Missing required field: {field}"}), 400

#     # Insert the new course into the database
#     result = mongo.db.courses.insert_one(new_course)
#     course_id = str(result.inserted_id)

#     return jsonify({"success": "Course created successfully", "course_id": course_id}), 201
#@app.route('/api/courses', methods=['POST'])
@app.route('/', methods=['POST'])
def create_course():
    if not request.json:
        return jsonify({"error": "Invalid input, JSON required"}), 400

    new_course = request.json

    # Validate required fields
    required_fields = ['university', 'city', 'country', 'coursename', 'coursedescription', 'start_date', 'end_date', 'price']
    for field in required_fields:
        if field not in new_course:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Insert the new course into the database
    result = mongo.db.courses.insert_one(new_course)
    course_id = str(result.inserted_id)

    return jsonify({"success": "Course created successfully", "course_id": course_id}), 201




if __name__ == '__main__':
    check_and_refresh_data()  # Check data expiration on app startup
    port = int(os.environ.get("PORT", 5000))
    app.run(host = '0.0.0.0', port = port)
