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
#mongo = PyMongo(app)
# Get MongoDB URI from environment variable
app = Flask(__name__)

# Replace with your actual MongoDB Atlas URI
#mongo_uri = os.getenv('MONGODB_URI')
# Connect to MongoDB Atlas
#mongo = PyMongo(app, uri=mongo_uri)
mongo_uri = os.getenv('MONGODB_URI')

if not mongo_uri:
    raise ValueError("No MongoDB URI found in environment variables.")

app.config["MONGO_URI"] = mongo_uri

# Initialize PyMongo with the Flask app
mongo = PyMongo(app, tls=True, tlsAllowInvalidCertificates=True)


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
    
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    text_fields = ['university', 'city', 'country', 'coursename', 'coursedescription', 'currency']
    existing_text_fields = [field for field in text_fields if field in df.columns]
    
    if existing_text_fields:
        df[existing_text_fields] = df[existing_text_fields].apply(lambda x: x.str.strip())
        df[existing_text_fields] = df[existing_text_fields].apply(lambda x: x.str.title())
    
    date_fields = ['start_date', 'end_date']
    for field in date_fields:
        if field in df.columns:
            df[field] = pd.to_datetime(df[field], errors='coerce')
    
    if 'start_date' in df.columns and 'end_date' in df.columns:
        df.dropna(subset=['start_date', 'end_date'], inplace=True)
        df = df[df['start_date'] <= df['end_date']]
    
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['price'].fillna(0, inplace=True)
    
    return df

def check_and_refresh_data():
    latest_record = mongo.db.courses.find_one(sort=[("last_update", -1)])
    
    if latest_record:
        last_update_time = latest_record.get('last_update')
        current_time = datetime.utcnow()
        
        if last_update_time and current_time - last_update_time > timedelta(minutes=10):
            print("Data is expired. Refreshing...")
            mongo.db.courses.delete_many({})
            refresh_data()
    else:
        print("No data found. Downloading...")
        refresh_data()

def refresh_data():
    file_path = download_data()
    df = normalize_data(file_path)
    
    df['last_update'] = datetime.utcnow()
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
