# GeoTrace

A Python traceroute tool with geolocation.

Uses UDP packets with TTL (Time to live) values to trace the route to a destination address. Location data is pulled from ip-api.com, and visualized on a map. 

## Usage

  You can run the GeoTracer script to trace the route to a specified domain or IP address. For example:

```sh
python geotracer.py
```

The target site is specified in the script. Modify the site variable in the script to trace a different destination:

```python
site = "docs.python.org"
```

## Example Output

```sh
Tracing to 151.101.64.223
Hop #1: 192.168.1.1, City1, Region1, Country1
Hop #2: 10.0.0.1, City2, Region2, Country2
Hop #3: 203.0.113.1, City3, Region3, Country3
```
