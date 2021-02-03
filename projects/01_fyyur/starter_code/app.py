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
from sqlalchemy import func
from datetime import datetime
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import re
from models import app, db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

# TODO: connect to a local postgresql database -> DONE


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
    #       num_shows should be aggregated based on number of upcoming shows per venue. -> DONE
    data = []
    error = False
    try:
        cities = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
        for city in cities:
            venues = db.session.query(Venue.id, Venue.name).filter(Venue.city==city[0], Venue.state==city[1]).all()
            venues_shows = []
            for venue in venues:
              num_upcoming_shows = db.session.query(Show).filter(Show.venue_id==venue[0], Show.start_time>datetime.utcnow()).count()
              #venue['num_upcoming_shows'] = num_upcoming_shows
              venue_shows = { 'id': venue[0], 'name': venue[1], 'num_upcoming_shows': num_upcoming_shows }
              venues_shows.append(dict(venue_shows))
            d = { 'city': city[0], 'state': city[1], 'venues': venues_shows }
            data.append(dict(d))
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" --> DONE
  response = {}
  data = []
  error = False
  search_term = request.form.get('search_term', '')
  try:
      search_results = db.session.query(Venue.id, Venue.name).filter(Venue.name.ilike('%{}%'.format(search_term))).all()
      for venue in search_results:
        num_upcoming_shows = db.session.query(Show).filter(Show.venue_id==venue[0], Show.start_time>datetime.utcnow()).count()
        venue_shows = { 'id': venue[0], 'name': venue[1], 'num_upcoming_shows': num_upcoming_shows }
        data.append(dict(venue_shows))
      response.update({'count':len(search_results), 'data':data })
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if not error:
      return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id --> DONE
  # TODO: replace with real venue data from the venues table, using venue_id
    error = False
    try:
        venue = Venue.query.get(venue_id)
        upcoming_shows_details = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id, Show.start_time > datetime.utcnow()).all()
        past_shows_details = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id, Show.start_time < datetime.utcnow()).all()
        upcoming_shows = []
        past_shows = []
        for show in upcoming_shows_details:
            upcoming_shows.append({
                        'artist_id' : show.Artist.id,
                        'artist_name': show.Artist.name,
                        'artist_image_link': show.Artist.image_link,
                        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                        })
        for show in past_shows_details:
            past_shows.append({
                        'artist_id' : show.Artist.id,
                        'artist_name': show.Artist.name,
                        'artist_image_link': show.Artist.image_link,
                        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                        })
        data = {
                "id": venue.id,
                "name": venue.name,
                "genres": list(re.sub('[^a-zA-Z+,]','',venue.genres).split(",")),
                "address": venue.address,
                "city": venue.city,
                "state": venue.state,
                "phone": venue.phone,
                "website": venue.website,
                "facebook_link": venue.facebook_link,
                "seeking_talent": venue.seeking_talent,
                "seeking_description": venue.seeking_description,
                "image_link": venue.image_link,
                "past_shows": past_shows,
                "upcoming_shows": upcoming_shows,
                "past_shows_count": len(past_shows),
                "upcoming_shows_count": len(upcoming_shows)
                }
    except:
        error: True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = VenueForm(request.form)
    try:
        # TODO: insert form data as a new Venue record in the db, instead --> DONE
        # TODO: modify data to be the data object returned from db insertion
        if form.validate():
            data = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=request.form.getlist('genres'),
                facebook_link=form.facebook_link.data,
                website=form.website.data,
                image_link=form.image_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(data)
            db.session.commit()
        else:
            error = True
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        # TODO: on unsuccessful db insert, flash an error instead. --> DONE
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        return render_template('forms/new_venue.html', form=form)
    else:
        # on successful db insert, flash success --> DONE
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail. -> DONE

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage -> DONE
  error = False
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Venue could not be deleted.')
      return redirect(url_for('venues'))
  else:
      flash('Venue was successfully deleted')
      return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
    error = False
    try:
        artists = Artist.query.with_entities(Artist.id, Artist.name).all()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
    error = False
    response = {}
    data = []
    search_term = request.form.get('search_term', '')
    try:
        search_results = db.session.query(Artist.id, Artist.name).filter(Artist.name.ilike('%{}%'.format(search_term))).all()
        for artist in search_results:
            num_upcoming_shows = db.session.query(Show).filter(Show.artist_id==artist[0], Show.start_time>datetime.utcnow()).count()
            artist_shows = { 'id': artist[0], 'name': artist[1], 'num_upcoming_shows': num_upcoming_shows }
            data.append(dict(artist_shows))
        response.update({'count':len(search_results), 'data':data })
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.commit()
    if not error:
        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    error = False
    try:
        artist = Artist.query.get(artist_id)
        upcoming_shows_details = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id, Show.start_time > datetime.utcnow()).all()
        past_shows_details = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id, Show.start_time < datetime.utcnow()).all()
        upcoming_shows = []
        past_shows = []
        for show in upcoming_shows_details:
            upcoming_shows.append({
                        'venue_id' : show.Venue.id,
                        'venue_name': show.Venue.name,
                        'venue_image_link': show.Venue.image_link,
                        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                        })
        for show in past_shows_details:
            past_shows.append({
                        'venue_id' : show.Venue.id,
                        'venue_name': show.Venue.name,
                        'venue_image_link': show.Venue.image_link,
                        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                        })
        data = {
            'id': artist.id,
            'name': artist.name,
            'genres': list(re.sub('[^a-zA-Z+,]','',artist.genres).split(",")),
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'website': artist.website,
            'facebook_link': artist.facebook_link,
            'seeking_venue': artist.seeking_venue,
            'seeking_description': artist.seeking_description,
            'image_link': artist.image_link,
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close
    if not error:
        return render_template('pages/show_artist.html', artist=data)
# shows the venue page with the given venue_id
# TODO: replace with real venue data from the venues table, using venue_id -> DONE

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.process(obj=artist)
  form.genres.data = artist.genres
  # TODO: populate form with fields from artist with ID <artist_id> --> DONE
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes -- DONE
  error=False
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  try:
      if form.validate():
          artist.name = request.form['name']
          artist.city = request.form['city']
          artist.state = request.form['state']
          artist.phone = request.form['phone']
          artist.genres = request.form.getlist('genres')
          artist.facebook_link = request.form['facebook_link']
          artist.website=request.form['website']
          artist.image_link=request.form['image_link']
          artist.seeking_venue=form.seeking_venue.data
          artist.seeking_description=request.form['seeking_description']
          db.session.commit()
      else:
          error=True
  except:
      error=True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.process(obj=venue)
  form.genres.data = venue.genres
  # TODO: populate form with values from venue with ID <venue_id> --> DONE
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    form = VenueForm(request.form)
    try:
        if form.validate():
            venue = Venue.query.get(venue_id)
            venue.name = request.form['name']
            venue.city = request.form['city']
            venue.state = request.form['state']
            venue.address = request.form['address']
            venue.phone = request.form['phone']
            venue.genres = request.form.getlist('genres')
            venue.facebook_link = request.form['facebook_link']
            venue.website=request.form['website']
            venue.image_link=request.form['image_link']
            venue.seeking_talent=form.seeking_talent.data
            venue.seeking_description=request.form['seeking_description']
            db.session.commit()
        else:
            error=True
    except:
        db.session.rollback()
        error=True
    finally:
        db.session.close()
    if error:
        flash("Something's wrong. Can't edit")
        return redirect(url_for('index'))
    else:
        return redirect(url_for('show_venue', venue_id=venue_id))
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes --> DONE

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    form = ArtistForm(request.form)
    try:
        # TODO: insert form data as a new Venue record in the db, instead
        # TODO: modify data to be the data object returned from db insertion --> DONE
        if form.validate():
            data = Artist(
                name=request.form['name'],
                city=request.form['city'],
                state=request.form['state'],
                phone=request.form['phone'],
                genres = request.form.getlist('genres'),
                facebook_link=request.form['facebook_link'],
                website=request.form['website'],
                image_link=request.form['image_link'],
                seeking_venue=form.seeking_venue.data,
                seeking_description=request.form['seeking_description']
                )
            db.session.add(data)
            db.session.commit()
        else:
            error=True
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.') --> DONE
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        return render_template('forms/new_artist.html', form=form)
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    error = False
    data = []
    try:
        shows = Show.query.all()
        for show in shows:
            d = {
                "venue_id": show.Venue.id,
                "venue_name": show.Venue.name,
                "artist_id": show.Artist.id,
                "artist_name": show.Artist.name,
                "artist_image_link": show.Artist.image_link,
                "start_time": show.start_time.isoformat(timespec='minutes')
            }
            data.append(dict(d))
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        return render_template('pages/shows.html', shows=data)

  # displays list of shows at /shows
  # TODO: replace with real venues data. --> DONE
  #       num_shows should be aggregated based on number of upcoming shows per venue.???

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        show = Show(artist_id=request.form['artist_id'], venue_id=request.form['venue_id'], start_time=request.form['start_time'])
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
    else:
        form = ShowForm()
        flash('An error occurred. Show could not be listed.')
        return render_template('forms/new_show.html', form=form)
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success --> DONE
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.') ->> DONE
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

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
