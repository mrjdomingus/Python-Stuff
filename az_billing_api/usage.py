# This module can be used to retrieve usage information from an Azure subscription
# Also see: https://docs.microsoft.com/en-us/azure/azure-stack/azure-stack-tenant-resource-usage-api for more info.

import jmespath
import json
import requests
import urllib
import configparser

import os
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

def process_usage_chunk(text):
    decoded_json = json.loads(text)
    values = jmespath.search('''value[*].{subscriptionId: properties.subscriptionId,
                         usageStartTime: properties.usageStartTime,
                         usageEndTime: properties.usageEndTime,
                         meterId: properties.meterId,
                         meterName: properties.meterName,
                         meterCategory: properties.meterCategory,
                         meterSubCategory: properties.meterSubCategory,
                         unit: properties.unit,
                         instanceData: properties.instanceData,
                         quantity: properties.quantity}''', decoded_json)
    nextLink = jmespath.search( 'nextLink', decoded_json)
    return (values, nextLink)

default_usage_params = {"api_version" : "2015-06-01-preview",
    "aggregationGranularity" : "Hourly", # Hourly or Daily
    "showDetails" : "true" # true or false
    }

def get_usage(subscriptionId, reportedStartTime, reportedEndTime, params = default_usage_params ):
    """
    Retrieve usage info from a specific Azure subscription via REST API.
        :param subscriptionId:
            Example: "d5e0a41f-5a1a-4ac1-a81b-0e12c702667a"
        :param reportedstartTime:
            Example: "2018-06-02T11:00:00Z" # Will be url quoted by function
        :param reportedEndTime:
            Example: "2018-06-02T12:00:00Z" # Will be url quoted by function
        :param params=default_usage_params:
            Reference to some default url parameters
    Returns:
        * List with results
        * Message of any error
    """
    config = configparser.ConfigParser()
    config.read(os.path.join(dir_path, 'Azure_API.ini'))
    token = config['DEFAULT']['azure_bearer_token']

    api_version = params.get('api_version', default_usage_params['api_version'])
    aggregationGranularity = params.get('aggregationGranularity', default_usage_params['aggregationGranularity'])
    showDetails = params.get('showDetails', default_usage_params['showDetails'])

    reportedStartTime = urllib.parse.quote(reportedStartTime)
    reportedEndTime = urllib.parse.quote(reportedEndTime)

    url = f"https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Commerce/UsageAggregates?api-version={api_version}&reportedstartTime={reportedStartTime}&reportedEndTime={reportedEndTime}&aggregationGranularity={aggregationGranularity}&showDetails={showDetails}"
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.get(url, headers=headers)

    result_list = []
    nextLink = None
    error = ""

    if r.status_code == requests.codes.ok: #pylint: disable=E1101
        result_list, nextLink = process_usage_chunk(r.text)
        while nextLink:
            r = requests.get(nextLink, headers=headers)
            if r.status_code == requests.codes.ok: #pylint: disable=E1101
                values, nextLink = process_usage_chunk(r.text)
                result_list.extend(values)
    else:
        error = r.text
    return result_list, error

if __name__ == "__main__":
    # Some code to exercise the functions...
    result, error = get_usage( subscriptionId = "d5e0a41f-5a1a-4ac1-a81b-0e12c702667a",
        reportedStartTime = "2018-06-02T11:00:00Z", reportedEndTime = "2018-06-03T12:00:00Z")
    if error:
        print(f"Error: {error}")
    else:
        print(f"Length of result: {len(result)}")