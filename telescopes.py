from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation
from astropy.coordinates import SkyCoord
from astropy.coordinates import AltAz
from abc import ABCMeta
from abc import abstractmethod


class TelescopeError(Exception):
    def __init__(self, msg):
        self.msg = msg

class TelescopeCommand(object):
    _cmd = ""


class BaseTelescope(object):
    """Base class for telescope"""
    __metaclass__ = ABCMeta

    def __init__(self, device="/dev/ttyUSB0"):
        """
        :param device: device which is attached to telescope. Default is "/dev/ttyUSB0"
        :return:
        """
        self.device = device

    @abstractmethod
    def _send_command(self, cmd):
        """Send arbritrary command to telescope

       :param cmd: Object of type TelescopeCommand
        """
        pass

    @abstractmethod
    def _read_response(self):
        """Read response from telescope to pevious sent command.
        :return: response object from telescope
        """
        pass

    @abstractmethod
    def is_aligned(self):
        """Returns true if telescope has been alignec"""
        pass

    @abstractmethod
    def cancel_current_operation(self):
        """Cancels any current operation the telescope is performing"""
        pass

    @abstractmethod
    def get_altaz(self):
        """Gets Altitude (elevation) and azimuth telescope is pointing to
        :return: object with alt az information.
        """
        pass

    @abstractmethod
    def get_location(self):
        """Returns telescope location in latitude and longitude.

        :return: object with latitude andlongitude information.
        """
        pass

    @abstractmethod
    def get_radec(self):
        """Returns Right Ascension and Declination telescope is pointing at

        :return: object with right ascension and declination information.
        """
        pass

    @abstractmethod
    def get_time(self):
        """Returns the time teleslcope is set to

        :return: object with time information
        """
        pass

    @abstractmethod
    def goto_altaz(self, altaz):
        """Points telescope to provided Alt/Ax coodinates.

        :param altaz: object containinng alt/az information.
        :return: object containing any error or other pertinent information
        """
        pass

    @abstractmethod
    def goto_radec(self, radec):
        """Points telescope to provided radec.

        :param radec: object containing necessary ra/dec information
        :return: object containing any error or other pertinent information
        """
        pass

    @abstractmethod
    def set_earth_location(self, latlong):
        """Sets telescope locatoin (lat and long) to provided earth location

        :param latlong: object containing earth location latitude and longitude
        :return: object containing any error or other pertinent information
        """
        pass

    @abstractmethod
    def set_time(self, time):
        """Configures time on telescope
        :param time: object containing time information
        :return: object containing any error or other pertinent information
        """

    @abstractmethod
    def display(self, msg):
        """Display message on telescope's control display

        :param msg: message to be displayed.
        :return: object containing any error or other pertinent information
        """
        pass

    @staticmethod
    def _convert_azel_to_radec(_az, _el, _location, _time):
        _azel = SkyCoord(alt=_el * u.deg, az=_az * u.deg, frame='altaz',
                         obstime=_time, location=_location)
        _radec = _azel.icrs
        return _radec.ra.degree, _radec.dec.degree

    def convert_azel_to_radec(self, _az, _el):
        _time = Time.now()
        _location = self._get_EarthLocation0()
        return self._convert_azel_to_radec(_az, _el, _location, _time)

    @staticmethod
    def _convert_radec_to_azel(_ra, _dec, _location, _time):
        _radec = SkyCoord(ra=_ra * u.degree, dec=_dec * u.degree, frame='icrs')
        _azel = _radec.transform_to(AltAz(obstime=_time, location=_location))
        return _azel.az.degree, _azel.alt.degree

    def _verify_connection(self):
        pass

    def get_earth_location(self):
         latitude, longitude = self.get_location()
         return EarthLocation(lat = latitude*u.deg, lon = longitude *u.deg)
