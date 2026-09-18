# Graphiti condition

Graphiti must be run as the real `graphiti-core` system against a real supported backend. Do not replace it with a local graph/vector approximation.

Official requirements documented by Zep include Python 3.10+, `graphiti-core`, and Neo4j 5.26+ or FalkorDB. Graphiti's standard `search()` performs hybrid semantic + BM25 retrieval, with configurable search recipes.

Official docs:
- https://help.getzep.com/v2/graphiti/getting-started/quick-start
- https://help.getzep.com/graphiti/working-with-data/searching
