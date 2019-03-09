from flask import g, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.local import LocalProxy
from werkzeug.contrib.cache import FileSystemCache


db = SQLAlchemy()


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)


class OpenStreetMapToken(db.Model):
    osm_uid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey("user.user_id"), nullable=False)
    display_name = db.Column(db.String(20), nullable=False)

    oauth_token = db.Column(db.String(48), nullable=False)
    oauth_token_secret = db.Column(db.String(48))

    def to_dict(self):
        return dict(
            oauth_token=self.oauth_token,
            oauth_token_secret=self.oauth_token_secret,
        )

    @classmethod
    def save(self, osm_uid, display_name, oauth_token, oauth_token_secret):
        osm_user = OpenStreetMapToken.query.get({"osm_uid": osm_uid})
        if osm_user is None:
            # This user has never logged in via OSM before and we don't have any info
            # about linking accounts (yet): add a new row to users and one to OSM
            # tokens
            # TODO: prevent creation of user prior to creation of OSM user - they
            # should be created simultaneously, otherwise rollback
            user = User()
            db.session.add(user)
            db.session.flush()
            db.session.commit()

            osm_user = OpenStreetMapToken(
                osm_uid=osm_uid,
                user_id=user.user_id,
                display_name=display_name,
                oauth_token=oauth_token,
                oauth_token_secret=oauth_token_secret
            )
        else:
            osm_user.display_name = display_name  # Sometimes this changes
            osm_user.oauth_token = oauth_token
            osm_user.oauth_token_secret = oauth_token_secret
        db.session.add(osm_user)
        db.session.flush()
        db.session.commit()

        return osm_user


class Profile(db.Model):
    profile_id = db.Column(db.Integer, primary_key=True)
    # TODO: remove uniqueness constraint when adding multiple profiles functionality
    user_id = db.Column(db.ForeignKey("user.user_id"), nullable=False, unique=True)
    uphill_max = db.Column(db.Float, nullable=False)
    downhill_max = db.Column(db.Float, nullable=False)
    avoid_curbs = db.Column(db.Boolean, nullable=False)

    @classmethod
    def save(self, user_id, uphill_max, downhill_max, avoid_curbs):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile is None:
            # This is a brand new profile - create a new row
            profile = Profile(
                user_id=user_id,
                uphill_max=uphill_max,
                downhill_max=downhill_max,
                avoid_curbs=avoid_curbs
            )
            db.session.add(profile)
            db.session.flush()
            db.session.commit()
        else:
            # Update the profile
            profile.uphill_max = uphill_max
            profile.downhill_max = downhill_max
            profile.avoid_curbs = avoid_curbs
        db.session.add(profile)
        db.session.flush()
        db.session.commit()


def _get_cache():
    _cache = g.get('_oauth_cache')
    if _cache:
        return _cache
    _cache = FileSystemCache(current_app.config['OAUTH_CACHE_DIR'])
    g._oauth_cache = _cache
    return _cache


cache = LocalProxy(_get_cache)
