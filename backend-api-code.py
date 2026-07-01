# AI-based Drop-out Prediction System - Backend API
# Smart India Hackathon 2025

from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime, timedelta
import pymongo
from pymongo import MongoClient
import csv
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
jwt = JWTManager(app)
mail = Mail(app)

# MongoDB connection
try:
    client = MongoClient(os.environ.get('MONGO_URI', 'mongodb://localhost:27017/'))
    db = client['edupredict_db']
    students_collection = db['students']
    users_collection = db['users']
    notifications_collection = db['notifications']
    logger.info("Connected to MongoDB successfully")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")

# Risk assessment thresholds
RISK_THRESHOLDS = {
    'attendance_threshold': 75,
    'failed_subjects_threshold': 2,
    'fee_payment_threshold': 80,
    'high_risk_score': 0.7,
    'medium_risk_score': 0.4
}

# Sample users (In production, this would be in database with hashed passwords)
SAMPLE_USERS = {
    'admin@edupredict.com': {
        'password': generate_password_hash('admin123'),
        'role': 'Admin',
        'name': 'System Administrator'
    },
    'mentor@edupredict.com': {
        'password': generate_password_hash('mentor123'),
        'role': 'Mentor', 
        'name': 'Academic Mentor'
    }
}

class RiskAssessmentEngine:
    """Rule-based risk assessment engine for student dropout prediction"""
    
    def __init__(self, thresholds=None):
        self.thresholds = thresholds or RISK_THRESHOLDS
    
    def calculate_attendance_risk(self, total_classes, attended_classes):
        """Calculate risk based on attendance"""
        if total_classes == 0:
            return 0, []
        
        attendance_percentage = (attended_classes / total_classes) * 100
        
        if attendance_percentage < self.thresholds['attendance_threshold']:
            risk_score = max(0, (self.thresholds['attendance_threshold'] - attendance_percentage) / 100)
            return risk_score, [f"Low Attendance ({attendance_percentage:.1f}%)"]
        
        return 0, []
    
    def calculate_academic_risk(self, subjects_data):
        """Calculate risk based on academic performance"""
        failed_subjects = 0
        total_subjects = len(subjects_data)
        risk_factors = []
        
        for subject in subjects_data:
            if subject['marks_obtained'] < subject['max_marks'] * 0.4:  # 40% pass mark
                failed_subjects += 1
        
        if failed_subjects >= self.thresholds['failed_subjects_threshold']:
            risk_score = min(1.0, failed_subjects / total_subjects)
            risk_factors.append(f"Failed {failed_subjects} subjects")
            return risk_score, risk_factors
        
        return 0, []
    
    def calculate_financial_risk(self, total_fees, fees_paid):
        """Calculate risk based on fee payment status"""
        if total_fees == 0:
            return 0, []
        
        payment_percentage = (fees_paid / total_fees) * 100
        
        if payment_percentage < self.thresholds['fee_payment_threshold']:
            risk_score = (self.thresholds['fee_payment_threshold'] - payment_percentage) / 100
            pending_percentage = 100 - payment_percentage
            return risk_score, [f"Fee overdue ({pending_percentage:.1f}% pending)"]
        
        return 0, []
    
    def assess_overall_risk(self, student_data):
        """Calculate overall risk score and determine risk level"""
        total_risk_score = 0
        all_risk_factors = []
        
        # Attendance risk (40% weight)
        attendance_risk, attendance_factors = self.calculate_attendance_risk(
            student_data['total_classes'], student_data['classes_attended']
        )
        total_risk_score += attendance_risk * 0.4
        all_risk_factors.extend(attendance_factors)
        
        # Academic risk (40% weight)
        academic_risk, academic_factors = self.calculate_academic_risk(student_data['subjects'])
        total_risk_score += academic_risk * 0.4
        all_risk_factors.extend(academic_factors)
        
        # Financial risk (20% weight)
        financial_risk, financial_factors = self.calculate_financial_risk(
            student_data['total_fees'], student_data['fees_paid']
        )
        total_risk_score += financial_risk * 0.2
        all_risk_factors.extend(financial_factors)
        
        # Determine risk level
        if total_risk_score >= self.thresholds['high_risk_score']:
            risk_level = 'red'
        elif total_risk_score >= self.thresholds['medium_risk_score']:
            risk_level = 'yellow'
        else:
            risk_level = 'green'
        
        return {
            'risk_score': round(total_risk_score, 3),
            'risk_level': risk_level,
            'risk_factors': all_risk_factors,
            'attendance_percentage': round((student_data['classes_attended'] / student_data['total_classes']) * 100, 1) if student_data['total_classes'] > 0 else 0,
            'fees_percentage': round((student_data['fees_paid'] / student_data['total_fees']) * 100, 1) if student_data['total_fees'] > 0 else 0
        }

