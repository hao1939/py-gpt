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


# tools_map is a map of name to function
available_functions = {
    "get_current_weather": get_current_weather,
    "execute_az_cmd": execute_az_cmd,
}
