import gtfs_realtime_pb2 as gtfs
import nyct_subway_pb2 as nyct

import requests as r
import json

from typing import Union, Type, List
from pydantic import BaseModel

MTA_ENDPOINTS = {
    "ACE": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "L": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l"
}


class ParseError(Exception):
    pass


# https://github.com/encode/django-rest-framework/blob/master/rest_framework/parsers.py#L32
class BaseParser:
    """
    All parsers should extend `BaseParser`, specifying a `media_type`
    attribute, and overriding the `.parse()` method.
    """
    media_type = None

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Given a stream to read from, return the parsed representation.
        Should return parsed data, or a `DataAndFiles` object consisting of the
        parsed data and files.
        """
        raise NotImplementedError(".parse() must be overridden.")


class GeneralTransitFeedParser(BaseParser):
    # https://datatracker.ietf.org/doc/html/draft-rfernando-protocol-buffers-00
    media_type = 'application/protobuf'

    @staticmethod
    def parse(stream, media_type=None, parser_context=None) -> gtfs.FeedMessage:

        from google.protobuf.message import DecodeError

        try:
            gfeed = gtfs.FeedMessage()
            gfeed.ParseFromString(stream.content)
            return gfeed
        except DecodeError as err:
            raise ParseError(f"GTFS Parse Error. Perhaps you forgot the api key? {err}")

    @staticmethod
    def toDict(stream: gtfs.FeedMessage) -> dict:
        from google.protobuf.json_format import MessageToDict

        return MessageToDict(stream)


class RequestHandler:

    def __init__(self, auth):
        self.auth = auth

    def get(self, endpoint, as_dict: False | True):
        headers = {"x-api-key": self.auth}

        response = r.get(MTA_ENDPOINTS[endpoint], headers=headers)

        if as_dict:
            stream = GeneralTransitFeedParser.parse(stream=response)
            return GeneralTransitFeedParser.toDict(stream)

        return GeneralTransitFeedParser.parse(stream=response)


# Basic interface for an MTA GTFS Service
class Service:
    """
    Base GTFS Interface for all MTA Service Providers, Subway, MNR, LIRR
    """

    def stop(self, stop: str):
        raise NotImplementedError(".stop() must be overridden.")


class SubwayStop(BaseModel):
    id: str
    stopId: str
    arrival: int
    departure: int


class Subway(Service):

    def __init__(self, endpoint, handle: RequestHandler):
        self.endpoint = endpoint
        self.handle = handle

    def stop(self, stop: str):
        response = self.handle.get(self.endpoint, as_dict=True)

        res = []

        for entity in response["entity"]:
            try:
                if entity["tripUpdate"]["stopTimeUpdate"][0]["stopId"] == stop:
                    res.append(SubwayStop(id=entity["id"],
                                          # trainId = ...
                                          stopId=entity["tripUpdate"]["stopTimeUpdate"][0]["stopId"],
                                          arrival=entity["tripUpdate"]["stopTimeUpdate"][0]["arrival"]["time"],
                                          departure=entity["tripUpdate"]["stopTimeUpdate"][0]["departure"]["time"],
                                          ))
            except KeyError:
                Warning("No TripUpdate for", entity["id"])
        return res


class TransitService:
    def __init__(self, auth):
        self.auth = auth
        self.handle = RequestHandler(auth)

    def service(self, provider: Union[Type[Subway]], endpoint):
        return provider(endpoint, self.handle)


def main():
    mta = TransitService("SECRET_KEY")

    line = mta.service(Subway, "ACE")

    stop = line.stop("A02S")

    for event in stop:
        print(event.arrival)


if __name__ == '__main__':
    main()
