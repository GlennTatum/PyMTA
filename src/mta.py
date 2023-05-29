import gtfs_realtime_pb2 as gtfs
import nyct_subway_pb2 as nyct

from google.protobuf.json_format import MessageToDict

import requests as r
import json

from typing import List
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
    def parseToDict(stream: gtfs.FeedMessage) -> dict:

        return MessageToDict(stream)


class Transit:

    def __init__(self, credentials: str):
        self.credentials = credentials

    @classmethod
    def from_credentials(cls, auth: str):
        return cls(auth)

    @classmethod
    def from_env(cls, auth):
        """
        Constructs an instance of Transit from environment variables
        """
        pass

    def _get(self, endpoint: str) -> gtfs.FeedMessage():
        headers = {"x-api-key": self.credentials}

        response = r.get(MTA_ENDPOINTS[endpoint], headers=headers)

        return GeneralTransitFeedParser.parse(stream=response)

    def getSubwayLine(self, endpoint: str):
        stream = self._get(endpoint)

        return Subway(stream=stream)


class SubwayStop(BaseModel):
    id: str
    stopId: str
    arrival: int
    departure: int


class Subway:
    def __init__(self, stream):
        self.stream = stream

    def __repr__(self):
        """
        Representation as a formatted and indented stream of data.
        """
        pass

    def stop(self, stop) -> List[SubwayStop]:

        msg = MessageToDict(self.stream)

        res = []

        for entity in msg["entity"]:
            try:
                if entity["tripUpdate"]["stopTimeUpdate"][0]["stopId"] == stop:
                    # TODO convert entity["tripUpdate"]["stopTimeUpdate"] to munch object type

                    # res.append(DefaultMunch.fromDict(entity["tripUpdate"], object()))

                    res.append(SubwayStop(id=entity["id"],
                                          # trainId = ...
                                          stopId=entity["tripUpdate"]["stopTimeUpdate"][0]["stopId"],
                                          arrival=entity["tripUpdate"]["stopTimeUpdate"][0]["arrival"]["time"],
                                          departure=entity["tripUpdate"]["stopTimeUpdate"][0]["departure"]["time"],
                                          ))

            except KeyError:
                Warning("No TripUpdate for", entity["id"])
        return res


def main():
    mta = Transit.from_credentials("SECRET_KEY")

    line = mta.getSubwayLine("ACE")

    stop = line.stop("A02N")

    for event in stop:
        print(event.arrival)

    #print(stop)

if __name__ == '__main__':
    main()
