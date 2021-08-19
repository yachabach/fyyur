#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import exc
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import exc, func


# Allow migration
from flask_migrate import Migrate

import sys


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

from models import *

# TODO: connect to a local postgresql database
    #connected through 'config' file
# Set up migration
migrate = Migrate(app, db)
  
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Helpers.
#----------------------------------------------------------------------------#

# Add genre associations to Venues
def aGenre(genreName):
    rslt = db.session.query(Genre).filter_by(name=genreName).first()
    if rslt is None:
        rslt = Genre()
        rslt.name = genreName
        db.session.add(rslt)
        db.session.commit()
        print('Genre didnt exist', sys.stderr, flush=True)
    else:
        print('Genre is here', sys.stderr, flush=True)
        
    return rslt
    
# Create a list of genres
def genreList(focus='Artist', itemId= ''):
    
    if itemId == '':
        return []
        
    genres = db.session.query(Genre.name)
    if focus.lower() == 'venue':
        genreList = genres.join(Venue.genres).filter(Venue.id==itemId).all()
    else:
        genreList = genres.join(Artist.genres).filter(Artist.id==itemId).all()
        
    rslt = [g[0] for g in genreList]
    return rslt
    
#--------------------------
# Add Artist associations to Shows
def aArtist(artist_id):
    rslt = db.session.query(Artist).filter_by(id=artist_id).first()
    if rslt is None:
        flash('Artist ' + artist_id + ' does not exist.')
    else:
        print('Genre is here', sys.stderr, flush=True)
               
    return rslt

#-----------------------
# Create a dictionary from the list of tuples
TestList = db.session.query(Venue.name, func.count(Show.id)).\
    outerjoin(Show, Show.start_time > datetime.now()).\
    group_by(Venue.name, Venue.id).all()

def TupToDict(tup, col_names):
    
    #Create a dictionary template
    rslt = {}
 
    #For each item in the tuple create a key:value pair
    i=0
    for item in tup:
        rslt[col_names[i]] = item
        i+=1

    # Return a dictionary
    return rslt

#---------------------------
#Take a list of tuples and create a list of 
#dictionaries
def TupListToDict(tupList, col_names):

    rslt = []
    for t in tupList:
        rslt.append(TupToDict(t, col_names))
        
    return rslt

