#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
import pytz

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)
    genres = db.relationship('Venue_Genre', lazy=True)

    def __repr__(self):
        return f"Venue('{self.name}', '{self.city}')"

    def asdict(self):
        shows = Show.query.filter_by(venue_id = self.id).all()
        upcomimg_shows = []
        past_shows = []
        timezone = pytz.timezone("America/Los_Angeles")
        for s in shows:
          # print(dateutil.parser.parse(s.start_time).strftime('%m/%d/%y %H:%M:%S'))
          # print(datetime.now().strftime('%m/%d/%y %H:%M:%S'))
          artist = Artist.query.filter_by(id = s.artist_id).first()
          show = {
              'start_time': s.start_time,
              'artist_name': artist.name,
              'artist_image_link': artist.image_link,
              'artist_id': s.artist_id
          }
          if (dateutil.parser.parse(s.start_time) > timezone.localize(datetime.now())):
            past_shows.append(show)
          else:
            upcomimg_shows.append(show)
        genres_id = Venue_Genre.query.filter_by(venue_id =  self.id).all()
        genres = []
        for g in genres_id:
          genres.append(Genre.query.filter_by(id=g.genre_id).first().name)
        return {
          'id' : self.id,
          'name' : self.name,
          'city' : self.city,
          'state' : self.state,
          'address' : self.address,
          'phone' : self.phone,
          'website' : self.website,
          'seeking_talent' : self.seeking_talent,
          'image_link' : self.image_link,
          'facebook_link' : self.facebook_link,
          'genres' : genres,
          "past_shows": past_shows,
          "upcoming_shows": upcomimg_shows,
          "past_shows_count": len(past_shows),
          "upcoming_shows_count": len(upcomimg_shows)
        }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('Artist_Genre', lazy=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    website = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f"Artist('{self.name}', '{self.city}')"

    def asdict(self):
        shows = Show.query.filter_by(artist_id = self.id).all()
        upcomimg_shows = []
        past_shows = []
        timezone = pytz.timezone("America/Los_Angeles")
        for s in shows:
          # print(dateutil.parser.parse(s.start_time).strftime('%m/%d/%y %H:%M:%S'))
          # print(datetime.now().strftime('%m/%d/%y %H:%M:%S'))
          venue = Venue.query.filter_by(id = s.venue_id).first()
          show = {
              'start_time': s.start_time,
              'venue_name': venue.name,
              'venue_image_link': venue.image_link,
              'venue_id': s.venue_id
          }
          if (dateutil.parser.parse(s.start_time) > timezone.localize(datetime.now())):
            past_shows.append(show)
          else:
            upcomimg_shows.append(show)
        genres_id = Artist_Genre.query.filter_by(artist_id =  self.id).all()
        genres = []
        for g in genres_id:
          genres.append(Genre.query.filter_by(id=g.genre_id).first().name)
        return {
          'id' : self.id,
          'name' : self.name,
          'city' : self.city,
          'state' : self.state,
          'phone' : self.phone,
          'website' : self.website,
          'seeking_venue' : self.seeking_venue,
          'image_link' : self.image_link,
          'genres' : genres,
          "past_shows": past_shows,
          "upcoming_shows": upcomimg_shows,
          "past_shows_count": len(past_shows),
          "upcoming_shows_count": len(upcomimg_shows)
        }
        
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = "Show"
  
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  start_time = db.Column(db.String)

  def __repr__(self):
        return f"Show('{self.venue_id}', '{self.start_time}', '{self.artist_id}')"
  
  def asdict(self):
    artist = Artist.query.filter_by(id = self.artist_id).first()
    venue = Venue.query.filter_by(id = self.venue_id).first()
    return
    {
      'venue_id': self.venue_id,
      'start_time': self.start_time,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'artist_id': self.artist_id,
      'venue_name': venue.name
    }

class Genre(db.Model):
  __tablename__ = "Genre"

  id = db.Column(db.Integer, primary_key=True)
  name =  db.Column(db.String)
  venue_genre = db.relationship('Venue_Genre', backref='venue_genre', lazy=True)
  artist_genre = db.relationship('Artist_Genre', backref='artist_genre', lazy=True)

  def __repr__(self):
      return f"Genre('{self.name}')"

class Artist_Genre(db.Model):
  __tablename__ = "Artist_Genre"
  
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  genre_id = db.Column(db.Integer, db.ForeignKey('Genre.id'))

  def __repr__(self):
      return f"Artist_Genre('{self.id}', '{self.artist_id}', '{self.genre_id}')"

class Venue_Genre(db.Model):
  __tablename__ = "Venue_Genre"
  
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  genre_id = db.Column(db.Integer, db.ForeignKey('Genre.id'))

  def __repr__(self):
      return f"Venue_Genre('{self.id}', '{self.genre_id}', '{self.venue_id}')"

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  city_count = db.session.query(Venue.city, Venue.state, db.func.count(Venue.id)).group_by(Venue.city).all()
  data2 = []
  for cc in city_count:
    venues = Venue.query.filter_by(city = cc.city).all()
    cc = cc._asdict()
    cc["venues"]=venues
    data2.append(cc)
  print(data2)
  return render_template('pages/venues.html', areas=data2)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response = {}
  search_term = request.form.get('search_term', '')
  response["count"] = db.session.query(db.func.count(Venue.id).label('count')).filter(Venue.name.like(f'%{search_term}%')).all()[0]._asdict()['count']
  data = db.session.query(Venue.id, Venue.name).filter(Venue.name.like(f'%{search_term}%')).all()
  response["data"] = []
  for d in data:
    response["data"].append(d._asdict())
  print(response)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.filter_by(id=venue_id).first()
  return render_template('pages/show_venue.html', venue=data.asdict())

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
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
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 1,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  response = {}
  search_term = request.form.get('search_term', '')
  response["count"] = db.session.query(db.func.count(Artist.id).label('count')).filter(Artist.name.like(f'%{search_term}%')).all()[0]._asdict()['count']
  data = db.session.query(Artist.id, Artist.name).filter(Artist.name.like(f'%{search_term}%')).all()
  response["data"] = []
  for d in data:
    response["data"].append(d._asdict())
  print(response)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Artist.query.filter_by(id=artist_id).first()
  return render_template('pages/show_artist.html', artist=data.asdict())

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
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

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data2 = db.session.query(Show.venue_id, Venue.name.label('venue_name'), Show.start_time, Artist.name.label('artist_name'), Show.artist_id, Artist.image_link.label('artist_image_link')).join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).all()
  for d in data2:
    print(d._asdict())
  return render_template('pages/shows.html', shows=data2)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
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
