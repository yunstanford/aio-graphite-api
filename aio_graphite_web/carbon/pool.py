import asyncio
from aio_graphite_web.hashing.keyfunc import key_func
from aio_graphite_web.hashing.hashingring import ConsistentHashRing


class CarbonConnPoolException(Exception):
    pass


class CarbonConnPool:
    """
    a Conn Pool, connecting to carbon-cache instances
    """

    def __init__(self, hosts,
                 replication_factor,
                 carbon_cache_hashing_type):
        # Example host: 127.0.0.1:7003:a
        # Only host and instance will be used for hashing
        # However, Port will not.
        # replication_factor should be consistent with
        # REPLICATION_FACTOR carbon.conf
        self.hosts, self.ports = self._parse_hosts_and_ports(hosts)
        self.conns = {}
        servers = set([server for (server, port, instance) in hosts])
        if len(servers) < settings.REPLICATION_FACTOR:
            raise CarbonConnPoolException(
                "REPLICATION_FACTOR=%d cannot exceed servers=%d" % (replication_factor, len(servers))
            )
        self.key_func = key_func
        self.hash_ring = ConsistentHashRing(self.hosts, hash_type=carbon_cache_hashing_type)


    async def connect(self):
        """
        connect to carbon cache hosts
        """


    def _parse_hosts_and_ports(self, carbon_hosts):
        """
        Example: 127.0.0.1:7003:a
        ()
        """
        hosts = []
        ports = {}
        for host in carbon_hosts:
            tmp = host.split(":")
            server = tmp[0]
            port = int (tmp[1])
            instance = None
            if len(tmp) > 2:
                instance = tmp[2]
            hosts.append((server, port, instance))
            ports[(server, instance)] = port
        return (hosts, ports)
