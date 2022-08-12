# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
from logging import Formatter, FileHandler

import babel
import dateutil.parser
from flask import render_template, request, flash, redirect, url_for

from forms import *
from models import Venue, Artist, app, db, Show


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def validate(date_text):
    # Validates a date string
    try:
        datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD HH:MM:SS")


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues = Venue.query.all()
    cities = db.session.query(Venue.city, Venue.state).filter(Venue.id > 0) \
        .order_by(Venue.state).order_by(Venue.city).distinct().all()
    print(cities)
    data = []
    for city in cities:
        city_venues = []
        for venue in venues:
            if venue.city == city[0] and venue.state == city[1]:
                city_venues.append({
                    "id": venue.id,
                    "name": venue.name
                })
        data.append({
            "city": city[0],
            "state": city[1],
            "venues": city_venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    search_term = "%{}%".format(search_term)
    venues = Venue.query.filter(Venue.name.ilike(search_term)).all()
    data = []
    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name
        })
    response = {
        "count": len(venues),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    upcoming_shows = db.session.query(Artist, Show) \
        .filter(Artist.id == Show.artist_id) \
        .filter(Show.venue_id == venue_id) \
        .filter(Show.start_time > datetime.now()) \
        .all()
    past_shows = db.session.query(Artist, Show) \
        .filter(Artist.id == Show.artist_id) \
        .filter(Show.venue_id == venue_id) \
        .filter(Show.start_time < datetime.now()) \
        .all()

    dict_list = []
    for (artist, show) in upcoming_shows:
        dict_list.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })
    upcoming_shows = dict_list

    dict_list = []
    for (artist, show) in past_shows:
        dict_list.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })
    past_shows = dict_list

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(','),
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "address": "1015 Folsom Street",
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    seeking_talent = request.form.get('seeking_talent', '')
    seeking_talent = bool(seeking_talent)
    new_venue = Venue(
        name=request.form["name"],
        city=request.form["city"],
        state=request.form["state"],
        phone=request.form["phone"],
        address=request.form["address"],
        genres=",".join(request.form.getlist('genres')),
        image_link=request.form.get('image_link', None),
        seeking_description=request.form.get('seeking_description', None),
        facebook_link=request.form.get('facebook_link', None),
        website_link=request.form.get('website_link', None),
        seeking_talent=seeking_talent
    )

    try:
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
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
    artists = Artist.query.all()
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search_term = "%{}%".format(search_term)
    artists = Artist.query.filter(Artist.name.ilike(search_term)).all()
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    response = {
        "count": len(artists),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    upcoming_shows = db.session.query(Venue, Show) \
        .filter(Venue.id == Show.venue_id) \
        .filter(Show.artist_id == artist_id) \
        .filter(Show.start_time > datetime.now()) \
        .all()
    past_shows = db.session.query(Artist, Show) \
        .filter(Venue.id == Show.venue_id) \
        .filter(Show.artist_id == artist_id) \
        .filter(Show.start_time < datetime.now()) \
        .all()

    dict_list = []
    for (venue, show) in upcoming_shows:
        dict_list.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })
    upcoming_shows = dict_list
    dict_list = []
    for (venue, show) in past_shows:
        dict_list.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })
    past_shows = dict_list

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.choices = [(artist.state, artist.state)]
    for state in STATE_CHOICES:
        if state[0] != artist.state:
            form.state.choices.append(state)
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.genres.data = artist.genres.split(",")
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website_link
    seeking_venue = "y" if artist.seeking_venue else ""
    form.seeking_venue.data = seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    artist.name = request.form["name"]
    artist.city = request.form["city"]
    artist.state = request.form["state"]
    artist.phone = request.form["phone"]
    artist.genres = ",".join(request.form.getlist('genres'))
    artist.image_link = request.form.get('image_link', None)
    artist.seeking_description = request.form.get('seeking_description', None)
    artist.facebook_link = request.form.get('facebook_link', None)
    artist.website_link = request.form.get('website_link', None)
    seeking_venue = bool(request.form.get('seeking_venue', ''))
    artist.seeking_venue = seeking_venue

    try:
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    except:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.address.data = venue.address
    form.state.choices = [(venue.state, venue.state)]
    for state in STATE_CHOICES:
        if state[0] != venue.state:
            form.state.choices.append(state)
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.genres.data = venue.genres.split(",")
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website_link
    seeking_talent = "y" if venue.seeking_talent else ""
    form.seeking_talent.data = seeking_talent
    form.seeking_description.data = venue.seeking_description

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
    seeking_venue = request.form.get('seeking_venue', '')
    seeking_venue = bool(seeking_venue)
    new_artist = Artist(
        name=request.form["name"],
        city=request.form["city"],
        state=request.form["state"],
        phone=request.form["phone"],
        genres=",".join(request.form.getlist('genres')),
        image_link=request.form.get('image_link', None),
        seeking_description=request.form.get('seeking_description', None),
        facebook_link=request.form.get('facebook_link', None),
        website_link=request.form.get('website_link', None),
        seeking_venue=seeking_venue
    )

    try:
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = []
    for show in shows:
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)
        data.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    artist_id = request.form["artist_id"]
    venue_id = request.form["venue_id"]
    start_time = request.form["start_time"]
    artist_exists = bool(Artist.query.filter_by(id=artist_id).first())
    venue_exists = bool(Venue.query.filter_by(id=venue_id).first())
    if artist_exists and venue_exists:
        try:
            validate(start_time)
            show = Show(
                artist_id=artist_id,
                venue_id=venue_id,
                start_time=start_time
            )
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except ValueError as error:
            flash(error)
        except Exception as ex:
            print(ex)
            db.session.rollback()
            flash('An error occurred. Show could not be listed.')
        finally:
            db.session.close()
    else:
        flash('Invalid artist or venue id')

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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
