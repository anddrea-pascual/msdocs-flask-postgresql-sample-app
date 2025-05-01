from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import validates
from datetime import datetime
from app import db


class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street_address = Column(String(50))
    description = Column(String(250))

    def __str__(self):
        rreturn (f"Usuario: {self.username}, Archivo: {self.filename}, "
                f"Rojos: {self.red_pixels}, Verdes: {self.green_pixels}, "
                f"Azules: {self.blue_pixels}, Fecha: {self.timestamp:%Y-%m-%d %H:%M:%S}")

class Review(db.Model):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey('restaurant.id', ondelete="CASCADE"))
    user_name = Column(String(30))
    rating = Column(Integer)
    review_text = Column(String(500))
    review_date = Column(DateTime)

    @validates('rating')
    def validate_rating(self, key, value):
        assert value is None or (1 <= value <= 5)
        return value

    def __str__(self):
        return f"{self.user_name}: {self.review_date:%x}"

class ImageUpload(db.Model):
    __tablename__ = 'image_upload'  # Nombre explícito de la tabla en la base de datos
    id = Column(Integer, primary_key=True)
    filename = Column(String(255))
    red_pixels = Column(Integer)
    green_pixels = Column(db.Integer)
    blue_pixels = Column(db.Integer)
    username = Column(String(255))
    timestamp = Column(DateTime)
