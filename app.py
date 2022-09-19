#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import abort
from ssl import CHANNEL_BINDING_TYPES
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import *
from flask_migrate import Migrate
from flask import Flask
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String)
    website_link=db.Column(db.String(120), nullable=True)
    talent=db.Column(db.Boolean,nullable=True)
    description = db.Column(db.String(500),nullable=True)
    show = db.relationship('Show',backref='venue',lazy=True)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link=db.Column(db.String,nullable=True)
    venue = db.Column(db.Boolean,nullable=True)
    description=db.Column(db.String,nullable=True)
    shows=db.relationship('Show', backref='artist',lazy=True)    

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer,primary_key=True)
    artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
    venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
    start_time = db.Column(db.DateTime,nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value,str):
    date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = []
  cities = db.session.query(Venue.city,Venue.state)
  for city in cities:
    venue = db.session.query(Venue).filter_by(city=city.city,state=city.state)
    
    for venue in venue:
      upcoming_shows_count = db.session.query(Show).filter_by(venue_id=venue.id).count()
      venues.append({
        'city':city.city,
        'state':city.state,
        "venues":[{
          'id':venue.id,
          'name':venue.name,
          'num_upcoming_shows':upcoming_shows_count
        }]
      })    
  return render_template('pages/venues.html', areas=venues)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venue = db.session.query(Venue).filter(Venue.name.ilike('%' + request.form.get('search_term') + '%')).all()
  response={
    "count": len(venue),
    "data": venue
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Artist.query.get(venue_id)
  now = datetime.now()
  data = venue.__dict__
  shows = db.session.query(Show).filter_by(venue_id=venue_id)
  past_shows = shows.filter(Show.start_time < now).all()
  upcoming_shows =  shows.filter(Show.start_time >= now).all()
  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)
  
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count']= upcoming_shows_count
  data['past_shows_count'] = past_shows_count 
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST', 'GET'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    error= False
    try:
        name = request.form['name']
        city= request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        genres = request.form['genres']
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        website_link = request.form['website_link']
        talent = request.form['seeking_talent']
        description = request.form['seeking_description']
        talent = talent == 'y'
  # TODO: modify data to be the data object returned from db insertion
        venue_data = Venue(name=name,city=city,state=state,address=address,phone=phone,genres=genres,image_link=image_link,facebook_link=facebook_link,website_link=website_link,talent=talent,description=description)
        db.session.add(venue_data)
        db.session.commit()

  # on successful db insert, flash success
        flash(f'Venue {venue_data.name} was successfully listed!')
    except Exception:
        db.session.rollback()
    finally:
        db.session.close()
    if error:
      flash('An error occurred. Venue could not be listed.')
    else:
      return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    venue = Venue.query.get(venue_id)

    if venue is None:
      abort(400)
    try:
        db.session.delete(venue)
        db.session.commit()
        flash('Venue deleted!')
    except Exception:
        error = True
        db.session.rollback()
        flash('Error occurred: Venue could not be deleted.')
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artist = db.session.query(Artist).filter(Artist.name.ilike('%' + request.form.get('search_term') + '%')).all()
  response={
    "count": len(artist),
    "data": artist
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  now = datetime.now()
  data = artist.__dict__
  shows = db.session.query(Show).filter_by(artist_id=artist_id)
  past_shows = shows.filter(Show.start_time < now).all()
  upcoming_shows =  shows.filter(Show.start_time >= now).all()
  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count']= upcoming_shows_count
  data['past_shows_count'] = past_shows_count
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  artist=Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    try:
        form.populate_obj(artist)
        db.session.commit()
        flash('Artist '+ request.form['name']+ ' was edited successfully!')
    except Exception:
        db.session.rollback()
        flash('Artist '+request.form['name']+' could not be listed')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue=Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    venue = Artist.query.get(venue_id)
    try:
        form.populate_obj(venue)
        db.session.commit()
        flash('Venue '+ request.form['name']+ ' was edited successfully!')
    except Exception:
        db.session.rollback()
        flash('Venue '+request.form['name']+' could not be listed')
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        image = request.form['image_link']
        genres = request.form['genres']
        facebook = request.form['facebook_link']
        website = request.form['website_link']
        venue = request.form.get('seeking_venue')
        description = request.form['seeking_description']
        venue = venue == 'y'
        artist_data = Artist(name=name,city=city,state=state,phone=phone,genres=genres,image=image,facebook=facebook,website=website,description=description,venue=venue)
        db.session.add(artist_data)
        db.session.commit()

  # on successful db insert, flash success
        flash(f'Artist {artist_data.name} was successfully listed!')
    except Exception:
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash(f'An error occurred. Artist {artist_data.name} could not be listed.')
    else:
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]
  now = datetime.now()
  shows =Show.query.all()
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    if show.start_time > now:
      data.append({
        'venue_id':show.venue_id,
        'artist_id':show.artist_id,
        'start_time':show.start_time,
        'artist_name':artist.name,
        'artist_image_link':artist.image,
        'venue_name':venue.name
      })
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
    try:
        artist = request.form['artist_id']
        venue = request.form['venue_id']
        date = request.form['start_time']
        show_data = Show(artist_id=artist,venue_id=venue,start_time=date)
        db.session.add(show_data)
        db.session.commit()

  # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
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
    app.debug=True
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
