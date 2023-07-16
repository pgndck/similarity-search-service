from db import create_connection
from helper import get_next_id

from concurrent import futures
from psycopg2 import Error
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import grpc
import numpy as np
import similarity_pb2
import similarity_pb2_grpc
import time


# Vectorizer class to implement the similarity search

class DescriptionVectorizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 3))
        self.descriptions = []

    def add_description(self, description: str):
        self.descriptions.append(description)
        self.vectorizer.fit(self.descriptions)

    def to_vector(self, description: str) -> np.array:
        return self.vectorizer.transform([description]).toarray()


# Computing the similarity

def compute_similarity(vector1: np.array, vector2: np.array) -> float:
    return cosine_similarity(vector1, vector2)[0][0]


# Similarity Search Service realisation

class SimilaritySearchService(similarity_pb2_grpc.SimilaritySearchServiceServicer):
    def AddItem(self, request, context):
        item_id = request.id
        description = request.description

        if not description:
            return similarity_pb2.AddItemResponse(
                status=500,
                message="An error occurred: Empty description"
            )

        try:
            # Connect to the database
            connection = create_connection()
            cursor = connection.cursor()

            # If the id is nor specified, use the max id + 1
            if not item_id:
                item_id = get_next_id('items', 'id')

            cursor.execute(
                "INSERT INTO items (id, description) VALUES (%s, %s)",
                (item_id, description)
            )

            connection.commit()

            # After inserting to the DB, adding the description to the vectorizer
            description_vectorizer.add_description(request.description)

            # Close the connection
            cursor.close()
            connection.close()

            return similarity_pb2.AddItemResponse(
                status=200,
                message="Item added successfully"
            )
        except Error as e:
            return similarity_pb2.AddItemResponse(
                status=500,
                message=f"An error occurred: {e}"
            )

    def SearchItems(self, request, context):
        # Convert the query to a vector
        query_vector = description_vectorizer.to_vector(request.query)

        try:
            # Connect to the database
            connection = create_connection()
            cursor = connection.cursor()

            # Get the descriptions and IDs of all items in the database
            cursor.execute("SELECT id, description FROM items")
            items = cursor.fetchall()

            # Compute the similarity of each item to the query
            search_scores = [(item_id, compute_similarity(query_vector, description_vectorizer.to_vector(str(description))))
                             for item_id, description in items]

            # Sort the items by similarity (from most to least similar)
            search_scores.sort(key=lambda x: x[1], reverse=True)

            search_id = get_next_id('search_results', 'search_id')

            # Store the results in the database under this search_id
            for item_id, search_score in search_scores:
                # We only want to store the results that are at least somehow relevant
                if search_score > 0:
                    cursor.execute(
                        "INSERT INTO search_results (search_id, item_id, search_score) VALUES (%s, %s, %s)",
                        (search_id, item_id, search_score)
                    )

            # Commit the transaction
            connection.commit()

            # Close the connection
            cursor.close()
            connection.close()

            return similarity_pb2.SearchItemsResponse(
                search_id=str(search_id)
            )
        except Error as e:
            return similarity_pb2.AddItemResponse(
                status=500,
                message=f"An error occurred: {e}"
            )

    def GetSearchResults(self, request, context):
        search_id = request.search_id

        try:
            connection = create_connection()
            cursor = connection.cursor()

            # Retrieve the search results for the given search_id from the database
            cursor.execute(
                "SELECT item_id, search_score FROM search_results WHERE search_id = %s", (search_id,))

            # Fetch all the search results
            search_results = cursor.fetchall()

            # Convert each search result to a SearchResult message
            results = []
            for item_id, search_score in search_results:
                # Retrieve the item's description from the items table

                cursor.execute(
                    "SELECT description FROM items WHERE id = %s", (item_id,))
                description = cursor.fetchone()[0]

                # Append a new SearchResult to the results list
                results.append(
                    similarity_pb2.SearchResult(
                        id=str(item_id),
                        description=str(description)
                    )
                )

            # Close the connection
            cursor.close()
            connection.close()

            # Return a GetSearchResultsResponse message containing the search results
            return similarity_pb2.GetSearchResultsResponse(results=results)
        except Error as e:
            print(f"An error occurred: {e}")
            return similarity_pb2.GetSearchResultsResponse()


# Initializing the vectorizer
description_vectorizer = DescriptionVectorizer()


# Main server function

def serve():
    # Initialize a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add the defined class to the server
    similarity_pb2_grpc.add_SimilaritySearchServiceServicer_to_server(
        SimilaritySearchService(), server
    )

    # Listen on port 5001
    print('Starting server. Listening on port 5001.')
    server.add_insecure_port('[::]:5001')
    server.start()

    # Keep the server running
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    # Connect to the database
    connection = create_connection()
    cursor = connection.cursor()

    # Load all item descriptions from the database
    cursor.execute("SELECT description FROM items")
    descriptions = [row[0] for row in cursor.fetchall()]

    # Add them to the vectorizer
    for description in descriptions:
        description_vectorizer.add_description(description)

    # Close the connection
    cursor.close()
    connection.close()

    serve()
