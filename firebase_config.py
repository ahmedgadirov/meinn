import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Path to service account credentials file
credentials_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', '/home/ahmd/Downloads/meinn-aa13d-firebase-adminsdk-fbsvc-106c3608d5.json')

# Firebase project ID
project_id = os.environ.get('FIREBASE_PROJECT_ID', 'meinn-aa13d')

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with provided credentials"""
    if not firebase_admin._apps:
        try:
            # Check if running on Vercel (environment variable as JSON string)
            firebase_credentials_json = os.environ.get('FIREBASE_CREDENTIALS')
            
            if firebase_credentials_json:
                # Parse JSON string from environment variable
                cred_dict = json.loads(firebase_credentials_json)
                cred = credentials.Certificate(cred_dict)
            else:
                # Use local credentials file
                cred = credentials.Certificate(credentials_path)
                
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
            
            print(f"Firebase initialized with project ID: {project_id}")
        except Exception as e:
            print(f"Error initializing Firebase: {str(e)}")
            raise e
    
    return firestore.client()

# Get Firestore client
def get_firestore_client():
    """Get Firestore client, initializing Firebase if necessary"""
    if not firebase_admin._apps:
        return initialize_firebase()
    return firestore.client()
