# Prerequest
  - Install MySQL database
  - Get Facebook Graph API key
  - Get Google API key

### Version
0.1.0

### Bots

Populate Facebook Shops
- fb_searcher.py
- fb_fetcher.py
- geo_walker.py

Match Google Shops
- gg_matcher.py
- gg_fetcher.py

### Running
```sh
# First time populate data
# Populate geo loctions to scan
python geo_walker.py -e prod  
# Scan fb shops by geo locations
python fb_searcher.py -e prod
```
License
----
BSD License