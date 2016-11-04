import peewee
from peewee_async import Manager, PostgresqlDatabase

database = PostgresqlDatabase(database='test')


class BaseModel(peewee.Model):
    class Meta:
        database = database


class KeyValue(BaseModel):
    key = peewee.CharField(max_length=40, unique=True)
    value = peewee.TextField(default='')


def initdb():
    with database.allow_sync():
        KeyValue.create_table(True)


def make_manager(loop=None):
    # create table synchronously
    manager = Manager(database, loop=loop)
    # disable any future syncronous calls
    # raise AssertionError on ANY sync call
    manager.database.allow_sync = False
    return manager