class MLPredictionEngine:
    """Machine Learning engine for dropout prediction"""
    
    def __init__(self, model_path=None):
        self.model = None
        self.scaler = None
        self.is_trained = False
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.create_sample_model()
    
    def create_sample_model(self):
        """Create and train a sample logistic regression model"""
        # Sample training data (in production, use historical data)
        np.random.seed(42)
        n_samples = 1000
        
        X = np.random.rand(n_samples, 4)  # attendance, avg_marks, fee_status, prev_performance
        
        # Create realistic labels based on features
        risk_scores = (
            (1 - X[:, 0]) * 0.4 +  # attendance (inverted)
            (1 - X[:, 1]) * 0.3 +  # marks (inverted)
            (1 - X[:, 2]) * 0.2 +  # fees (inverted)
            (1 - X[:, 3]) * 0.1    # previous performance (inverted)
        )
        
        y = (risk_scores > 0.5).astype(int)  # Binary classification
        
        # Train model
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = LogisticRegression(random_state=42)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        logger.info("Sample ML model created and trained")
    
    def predict_dropout_probability(self, student_data):
        """Predict dropout probability for a student"""
        if not self.is_trained:
            return 0.5  # Default probability
        
        # Extract features
        attendance_rate = student_data['classes_attended'] / max(student_data['total_classes'], 1)
        avg_marks = np.mean([s['marks_obtained'] / max(s['max_marks'], 1) for s in student_data['subjects']])
        fee_payment_rate = student_data['fees_paid'] / max(student_data['total_fees'], 1)
        prev_performance = 0.7  # Placeholder for previous semester data
        
        features = np.array([[attendance_rate, avg_marks, fee_payment_rate, prev_performance]])
        features_scaled = self.scaler.transform(features)
        
        probability = self.model.predict_proba(features_scaled)[0][1]  # Probability of dropout
        return round(probability, 3)
    
    def save_model(self, path):
        """Save the trained model"""
        if self.is_trained:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler
            }, path)
    
    def load_model(self, path):
        """Load a pre-trained model"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.is_trained = True

class NotificationService:
    """Email notification service for student alerts"""
    
    def __init__(self, mail_instance):
        self.mail = mail_instance
    
    def send_risk_alert(self, student_data, recipients, risk_assessment):
        """Send email alert for at-risk student"""
        try:
            risk_level_text = {
                'red': 'CRITICAL RISK',
                'yellow': 'MODERATE RISK',
                'green': 'LOW RISK'
            }
            
            subject = f"Student Alert: {risk_level_text[risk_assessment['risk_level']]} - {student_data['student_name']}"
            
            body = f"""
            Dear Mentor/Guardian,

            This is an automated alert from the EduPredict AI system regarding student {student_data['student_name']} (ID: {student_data['student_id']}).

            RISK ASSESSMENT:
            - Risk Level: {risk_level_text[risk_assessment['risk_level']]}
            - Risk Score: {risk_assessment['risk_score']}/1.0
            - Dropout Probability: {risk_assessment.get('ml_probability', 'N/A')}

            CURRENT STATUS:
            - Attendance: {risk_assessment['attendance_percentage']}% ({student_data['classes_attended']}/{student_data['total_classes']} classes)
            - Fee Payment: {risk_assessment['fees_percentage']}% (₹{student_data['fees_paid']}/₹{student_data['total_fees']})

            RISK FACTORS:
            {chr(10).join('• ' + factor for factor in risk_assessment['risk_factors'])}

            RECOMMENDED ACTIONS:
            - Schedule immediate counseling session
            - Contact parent/guardian
            - Review academic support options
            - Discuss financial assistance if needed

            Please take appropriate action to support this student.

            Best regards,
            EduPredict AI System
            Smart India Hackathon 2025
            """
            
            msg = Message(
                subject=subject,
                sender=app.config['MAIL_USERNAME'],
                recipients=recipients,
                body=body
            )
            
            self.mail.send(msg)
            
            # Log notification
            notification_record = {
                'student_id': student_data['student_id'],
                'recipients': recipients,
                'risk_level': risk_assessment['risk_level'],
                'sent_at': datetime.utcnow(),
                'status': 'sent'
            }
            notifications_collection.insert_one(notification_record)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

# Initialize engines
risk_engine = RiskAssessmentEngine()
ml_engine = MLPredictionEngine()
notification_service = NotificationService(mail)

# API Routes

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User authentication endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        
        if not email or not password or not role:
            return jsonify({'error': 'Missing credentials'}), 400
        
        user = SAMPLE_USERS.get(email)
        if not user or not check_password_hash(user['password'], password) or user['role'] != role:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(
            identity=email,
            additional_claims={'role': user['role'], 'name': user['name']}
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'email': email,
                'role': user['role'],
                'name': user['name']
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    """Get list of all students with risk assessment"""
    try:
        risk_filter = request.args.get('risk_level')
        
        students = list(students_collection.find({}, {'_id': 0}))
        
        # Apply risk assessment to each student
        for student in students:
            risk_assessment = risk_engine.assess_overall_risk(student)
            ml_probability = ml_engine.predict_dropout_probability(student)
            
            student.update(risk_assessment)
            student['ml_probability'] = ml_probability
        
        # Filter by risk level if specified
        if risk_filter:
            students = [s for s in students if s['risk_level'] == risk_filter]
        
        return jsonify({'students': students, 'total': len(students)})
        
    except Exception as e:
        logger.error(f"Get students error: {e}")
        return jsonify({'error': 'Failed to fetch students'}), 500

@app.route('/api/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_details(student_id):
    """Get detailed information for a specific student"""
    try:
        student = students_collection.find_one({'student_id': student_id}, {'_id': 0})
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Add risk assessment
        risk_assessment = risk_engine.assess_overall_risk(student)
        ml_probability = ml_engine.predict_dropout_probability(student)
        
        student.update(risk_assessment)
        student['ml_probability'] = ml_probability
        
        # Get notification history
        notifications = list(notifications_collection.find(
            {'student_id': student_id}, 
            {'_id': 0}
        ).sort('sent_at', -1).limit(10))
        
        student['notification_history'] = notifications
        
        return jsonify(student)
        
    except Exception as e:
        logger.error(f"Get student details error: {e}")
        return jsonify({'error': 'Failed to fetch student details'}), 500

@app.route('/api/upload/csv', methods=['POST'])
@jwt_required()
def upload_csv():
    """Upload and process CSV files (attendance, marks, fees)"""
    try:
        current_user = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        data_type = request.form.get('data_type')  # attendance, marks, or fees
        
        if not data_type or data_type not in ['attendance', 'marks', 'fees']:
            return jsonify({'error': 'Invalid data type'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        # Read CSV file
        csv_data = file.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_data))
        
        # Validate CSV structure
        validation_result = validate_csv_structure(df, data_type)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        # Process and merge data
        processed_count = process_csv_data(df, data_type)
        
        return jsonify({
            'message': f'Successfully processed {processed_count} records',
            'data_type': data_type,
            'processed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"CSV upload error: {e}")
        return jsonify({'error': 'Failed to process CSV file'}), 500

@app.route('/api/notifications/send', methods=['POST'])
@jwt_required()
def send_notification():
    """Send notification for at-risk students"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        recipients = data.get('recipients', [])
        
        if not student_id or not recipients:
            return jsonify({'error': 'Student ID and recipients required'}), 400
        
        student = students_collection.find_one({'student_id': student_id}, {'_id': 0})
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        risk_assessment = risk_engine.assess_overall_risk(student)
        risk_assessment['ml_probability'] = ml_engine.predict_dropout_probability(student)
        
        success = notification_service.send_risk_alert(student, recipients, risk_assessment)
        
        if success:
            return jsonify({'message': 'Notification sent successfully'})
        else:
            return jsonify({'error': 'Failed to send notification'}), 500
            
    except Exception as e:
        logger.error(f"Send notification error: {e}")
        return jsonify({'error': 'Failed to send notification'}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_students = students_collection.count_documents({})
        
        students = list(students_collection.find({}, {'_id': 0}))
        risk_counts = {'red': 0, 'yellow': 0, 'green': 0}
        
        for student in students:
            risk_assessment = risk_engine.assess_overall_risk(student)
            risk_counts[risk_assessment['risk_level']] += 1
        
        recent_notifications = list(notifications_collection.find(
            {}, {'_id': 0}
        ).sort('sent_at', -1).limit(5))
        
        stats = {
            'total_students': total_students,
            'high_risk_students': risk_counts['red'],
            'medium_risk_students': risk_counts['yellow'],
            'low_risk_students': risk_counts['green'],
            'recent_notifications': recent_notifications,
            'risk_distribution': risk_counts
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@app.route('/api/config/thresholds', methods=['GET', 'PUT'])
@jwt_required()
def manage_risk_thresholds():
    """Get or update risk assessment thresholds"""
    try:
        if request.method == 'GET':
            return jsonify(RISK_THRESHOLDS)
        
        # PUT request - update thresholds
        data = request.get_json()
        
        # Validate threshold values
        for key, value in data.items():
            if key in RISK_THRESHOLDS and isinstance(value, (int, float)) and 0 <= value <= 100:
                RISK_THRESHOLDS[key] = value
        
        # Update risk engine
        risk_engine.thresholds = RISK_THRESHOLDS
        
        return jsonify({
            'message': 'Thresholds updated successfully',
            'thresholds': RISK_THRESHOLDS
        })
        
    except Exception as e:
        logger.error(f"Threshold management error: {e}")
        return jsonify({'error': 'Failed to manage thresholds'}), 500

# Helper Functions

def validate_csv_structure(df, data_type):
    """Validate CSV file structure"""
    required_columns = {
        'attendance': ['student_id', 'student_name', 'total_classes', 'classes_attended'],
        'marks': ['student_id', 'student_name', 'subject', 'marks_obtained', 'max_marks'],
        'fees': ['student_id', 'student_name', 'total_fees', 'fees_paid']
    }
    
    expected_cols = required_columns.get(data_type, [])
    
    if not all(col in df.columns for col in expected_cols):
        missing_cols = [col for col in expected_cols if col not in df.columns]
        return {
            'valid': False,
            'message': f'Missing columns: {", ".join(missing_cols)}'
        }
    
    return {'valid': True, 'message': 'Valid structure'}

def process_csv_data(df, data_type):
    """Process and merge CSV data into student records"""
    processed_count = 0
    
    if data_type == 'attendance':
        for _, row in df.iterrows():
            student_data = {
                'student_id': int(row['student_id']),
                'student_name': row['student_name'],
                'total_classes': int(row['total_classes']),
                'classes_attended': int(row['classes_attended'])
            }
            
            students_collection.update_one(
                {'student_id': student_data['student_id']},
                {'$set': student_data},
                upsert=True
            )
            processed_count += 1
    
    elif data_type == 'marks':
        # Group marks by student
        for student_id, group in df.groupby('student_id'):
            subjects = []
            for _, row in group.iterrows():
                subjects.append({
                    'subject': row['subject'],
                    'marks_obtained': int(row['marks_obtained']),
                    'max_marks': int(row['max_marks']),
                    'status': 'pass' if int(row['marks_obtained']) >= int(row['max_marks']) * 0.4 else 'fail'
                })
            
            students_collection.update_one(
                {'student_id': int(student_id)},
                {
                    '$set': {
                        'student_name': group.iloc[0]['student_name'],
                        'subjects': subjects
                    }
                },
                upsert=True
            )
            processed_count += 1
    
    elif data_type == 'fees':
        for _, row in df.iterrows():
            fee_data = {
                'student_id': int(row['student_id']),
                'student_name': row['student_name'],
                'total_fees': int(row['total_fees']),
                'fees_paid': int(row['fees_paid'])
            }
            
            students_collection.update_one(
                {'student_id': fee_data['student_id']},
                {'$set': fee_data},
                upsert=True
            )
            processed_count += 1
    
    return processed_count

# Error Handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token'}), 401

@app.route('/api/version', methods=['GET'])
def version():
    return jsonify({
        "application": "EduPredict Backend API",
        "version": "1.0.0",
        "hackathon": "Smart India Hackathon 2025"
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "success",
        "message": "EduPredict Backend API is running",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# Initialize sample data
def init_sample_data():
    """Initialize database with sample student data"""
    if students_collection.count_documents({}) == 0:
        sample_students = [
            {
                "student_id": 1,
                "student_name": "Rahul Sharma",
                "total_classes": 50,
                "classes_attended": 35,
                "subjects": [
                    {"subject": "Math", "marks_obtained": 42, "max_marks": 100, "status": "fail"},
                    {"subject": "Physics", "marks_obtained": 78, "max_marks": 100, "status": "pass"},
                    {"subject": "Chemistry", "marks_obtained": 35, "max_marks": 100, "status": "fail"}
                ],
                "total_fees": 50000,
                "fees_paid": 30000
            },
            {
                "student_id": 2,
                "student_name": "Priya Patel", 
                "total_classes": 48,
                "classes_attended": 40,
                "subjects": [
                    {"subject": "Math", "marks_obtained": 65, "max_marks": 100, "status": "pass"},
                    {"subject": "Physics", "marks_obtained": 58, "max_marks": 100, "status": "pass"},
                    {"subject": "Chemistry", "marks_obtained": 72, "max_marks": 100, "status": "pass"}
                ],
                "total_fees": 50000,
                "fees_paid": 45000
            }
        ]
        
        students_collection.insert_many(sample_students)
        logger.info("Sample data initialized")

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    init_sample_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
