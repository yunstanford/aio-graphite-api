import os
from aio_graphite_api.models.node import BranchNode, LeafNode
try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk


def _has_wild_cards(query):
	return query.find('{') > -1 or query.find('[') > -1 or query.find('*') > -1 or query.find('?') > -1


class StandardFinder:

	def __int__(self, storage_dirs):
		self.storage_dirs = storage_dirs

	def find(self, query):
		"""
		Finds nodes based on the query.

		args: metric query.

		Returns a list of Nodes.
		"""
		cleaned_query = query.replace('\\', '')
		query_parts = cleaned_query.split('.')

		for root_dir in self.storage_dirs:
			for abs_file_path, metric_name in self._find(root_dir, query_parts):

				# Filter out . and ..
				if os.basename(abs_file_path).startswith('.'):
					continue



	def _find(self, root_dir, query_parts):
		pass
