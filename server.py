from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///listings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

class Listing(db.Model):
    #turn fields in listings dictionary to db columns
    id=db.Column(db.Integer, primary_key=True)
    address=db.Column(db.String(200), nullable=False)
    type=db.Column(db.String(10), nullable=False)
    sqft=db.Column(db.String(20), nullable=False)
    price=db.Column(db.Integer, nullable=False)
    bedrooms=db.Column(db.Integer, nullable=False)
    baths = db.Column(db.Integer, nullable=False)
    img=db.Column(db.String(200), nullable=False)

    def to_dict(self):
        #convert db objects to dictionary
        return{
            'id':self.id,
            'address':self.address,
            'type':self.type,
            'sqft':self.sqft,
            'price':self.price,
            'bedrooms':self.bedrooms,
            'baths':self.baths,
            'img':self.img
        }
def seed_database():
    #makes sure listings populate database automatically
    if not Listing.query.first():
            
        initial_listings = [
            {"address": "47 Maplewood Crescent, Oakville, ON", "type": "sale", "sqft": "2500-3000", "price": 1249000, "bedrooms": 4, "baths": 3, "img": "images/house1.jpeg"},
            {"address": "56 Rosewood Lane, Hamilton, ON", "type": "sale", "sqft": "2500-3000", "price": 1116000, "bedrooms": 3, "baths": 3, "img": "images/house2.webp"},
            {"address": "34 Margerita Crescent, Mississauga, ON", "type": "rent", "sqft": "2000-2500", "price": 2000, "bedrooms": 2, "baths": 2, "img": "images/condo1.png"},
            {"address": "23 Venice Drive, Mississauga ON", "type": "sale", "sqft": "1500-2000", "price": 845000, "bedrooms": 3, "baths": 3, "img": "images/house4.jpeg"},
            {"address": "87 Viscount Drive, Toronto, ON", "type": "sale", "sqft": "3500-4000", "price": 2544700, "bedrooms": 5, "baths": 4, "img": "images/house5.webp"},
            {"address": "43 Cedar Creek Drive, Mississauga, ON", "type": "sale", "sqft": "4000-4500", "price": 2688900, "bedrooms": 5, "baths": 4, "img": "images/house6.jpeg"},
            {"address": "100 Pine Drive, Toronto, ON", "type": "sale", "sqft": "3500-4000", "price": 1766900, "bedrooms": 4, "baths": 3, "img": "images/house7.jpg"},
            {"address": "59 Constellation Drive, Vaughan, ON", "type": "rent", "sqft": "2000-2500", "price": 1600, "bedrooms": 2, "baths": 1, "img": "images/condo2.jpg"},
            {"address": "99 Yonge Street, Toronto, ON", "type": "rent", "sqft": "2500-3000", "price": 2000, "bedrooms": 3, "baths": 2, "img": "images/condo3.jpg"},
            {"address": "74 Financial Drive, Mississauga, ON", "type": "sale", "sqft": "4000-5000", "price": 4388400, "bedrooms": 5, "baths": 5, "img": "images/house10.webp"},
            {"address": "82 Sinclair Drive, Vaughan, ON", "type": "sale", "sqft": "3500-4000", "price": 3566700, "bedrooms": 4, "baths": 3, "img": "images/house11.jpg"},
            {"address": "426 Lions Gate, Concord, ON", "type": "sale", "sqft": "5000-6000", "price": 5856000, "bedrooms": 6, "baths": 5, "img": "images/house12.jpg"}
        ] 
        for item in initial_listings:
            listing = Listing(**item)
            db.session.add(listing)
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_database()

def validate_listing_data(data, is_update=False):
    #input validation - makes sure fields entered are in correct format
    required_fields = ["address", "type", "sqft", "price", "bedrooms", "baths", "img"]

    if not is_update:
        for field in required_fields:
            if field not in data or data[field] is None or data[field]=="":
                return "Field is invalid"

    if "type" in data and data["type"] not in ["sale", "rent"]:
        return "Type must be sale or rent"

    numeric_fields = {
        "price":(int, float),
        "bedrooms": int,
        "baths" : (int, float)
    }
    for field, expected_type in numeric_fields.items():
        if field in data and data[field] is not None:
            value = data[field]

            if not isinstance(value, expected_type) or isinstance(value, bool):
                return "Field must be a valid number"
            if value<0:
                return "Field must be a positive number"

    return None
@app.route ('/api/listings', methods=['GET'])
def get_listings():
    all_listings = Listing.query.all()

    listings_data = [listing.to_dict() for listing in all_listings]


    return jsonify({'listings': listings_data}), 200

@app.route ('/api/listings/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    listing = Listing.query.get(listing_id)

    if listing is None:
        return jsonify({"error": "Listing not found"}), 404
    return jsonify(listing.to_dict()), 200

@app.route ('/api/listings', methods=['POST'])
def create_listing():
    if not request.is_json:
        return jsonify({"error" : "Request must be JSON"}), 400

    data = request.get_json()

    error = validate_listing_data(data, is_update=False)
    if error:
        return jsonify({"error": error}), 400
    
    new_listing = Listing(
        address=data.get("address"), 
        type=data.get("type"), 
        sqft=data.get("sqft"), 
        price=data.get("price"), 
        bedrooms=data.get("bedrooms"), 
        baths=data.get("baths"), 
        img=data.get("img")
        )
    
    db.session.add(new_listing)
    db.session.commit()
    
    return jsonify(new_listing.to_dict()), 201

@app.route ('/api/listings/<int:listing_id>', methods=['PUT'])
def update_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if listing is None:
        return jsonify({"error":"Listing not found"}), 404
    
    if not request.is_json:
        return jsonify({"error":"Request must be JSON"}), 400


    data = request.get_json()

    error = validate_listing_data(data, is_update=True)
    if error:
        return jsonify({"error": error}), 400
    listing.address=data.get("address", listing.address) 
    listing.type = data.get("type", listing.type)
    listing.sqft = data.get("sqft", listing.sqft)
    listing.price = data.get("price", listing.price)
    listing.bedrooms = data.get("bedrooms", listing.bedrooms)
    listing.baths = data.get("baths", listing.baths)
    listing.img = data.get("img", listing.img)
                    
    db.session.commit()
    return jsonify(listing.to_dict()), 200

@app.route('/api/listings/<int:listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if listing is None:
        return jsonify({"error":"Listing not found"}), 404
    db.session.delete(listing)
    db.session.commit()

    return jsonify({"message": "Listing has been removed"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)