"""
🇧🇩 BENGALI NLP ADVANCED
Advanced Bengali Language Processing
"""

import re
import json
import random
from typing import List, Dict, Tuple
import numpy as np
from collections import defaultdict

class BengaliNLP:
    def __init__(self):
        self.bengali_stopwords = self.load_bengali_stopwords()
        self.sentiment_words = self.load_sentiment_words()
        self.response_patterns = self.load_response_patterns()
        
    def load_bengali_stopwords(self):
        """Load Bengali stopwords"""
        return {
            'এবং', 'আর', 'ও', 'কিন্তু', 'যে', 'যিনি', 'যারা', 'যার', 'তা', 'তাই', 
            'তিনি', 'তুমি', 'তোমার', 'তারা', 'তার', 'এই', 'একটি', 'এক', 'কি', 'কী',
            'কেন', 'কোথায়', 'কখন', 'কেমন', 'কে', 'কাউকে', 'কিছু', 'সব', 'সেটা',
            'হয়', 'হচ্ছে', 'হয়েছে', 'হবেন', 'নেই', 'না', 'নয়', 'হবে', 'হতো'
        }
    
    def load_sentiment_words(self):
        """Load sentiment words"""
        return {
            "positive": {
                "bn": ["ভাল", "সুন্দর", "চমৎকার", "বেশ", "মজা", "খুশি", "আনন্দ", "প্রশংসা"],
                "en": ["good", "nice", "excellent", "great", "happy", "joy", "praise"]
            },
            "negative": {
                "bn": ["খারাপ", "মন্দ", "অসুন্দর", "বাজে", "দুঃখ", "কষ্ট", "সমস্যা"],
                "en": ["bad", "poor", "ugly", "sad", "pain", "problem"]
            },
            "neutral": {
                "bn": ["ঠিক", "সাধারণ", "মোটামুটি", "হল", "হয়"],
                "en": ["ok", "normal", "average", "is", "am"]
            }
        }
    
    def load_response_patterns(self):
        """Load response patterns"""
        return {
            "greeting": {
                "bn": [
                    "হ্যালো! আমি MASTER 🪓, আপনার AI সহায়ক।",
                    "নমস্কার! কেমন আছেন?",
                    "আসসালামু আলাইকুম! আমি আপনার সাথে আছি।"
                ],
                "en": [
                    "Hello! I'm MASTER 🪓, your AI assistant.",
                    "Hi there! How can I help you today?",
                    "Greetings! I'm here to assist you."
                ]
            },
            "question": {
                "bn": [
                    "আপনি কি জানতে চান {} সম্পর্কে?",
                    "{} - এটি একটি ভাল প্রশ্ন।",
                    "আমি {} সম্পর্কে তথ্য দিতে পারি।"
                ],
                "en": [
                    "Do you want to know about {}?",
                    "{} - that's a good question.",
                    "I can provide information about {}."
                ]
            },
            "thanks": {
                "bn": [
                    "আপনাকেও ধন্যবাদ!",
                    "কিছু না, সাহায্য করতে পেরে ভালো লাগলো।",
                    "আরও কোনো সাহায্য লাগলে জানাবেন।"
                ],
                "en": [
                    "You're welcome!",
                    "No problem, happy to help!",
                    "Let me know if you need anything else."
                ]
            },
            "unknown": {
                "bn": [
                    "দুঃখিত, আমি এখনো এটি শিখিনি।",
                    "আমি এই প্রশ্নের উত্তর এখনো জানি না।",
                    "এটি সম্পর্কে আমি এখনো শিখিনি, কিন্তু শিখবো!"
                ],
                "en": [
                    "Sorry, I haven't learned that yet.",
                    "I don't know the answer to that question yet.",
                    "I haven't learned about that yet, but I will!"
                ]
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Detect if text is Bengali or English"""
        # Count Bengali characters
        bengali_pattern = re.compile(r'[\u0980-\u09FF]')
        bengali_count = len(bengali_pattern.findall(text))
        
        # Count English characters
        english_pattern = re.compile(r'[a-zA-Z]')
        english_count = len(english_pattern.findall(text))
        
        if bengali_count > english_count:
            return "bengali"
        elif english_count > bengali_count:
            return "english"
        else:
            return "mixed"
    
    def extract_keywords_bengali(self, text: str) -> List[str]:
        """Extract keywords from Bengali text"""
        # Remove punctuation
        text = re.sub(r'[^\u0980-\u09FF\s]', '', text)
        
        # Split into words
        words = text.split()
        
        # Remove stopwords
        keywords = [word for word in words 
                   if word not in self.bengali_stopwords and len(word) > 1]
        
        # Remove duplicates but preserve order
        seen = set()
        unique_keywords = []
        for word in keywords:
            if word not in seen:
                seen.add(word)
                unique_keywords.append(word)
        
        return unique_keywords[:10]  # Return top 10 keywords
    
    def extract_keywords_english(self, text: str) -> List[str]:
        """Extract keywords from English text"""
        # Convert to lowercase and remove punctuation
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Split into words
        words = text.split()
        
        # Simple English stopwords
        english_stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'is', 'am', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could'
        }
        
        # Remove stopwords
        keywords = [word for word in words 
                   if word not in english_stopwords and len(word) > 2]
        
        # Remove duplicates
        return list(set(keywords))[:10]
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        text_lower = text.lower()
        
        positive_count = 0
        negative_count = 0
        
        # Check Bengali positive words
        for word in self.sentiment_words["positive"]["bn"]:
            if word in text_lower:
                positive_count += 1
        
        # Check Bengali negative words
        for word in self.sentiment_words["negative"]["bn"]:
            if word in text_lower:
                negative_count += 1
        
        # Check English positive words
        for word in self.sentiment_words["positive"]["en"]:
            if word in text_lower:
                positive_count += 1
        
        # Check English negative words
        for word in self.sentiment_words["negative"]["en"]:
            if word in text_lower:
                negative_count += 1
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def generate_response(self, message: str) -> str:
        """Generate intelligent response"""
        language = self.detect_language(message)
        sentiment = self.analyze_sentiment(message)
        
        # Extract intent
        if any(word in message.lower() for word in ["হ্যালো", "হাই", "hello", "hi"]):
            intent = "greeting"
        elif any(word in message.lower() for word in ["ধন্যবাদ", "থ্যাংকস", "thank"]):
            intent = "thanks"
        elif "?" in message:
            intent = "question"
        else:
            intent = "unknown"
        
        # Get appropriate response pattern
        if intent in self.response_patterns:
            patterns = self.response_patterns[intent].get(language, 
                                                         self.response_patterns[intent]["en"])
            
            if intent == "question":
                # Extract main topic from question
                keywords = (self.extract_keywords_bengali(message) 
                           if language == "bengali" 
                           else self.extract_keywords_english(message))
                topic = keywords[0] if keywords else "এটি"
                
                # Format response with topic
                response = random.choice(patterns).format(topic)
            else:
                response = random.choice(patterns)
        else:
            response = random.choice(self.response_patterns["unknown"][language])
        
        # Add sentiment-based modifier
        if sentiment == "positive":
            modifiers = [" 😊", " 👍", " 🎉"]
            response += random.choice(modifiers)
        elif sentiment == "negative":
            modifiers = [" 😔", " 🤗", " 💪"]
            response += random.choice(modifiers)
        
        return response
    
    def translate_bengali_to_english(self, text: str) -> str:
        """Simple Bengali to English translation (basic)"""
        # Basic word mapping
        translation_dict = {
            "হ্যালো": "Hello",
            "কেমন": "how",
            "আছেন": "are you",
            "ধন্যবাদ": "thank you",
            "নাম": "name",
            "কি": "what",
            "কেন": "why",
            "কখন": "when",
            "কোথায়": "where",
            "কে": "who"
        }
        
        words = text.split()
        translated_words = []
        
        for word in words:
            if word in translation_dict:
                translated_words.append(translation_dict[word])
            else:
                translated_words.append(word)
        
        return " ".join(translated_words)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Simple Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def extract_named_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text (simplified)"""
        entities = []
        
        # Patterns for different entity types
        patterns = {
            "name": r'(?:(?:শ্রী|জনাব|মিস্টার|মিস|মিসেস)\s+)?([আ-হ]{2,})(?:\s+([আ-হ]{2,}))?',
            "location": r'([আ-হ]+(?:গ্রাম|নগর|পুর|বাদ|খালি|বাজার|রোড|স্ট্রিট))',
            "organization": r'([আ-হ]+(?:বিদ্যালয়|কলেজ|বিশ্ববিদ্যালয়|কোম্পানি|লিমিটেড|ট্রাস্ট))'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    "text": match.group(),
                    "type": entity_type,
                    "start": match.start(),
                    "end": match.end()
                })
        
        return entities