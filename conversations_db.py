"""
Conversation Database - SQLite storage for chat history
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class ConversationsDB:
    """Manage conversation storage in SQLite"""

    def __init__(self, db_path: str = "data/conversations.db"):
        """Initialize database connection"""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                type TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_updated
            ON conversations(updated_at DESC)
        """)

        self.conn.commit()

    def create_conversation(self, conversation_id: str) -> Dict:
        """Create a new conversation"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO conversations (id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (conversation_id, "New conversation", now, now))

        self.conn.commit()

        return {
            "id": conversation_id,
            "title": "New conversation",
            "messages": [],
            "createdAt": now,
            "updatedAt": now
        }

    def get_all_conversations(self) -> List[Dict]:
        """Get all conversations ordered by most recent"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT id, title, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC
        """)

        conversations = []
        for row in cursor.fetchall():
            # Get message count for this conversation
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM messages
                WHERE conversation_id = ?
            """, (row['id'],))

            message_count = cursor.fetchone()['count']

            conversations.append({
                "id": row['id'],
                "title": row['title'],
                "messageCount": message_count,
                "createdAt": row['created_at'],
                "updatedAt": row['updated_at']
            })

        return conversations

    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """Get all messages for a conversation"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT id, type, text, timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        """, (conversation_id,))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                "id": row['id'],
                "type": row['type'],
                "text": row['text'],
                "timestamp": row['timestamp']
            })

        return messages

    def add_message(self, conversation_id: str, msg_type: str, text: str) -> Dict:
        """Add a message to a conversation"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()

        # Add the message
        cursor.execute("""
            INSERT INTO messages (conversation_id, type, text, timestamp)
            VALUES (?, ?, ?, ?)
        """, (conversation_id, msg_type, text, now))

        message_id = cursor.lastrowid

        # Update conversation's updated_at timestamp
        cursor.execute("""
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ?
        """, (now, conversation_id))

        # Auto-generate title from first user message
        cursor.execute("""
            SELECT title FROM conversations WHERE id = ?
        """, (conversation_id,))

        current_title = cursor.fetchone()['title']

        if current_title == "New conversation" and msg_type == "user":
            # Use first 40 chars of first user message as title
            new_title = text[:40] + ("..." if len(text) > 40 else "")
            cursor.execute("""
                UPDATE conversations
                SET title = ?
                WHERE id = ?
            """, (new_title, conversation_id))

        self.conn.commit()

        return {
            "id": message_id,
            "type": msg_type,
            "text": text,
            "timestamp": now
        }

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        cursor = self.conn.cursor()

        # Delete messages first (due to foreign key)
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))

        # Delete conversation
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))

        self.conn.commit()

        return cursor.rowcount > 0

    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM conversations WHERE id = ? LIMIT 1", (conversation_id,))
        return cursor.fetchone() is not None

    def close(self):
        """Close database connection"""
        self.conn.close()
