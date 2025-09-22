import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dbsharing.db.database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID,JSONB
import uuid



class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {"schema": "rag_chatbot"}

    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique = True, nullable = False)
    username = Column(String, unique = True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)  # Active status of the user
    role = Column(String)
    phone_number = Column(String)
    created_at = Column(DateTime(timezone = True),server_default = func.now())

    # Relationships
    chat_sessions = relationship("ChatSessions", back_populates="user")


class ChatSessions(Base):
    __tablename__ = 'chat_sessions'
    __table_args__ = {"schema": "rag_chatbot"}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique = True, index = True)
    user_id = Column(Integer, ForeignKey("rag_chatbot.users.id"))
    chat_type =  Column(String, default = "conversational")   # Type of chat session, e.g., conversation, rag, etc.
    title = Column(String, default = "New Chat")  # Title of the chat session
    is_active = Column(Boolean, default=True)  # Active status of the chat session
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Timestamp for session creation
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # Timestamp for last activity

    # Relationship to Users table
    user = relationship("Users", back_populates="chat_sessions")

class LangchainEmbeddings(Base):
    __tablename__ = 'embeddings'
    __table_args__ = {"schema": "rag_chatbot"}

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Unique ID per chunk
    document_id = Column(String, nullable=False)  # Same ID for all chunks of a document
    document = Column(Text, nullable=False)
    embeddings = Column(Vector(300), nullable=False)


class ChatHistory(Base):
    __tablename__ = 'chat_history'
    __table_args__ = {"schema": "rag_chatbot"}
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    message = Column(String)
    response = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.now())  # Timestamp for tracking


class DocumentEmbeddings(Base):
    __tablename__ = "document_embeddings"
    __table_args__ = {"schema": "rag_chatbot"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_name = Column(String, nullable=False)
    document_id = Column(String, nullable=False)
    document = Column(Text, nullable=False)
    meta_data = Column(Text, nullable=True)
    embeddings = Column(Vector(300), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())


class ModelParameters(Base):
    __tablename__ = "llm_models"
    __table_args__ = {"schema": "rag_chatbot"}

    model_id = Column(Integer, primary_key=True, index=True)
    model_name = Column(Text, nullable=False)
    max_p = Column(Float)
    max_temp = Column(Float)
    max_tokens = Column(Integer)
    

class LangchainPGCollection(Base):
    __tablename__ = "langchain_pg_collection"
    __table_args__ = {"schema":"public"}

    uuid = Column(UUID(as_uuid = True),primary_key = True, default = uuid.uuid4)
    name = Column(String)
    cmetadata = Column(JSONB,nullable = False)


class HistoryChat(Base):
    __tablename__ = "history_chat"
    __table_args__ = {"schema":"public"}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(UUID(as_uuid = True), index=True, default=uuid.uuid4, nullable=False)
    message = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())