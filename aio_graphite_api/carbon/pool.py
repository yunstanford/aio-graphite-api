import asyncio
import random
from aio_graphite_web.hashing.keyfunc import key_func
from aio_graphite_web.hashing.hashingring import ConsistentHashRing
from .connection import CarbonConn


class CarbonConnPoolException(Exception):
    pass


class CarbonConnPoolRequestError(Exception):
    pass


class CarbonConnPool:
    """
    a Conn Pool, connecting to carbon-cache instances.

    This class were largely derived from graphite-web CarbonLink class
    https://github.com/graphite-project/graphite-web/blob/master/webapp/graphite/carbonlink.py

    """

    def __init__(self, hosts,
                 replication_factor,
                 carbon_cache_hashing_type,
                 loop=None):
        # Example host: 127.0.0.1:7003:a
        # Only host and instance will be used for hashing
        # However, Port will not.
        # replication_factor should be consistent with
        # REPLICATION_FACTOR carbon.conf
        self.hosts, self.ports = self._parse_hosts_and_ports(hosts)
        self._conns = {}
        server_num = self._get_distinct_server()
        if server_num < replication_factor:
            raise CarbonConnPoolException(
                "replication_factor should less than server num"
            )
        self.key_func = key_func
        self.hash_ring = ConsistentHashRing(self.hosts, hash_type=carbon_cache_hashing_type)
        self.replication_factor = replication_factor
        self.loop = loop or asyncio.get_event_loop()


    async def connect(self):
        """
        connect to carbon cache hosts
        """
        for host in self.hosts:
            server = host[0]
            instance = host[1]
            port = self.ports[host]
            self._conns[host] = CarbonConn(server, port, instance, self.loop)
            try:
                await self._conns[host].connect()
            except Exception:
                raise CarbonConnPoolException(
                    "Unable to connect to carbon cache server %s:%s:%s"
                    % server, port, instance
                )


    async def query(self, metric):
        """
        query by metric
        """
        if not self._conns:
            raise CarbonConnPoolException(
                "No Connections yet."
            )
        host = self._get_host(metric)
        conn = self._conns[host]
        try:
            result = await conn.query(metric)
        except Exception as e:
            raise CarbonConnPoolRequestError(
                "Unable to query %s: %s"
                % metric, e
            )
        return result


    def _get_host(self, metric):
        """
        Get carbon cache host for metric based on consistent hashing.
        
        """
        key = self.key_func(metric)
        nodes = []
        servers = set()
        for node in self.hash_ring.get_nodes(key):
            (server, instance) = node
            if server not in servers:
                servers.add(server)
                nodes.append(node)
            if len(servers) >= self.replication_factor:
                break
        return random.choice(nodes)


    @property
    def conns(self):
        return self._conns


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


    def _get_distinct_server(self):
        """
        Return server with diff host addr.
        """
        return len(set([server for (server, instance) in self.hosts]))
