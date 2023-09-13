# Importing required modules from Flask, Flask extensions, and your model
from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Plant

# Creating an instance of the Flask app
app = Flask(__name__)

# Configuring database connection and settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False  # Configure Flask's JSON encoder to format with spaces

# Setting up migration with the app and database
migrate = Migrate(app, db)
db.init_app(app)  # Initializing the database with the app

# Setting up an API instance with the Flask app
api = Api(app)


class Plants(Resource):
    """Resource for /plants endpoint to handle multiple plants"""

    def get(self):
        """Return all plants in the database."""
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        """Create a new plant in the database."""
        data = request.get_json()
        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price']
        )
        db.session.add(new_plant)
        db.session.commit()
        return make_response(new_plant.to_dict(), 201)


# Associating the Plants class with the /plants endpoint
api.add_resource(Plants, '/plants')


class PlantByID(Resource):
    """Resource for /plants/:id endpoint to handle a single plant by its ID"""

    def get(self, id):
        """Return a specific plant by its ID."""
        plant = Plant.query.filter_by(id=id).first()
        if plant:
            return make_response(jsonify(plant.to_dict()), 200)
        return make_response(jsonify({"error": "Plant not found"}), 404)

    def patch(self, id):
        """Update a specific plant by its ID."""
        plant = Plant.query.filter(Plant.id == id).first()
        if not plant:
            return make_response(jsonify({"error": "Plant not found"}), 404)
        data = request.get_json()
        if 'is_in_stock' in data:  # Strong parameter handling
            plant.is_in_stock = data['is_in_stock']
        db.session.add(plant)
        db.session.commit()
        return make_response(jsonify(plant.to_dict()), 200)

    def delete(self, id):
        """Delete a specific plant by its ID."""
        plant = Plant.query.filter(Plant.id == id).first()
        if not plant:
            return make_response(jsonify({"error": "Plant not found"}), 404)
        db.session.delete(plant)
        db.session.commit()
        return make_response("", 204)  # No content response for successful deletion


# Associating the PlantByID class with the /plants/:id endpoint
api.add_resource(PlantByID, '/plants/<int:id>')


# Main execution
if __name__ == '__main__':
    app.run(port=5555, debug=True)  # Running the Flask app on port 5555 with debug mode on
