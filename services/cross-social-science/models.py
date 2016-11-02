import peewee
from peewee_async import Manager, PostgresqlDatabase

database = PostgresqlDatabase(database='test')


class BaseModel(peewee.Model):
    class Meta:
        database = database


def make_models(database=database, base_model=BaseModel, loop=None):
    class KeyValue(base_model):
        key = peewee.CharField(max_length=40, unique=True)
        value = peewee.TextField(default='')

    # create table synchronously
    KeyValue.create_table(True)
    database.close()

    manager = Manager(database, loop=loop)
    # disable any future syncronous calls
    # raise AssertionError on ANY sync call
    manager.database.allow_sync = False

    return manager, KeyValue


# @app.route('/post/<key>/<value>')
# async def post(request, key, value):
#     """
#     Save get parameters to database
#     """
#     obj = await objects.create(KeyValue, key=key, text=value)
#     return json({'object_id': obj.id})
#
#
# @app.route('/get')
# async def get(request):
#     """
#     Load all objects from database
#     """
#     all_objects = await objects.execute(KeyValue.select())
#     serialized_obj = []
#     for obj in all_objects:
#         serialized_obj.append({
#             'id': obj.id,
#             'key': obj.key,
#             'value': obj.text}
#         )
#
#     return json({'objects': serialized_obj})
