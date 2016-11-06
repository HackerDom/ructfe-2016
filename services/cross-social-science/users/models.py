from datetime import datetime
from json import loads

import peewee
from peewee_async import Manager


class AnonymousUser:
    username = 'AnonymousUser'

    def is_authenticated(self):
        return False

    def __str__(self):
        return 'AnonymousUser'


def make_models(db, db_name, loop):
    class User(peewee.Model):
        username = peewee.CharField(unique=True, max_length=50)
        password_hash = peewee.CharField(max_length=60)
        created = peewee.DateTimeField(default=datetime.now, index=True)
        raw_meta = peewee.TextField(default='')

        @property
        def meta(self):
            if not self.raw_meta:
                return None
            try:
                return loads(self.raw_meta)
            except (TypeError, ValueError):
                pass
            return None

        def is_authenticated(self):
            return True

        def __str__(self):
            return self.username

        class Meta:
            database = db
            db_table = db_name

    def initdb():
        with db.allow_sync():
            User.create_table(True)

    def dropdb():
        with db.allow_sync():
            User.drop_table(True)

    def make_manager():
        manager = Manager(db, loop=loop)
        manager.database.allow_sync = False
        return manager

    return initdb, dropdb, make_manager(), User
