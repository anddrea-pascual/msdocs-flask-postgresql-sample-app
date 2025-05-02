import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Restaurant, Review, ImageUpload

@app.route('/api/images', methods=['GET'])
def get_images_api():
    try:
        image_uploads = ImageUpload.query.order_by(ImageUpload.timestamp.desc()).all()
        images = [
            {
                'filename': image.filename,
                'red_pixels': image.red_pixels,
                'green_pixels': image.green_pixels,
                'blue_pixels': image.blue_pixels,
                'timestamp': image.timestamp.isoformat(),  # Convertir a string ISO
                'username': image.username
            } for image in image_uploads
        ]
        return jsonify(images)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    restaurants = Restaurant.query.all()
    return render_template('index.html', restaurants=restaurants)

@app.route('/<int:id>', methods=['GET'])
def details(id):
    restaurant = Restaurant.query.where(Restaurant.id == id).first()
    reviews = Review.query.where(Review.restaurant == id)
    return render_template('details.html', restaurant=restaurant, reviews=reviews)

@app.route('/create', methods=['GET'])
def create_restaurant():
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_restaurant():
    try:
        name = request.form.get('restaurant_name')
        street_address = request.form.get('street_address')
        description = request.form.get('description')
        if not all([name, street_address, description]):
            raise ValueError("You must include a restaurant name, address, and description")
    except (ValueError, KeyError) as e:
        return render_template('create_restaurant.html', {
            'error_message': str(e)
        })
    else:
        restaurant = Restaurant(
            name=name,
            street_address=street_address,
            description=description
        )
        db.session.add(restaurant)
        db.session.commit()
        return redirect(url_for('details', id=restaurant.id))

@app.route('/review/<int:id>', methods=['POST'])
@csrf.exempt
def add_review(id):
    try:
        user_name = request.form.get('user_name')
        rating = request.form.get('rating')
        review_text = request.form.get('review_text')
        if not all([user_name, rating, review_text]):
            raise ValueError("You must include a user name, rating, and review text")
        rating = int(rating)
    except (ValueError, KeyError, TypeError) as e:
        return render_template('add_review.html', {
            'error_message': f"Error adding review: {str(e)}"
        })
    else:
        review = Review(
            restaurant=id,
            review_date=datetime.now(),
            user_name=user_name,
            rating=rating,
            review_text=review_text
        )
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('details', id=id))

@app.route('/add_imageUpload', methods=['POST'])
@csrf.exempt
def add_imageUpload():
    try:
        # Validar campos requeridos
        filename = request.form.get('filename')
        red_pixels = request.form.get('redPixels')
        green_pixels = request.form.get('greenPixels')
        blue_pixels = request.form.get('bluePixels')
        username = request.form.get('username')
        timestamp_str = request.form.get('timestamp')

        if not all([filename, red_pixels, green_pixels, blue_pixels, username, timestamp_str]):
            raise ValueError("Missing required fields")

        # Convertir y validar tipos
        red_pixels = int(red_pixels)
        green_pixels = int(green_pixels)
        blue_pixels = int(blue_pixels)

        # Parsear el timestamp
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format. Expected 'YYYY-MM-DDTHH:MM:SS', got '{timestamp_str}'")

        # Crear el objeto ImageUpload
        image_upload = ImageUpload(
            filename=filename,
            red_pixels=red_pixels,
            green_pixels=green_pixels,
            blue_pixels=blue_pixels,
            username=username,
            timestamp=timestamp
        )

        # Guardar en la base de datos
        db.session.add(image_upload)
        db.session.commit()

        # Redirigir al índice con mensaje de éxito
        return redirect(url_for('index'))

    except (ValueError, KeyError, TypeError) as e:
        # Redisplay the form with an error message
        return render_template('add_imageUpload.html', {
            'error_message': f"Error adding image upload: {str(e)}"
        })

@app.context_processor
def utility_processor():
    def star_rating(id):
        reviews = Review.query.where(Review.restaurant == id)
        ratings = []
        review_count = 0
        for review in reviews:
            ratings.append(review.rating)
            review_count += 1
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}
    return dict(star_rating=star_rating)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
