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

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# done: connect to a local postgresql database
# done form comfig.py

#----------------------------------------------------------------------------#
# Models.

#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)
    genres = db.Column(db.String(250))
    shows = db.relationship('Show', backref=db.backref('venue', uselist=False), lazy='dynamic')

    # done: implement any missing fields, as a database migration using Flask-Migrate
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)
    shows = db.relationship('Show', backref=db.backref('artist', uselist=False), lazy='dynamic')



    def __repr__(self):
      return f'Artist: <{self.id}, {self.name}, {self.city}>'

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


    def __repr__(self):
      return f'Show: <{self.id}, {self.artist_id}, {self.venue_id}, {self.start_time}>'

    # done: implement any missing fields, as a database migration using Flask-Migrate

# dorn Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
#add class show

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
  venues = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()
  return render_template('pages/venues.html', venues=venues)
  # done: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response=request.form.get('search_term', None)
  value=Venue.query.filter(Venue.name.ilike('%' + response + '%')).all()
  return render_template('pages/search_venues.html', results=value, search_term=response)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # done: replace with real venue data from the venues table, using venue_id
  
  data = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()
  upcoming_shows = [i for i in shows if i.start_time>datetime.utcnow()]
  upcoming_shows_count = len(upcoming_shows)
  past_shows = [i for i in shows if i.start_time<datetime.utcnow()]
  past_shows_count = len(past_shows)
  return render_template('pages/show_venue.html', venue=data, shows=shows, upcoming_shows=upcoming_shows, upcoming_shows_count=upcoming_shows_count, past_shows=past_shows, past_shows_count=past_shows_count)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name=request.form.get('name', '')
    city=request.form.get('city', '')
    state=request.form.get('state', '')
    address=request.form.get('address', '')
    phone=request.form.get('phone', '')
    image_link=request.form.get('image_link', '')
    genres=request.form.get('genres', '')
    facebook_link=request.form.get('facebook_link', '')
    venue=Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()
  # done: insert form data as a new Venue record in the db, instead
  # done: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
    flash('Venue ' + name + ' was successfully listed!')
  # done: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Todo.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # done: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # done: replace with real data returned from querying the database
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response=request.form.get('search_term', None)
  value=Artist.query.filter(Artist.name.ilike('%' + response + '%')).all()
  result_count=len(value)
  return render_template('pages/search_artists.html', results=value, search_term=response, result_count=result_count)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # done: replace with real venue data from the venues table, using venue_id
  data = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()
  upcoming_shows = [i for i in shows if i.start_time>datetime.utcnow()]
  upcoming_shows_count = len(upcoming_shows)
  past_shows = [i for i in shows if i.start_time<datetime.utcnow()]
  past_shows_count = len(past_shows)
  return render_template('pages/show_artist.html', artist=data, shows=shows, upcoming_shows=upcoming_shows, upcoming_shows_count=upcoming_shows_count, past_shows=past_shows, past_shows_count=past_shows_count)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  # done: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # done: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist=Artist.query.get(artist_id)
    artist.name=request.form.get('name', '')
    artist.city=request.form.get('city', '')
    artist.state=request.form.get('state', '')
    artist.phone=request.form.get('phone', '')
    artist.image_link=request.form.get('image_link', '')
    artist.genres=request.form.get('genres', '')
    artist.facebook_link=request.form.get('facebook_link', '')
    db.session.commit()
    flash('Your changes have been saved')
  except:
    db.session.rollback()
    flash('Something went wrong! Please try again')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # done: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # done: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue=Venue.query.get(venue_id)
    venue.name=request.form.get('name', '')
    venue.city=request.form.get('city', '')
    venue.state=request.form.get('state', '')
    venue.address=request.form.get('address', '')
    venue.phone=request.form.get('phone', '')
    venue.image_link=request.form.get('image_link', '')
    venue.genres=request.form.get('genres', '')
    venue.facebook_link=request.form.get('facebook_link', '')
    db.session.commit()
    flash('Your changes have been saved')
  except:
    db.session.rollback()
    flash('Something went wrong! Please try again')
  finally:
    db.session.close()
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
  # done: insert form data as a new Venue record in the db, instead
  # done: modify data to be the data object returned from db insertion
  try:
    name=request.form.get('name', '')
    city=request.form.get('city', '')
    state=request.form.get('state', '')
    phone=request.form.get('phone', '')
    image_link=request.form.get('image_link', '')
    genres=request.form.get('genres', '')
    facebook_link=request.form.get('facebook_link', '')
    artist=Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()

  # on successful db insert, flash success
    flash('Artist ' + name + ' was successfully listed!')
  # done: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=Show.query.order_by(Show.start_time<datetime.utcnow()).all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # done: insert form data as a new Show record in the db, instead
  try:
    artist_id=request.form.get('artist_id')
    venue_id=request.form.get('venue_id')
    start_time=request.form.get('start_time')
    show=Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()

  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # done: on unsuccessful db insert, flash an error instead.
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
