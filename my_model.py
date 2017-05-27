
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import datetime
import os

DB_PATH = 'data.db'
db = SqliteExtDatabase(DB_PATH)

class BaseModel(Model):
    class Meta:
        database = db


class Instrument(BaseModel):
    ticker = CharField(unique=True)

class OrderBookUpdate(BaseModel):
    created_utc = DateTimeField(default=datetime.datetime.utcnow)
    ms_out = IntegerField()
    instrument = ForeignKeyField(Instrument)

class OrderBook(BaseModel):
    is_bid = BooleanField()
    cm = FloatField()
    price = FloatField()
    qty = FloatField()
    update = ForeignKeyField(OrderBookUpdate)

class Summary(BaseModel):
    high = FloatField()
    last = FloatField()
    low = FloatField()
    update = ForeignKeyField(OrderBookUpdate)

if not os.path.exists(DB_PATH):
    db.connect()
    db.create_tables([Instrument, OrderBookUpdate, OrderBook, Summary])