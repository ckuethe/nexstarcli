from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation
from astropy.coordinates import SkyCoord
from astropy.coordinates import AltAz

class BaseTelescope(object):
    """class represents a telescope"""
    def __init__(self):
        pass

    def _convert_azel_to_radec(_az, _el, _location, _time):
        _azel = SkyCoord(alt=_el*u.deg, az=_az*u.deg, frame='altaz', obstime=_time, location=_location)
        _radec = _azel.icrs
        return _radec.ra.degree, _radec.dec.degree

    def convert_azel_to_radec(self, _az, _el):
        _time = Time.now()
        _location = self._get_EarthLocation0()
        return self._convert_azel_to_radec(_az, _el, _location, _time)

    def _convert_radec_to_azel(_ra, _dec, _location, _time):
        _radec = SkyCoord(ra=_ra*u.degree, dec=_dec*u.degree, frame='icrs')
        _azel = _radec.transform_to(AltAz(obstime=_time, location = _location))
        return _azel.az.degree, _azel.alt.degree

    def convert_radec_to_azel(self, _ra, _dec):
        _time = Time.now()
        _location = self._get_EarthLocation0()
        return self._convert_radec_to_azel(_az, _el, _location, _time)


    def _get_EarthLocation0(self):
        _latitude, _longitude = self.get_location()

        _latitude_deg = _latitude[0] + (_latitude[1]/60.0) + (_latitude[2]/(60.0 * 60.0))
        if _latitude[3] >0:
            _latitude_deg *= -1.0

        _longitude_deg = _longitude[0] + (_longitude[1]/60.0) + (_longitude[2]/(60.0 * 60.0))
        if _longitude[3] > 0:
            _longitude_deg *= -1.0

        telescope_location = EarthLocation(lat=_latitude_deg*u.deg, lon=_longitude_deg*u.deg)
        return telescope_location

    def _verify_connection(self):
        pass