from datetime import datetime
from json import loads

import peewee
from peewee_async import Manager
from markdown import markdown
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache

# Configure micawber with the default OEmbed providers (YouTube, Flickr, etc).
# We'll use a simple in-memory cache so that multiple requests for the same
# video don't require multiple network requests.
oembed_providers = bootstrap_basic(OEmbedCache())


def make_models(db, db_name, loop):
    class Entry(peewee.Model):
        title = peewee.CharField()
        slug = peewee.CharField(unique=True)
        content = peewee.TextField(default='')
        raw_meta = peewee.TextField(default='')
        is_published = peewee.BooleanField(default=False, index=True)
        timestamp = peewee.DateTimeField(default=datetime.now, index=True)

        @property
        def meta(self):
            if not self.raw_meta:
                return None
            try:
                return loads(self.raw_meta)
            except (TypeError, ValueError):
                pass
            return None

        @property
        def html_content(self):
            """
            Generate HTML representation of the markdown-formatted blog entry,
            and also convert any media URLs into rich media objects such as
            video players or images.
            """
            try:
                markdown_content = markdown(self.content, extensions=[])
                oembed_content = parse_html(
                    markdown_content,
                    oembed_providers,
                    urlize_all=True)
            except Exception as e:
                print(e)
                raise
            return oembed_content

        class Meta:
            database = db
            db_table = db_name

    def initdb():
        with db.allow_sync():
            Entry.create_table(True)

    def dropdb():
        with db.allow_sync():
            Entry.drop_table(True)

    def make_manager():
        # create table synchronously
        manager = Manager(db, loop=loop)
        # disable any future syncronous calls
        # raise AssertionError on ANY sync call
        manager.database.allow_sync = False
        return manager

    return initdb, dropdb, make_manager(), Entry
