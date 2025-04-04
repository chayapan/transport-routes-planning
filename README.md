# transport-routes-planning

- location table
- distance matrix
- plot nodes (location marker) on a map with GeoJSON/Leaflet
- TODO: produce GeoJSON for plotting
- TODO: calculate linehaul for 30 locations and put in DistanceMatrix

Features and FeatureCollections  
https://leafletjs.com/examples/geojson/  
https://tools.ietf.org/html/rfc7946#section-3.3


```
npm run test
npm run start  # starts app at http://127.0.0.1:8080
```


```
pytest --junit-xml=test_report.xml
```

### locations

python3 cli.py locations --files=../data/locations.json

### run

python3 cli.py run
