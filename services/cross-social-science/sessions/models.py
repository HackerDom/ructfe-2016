import peewee
from peewee_async import Manager


def make_models(db, db_name, loop):
    class KeyValue(peewee.Model):
        key = peewee.CharField(max_length=40, unique=True)
        value = peewee.TextField(default='')

        class Meta:
            database = db
            db_table = db_name

    def initdb():
        with db.allow_sync():
            KeyValue.create_table(True)

    def dropdb():
        with db.allow_sync():
            KeyValue.drop_table(True)

    def make_manager():
        # create table synchronously
        manager = Manager(db, loop=loop)
        # disable any future syncronous calls
        # raise AssertionError on ANY sync call
        manager.database.allow_sync = False
        return manager

    return initdb, dropdb, make_manager(), KeyValue
