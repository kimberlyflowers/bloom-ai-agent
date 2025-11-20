"""
Conversation Database - PostgreSQL/Supabase storage for chat history
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ConversationsDB:
    """Manage conversation storage in PostgreSQL/Supabase"""

    def __init__(self):
        """Initialize database connection"""
        # Get Supabase connection string from environment
        self.connection_string = os.getenv("SUPABASE_DB_URL")

        if not self.connection_string:
            raise ValueError("SUPABASE_DB_URL environment variable is required!")

        # Debug: Log connection string format (mask password)
        if self.connection_string:
            # Show first 50 chars to see the username format
            masked_string = self.connection_string[:50] + "..." if len(self.connection_string) > 50 else self.connection_string
            logger.info(f"🔍 DEBUG - Connection string start: {masked_string}")
            # Check if it has the critical dot after postgres
            if "postgres." in self.connection_string:
                logger.info("✅ Connection string has postgres. format (CORRECT)")
            else:
                logger.warning("⚠️ Connection string missing postgres. format (MIGHT BE WRONG)")

        self.conn = None
        self.connect()
        self.create_tables()
        logger.info("✅ Connected to Supabase PostgreSQL database")

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                self.connection_string,
                cursor_factory=RealDictCursor
            )
            self.conn.autocommit = False  # Use transactions
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise

    def create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        try:
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """)

            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    text TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
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
            logger.info("✅ Database tables created/verified")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error creating tables: {e}")
            raise

    def create_conversation(self, conversation_id: str) -> Dict:
        """Create a new conversation"""
        cursor = self.conn.cursor()
        now = datetime.now()

        try:
            cursor.execute("""
                INSERT INTO conversations (id, title, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
            """, (conversation_id, "New conversation", now, now))

            self.conn.commit()

            return {
                "id": conversation_id,
                "title": "New conversation",
                "messages": [],
                "createdAt": now.isoformat(),
                "updatedAt": now.isoformat()
            }
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error creating conversation: {e}")
            raise

    def get_all_conversations(self) -> List[Dict]:
        """Get all conversations ordered by most recent"""
        cursor = self.conn.cursor()

        try:
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
                    WHERE conversation_id = %s
                """, (row['id'],))

                message_count = cursor.fetchone()['count']

                conversations.append({
                    "id": row['id'],
                    "title": row['title'],
                    "messageCount": message_count,
                    "createdAt": row['created_at'].isoformat(),
                    "updatedAt": row['updated_at'].isoformat()
                })

            return conversations
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []

    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """Get all messages for a conversation"""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT id, type, text, timestamp
                FROM messages
                WHERE conversation_id = %s
                ORDER BY timestamp ASC
            """, (conversation_id,))

            messages = []
            for row in cursor.fetchall():
                messages.append({
                    "id": row['id'],
                    "type": row['type'],
                    "text": row['text'],
                    "timestamp": row['timestamp'].isoformat()
                })

            return messages
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []

    def add_message(self, conversation_id: str, msg_type: str, text: str) -> Dict:
        """Add a message to a conversation"""
        cursor = self.conn.cursor()
        now = datetime.now()

        try:
            # Add the message
            cursor.execute("""
                INSERT INTO messages (conversation_id, type, text, timestamp)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (conversation_id, msg_type, text, now))

            message_id = cursor.fetchone()['id']

            # Update conversation's updated_at timestamp
            cursor.execute("""
                UPDATE conversations
                SET updated_at = %s
                WHERE id = %s
            """, (now, conversation_id))

            # Auto-generate title from first user message
            cursor.execute("""
                SELECT title FROM conversations WHERE id = %s
            """, (conversation_id,))

            current_title = cursor.fetchone()['title']

            if current_title == "New conversation" and msg_type == "user":
                # Use first 40 chars of first user message as title
                new_title = text[:40] + ("..." if len(text) > 40 else "")
                cursor.execute("""
                    UPDATE conversations
                    SET title = %s
                    WHERE id = %s
                """, (new_title, conversation_id))

            self.conn.commit()

            return {
                "id": message_id,
                "type": msg_type,
                "text": text,
                "timestamp": now.isoformat()
            }
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error adding message: {e}")
            raise

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        cursor = self.conn.cursor()

        try:
            # Delete messages first (due to foreign key)
            cursor.execute("""
                DELETE FROM messages WHERE conversation_id = %s
            """, (conversation_id,))

            # Delete conversation
            cursor.execute("""
                DELETE FROM conversations WHERE id = %s
            """, (conversation_id,))

            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error deleting conversation: {e}")
            return False

    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists"""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT 1 FROM conversations WHERE id = %s
            """, (conversation_id,))

            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking conversation existence: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
