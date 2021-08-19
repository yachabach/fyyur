from app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

    #Create Genre class to allow many-to-many relationships and referential integrity
class Genre(db.Model):
    __tablename__ = 'Genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    wiki_link = db.Column(db.String(500))
   
    #Association table for venues and genres (Ven_Gen)
Ven_Gen_MM = db.Table('Ven_Gen_MM',
  db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), 
            primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('Genres.id', ondelete='CASCADE'), 
            primary_key=True)
  )
  
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.relationship('Genre', 
                            secondary=Ven_Gen_MM,
                            passive_deletes=True,
                            backref=db.backref('Venues', lazy=True))
                                 
    # Format print statement for debugging    
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
  
     # Association table for Artists and Genres (Art_Gen)
Art_Gen_MM = db.Table('Art_Gen_MM', 
  db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('Genres.id', ondelete='CASCADE'), primary_key=True)
  )  

#Association table for artists and shows (Art_Show)
Art_Show_MM = db.Table('Art_Show_MM',
                  db.Column('show_id', db.Integer, 
                        db.ForeignKey('Show.id', ondelete='CASCADE'), 
                        primary_key=True),
                  db.Column('artist_id', 
                        db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), 
                        primary_key=True)
)

  
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.relationship('Genre', 
                            secondary=Art_Gen_MM, passive_deletes=True,
                            backref=db.backref('Artists', lazy=True))
                            
    # shows = db.relationship('Show', 
                            # secondary=Art_Show_MM, 
                            # backref=db.backref('Artists', lazy=True))
                            
    # Format print statement for debugging    
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'                        

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# Table for shows.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    
    artists = db.relationship('Artist', 
                            secondary=Art_Show_MM, 
                            backref=db.backref('Show', lazy=True))
    
    