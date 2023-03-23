import time
import numpy as np
import argparse
import tqdm
from SPARQLWrapper import SPARQLWrapper
import matplotlib.pyplot as plt


# -------------------------------------------- Queries --------------------------------------------
QUERY_1 = """
PREFIX xs: <http://www.w3.org/2001/XMLSchema#>
SELECT ?stringvalue ?number ?check ?check2
WHERE{{
  			BIND( {} as ?value)
 			BIND( STR(?value) AS ?stringvalue )
            BIND( SUBSTR(CONCAT("000",?stringvalue), STRLEN(?stringvalue) +1) AS ?test)
  			BIND( IF(STRLEN(?stringvalue) < 3, SUBSTR(CONCAT("000",?stringvalue), STRLEN(?stringvalue) + 1), ?stringvalue) AS ?paddedstringvalue)
            BIND( xs:integer(SUBSTR(?paddedstringvalue, 1, STRLEN(?paddedstringvalue) - 2)) AS ?number )
            BIND( xs:integer(SUBSTR(?paddedstringvalue, STRLEN(?paddedstringvalue) - 1)) AS ?check )
            BIND( ?number - (97 * FLOOR(?number / 97)) AS ?rest )
            BIND( 97 - ?rest AS ?check2 )
}}
"""

QUERY_2 = """   
SELECT ?stringvalue ?number ?check ?check2
WHERE{{
  			BIND( {} as ?value)
  			BIND( FLOOR(?value / 100) AS ?number )
            BIND( ?value - (100 * FLOOR(?value / 100)) AS ?check )
            BIND( ?number - (97 * FLOOR(?number / 97)) AS ?rest )
            BIND( 97 - ?rest AS ?check2 )
}}
"""


# -------------------------------------------- Code --------------------------------------------
# Create an argument parser.
def create_parser():
    parser = argparse.ArgumentParser(
        description="Benchmarking script for querying a SPARQL endpoint."
    )
    parser.add_argument(
        '--endpoints',
        help="SPARQL endpoints.",
        nargs='+'
    )
    parser.add_argument(
        '--names',
        help="Name of endpoints for charts.",
        nargs='+'
    )
    return parser


# Make a box-plot from a series of response times
def box_plot_chart(names, serie):
    plt.rcParams.update({'font.size': 18})
    fig, ax1 = plt.subplots()
    ax1.set_ylabel("Response time (ms)")
    ax1.boxplot(
        x=serie,
        labels=names,
        widths=np.ones(len(names)) * 0.5
    )
    plt.show()


# Run a query for 'nb_runs' times on each endpoint
# Report mean and stddev and show a box-plot of response times across endpoints
# Return response times where endpoint_times[i][j] is for endpoint i and run j
def benchmark_query(endpoints, names, query, nb_runs = 50):
    assert nb_runs > 1 and len(endpoints) > 0

    # Loop over endpoints
    endpoint_times = []
    for endpoint in endpoints:
        # Create wrapper
        sparql = SPARQLWrapper(endpoint)

        # Run nb_runs time query
        times = np.ndarray(nb_runs)
        for i in tqdm.tqdm(range(nb_runs)):
            sparql.setQuery(query.format(str(i)))
            start = time.time()
            _ = sparql.query()

            end = time.time()
            times[i] = (end - start) * 1000
            

        endpoint_times.append(times[1:])
        mean = np.mean(times)
        std = np.std(times)
        print(f"* Endpoint: {endpoint}")
        print(f"\tMean:  {mean:.5f} ms")
        print(f"\tStdev: {std:.5f} ms")
        
    # Make a box-plot
    box_plot_chart(names, endpoint_times)
    
    # Return response times
    return endpoint_times


if __name__ == '__main__':
    # Parser
    parser = create_parser()
    args = parser.parse_args()

    # # Query 1
    print("Benchmarking query 1 ...")
    _ = benchmark_query(args.endpoints, args.names, QUERY_1, 10000)

    # # Query 2
    print("Benchmarking query 2 ...")
    _ = benchmark_query(args.endpoints, args.names, QUERY_2, 10000)