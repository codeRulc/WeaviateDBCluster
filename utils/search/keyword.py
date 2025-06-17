import time
import json
import pandas as pd
from typing import Tuple
from weaviate import Client
from weaviate.classes.query import MetadataQuery

# Keyword search function
# This function performs a keyword search on a specified collection in Weaviate.
def keyword_search(client: Client, collection: str, query: str, tenant_name: str = None, limit: int = 3) -> Tuple[bool, str, pd.DataFrame, float]:
	try:
		# Get collection
		coll = client.collections.get(collection)
		if tenant_name:
			coll = coll.with_tenant(tenant_name)

		# Measure performance
		start_time = time.time() * 1000 # Convert to milliseconds

		# Perform search
		response = coll.query.bm25(
			query=query,
			limit=limit,
			return_metadata=MetadataQuery(
				creation_time=True,
				last_update_time=True,
				score=True,
				explain_score=True,
				is_consistent=True
			)
		)

		# Calculate time taken
		end_time = time.time() * 1000
		time_taken = end_time - start_time

		# Process results into a list of dictionaries
		results = []
		for obj in response.objects:
			result_dict = {
				"Score": f"{obj.metadata.score:.6f}",
				"Explain Score": obj.metadata.explain_score,
				"Is Consistent": obj.metadata.is_consistent if hasattr(obj.metadata, 'is_consistent') else 'N/A',
				"Creation Time": obj.metadata.creation_time if hasattr(obj.metadata, 'creation_time') else 'N/A',
				"Last Update Time": obj.metadata.last_update_time if hasattr(obj.metadata, 'last_update_time') else 'N/A'
			}

			# Add properties
			for key, value in obj.properties.items():
				if isinstance(value, (dict, list)):
					result_dict[key] = json.dumps(value, indent=2)
				else:
					result_dict[key] = value

			results.append(result_dict)

		# Convert to DataFrame
		df = pd.DataFrame(results)
		return True, f"Found {len(results)} results", df, time_taken

	except Exception as e:
		return False, f"Error performing keyword search: {str(e)}", pd.DataFrame(), 0.0
