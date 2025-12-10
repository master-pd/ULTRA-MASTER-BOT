"""
💾 MEMORY ULTRA - Advanced Memory System
With Long-term & Short-term Memory
"""

import json
import pickle
import sqlite3
from datetime import datetime, timedelta
from collections import OrderedDict
import hashlib
from typing import Dict, List, Optional
import numpy as np

class MemoryUltra:
    def __init__(self):
        self.memory_file = "data/memory.db"
        self.cache_size = 1000
        self.short_term_cache = OrderedDict()
        self.long_term_memory = {}
        
        self.init_database()
        self.load_memory()
    
    def init_database(self):
        """Initialize SQLite database for memory"""
        self.conn = sqlite3.connect(self.memory_file)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                message TEXT,
                response TEXT,
                timestamp DATETIME,
                context TEXT,
                sentiment TEXT,
                learned INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id TEXT PRIMARY KEY,
                topic TEXT,
                content TEXT,
                source TEXT,
                confidence REAL,
                last_used DATETIME,
                use_count INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                pattern_type TEXT,
                pattern_data TEXT,
                frequency INTEGER,
                last_seen DATETIME
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                preferences TEXT,
                interaction_count INTEGER DEFAULT 0,
                last_interaction DATETIME,
                sentiment_history TEXT
            )
        ''')
        
        self.conn.commit()
    
    def generate_id(self, text: str) -> str:
        """Generate unique ID from text"""
        return hashlib.md5(text.encode()).hexdigest()[:16]
    
    def store_conversation(self, user_id: str, message: str, response: str, 
                          context: str = "", sentiment: str = "neutral"):
        """Store conversation in memory"""
        conv_id = self.generate_id(f"{user_id}_{message}_{datetime.now().timestamp()}")
        
        # Store in short-term cache
        self.short_term_cache[conv_id] = {
            "user_id": user_id,
            "message": message,
            "response": response,
            "timestamp": datetime.now(),
            "context": context,
            "sentiment": sentiment
        }
        
        # Maintain cache size
        if len(self.short_term_cache) > self.cache_size:
            self.short_term_cache.popitem(last=False)
        
        # Store in database
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO conversations 
                (id, user_id, message, response, timestamp, context, sentiment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (conv_id, user_id, message, response, 
                  datetime.now().isoformat(), context, sentiment))
            
            # Update user profile
            self.update_user_profile(user_id, message, sentiment)
            
            # Extract patterns
            self.extract_patterns(message, response)
            
            self.conn.commit()
            
        except Exception as e:
            print(f"❌ Error storing conversation: {e}")
    
    def recall_conversation(self, user_id: str, message: str) -> Optional[str]:
        """Recall similar conversation from memory"""
        # Check short-term cache first
        for conv in self.short_term_cache.values():
            if conv["user_id"] == user_id:
                similarity = self.calculate_similarity(message, conv["message"])
                if similarity > 0.8:  # 80% similar
                    return conv["response"]
        
        # Check database for similar conversations
        try:
            self.cursor.execute('''
                SELECT message, response FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 50
            ''', (user_id,))
            
            rows = self.cursor.fetchall()
            
            for db_message, db_response in rows:
                similarity = self.calculate_similarity(message, db_message)
                if similarity > 0.7:  # 70% similar
                    # Update use count
                    self.cursor.execute('''
                        UPDATE conversations SET learned = learned + 1 
                        WHERE message = ? AND response = ?
                    ''', (db_message, db_response))
                    self.conn.commit()
                    
                    return db_response
                    
        except Exception as e:
            print(f"❌ Error recalling conversation: {e}")
        
        return None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Simple Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def store_knowledge(self, topic: str, content: str, source: str = "learned", 
                       confidence: float = 0.5):
        """Store knowledge in long-term memory"""
        knowledge_id = self.generate_id(f"{topic}_{content}")
        
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO knowledge 
                (id, topic, content, source, confidence, last_used, use_count)
                VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT use_count FROM knowledge WHERE id = ?), 0) + 1)
            ''', (knowledge_id, topic, content, source, confidence, 
                  datetime.now().isoformat(), knowledge_id))
            
            self.conn.commit()
            
            # Also store in memory cache
            if topic not in self.long_term_memory:
                self.long_term_memory[topic] = []
            
            self.long_term_memory[topic].append({
                "content": content,
                "confidence": confidence,
                "source": source,
                "timestamp": datetime.now()
            })
            
        except Exception as e:
            print(f"❌ Error storing knowledge: {e}")
    
    def get_knowledge(self, topic: str, min_confidence: float = 0.3) -> List[Dict]:
        """Retrieve knowledge about a topic"""
        results = []
        
        try:
            self.cursor.execute('''
                SELECT content, confidence, source FROM knowledge 
                WHERE topic LIKE ? AND confidence >= ?
                ORDER BY confidence DESC, use_count DESC
                LIMIT 10
            ''', (f"%{topic}%", min_confidence))
            
            rows = self.cursor.fetchall()
            
            for content, confidence, source in rows:
                results.append({
                    "content": content,
                    "confidence": confidence,
                    "source": source
                })
                
                # Update last used
                self.cursor.execute('''
                    UPDATE knowledge SET last_used = ?, use_count = use_count + 1
                    WHERE content = ? AND topic = ?
                ''', (datetime.now().isoformat(), content, topic))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"❌ Error retrieving knowledge: {e}")
        
        return results
    
    def update_user_profile(self, user_id: str, message: str, sentiment: str):
        """Update user profile with interaction"""
        try:
            # Check if user exists
            self.cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
            user = self.cursor.fetchone()
            
            if user:
                # Update existing user
                self.cursor.execute('''
                    UPDATE user_profiles 
                    SET interaction_count = interaction_count + 1,
                        last_interaction = ?,
                        sentiment_history = COALESCE(sentiment_history, '') || ?
                    WHERE user_id = ?
                ''', (datetime.now().isoformat(), f"{sentiment},", user_id))
            else:
                # Create new user profile
                self.cursor.execute('''
                    INSERT INTO user_profiles 
                    (user_id, interaction_count, last_interaction, sentiment_history)
                    VALUES (?, 1, ?, ?)
                ''', (user_id, datetime.now().isoformat(), f"{sentiment},"))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"❌ Error updating user profile: {e}")
    
    def extract_patterns(self, message: str, response: str):
        """Extract patterns from conversations"""
        # Simple pattern extraction
        words = message.lower().split()
        
        if len(words) >= 3:
            # Extract common patterns (trigrams)
            for i in range(len(words) - 2):
                pattern = " ".join(words[i:i+3])
                pattern_id = self.generate_id(pattern)
                
                try:
                    self.cursor.execute('''
                        INSERT OR REPLACE INTO patterns 
                        (id, pattern_type, pattern_data, frequency, last_seen)
                        VALUES (?, 'trigram', ?, 
                                COALESCE((SELECT frequency FROM patterns WHERE id = ?), 0) + 1,
                                ?)
                    ''', (pattern_id, pattern, pattern_id, datetime.now().isoformat()))
                    
                    self.conn.commit()
                    
                except Exception as e:
                    print(f"❌ Error extracting pattern: {e}")
    
    def get_user_patterns(self, user_id: str) -> List[Dict]:
        """Get conversation patterns for a user"""
        patterns = []
        
        try:
            self.cursor.execute('''
                SELECT message, response, COUNT(*) as frequency
                FROM conversations
                WHERE user_id = ?
                GROUP BY message, response
                HAVING COUNT(*) > 1
                ORDER BY frequency DESC
                LIMIT 20
            ''', (user_id,))
            
            rows = self.cursor.fetchall()
            
            for message, response, frequency in rows:
                patterns.append({
                    "message": message,
                    "response": response,
                    "frequency": frequency
                })
                
        except Exception as e:
            print(f"❌ Error getting user patterns: {e}")
        
        return patterns
    
    def cleanup_old_memories(self, days_old: int = 30):
        """Clean up old memories"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            # Delete old conversations with low learning value
            self.cursor.execute('''
                DELETE FROM conversations 
                WHERE timestamp < ? AND learned = 0
            ''', (cutoff_date,))
            
            # Delete old knowledge with low confidence
            self.cursor.execute('''
                DELETE FROM knowledge 
                WHERE last_used < ? AND confidence < 0.3
            ''', (cutoff_date,))
            
            # Delete old patterns with low frequency
            self.cursor.execute('''
                DELETE FROM patterns 
                WHERE last_seen < ? AND frequency < 3
            ''', (cutoff_date,))
            
            deleted_count = self.cursor.rowcount
            self.conn.commit()
            
            print(f"🧹 Cleaned up {deleted_count} old memories")
            
        except Exception as e:
            print(f"❌ Error cleaning up memories: {e}")
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        stats = {}
        
        try:
            # Conversation stats
            self.cursor.execute('SELECT COUNT(*) FROM conversations')
            stats["total_conversations"] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(DISTINCT user_id) FROM conversations')
            stats["unique_users"] = self.cursor.fetchone()[0]
            
            # Knowledge stats
            self.cursor.execute('SELECT COUNT(*) FROM knowledge')
            stats["knowledge_items"] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(DISTINCT topic) FROM knowledge')
            stats["unique_topics"] = self.cursor.fetchone()[0]
            
            # Pattern stats
            self.cursor.execute('SELECT COUNT(*) FROM patterns')
            stats["patterns"] = self.cursor.fetchone()[0]
            
            # Recent activity
            self.cursor.execute('''
                SELECT COUNT(*) FROM conversations 
                WHERE timestamp > datetime('now', '-1 day')
            ''')
            stats["conversations_today"] = self.cursor.fetchone()[0]
            
        except Exception as e:
            print(f"❌ Error getting memory stats: {e}")
        
        return stats
    
    def backup_memory(self, backup_path: str = None):
        """Backup memory database"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backups/memory_backup_{timestamp}.db"
        
        try:
            # Create backup
            backup_conn = sqlite3.connect(backup_path)
            self.conn.backup(backup_conn)
            backup_conn.close()
            
            print(f"💾 Memory backed up to: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Error backing up memory: {e}")
            return None
    
    def load_memory(self):
        """Load memory from database into cache"""
        try:
            # Load recent conversations into cache
            self.cursor.execute('''
                SELECT * FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (self.cache_size,))
            
            rows = self.cursor.fetchall()
            
            for row in rows:
                conv_id, user_id, message, response, timestamp, context, sentiment, learned = row
                
                self.short_term_cache[conv_id] = {
                    "user_id": user_id,
                    "message": message,
                    "response": response,
                    "timestamp": datetime.fromisoformat(timestamp),
                    "context": context,
                    "sentiment": sentiment
                }
            
            # Load knowledge into memory
            self.cursor.execute('SELECT DISTINCT topic FROM knowledge LIMIT 100')
            topics = self.cursor.fetchall()
            
            for (topic,) in topics:
                self.long_term_memory[topic] = []
                
                self.cursor.execute('''
                    SELECT content, confidence, source FROM knowledge 
                    WHERE topic = ? 
                    ORDER BY confidence DESC 
                    LIMIT 5
                ''', (topic,))
                
                knowledge_rows = self.cursor.fetchall()
                
                for content, confidence, source in knowledge_rows:
                    self.long_term_memory[topic].append({
                        "content": content,
                        "confidence": confidence,
                        "source": source
                    })
            
            print(f"🧠 Memory loaded: {len(self.short_term_cache)} conversations, {len(self.long_term_memory)} topics")
            
        except Exception as e:
            print(f"❌ Error loading memory: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.conn.close()
        except:
            pass