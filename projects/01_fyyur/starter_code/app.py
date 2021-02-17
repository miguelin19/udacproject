#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask import Flask, flash, render_template, request,redirect, url_for,jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from forms import ShowForm, VenueForm, ArtistForm
from datetime import *
import dateutil.parser
import babel
import sys
from models import Show, Venue, Artist
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
#moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
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
  now = datetime.today()
  areas = db.session.query(Venue.city, Venue.state).order_by(Venue.city).distinct()
  venues = Venue.query.all()
  query = db.session.query(Venue.id, func.count(Show.venue_id)).filter(Show.start_time > now )
  query = query.outerjoin(Show, Venue.id == Show.venue_id)
  query = query.group_by(Venue.id)
  return render_template('pages/venues.html', areas=areas, venues=venues, up_shows=query)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search = request.form.get('search_term', '')
  search_term = "%{}%".format(search)
  results = Venue.query.filter(Venue.name.ilike(search_term))
  return render_template('pages/search_venues.html', results=results, search_term=search)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  now = datetime.today()
  past_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time < now ).all()
  p_shows = len(past_shows)
  upcoming_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time > now ).all()
  u_shows = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=Venue.query.get(venue_id),past_shows = past_shows, upcoming_shows = upcoming_shows,
                          p_shows=p_shows, u_shows=u_shows)

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)
  # TODO: modify data to be the data object returned from db insertion
  if form.validate_on_submit():
    try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      address = form.address.data
      phone = form.phone.data
      facebook_link = form.facebook_link.data
      genres = form.genres.data
      image_link = form.image_link.data
      website = form.website.data
      seeking_talent = form.seeking_talent.data
      seeking_description = form.seeking_description.data
      venue = Venue(name=name, city=city, state=state, address=address, phone=phone, facebook_link=facebook_link, genres=genres,
                    image_link=image_link, website=website, seeking_talent=bool(seeking_talent), seeking_description=seeking_description)
      db.session.add(venue)
      db.session.commit()
    # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')
  else:
    print(form.errors)
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue=Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    flash('Venue ' + venue.name + ' could not be deleted!')
    db.session.rollback()
    print(sys.exc_info())
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
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search = request.form.get('search_term', '')
  search_term = "%{}%".format(search)
  results = Artist.query.filter(Artist.name.ilike(search_term))
  return render_template('pages/search_artists.html', results=results, search_term=search)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using artist_id
  now = datetime.today()
  past_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time < now ).all()
  p_shows = len(past_shows)
  upcoming_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time > now ).all()
  u_shows = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=Artist.query.get(artist_id), past_shows = past_shows, upcoming_shows = upcoming_shows,
                          p_shows = p_shows, u_shows=u_shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist=Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.website.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  # TODO: take values from the form submitted, and update existing
  if form.validate_on_submit():
    try:
      a = db.session.query(Artist).get(artist_id)
      a.name = form.name.data
      a.city = form.city.data
      a.state = form.state.data
      a.phone = form.phone.data
      a.facebook_link = form.facebook_link.data
      a.genres = form.genres.data
      a.image_link = form.image_link.data
      a.website = form.website.data
      a.seeking_venue = bool(form.seeking_venue.data)
      a.seeking_description = form.seeking_description.data
    # artist record with ID <artist_id> using the new attributes
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
      flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    print(form.errors)
    return render_template('forms/edit_artist.html', form=form)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.facebook_link.data = venue.facebook_link
  form.genres.data = venue.genres
  form.image_link.data = venue.image_link
  form.website.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  # # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  # TODO: take values from the form submitted, and update existing
  if form.validate_on_submit():
    try:
      a = db.session.query(Venue).get(venue_id)
      a.name = form.name.data
      a.city = form.city.data
      a.state = form.state.data
      a.phone = form.phone.data
      a.address = form.address.data
      a.facebook_link = form.facebook_link.data
      a.genres = form.genres.data
      a.image_link = form.image_link.data
      a.website = form.website.data
      a.seeking_talent = bool(form.seeking_talent.data)
      a.seeking_description = form.seeking_description.data
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
      flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    print(form.errors)
    return render_template('forms/edit_venue.html', form=form)
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form)
  # TODO: insert form data as a new Venue record in the db, instead
  if form.validate_on_submit():
    try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      facebook_link = form.facebook_link.data
      genres = form.genres.data
      image_link = form.image_link.data
      website = form.website.data
      seeking_venue = form.seeking_venue.data
      seeking_description = form.seeking_description.data
      artist = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link, genres=genres,
      image_link=image_link, website=website, seeking_venue=bool(seeking_venue), seeking_description=seeking_description)
      db.session.add(artist)
      db.session.commit()
    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    return render_template('pages/home.html')
  else:
    print(form.errors)
    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  return render_template('pages/shows.html', shows=Show.query.order_by(Show.start_time.desc()).all())

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  # on successful db insert, flash success
  try:
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data
    if not start_time:
      flash('Wrong time format')
    show = Show(venue_id = venue_id, artist_id = artist_id, start_time = start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''