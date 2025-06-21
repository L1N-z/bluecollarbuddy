import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class WhatsAppDatabase:
    def __init__(self, db_path: str = "whatsapp_agent.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_sid TEXT UNIQUE,
                from_number TEXT NOT NULL,
                to_number TEXT NOT NULL,
                body TEXT,
                direction TEXT CHECK(direction IN ('inbound', 'outbound')),
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE,
                intent TEXT,
                sentiment TEXT,
                entities TEXT
            )
        ''')
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT UNIQUE NOT NULL,
                first_contact DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_contact DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Agent responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                response_text TEXT NOT NULL,
                response_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages (id)
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                total_messages INTEGER DEFAULT 0,
                inbound_messages INTEGER DEFAULT 0,
                outbound_messages INTEGER DEFAULT 0,
                unique_contacts INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    
    def save_message(self, message_data: Dict) -> int:
        """Save a message to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO messages 
                (message_sid, from_number, to_number, body, direction, status, intent, sentiment, entities)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_data.get('message_sid'),
                message_data.get('from_number'),
                message_data.get('to_number'),
                message_data.get('body'),
                message_data.get('direction'),
                message_data.get('status'),
                message_data.get('intent'),
                message_data.get('sentiment'),
                json.dumps(message_data.get('entities', {}))
            ))
            
            message_id = cursor.lastrowid
            
            # Update or create conversation
            phone_number = message_data.get('from_number') if message_data.get('direction') == 'inbound' else message_data.get('to_number')
            self.update_conversation(cursor, phone_number)
            
            conn.commit()
            return message_id
            
        except sqlite3.IntegrityError as e:
            print(f"Message already exists: {e}")
            return None
        finally:
            conn.close()
    
    def update_conversation(self, cursor, phone_number: str):
        """Update conversation record"""
        cursor.execute('''
            INSERT OR REPLACE INTO conversations 
            (phone_number, first_contact, last_contact, message_count)
            VALUES (
                ?, 
                COALESCE((SELECT first_contact FROM conversations WHERE phone_number = ?), CURRENT_TIMESTAMP),
                CURRENT_TIMESTAMP,
                COALESCE((SELECT message_count FROM conversations WHERE phone_number = ?), 0) + 1
            )
        ''', (phone_number, phone_number, phone_number))
    
    def save_agent_response(self, message_id: int, response_text: str, response_type: str = 'automated'):
        """Save agent response to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_responses (message_id, response_text, response_type)
            VALUES (?, ?, ?)
        ''', (message_id, response_text, response_type))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, phone_number: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a phone number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, ar.response_text, ar.response_type
            FROM messages m
            LEFT JOIN agent_responses ar ON m.id = ar.message_id
            WHERE m.from_number = ? OR m.to_number = ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        ''', (phone_number, phone_number, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_analytics(self, days: int = 7) -> Dict:
        """Get analytics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get message counts
        cursor.execute('''
            SELECT 
                COUNT(*) as total_messages,
                SUM(CASE WHEN direction = 'inbound' THEN 1 ELSE 0 END) as inbound_messages,
                SUM(CASE WHEN direction = 'outbound' THEN 1 ELSE 0 END) as outbound_messages
            FROM messages 
            WHERE timestamp >= datetime('now', '-{} days')
        '''.format(days))
        
        message_stats = cursor.fetchone()
        
        # Get unique contacts
        cursor.execute('''
            SELECT COUNT(DISTINCT 
                CASE WHEN direction = 'inbound' THEN from_number ELSE to_number END
            ) as unique_contacts
            FROM messages 
            WHERE timestamp >= datetime('now', '-{} days')
        '''.format(days))
        
        unique_contacts = cursor.fetchone()[0]
        
        # Get intent distribution
        cursor.execute('''
            SELECT intent, COUNT(*) as count
            FROM messages 
            WHERE timestamp >= datetime('now', '-{} days') AND intent IS NOT NULL
            GROUP BY intent
        '''.format(days))
        
        intent_distribution = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_messages': message_stats[0],
            'inbound_messages': message_stats[1],
            'outbound_messages': message_stats[2],
            'unique_contacts': unique_contacts,
            'intent_distribution': intent_distribution
        }
    
    def export_data(self, table_name: str, output_file: str):
        """Export table data to JSON file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        data = [dict(zip(columns, row)) for row in rows]
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        conn.close()
        print(f"Exported {len(data)} records from {table_name} to {output_file}")

# Example usage
if __name__ == "__main__":
    db = WhatsAppDatabase()
    
    # Test saving a message
    test_message = {
        'message_sid': 'SM123456789',
        'from_number': 'whatsapp:+1234567890',
        'to_number': 'whatsapp:+1987654321',
        'body': 'Hello, I need help with my order',
        'direction': 'inbound',
        'status': 'received',
        'intent': 'order',
        'sentiment': 'neutral',
        'entities': {'order_numbers': ['ORD123456']}
    }
    
    message_id = db.save_message(test_message)
    if message_id:
        print(f"Message saved with ID: {message_id}")
        
        # Save agent response
        db.save_agent_response(message_id, "I'd be happy to help with your order. Could you please provide your order number?")
        print("Agent response saved")
    
    # Get analytics
    analytics = db.get_analytics(7)
    print(f"Analytics: {json.dumps(analytics, indent=2)}")
    
    # Export data
    db.export_data('messages', 'messages_export.json')
