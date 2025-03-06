## Weather Notifications

A basic python module and script for pulling nightly temperatures for a specific lat/long location to determine if facuets should be left open over night for freezing temperatures.


## Data Source
* National Weather Service API
    * See [NWS API Documentation](https://www.weather.gov/documentation)

### Terminology

* CWFA: County Warning and Forecast Area 
* NWS: National Weather Service
* WFO: Weather Forecast Office
* FIPS: Federal Information Processing System code
* CWA: County Warning Area

#### Forcast Example:

Bentonville, AR is in the NWS Southern region. Within that region, it is aligned to the Tulsa, OK (TSA) WFO. This means weather warnings and forecasts are issued from the TSA WFO. However, forcasts are specific to Benton County - See [AR County Map](./archive/ar_zone.pdf).


How are observations taken?

* Station -> WFO? 