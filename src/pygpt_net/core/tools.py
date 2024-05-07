import json
import subprocess

# Example function hard coded to return the same weather
# In production, this could be your backend API or an external API


def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})



def execute_az_cmd(command):
    output = "command output: "
    try:
        """Execute an Azure CLI command"""
        # return json.dumps({"cmd": command, "output": "dry run successful"})
        # os.system(command)
        output = subprocess.check_output(command, shell=True,
                                         text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
    return output



from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table

connection_string = "https://aks.kusto.windows.net/"
db = "AKSprod"

kcsb = KustoConnectionStringBuilder.with_az_cli_authentication(connection_string)
# It is a good practice to re-use the KustoClient instance, as it maintains a pool of connections to the Kusto service.
# This sample shows how to create a client and close it in the same scope, for demonstration purposes.

client = KustoClient(kcsb)

# run kusto query and return result in json
def run_kusto_query(query):
    print("Running query: ", query)
    # with KustoClient(kcsb) as client:
    response = client.execute(db, query)
    dataframe = dataframe_from_result_table(response.primary_results[0])
    return dataframe.to_json()

# tools_map is a map of name to function
available_functions = {
    "get_current_weather": get_current_weather,
    "execute_az_cmd": execute_az_cmd,
    "run_kusto_query": run_kusto_query
}
