import time

from datetime import datetime

from typing import Type

import requests as http

import pandas as pd
import json

import gtfs_realtime_pb2 as gtfs
from google.protobuf.json_format import MessageToJson


class Api(object):
    """

    TODO: 
    - Add expired check
    - Configure sling like urls
    - Create setters and getters with @property 
    
    A python interface to the MTA GTFS API

    Example usage:

        To create an instance of the MTA API class

        import twitter
        api = mta.Api(
            access_key='mta access key'
        )

        To fetch a subway station

        api.GetSubwayStation(station_id)
    
    """

    def __init__(
        self,
        api_key,
        secret_key=None,
        base_url=None,
        ):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url or "https://api-endpoint.mta.info/"
        self._expired = False
        self._endpoints = self._LoadEndpoints()
        

    def get(self, endpoint):

        if self.api_key is self._Expired():
            return "Expired error"

        headers = {"x-api-key": self.api_key}

        resp = http.get(endpoint, headers=headers)

        gfeed = gtfs.FeedMessage()
    
        gfeed.ParseFromString(resp.content)

        return gfeed

    def FeedtoJSON(message: gtfs_realtime_pb2.FeedMessage) -> str:
 
        return "json"

    def _LoadEndpoints(self) -> dict:

        "Loads endpoints from a urls.ini file"

        return "Endpoints"

    def _Expired(self) -> None:

        """
        API Keys are redacted if they have been not been used within 30 days. This gracefully handles the process of an expired
        API key when dealing with protobufs.

        api_key -> jwt -> api_key > 30 and not expired
        
        """
        expired = 30

        if expired >= 30:

            self._expired = True
        else:
            return False

# Example

def main():

    api = Api(api_key="API_KEY")

    r = api.get("https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l")

    print(r)

main()