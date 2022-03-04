from app import db
from datetime import datetime



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    access_level = db.Column(db.Integer, nullable=False, default=3)

    def __repr__(self):
        return '<User {}>'.format(self.username)



class EncyclopedicInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry = db.Column(db.String(64), index=True, unique=True)
    type = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.String(10000), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)


    creator = db.relationship('User')

    def __repr__(self):
        return '<EI {}>'.format(self.entry)



class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scientific_name = db.Column(db.String(100), index=True, unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return '<Plant {}({})>'.format(self.name, self.scientific_name)



class Farm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    description = db.Column(db.String(1000), nullable=True)
    city = db.Column(db.String(200), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    
    owner = db.relationship('User')

    def __repr__(self):
        return '<Farm {}>'.format(self.name)




class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area_covered = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    plant_time = db.Column(db.DateTime, nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey("farm.id"), nullable=False)
    
    farm = db.relationship('Farm')
    plant = db.relationship('Plant')


    def __repr__(self):
        return '<Crop {} at {}>'.format(self.plant.name, self.farm.name)


class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment = db.Column(db.String(1000))
    type = db.Column(db.Integer, nullable=False, default=0)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farm.id"), nullable=False)
    
    farm = db.relationship('Farm')
    actor = db.relationship('User')

    def __repr__(self):
        return '<AL {} at {}>'.format(self.farm.name, str(self.timestamp))


class Drone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(1000))
    network_address = db.Column(db.String(256))
    mac_address = db.Column(db.String(256))
    stream_address = db.Column(db.String(256))
    farm_id = db.Column(db.Integer, db.ForeignKey("farm.id"), nullable=False)
    
    farm = db.relationship('Farm')

    def __repr__(self):
        return '<Drone {} at {}>'.format(self.uri, self.farm.name)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frequency = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, default=0)
    slope = db.Column(db.Float, default=0)
    spacing = db.Column(db.Float, default=0)
    altitude = db.Column(db.Float, default=0)
    speed = db.Column(db.Float, default=0)
    drone_id = db.Column(db.Integer, db.ForeignKey("drone.id"), nullable=False)
    
    drone = db.relationship('Drone')

    def __repr__(self):
        return '<Schedule for {}>'.format(self.drone.uri)


class Path(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    schedule_id = db.Column(db.Integer, db.ForeignKey("schedule.id"), nullable=False)
    
    schedule = db.relationship('Schedule')

    def __repr__(self):
        return '<Path for {}>'.format(str(self.schedule))


class LocationPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey("farm.id"), nullable=True)
    path_id = db.Column(db.Integer, db.ForeignKey("path.id"), nullable=True)
    
    path = db.relationship('Path')
    farm = db.relationship('Farm')

    def __repr__(self):
        return '<LP at ({}, {})>'.format(self.lat, self.lon)

class WeatherInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(1000), nullable=True)
    city = db.Column(db.String(200), nullable=True)
    wind_level = db.Column(db.Float, nullable=False)
    rain_level = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    humidity = db.Column(db.Float, nullable=False)
    clouds = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<WI {} at {}>'.format(self.city, str(self.timestamp))


class CollectedImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.String(1000), nullable=False, default='')
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image = db.Column(db.String(1000))
    status = db.Column(db.Integer, nullable=False, default=0)
    drone_id = db.Column(db.Integer, db.ForeignKey("drone.id"), nullable=False)
    
    drone = db.relationship('Drone')

    def __repr__(self):
        return '<WI {} at {}>'.format(self.city, str(self.timestamp))


class SurveyParameters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slope = db.Column(db.Float, default=0)
    spacing = db.Column(db.Float, default=0)
    altitude = db.Column(db.Float, default=0)
    speed = db.Column(db.Float, default=0)
    farm_id = db.Column(db.Integer, db.ForeignKey("farm.id"), nullable=False)
    
    farm = db.relationship('Farm')

    def __repr__(self):
        return '<WI {} at {}>'.format(self.city, str(self.timestamp))

