
class Node:

	def __init__(self, path):
		self.path = path
		self.local = True
		self.is_leaf = False


class BranchNode(Node):
	pass


class LeafNode(Node):
	
	def __init__(self, path, reader):
		Node.__init__(self, path)
		self.reader = reader
		self.is_leaf = True

	async def fetch(start_time, end_time):
		pass
