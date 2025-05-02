from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import validates
from datetime import datetime
from app import db

class ImageUpload(db.Model):
    __tablename__ = 'image_upload'  # Nombre explícito de la tabla en la base de datos
    id = Column(Integer, primary_key=True)
    filename = Column(String(255))
    red_pixels = Column(Integer)
    green_pixels = Column(db.Integer)
    blue_pixels = Column(db.Integer)
    username = Column(String(255))
    timestamp = Column(DateTime)
