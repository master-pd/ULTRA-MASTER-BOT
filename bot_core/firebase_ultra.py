"""
📦 FIREBASE ULTRA - Complete Firebase Integration
"""

import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class FirebaseUltra:
    def __init__(self):
        self.db = None
        self.bucket = None
        self.auth_client = None
        self.initialized = False
        self.initialize()
    
    def initialize(self):
        """Initialize Firebase with service account"""
        try:
            # Check if already initialized
            if len(firebase_admin._apps) > 0:
                self.db = firestore.client()
                self.bucket = storage.bucket()
                self.auth_client = auth
                self.initialized = True
                print("✅ Firebase already initialized")
                return
            
            # Load credentials from environment or file
            cred_path = "config/firebase_credentials.json"
            
            if os.path.exists(cred_path):
                # Load from file
                cred = credentials.Certificate(cred_path)
            else:
                # Load from environment variables
                cred_dict = {
                    "type": "service_account",
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
                }
                
                cred = credentials.Certificate(cred_dict)
            
            # Initialize Firebase
            firebase_admin.initialize_app(cred, {
                'storageBucket': f"{os.getenv('FIREBASE_PROJECT_ID')}.appspot.com"
            })
            
            self.db = firestore.client()
            self.bucket = storage.bucket()
            self.auth_client = auth
            self.initialized = True
            
            print("✅ Firebase initialized successfully!")
            
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            self.initialized = False
    
    # ========== FIRESTORE DATABASE OPERATIONS ==========
    
    def save_conversation(self, conversation_data: Dict) -> str:
        """Save conversation to Firestore"""
        if not self.initialized:
            return None
        
        try:
            doc_ref = self.db.collection('conversations').document()
            conversation_data.update({
                'created_at': datetime.now(),
                'bot_name': 'MASTER 🪓',
                'processed': False
            })
            doc_ref.set(conversation_data)
            return doc_ref.id
            
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")
            return None
    
    def save_knowledge(self, knowledge_data: Dict) -> str:
        """Save learned knowledge"""
        if not self.initialized:
            return None
        
        try:
            doc_ref = self.db.collection('knowledge').document()
            knowledge_data.update({
                'learned_at': datetime.now(),
                'confidence': knowledge_data.get('confidence', 0.5),
                'verified': False,
                'source': knowledge_data.get('source', 'bot_learning')
            })
            doc_ref.set(knowledge_data)
            return doc_ref.id
            
        except Exception as e:
            print(f"❌ Error saving knowledge: {e}")
            return None
    
    def save_diagram(self, diagram_data: Dict) -> str:
        """Save diagram data"""
        if not self.initialized:
            return None
        
        try:
            # Remove base64 image if too large
            if 'image_base64' in diagram_data:
                if len(diagram_data['image_base64']) > 100000:  # 100KB limit
                    diagram_data['image_base64'] = "TOO_LARGE"
            
            doc_ref = self.db.collection('diagrams').document()
            diagram_data.update({
                'created_at': datetime.now(),
                'bot_version': '4.0 ULTRA'
            })
            doc_ref.set(diagram_data)
            return doc_ref.id
            
        except Exception as e:
            print(f"❌ Error saving diagram: {e}")
            return None
    
    def save_image(self, image_data: Dict) -> str:
        """Save image data"""
        if not self.initialized:
            return None
        
        try:
            # Remove base64 image if too large
            if 'image_base64' in image_data:
                if len(image_data['image_base64']) > 100000:  # 100KB limit
                    image_data['image_base64'] = "TOO_LARGE"
            
            doc_ref = self.db.collection('images').document()
            image_data.update({
                'created_at': datetime.now(),
                'bot_version': '4.0 ULTRA'
            })
            doc_ref.set(image_data)
            return doc_ref.id
            
        except Exception as e:
            print(f"❌ Error saving image: {e}")
            return None
    
    def get_recent_conversations(self, limit: int = 50) -> List[Dict]:
        """Get recent conversations"""
        if not self.initialized:
            return []
        
        try:
            docs = self.db.collection('conversations') \
                         .order_by('created_at', direction=firestore.Query.DESCENDING) \
                         .limit(limit) \
                         .stream()
            
            conversations = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                conversations.append(data)
            
            return conversations
            
        except Exception as e:
            print(f"❌ Error getting conversations: {e}")
            return []
    
    def get_knowledge_by_topic(self, topic: str, limit: int = 20) -> List[Dict]:
        """Get knowledge by topic"""
        if not self.initialized:
            return []
        
        try:
            docs = self.db.collection('knowledge') \
                         .where('topic', '==', topic) \
                         .order_by('confidence', direction=firestore.Query.DESCENDING) \
                         .limit(limit) \
                         .stream()
            
            knowledge = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                knowledge.append(data)
            
            return knowledge
            
        except Exception as e:
            print(f"❌ Error getting knowledge: {e}")
            return []
    
    # ========== FIREBASE STORAGE OPERATIONS ==========
    
    def upload_file(self, file_path: str, destination_path: str) -> str:
        """Upload file to Firebase Storage"""
        if not self.initialized:
            return None
        
        try:
            blob = self.bucket.blob(destination_path)
            blob.upload_from_filename(file_path)
            
            # Make public
            blob.make_public()
            
            print(f"✅ File uploaded: {destination_path}")
            return blob.public_url
            
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            return None
    
    def upload_bytes(self, data: bytes, destination_path: str, content_type: str = 'application/octet-stream') -> str:
        """Upload bytes to Firebase Storage"""
        if not self.initialized:
            return None
        
        try:
            blob = self.bucket.blob(destination_path)
            blob.upload_from_string(data, content_type=content_type)
            
            # Make public
            blob.make_public()
            
            print(f"✅ Bytes uploaded: {destination_path}")
            return blob.public_url
            
        except Exception as e:
            print(f"❌ Error uploading bytes: {e}")
            return None
    
    def download_file(self, source_path: str, destination_path: str) -> bool:
        """Download file from Firebase Storage"""
        if not self.initialized:
            return False
        
        try:
            blob = self.bucket.blob(source_path)
            blob.download_to_filename(destination_path)
            
            print(f"✅ File downloaded: {source_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error downloading file: {e}")
            return False
    
    # ========== STATISTICS & ANALYTICS ==========
    
    def get_statistics(self) -> Dict:
        """Get bot statistics"""
        if not self.initialized:
            return {}
        
        try:
            stats = {}
            
            # Count conversations
            conv_count = self.db.collection('conversations').count().get()[0][0].value
            stats['total_conversations'] = conv_count
            
            # Count knowledge items
            know_count = self.db.collection('knowledge').count().get()[0][0].value
            stats['total_knowledge'] = know_count
            
            # Count diagrams
            diagram_count = self.db.collection('diagrams').count().get()[0][0].value
            stats['total_diagrams'] = diagram_count
            
            # Count images
            image_count = self.db.collection('images').count().get()[0][0].value
            stats['total_images'] = image_count
            
            # Get today's counts
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            today_convs = self.db.collection('conversations') \
                                .where('created_at', '>=', today) \
                                .count().get()[0][0].value
            stats['conversations_today'] = today_convs
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def save_bot_stats(self, stats: Dict):
        """Save bot statistics"""
        if not self.initialized:
            return
        
        try:
            doc_ref = self.db.collection('bot_stats').document()
            stats.update({
                'timestamp': datetime.now(),
                'bot_name': 'MASTER 🪓',
                'version': '4.0 ULTRA'
            })
            doc_ref.set(stats)
            
        except Exception as e:
            print(f"❌ Error saving bot stats: {e}")
    
    # ========== BACKUP & RESTORE ==========
    
    def backup_data(self, backup_name: str = None):
        """Backup all data to Firebase"""
        if not self.initialized:
            return False
        
        try:
            if backup_name is None:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Collect all data
            all_data = {
                'conversations': [],
                'knowledge': [],
                'diagrams': [],
                'images': []
            }
            
            # Backup conversations
            conv_docs = self.db.collection('conversations').limit(1000).stream()
            for doc in conv_docs:
                data = doc.to_dict()
                data['id'] = doc.id
                all_data['conversations'].append(data)
            
            # Backup knowledge
            know_docs = self.db.collection('knowledge').limit(1000).stream()
            for doc in know_docs:
                data = doc.to_dict()
                data['id'] = doc.id
                all_data['knowledge'].append(data)
            
            # Convert to JSON
            backup_json = json.dumps(all_data, default=str, indent=2)
            
            # Upload to storage
            backup_path = f"backups/{backup_name}.json"
            url = self.upload_bytes(backup_json.encode(), backup_path, 'application/json')
            
            if url:
                print(f"✅ Backup created: {url}")
                return url
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False
    
    # ========== REAL-TIME UPDATES ==========
    
    def setup_realtime_listener(self, collection: str, callback):
        """Setup real-time listener for collection"""
        if not self.initialized:
            return None
        
        try:
            def on_snapshot(col_snapshot, changes, read_time):
                for change in changes:
                    if change.type.name == 'ADDED':
                        data = change.document.to_dict()
                        data['id'] = change.document.id
                        callback('added', data)
                    elif change.type.name == 'MODIFIED':
                        data = change.document.to_dict()
                        data['id'] = change.document.id
                        callback('modified', data)
                    elif change.type.name == 'REMOVED':
                        callback('removed', change.document.id)
            
            # Create listener
            query = self.db.collection(collection)
            listener = query.on_snapshot(on_snapshot)
            
            return listener
            
        except Exception as e:
            print(f"❌ Error setting up listener: {e}")
            return None