from hashlib import md5
from itertools import chain
import bisect

try:
	import pyhash
	hasher = pyhash.fnv1a_32()
	def fnv32a(string, seed=0x811c9dc5):
		return hasher(string, seed=seed)
except ImportError:
	def fnv32a(string, seed=0x811c9dc5):
		"""
		FNV-1a Hash (http://isthe.com/chongo/tech/comp/fnv/) in Python.
		Taken from https://gist.github.com/vaiorabbit/5670985
		"""
		hval = seed
		fnv_32_prime = 0x01000193
		uint32_max = 2 ** 32
		for s in string:
			hval = hval ^ ord(s)
			hval = (hval * fnv_32_prime) % uint32_max
		return hval


class ConsistentHashRing:
	"""
	This class is completely from graphite-web, let's just use that consistent
	hashing algorithm. 
	Ref:
	https://github.com/graphite-project/graphite-web/blob/master/webapp/graphite/render/hashing.py
	"""
	def __init__(self, nodes, replica_count=100, hash_type='carbon_ch'):
		self.ring = []
		self.ring_len = len(self.ring)
		self.nodes = set()
		self.nodes_len = len(self.nodes)
		self.replica_count = replica_count
		self.hash_type = hash_type
		for node in nodes:
			self.add_node(node)

	def compute_ring_position(self, key):
	    if self.hash_type == 'fnv1a_ch':
			big_hash = '{:x}'.format(int(fnv32a( str(key) )))
			small_hash = int(big_hash[:4], 16) ^ int(big_hash[4:], 16)
	    else:
			big_hash = md5(str(key)).hexdigest()
			small_hash = int(big_hash[:4], 16)
	    return small_hash

	def add_node(self, key):
	    self.nodes.add(key)
	    self.nodes_len = len(self.nodes)
	    for i in range(self.replica_count):
	      	if self.hash_type == 'fnv1a_ch':
	        	replica_key = "%d-%s" % (i, key[1])
	      	else:
	        	replica_key = "%s:%d" % (key, i)
		    position = self.compute_ring_position(replica_key)
		    entry = (position, key)
		    bisect.insort(self.ring, entry)
	    self.ring_len = len(self.ring)

	def remove_node(self, key):
	    self.nodes.discard(key)
	    self.nodes_len = len(self.nodes)
	    self.ring = [entry for entry in self.ring if entry[1] != key]
	    self.ring_len = len(self.ring)

	def get_node(self, key):
	    assert self.ring
	    position = self.compute_ring_position(key)
	    search_entry = (position, None)
	    index = bisect.bisect_left(self.ring, search_entry) % self.ring_len
	    entry = self.ring[index]
	    return entry[1]

	def get_nodes(self, key):
	    nodes = []
	    position = self.compute_ring_position(key)
	    search_entry = (position, None)
	    index = bisect.bisect_left(self.ring, search_entry) % self.ring_len
	    last_index = (index - 1) % self.ring_len
	    nodes_len = len(nodes)
	    while nodes_len < self.nodes_len and index != last_index:
	        next_entry = self.ring[index]
	        (position, next_node) = next_entry
	        if next_node not in nodes:
	            nodes.append(next_node)
	            nodes_len += 1
	  
	        index = (index + 1) % self.ring_len

	    return nodes