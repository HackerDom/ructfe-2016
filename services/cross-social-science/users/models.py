import peewee
from peewee_async import Manager


def make_models(db, db_name, loop):
    class User(peewee.Model):
        username = peewee.CharField(unique=True, max_length=40)
        password_hash = peewee.CharField()
        registration_date = peewee.DateField()

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
