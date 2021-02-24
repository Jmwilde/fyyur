#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, jsonify, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# TODO: Add in Genre class to make tables follow 3rd Normal Form.

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(200)) # json as a string
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship("Show", backref="venue")

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(200))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship("Show", backref="artist")

# 1 Show -> 1 artist
# 1 Show -> 1 venue
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    # Note: Show.artist and Show.venue exist via backref

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # Values already stored as datetime objects
  # date = dateutil.parser.parse(value)
  date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

def flash_errors(form):
  for field, errors in form.errors.items():
    for error in errors:
      flash("Error in the {} field - {}".format(getattr(form, field).label.text,error))

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
  ordered_venues = []
  now = datetime.now()

  # Get all unique city/state places
  places = Venue.query.distinct(Venue.city, Venue.state).order_by(Venue.state).all()
  for place in places:
    # Venues that match the city and state
    venues = Venue.query.filter(Venue.city == place.city, Venue.state == place.state).order_by(Venue.state, Venue.city).all()
    venues_list = []
    for venue in venues:
      num_upcoming = 0
      for show in venue.shows:
        if show.start_time > now:
          num_upcoming += 1
      venues_list.append({'id': venue.id, 'name': venue.name, 'num_upcoming_shows': num_upcoming})
    ordered_venues.append({'city':place.city, 'state':place.state, 'venues':venues_list})

  return render_template('pages/venues.html', areas=ordered_venues)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search = '%{}%'.format(search_term) # Same as SQL LIKE operator, '%' is 0,1, or more chars 
  venues = Venue.query.filter(Venue.name.ilike(search)).all()

  data = []
  now = datetime.now()
  for venue in venues:
    upcoming = sum(map(lambda s: s.start_time > now, venue.shows))
    data.append({'id':venue.id, 'name':venue.name, 'num_upcoming_shows':upcoming})
  results = {
    'count':len(venues),
    'data':data
  }
  return render_template('pages/search_venues.html', results=results, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  now = datetime.now()
  past_shows = []
  upcoming_shows = []
  for show in venue.shows:
    show_info = {
      'artist_id': show.artist_id, 'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link, 'start_time': show.start_time
    }
    if show.start_time > now:
      upcoming_shows.append(show_info)
    else:
      past_shows.append(show_info)
  venue_info = {
    'id': venue.id,
    'name': venue.name,
    'genres': [g.name for g in venue.genres],
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }
  return render_template('pages/show_venue.html', venue=venue_info)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'csrf':False})
  if form.validate():
    error = False
    venue = {
      'name': form.name.data, 'city':form.city.data, 'state':form.state.data,
      'phone': form.phone.data, 'genres':json.dumps(form.genres.data), 'image_link':form.image_link.data,
      'facebook_link':form.facebook_link.data, 'website':form.website.data,
      'seeking_talent':form.seeking_talent.data, 'seeking_description':form.seeking_description.data
    }
    try:
      venue_model = Venue(**venue)
      db.session.add(venue_model)
      db.session.commit()
    except Exception as e:
      error = True
      db.session.rollback()
      print("Error on Artist db model: {}".format(e))
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Venue could not be listed.')
      return render_template('forms/new_venue.html', form=form)
    else:
      flash('Venue ' + venue['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  else:
    flash_errors(form)
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Deletes a venue using an AJAX call on the show venue page
  venue = Venue.query.get(venue_id)
  if not venue:
    return redirect(url_for('index'))

  error = False
  # Save the venue name before deletion
  venue_name = venue.name
  try:
      db.session.delete(venue)
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      abort(400)
  else:
      # Flask cannot redirect via an AJAX call, so it gets handled on the JavaScript side
      flash('Venue ' + venue_name + ' was successfully deleted!')
      return jsonify({'success': True, 'redirect': url_for('index')})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  artists_info = []
  for artist in artists:
    artists_info.append({'id':artist.id, 'name':artist.name})
  return render_template('pages/artists.html', artists=artists_info)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search = '%{}%'.format(search_term) # Same as SQL LIKE operator, '%' is 0,1, or more chars 
  artists = Artist.query.filter(Artist.name.ilike(search)).all()

  data = []
  now = datetime.now()
  for artist in artists:
    upcoming = sum(map(lambda s: s.start_time > now, artist.shows))
    data.append({'id':artist.id, 'name':artist.name, 'num_upcoming_shows':upcoming})
  results = {
    'count':len(artists),
    'data':data
  }
  return render_template('pages/search_artists.html', results=results, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data1={
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
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  return render_template('pages/show_artist.html', artist=artist_info)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist_info = {
    'id': artist.id,
    'name': artist.name,
    'genres': [g.name for g in artist.genres],
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link
  }
  # Presets the values rendered for select and multiple select fields
  form.state.default = artist_info['state']
  form.genres.default = artist_info['genres']
  form.seeking_venue.default = artist_info['seeking_venue']
  form.process()
  return render_template('forms/edit_artist.html', form=form, artist=artist_info)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form, meta={'csrf':False})
  error = False
  if form.validate():
    try:
      # Get the existing artist.
      artist = Artist.query.get(artist_id)

      # Update the fields.
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = get_genres(form.genres.data)
      artist.image_link = form.image_link.data
      artist.facebook_link = form.facebook_link.data
      artist.website = form.website.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      db.session.commit()
    except Exception as e:
      error = True
      db.session.rollback()
      print("Error on Artist db model: {}".format(e))
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Artist could not be edited.')
      return redirect(url_for('edit_artist_submission', artist_id=artist_id))
    else:
      flash('Artist was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    # Validation failed - flash all errors & return to editing
    flash_errors(form)
    return redirect(url_for('edit_artist_submission', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue_info = {
    'id': venue.id,
    'name': venue.name,
    'genres': [g.name for g in venue.genres],
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link
  }
  # Presets the values rendered for select and multiple select fields
  form.state.default = venue_info['state']
  form.genres.default = venue_info['genres']
  form.seeking_talent.default = venue_info['seeking_talent']
  form.process()
  return render_template('forms/edit_venue.html', form=form, venue=venue_info)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form, meta={'csrf':False})
  error = False
  if form.validate():
    try:
      # Get the existing artist.
      venue = Venue.query.get(venue_id)

      # Update the fields.
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.genres = get_genres(form.genres.data)
      venue.image_link = form.image_link.data
      venue.facebook_link = form.facebook_link.data
      venue.website = form.website.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      db.session.commit()
    except Exception as e:
      error = True
      db.session.rollback()
      print("Error on Venue db model: {}".format(e))
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Venue could not be edited.')
      return redirect(url_for('edit_venue_submission', venue_id=venue_id))
    else:
      flash('Venue was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    # Validation failed - flash all errors & return to editing
    flash_errors(form)
    return redirect(url_for('edit_venue_submission', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf':False})
  if form.validate():
    error = False
    artist = {
      'name': form.name.data, 'city':form.city.data, 'state':form.state.data,
      'phone': form.phone.data, 'genres':json.dumps(form.genres.data), 'image_link':form.image_link.data,
      'facebook_link':form.facebook_link.data, 'website':form.website.data,
      'seeking_venue':form.seeking_venue.data, 'seeking_description':form.seeking_description.data
    }
    # Todo: json.dumps(genres) before inserting into db
    try:
      artist_model = Artist(**artist)
      db.session.add(artist_model)
      db.session.commit()
    except Exception as e:
      error = True
      db.session.rollback()
      print("Error on Artist db model: {}".format(e))
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Artist could not be listed.')
      return render_template('forms/new_artist.html', form=form)
    else:
      flash('Artist ' + artist['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  else:
    flash_errors(form)
    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  shows_info = []

  for show in shows:
    shows_info.append({
      'venue_id':show.venue_id, 'venue_name':show.venue.name,
      'artist_id':show.artist_id, 'artist_name':show.artist.name,
      'artist_image_link':show.artist.image_link, 'start_time':show.start_time})
  return render_template('pages/shows.html', shows=shows_info)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form, meta={'csrf':False})
  # Todo: check for existence of foreign keys
  if form.validate():
    error = False
    err_msg = 'An error occurred. Show could not be listed.'
    show = {
      'artist_id':form.artist_id.data, 'venue_id':form.venue_id.data, 'start_time':form.start_time.data
    }
    try:
      show_model = Show(**show)
      db.session.add(show_model)
      db.session.commit()
    # except IntegrityError as e:
    #   print("Statement: ", e.statement)
    #   print("Params: ", e.params)
    #   print("Orig: ", e.orig)
    #   err_msg = 'Integrity error!'
    #   raise e
    except Exception as e:
      # if isinstance(e, IntegrityError):
      #   print("Integrity Error!")
      #   print("Statement: ", e.statement)
      #   print("Params: ", e.params)
      #   print("Orig: -->{}<--".format(e.orig))
      #   err_msg = 'Integrity error!'
      #   if isinstance(e.orig, ForeignKeyViolation):
      #     print("It's an FK violation!")
      if e.orig and isinstance(e.orig, ForeignKeyViolation):
        err_msg = 'Invalid submission. Show must use valid artist and venue ids.'
      # psycopg2.errors.ForeignKeyViolation
      # sqlalchemy.exc.IntegrityError
      #print("Exception class:", e.__class__)
      error = True
      db.session.rollback()
      print("Error on Show db model: {}".format(e))
    finally:
      db.session.close()

    if error:
      flash(err_msg)
      return render_template('forms/new_show.html', form=form)
    else:
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
  else:
    flash_errors(form)
    return render_template('forms/new_show.html', form=form)

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
