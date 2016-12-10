import asyncio
import struct
from .util import unpickle

# cPickle is faster than pickle
# It is common to first try to import cPickle, 
# giving an alias of “pickle”.
try:
  import cPickle as pickle
except ImportError:
  import pickle


# Constants
HEADER_SIZE = 4


class CarbonConnException(Exception):
    pass


class CarbonConn:
    """
    A async connection to a carbon cache instance.
    """
    def __init__(self, host, port, instance, loop=None):
        self.server = host
        self.port = port
        self.server_address = (server, port)
        self.instance = instance
        self.reader, self.writer = None, None
        self.loop = loop or asyncio.get_event_loop()


    async def connect(self):
        """
        Connect to carbon cache server.
        """
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.server,
                self.port,
                loop=self.loop)
        except Exception:
            raise CarbonConnException(
                "Unable to connect to the provided server address %s:%s"
                % self.server_address
                )


    async def close(self):
        """
        Close Connection to carbon cache server
        """
        try:
            self.writer.close()
        finally:
            self.writer = None
            self.reader = None


    async def query(self, metric):
        """
        query by metric
        """
        request = {
            "type": "cache-query",
            "metric": metric
        }
        res = await self.send_request(request)
        # res relies on carchon cache
        # let't keep it consistent
        return res['datapoints']


    async def metric_metadata(self, metric, key):
        """
        get metadata by metric and key
        """
        request = {
            "type": "get-metadata",
            "metric": metric,
            "key": key
        }
        res = await self.send_request(request)
        # res relies on carchon cache
        # let't keep it consistent
        return res['value']


    async def send_request(self, request):
        """
        send request to carbon cache instance,
        and recv response.
        """
        # required format for request, we should keep it
        # consistent
        metric = request['metric']
        serialized_body = pickle.dumps(request, protocol=-1)
        header = struct.pack("!L", len(serialized_body))
        serialized_packet = header + serialized_body
        # Set default
        result = {}
        result.setdefault('datapoints', [])
        # Send request to carbon cache instance
        try:
            await self._send_message(serialized_packet)
            result = await self._recv_response()
        except Exception as e:
            raise CarbonConnException(
                "Failed to get data from carbon cache %s: %s"
                % self.server, e
                )
        else:
            # Probably return 'error' from carbon cache.
            # We have to catch it here if so.
            if "error" in result:
                raise CarbonConnException(
                    "Error when getting data from carbon cache %s"
                    % self.server
                )
        return result


    async def _send_message(self, message):
        """
        Send message to carbon cache instance.
        """
        if not self.writer:
            await self.connect()
        attempts = 3
        while attempts > 0:
            try:
                self.writer.write(message)
                await self.writer.drain()
                return
            except Exception:
                # If failed to send data, then try to set up a
                # new connection
                try:
                    await self.close()
                    await self.connect()
                except Exception:
                    # if all attempts failed, then raise exception
                    if attempts == 1:
                        raise CarbonConnException(
                            "Failed to send after {0} attempts!"
                            .format(str(attempts)))
                    else:
                        pass
                attempts = attempts - 1


    async def _recv_response(self):
        """
        Receive response from carbon cache. This coroutine should be
        called after _send_message.
        """
        if not self.reader:
            return
        try:
            # read header to get body size
            header = await self.reader.readexactly(HEADER_SIZE)
            body_size = struct.unpack("!L", header)[0]
            body = await self.reader.readexactly(body_size)
            return unpickle.loads(body)
        except IncompleteReadError as err:
            raise err
        except Exception:
            raise CarbonConnException(
                "Unable to receive response from carbon cache")
