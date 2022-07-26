#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
  )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
#My code
#----------------------------------------------------------------------------#
from flask_migrate import Migrate
from datetime import datetime
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)
# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  #date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(value, format, locale='en')

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
  venues = Venue.query.all() 
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.


  return render_template('pages/venues.html', areas=venues);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  if search_term:
    response = Venue.query.filter(Venue.name.ilike('%'+search_term+'%'))
    count = response.count()
  else:
    count = ''
    response = ''
    flash('Please insert a value to search for a venue')
  return render_template(
      'pages/search_venues.html', 
      count=count, 
      results=response, 
      search_term=search_term
    )

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  """  num_upcoming_shows = Show.query.join(Artist).join(Venue)\
  .filter((Show.artist_id == Artist.id) & (Show.venue_id == Venue.id)).all()"""

  upcoming_shows = []
  past_shows = []

  for show in venue.shows:
    filtered_show = {
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y at %H:%M") 
    }
    if show.start_time <= datetime.now():
      past_shows.append(filtered_show)
    else:
      upcoming_shows.append(filtered_show)

  data = vars(venue)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  #this is not secure but since we haven't done how to propaly
  #manage secret keys in this course, I guess we will leave it
  #till then so we can write meta={'csrf': True} or just leave
  #it as it is session secure.
  form = VenueForm(request.form, meta={'csrf': False})

  if form.validate():
    try:
      venue = Venue(
          name = form.name.data,
          city = form.city.data,
          state = form.state.data,
          address = form.address.data,
          phone = form.phone.data,
          genres = form.genres.data,
          image_link = form.image_link.data,
          facebook_link = form.facebook_link.data,
          website_link = form.website_link.data,
          seeking_talent = form.seeking_talent.data,
          seeking_description = form.seeking_description.data
      )

      db.session.add(venue)
      db.session.commit()
      flash('Venue, ' + form.name.data + ' was successfully listed!')
    except ValueError as e:
        print(e)
        db.session.rollback()
    finally:
        db.session.close()
  else:
      message = []
      for field, err in form.errors.items():
          message.append(field + ' ' + '|'.join(err))
      flash('Errors ' + str(message))
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False 

  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    print(sys.exc_info)
    db.session.rollback()
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
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  if search_term:
    response = Artist.query.filter(Artist.name.ilike('%'+search_term+'%'))
    count = response.count()
  else:
    count = ''
    response = ''
    flash('Please insert a value to search for artist')
  return render_template('pages/search_artists.html', count=count, results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get_or_404(artist_id)

  upcoming_shows = []
  past_shows = []

  for show in artist.shows:
    filtered_show = {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M") 
    }
    if show.start_time <= datetime.now():
      past_shows.append(filtered_show)
    else:
      upcoming_shows.append(filtered_show)

  data = vars(artist)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)


  error = False
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    artist.seeking_venue = request.form.get('seeking_venue', '')
    if artist.seeking_venue == '':
      artist.seeking_venue = False
    else:
      artist.seeking_venue = True
    artist.seeking_description = request.form['seeking_description']
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Aritst details could not be edited.')
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  venue = Venue.query.get(venue_id)

  error = False
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = request.form.get('seeking_talent', '')
    if venue.seeking_talent == '':
      venue.seeking_talent = False
    else:
      venue.seeking_talent = True
    venue.seeking_description = request.form['seeking_description']
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue details could not be edited.')
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm(request.form, meta={'csrf': False})

  if form.validate():
    try:
      artist = Artist(
          name = form.name.data,
          city = form.city.data,
          state = form.state.data,
          phone = form.phone.data,
          genres = form.genres.data,
          image_link = form.image_link.data,
          facebook_link = form.facebook_link.data,
          website_link = form.website_link.data,
          seeking_venue = form.seeking_venue.data,
          seeking_description = form.seeking_description.data
      )

      db.session.add(artist)
      db.session.commit()
      flash('Artist, ' + form.name.data + ' was successfully listed!')
    except ValueError as e:
        print(e)
        db.session.rollback()
    finally:
        db.session.close()
  else:
      message = []
      for field, err in form.errors.items():
          message.append(field + ' ' + '|'.join(err))
      flash('Errors ' + str(message))
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.join(Artist).join(Venue).\
  filter((Show.artist_id == Artist.id) & (Show.venue_id == Venue.id)).all()

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  form = ShowForm()
  if form.validate():
    try:
        start_time = request.form['start_time']
        show = Show(start_time=start_time)
        show.artist_id = request.form['artist_id']
        show.venue_id = request.form['venue_id']
        print(show.artist_id, show.venue_id)
        print(show.start_time)


        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
      error = True
      print(sys.exc_info())
      db.session.rollback()
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Show could not be listed.')
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