#-------------------------    
# Return the number of shows for a given Artist or Venue
#
#   focus - 'Artist' (default), 'Venue
#   tense - 'All' (default), 'Past', 'Future'
#   
def numShows(id='',focus='Artist', tense='All'):

    # Test for inputs
    if id=='':
        return -1
        
    # Get the query object
    if focus.lower()=='venue':
        num = db.session.query(func.count(Show.id)).filter(Show.venue_id==id)
    else:
        num = db.session.query(func.count(Artist.id)).\
                join(Show.artists).filter(Artist.id==1)
    
    # Modify object with appropriate filter
    if tense.lower() == 'past':
        num = num.filter(Show.start_time < datetime.now())
    elif tense.lower() == 'future':
        num = num.filter(Show.start_time > datetime.now())
        
    # Return the resulting scalar
    return num.scalar()
                        
    
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  areaList = []
    
  #Gather the list of areas (cities)
  cityList = db.session.query(Venue.city, Venue.state).distinct().all()
  
  # Create a dictionary for each city
  areaList = TupListToDict(cityList, ['city', 'state'])
  for area in areaList:
    venueList = db.session.query(Venue.id, Venue.name).\
                filter(Venue.city==area['city']).all()
    area['venues']=TupListToDict(venueList, ['id', 'name'])
    for v in area['venues']:
        v['num_upcoming_shows'] = numShows(v['id'], 'Venue', 'future')
      
  return render_template('pages/venues.html', areas=areaList);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term= '%' + request.form.get('search_term', '') + '%'
  matchVenues = db.session.query(Venue.id, Venue.name).\
        filter(Venue.name.ilike(search_term)).all()
        
  response = {}
  response['count']=len(matchVenues)
  response['data'] = TupListToDict(matchVenues, ['id', 'name'])
  for v in response['data']:
    v['num_upcoming_shows'] = numShows(v['id'], 'Venue', 'future')
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  sVenue = Venue.query.filter_by(id=venue_id).first()
  data = {
    "id": sVenue.id,
    "name": sVenue.name,
    "genres": genreList('Venue', venue_id),
    "address": sVenue.address,
    "city": sVenue.city,
    "state": sVenue.state,
    "phone": sVenue.phone,
    "website": sVenue.website,
    "facebook_link": sVenue.facebook_link,
    "seeking_talent": sVenue.seeking_talent,
    "seeking_description": sVenue.seeking_description,
    "image_link": sVenue.image_link
  }
  
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)
  consol.log('name: ', form.name)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  newVenue = Venue()
  newVenue.name = request.form['name']
  newVenue.city = request.form['city']
  newVenue.state = request.form['state']
  newVenue.address = request.form['address']
  newVenue.phone = request.form['phone']
  newVenue.image_link = request.form['image_link']
  newVenue.facebook_link = request.form['facebook_link']
  newVenue.website = request.form['website']
  newVenue.image_link = request.form['image_link']
  newVenue.seeking_talent = request.form['seeking_talent']=='y'
  newVenue.seeking_description = request.form['seeking_description']
  
  genreList = request.form.getlist('genres')
  for G in genreList:
    newVenue.genres.append(aGenre(G))
  
  try:
    db.session.add(newVenue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except exc.IntegrityError:
    db.session.rollback()
    flash('Venue ' + request.form['name'] + ' could not be listed')
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  rslt = db.session.query(Artist.id, Artist.name).all()
  data = TupListToDict(rslt, ['id', 'name'])
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    artist = db.session.query(Artist).filter(Artist.id==artist_id).all()[0]

    data = {}
    data['id'] = artist.id
    data['name'] = artist.name
    data['city'] = artist.city
    data['state'] = artist.state
    data['phone'] = artist.phone
    data['website'] = artist.website_link
    data['facebook_link'] = artist.facebook_link
    data['image_link'] = artist.image_link
    data['seeking_venue'] = artist.seeking_venue
    data['seeking_description'] = artist.seeking_description
    data['genres'] = genreList('Artist', artist_id)

    artistShows = db.session.query(Venue.id.label('venue_id'),\
                            Venue.name.label('venue_name'),\
                            Venue.image_link.label('venue_image_link'),\
                            Show.start_time).\
                    join(Show).join(Show.artists).\
                    filter(Artist.id==artist_id)

    pastShows = artistShows.filter(Show.start_time < datetime.now()).all()  
    data['past_shows'] = TupListToDict(pastShows,\
        ['venue_id', 'venue_name', 'venue_image_link', 'start_time'])

    futureShows = artistShows.filter(Show.start_time > datetime.now()).all()
    data['upcoming_shows'] = TupListToDict(pastShows,\
        ['venue_id', 'venue_name', 'venue_image_link', 'start_time'])

    data['past_shows_count'] = numShows(artist_id, 'Artist', 'past')
    data['upcoming_shows_count'] = numShows(artist_id, 'Artist', 'future')
    
    #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  dbArtist = db.session.query(Artist).filter(Artist.id == artist_id).all()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  newArtist = Artist(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    phone = request.form['phone'],
    facebook_link = request.form['facebook_link'],
    website_link = request.form['website_link'],
    image_link = request.form['image_link'],
    seeking_venue = request.form.get('seeking_venue')=='y',
    seeking_description = request.form['seeking_description']
  )
  
  genreList = request.form.getlist('genres')
  for G in genreList:
    newArtist.genres.append(aGenre(G))
  
  try:
    db.session.add(newArtist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except exc.IntegrityError:
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' could not be listed')
    

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  newShow = Show()
  newShow.name = 'The Noname Show' #request.form['name']
  newShow.start_time = request.form['start_time']
  newShow.venue_id = request.form['venue_id']
  
  artist_id = request.form['artist_id']
  aArtist = db.session.query(Artist).filter_by(id=artist_id).first()
  if aArtist is None:
    flash('Artist ' + artist_id + ' does not exist')
  else:
    newShow.artists.append(aArtist)
  
  try:
    db.session.add(newShow)
    db.session.commit()
  # on successful db insert, flash success
    flash('The Noname Show was successfully listed!')

  except exc.IntegrityError:
    db.session.rollback()
    flash('The Noname Show could not be listed')
  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
