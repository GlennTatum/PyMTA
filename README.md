# PyMTA
A Python API Wrapper built around the MTA's GTFS based protobuf api.

### Example
```python
def main():
    mta = TransitService("SECRETKEY")

    line = mta.service(Subway, "ACE")

    stop = line.stop("A02S")

    for event in stop:
        print(event.arrival)
```


### Dependencies

- requests

- protobuf

- pydantic
