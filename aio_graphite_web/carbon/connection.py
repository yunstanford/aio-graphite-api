import asyncio


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



	async def send_request(self, request):



	async def _send_message(self, message):
		"""
		Send request to carbon cache instance.
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

