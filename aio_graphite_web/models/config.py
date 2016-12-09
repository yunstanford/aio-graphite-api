from schematics.models import Model
from schematics.types import StringType, IntType, ListType, FloatType


class Config(Model):
    cluster_servers = ListType(StringType, required=False)
    carbon_conn_hosts = ListType(StringType, required=False)
    storage_dir = StringType(required=True)
    carbon_conn_timeout = FloatType(required=True)
