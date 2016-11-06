import peewee
from peewee_async import Manager


def make_models(db, db_name, loop):
    class BaseModel(peewee.Model):
        class Meta:
            database = db
            db_table = db_name

    class User(BaseModel):
        username = peewee.CharField(unique=True, max_length=40)
        password_hash = peewee.CharField()
        registration_date = peewee.DateField()

    def init_db():
        with db.allow_sync():
            User.create_table(True)

    def drop_db():
        with db.allow_sync():
            User.drop_table(True)

    def make_manager():
        manager = Manager(db, loop=loop)
        manager.database.allow_sync = False
        return manager

    return init_db, drop_db, make_manager(), User
