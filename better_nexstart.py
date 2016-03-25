#!/usr/bin/python

import serial
import telescopes
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation
from astropy.coordinates import SkyCoord
from astropy.coordinates import AltAz

RADEC = 'e'
AZEL = 'z'

class TelescopeAlignmentNotSet(telescopes.TelescopeError):
    def __ini__(self):
        msg = "Telescope alignment not set"
        super(TelescopeAlignmentNotSet, self).__init__(msg)


class NexStarSLT130(telescopes.BaseTelescope):


    def __init__(self, device):
        super(NexStarSLT130, self).__init__(device)
        self.serial = serial.Serial(device, baudrate=9600, timeout=2)
        self.DIR_AZIMUTH = 0
        self.DIR_ELEVATION = 1

    def _send_command(self, cmd):
        self.serial.write(cmd)
        return True

    def _read_response(self, n_bytes=1):
        """ Reads response from telescope

        :param b_bytes: the number of bytes to read form the telescope's response
        :return : n_bytes number of bytes from response or None if error
        """
        return self.serial.read(n_bytes)


    @staticmethod
    def _validate_command(response):
        assert response == '#', 'Command failed'

    @staticmethod
    def _convert_hex_to_percentage_of_revolution(string):
        return int(string, 16) / 2. ** 32 * 360.

    @staticmethod
    def _convert_to_percentage_of_revolution_in_hex(degrees):
        rounded = round(degrees / 360. * 2. ** 32)
        return '%08X' % rounded

    def _get_position(self, coordinate_system):
        """Returns telescope postion in the requested coordinate system.

        Possible coordinagte systems are radec(e) and azel(z)

        """
        self._send_command(coordinate_system)
        response = self._read_response(18)
        return (self._convert_hex_to_percentage_of_revolution(response[:8]),
                self._convert_hex_to_percentage_of_revolution(response[9:17]))

    def get_azel(self):
        """Returns az and el in degrees"""
        _altaz = self.get_altaz()
        return _altaz.az.degrees, _altaz.alt.degrees

    def get_radec(self):
        """Returns RaDec coordinates """

        # Get observation time
        _obstime = self.get_time_initilizer()
        _ra, _dec = self._get_position(RADEC)
        _radec = SkyCoord(ra=_ra*u.degree, dec=_dec*u.degree, frame='icrs', obstime=_obstime)
        return _radec


    def _goto_command(self, char, values):
        command = (char + self._convert_to_percentage_of_revolution_in_hex(values[0]) + ',' +
                   self._convert_to_percentage_of_revolution_in_hex(values[1]))
        print command
        self._send_command(command)
        response = self._read_response(1)
        return "#" in response

    def safe_goto_azel(self, az, el):
        if not self.alignment_complete():
            raise TelescopeAlignmentNotSet
        if el > 90.0:
            raise TelescopeError(
                "elevation larger than 90 degrees not allowed")
        if az >= 360.0:
            az = 0.0
        self.goto_azel(az, el)

    def goto_azel(self, az, el):
        print "going to %s %s" % (az, el)
        self._goto_command('b', (az, el))

    @staticmethod
    def determine_azel_are_safe(_az, _el):
        """Checks if ra and dec are safe for telescope

        Based on the location this function should determine if the
        given Right Assention and Declination are safe for the telescope
        to point to. (we don't want pointing at floor :)
        :param _el:
        :param _az:
        """
        if _az and _el:
            return True

    def safe_goto_radec(self, ra, dec):
        if not self.alignment_complete():
            raise TelescopeAlignmentNotSet
        if not self.DetermineRaDecAreSafe(ra, dec):
            raise TelescopeError(
                "Ra: %s, Dec: %s are not safe at current location" %
                (ra, dec))
        self.goto_radec(ra, dec)

    def goto_radec(self, ra, dec):
        print "goto: %s %s " % (ra, dec)
        self._goto_command('r', (ra, dec))

    def sync(self, ra, dec):
        self._goto_command('s', (ra, dec))

    def get_tracking_mode(self):
        self.serial.write('t')
        response = self.serial.read(2)
        return ord(response[0])

    def set_tracking_mode(self, mode):
        command = 'T' + chr(mode)
        self.serial.write(command)
        response = self.serial.read(1)
        self._validate_command(response)

    def _var_slew_command(self, direction, rate):
        negative_rate = True if rate < 0 else False
        track_rate_high = (int(abs(rate)) * 4) / 256
        track_rate_low = (int(abs(rate)) * 4) % 256
        direction_char = chr(16) if direction == self.DIR_AZIMUTH else chr(17)
        sign_char = chr(7) if negative_rate is True else chr(6)
        command = ('P' + chr(3) + direction_char + sign_char +
                   chr(track_rate_high) + chr(track_rate_low) + chr(0) +
                   chr(0))
        self.serial.write(command)
        response = self.serial.read(1)
        self._validate_command(response)

    def slew_var(self, az_rate, el_rate):
        self._var_slew_command(self.DIR_AZIMUTH, az_rate)
        self._var_slew_command(self.DIR_ELEVATION, el_rate)

    def _fixed_slew_command(self, direction, rate):
        negative_rate = True if rate < 0 else False
        sign_char = chr(37) if negative_rate is True else chr(36)
        direction_char = chr(16) if direction == self.DIR_AZIMUTH else chr(17)
        rate_char = chr(int(abs(rate)))
        command = ('P' + chr(2) + direction_char + sign_char + rate_char +
                   chr(0) + chr(0) + chr(0))
        self.serial.write(command)
        response = self.serial.read(1)
        self._validate_command(response)

    def slew_fixed(self, az_rate, el_rate):
        assert (az_rate >= -9) and (az_rate <= 9), 'az_rate out of range'
        assert (el_rate >= -9) and (el_rate <= 9), 'az_rate out of range'
        self._fixed_slew_command(self.DIR_AZIMUTH, az_rate)
        self._fixed_slew_command(self.DIR_ELEVATION, el_rate)



    def get_location(self):
        """Get location in latitude and longitude

        Positive latitude is above the equator (N), and negative latitude is
        below the equator (S). Positive longitude is east of the prime
        meridian, while negative longitude is west of the prime meridian
        (a north-south line that runs through a point in England)

        If the response contains N = 0 (positive), and E = 0 (positive).

        :return:
        """
        self.serial.write('w')
        response = self.serial.read(9)

        lat = ()
        for char in response[:4]:
            lat = lat + (ord(char),)
        _lat_degrees= lat[0] + (lat[1] / 60.0) + (lat[2]/(60.0 * 60.0))
        if lat[3] != 0:
            _lat_degrees *= -1.0

        _long = ()
        for char in response[4:-1]:
            _long = _long + (ord(char),)
        _long_degrees= _long[0] + (_long[1] / 60.0) + (_long[2]/(60.0 * 60.0))
        if _long[3] != 0:
            _long_degrees *= -1.0

        return _lat_degrees, _long_degrees

    def set_location(self, lat, lon):
        command = 'W'
        for p in lat:
            command += chr(p)
        for p in lon:
            command += chr(p)
        self.serial.write(command)
        response = self.serial.read(1)
        self._validate_command(response)

    def _get_time(self):
        self._send_command('h')
        response = self._read_response(9)
        time = ()
        for char in response[:-1]:
            time = time + (ord(char),)
        return time

    def get_time_initilizer(self):
        """Returns time initializer  of the format YYYYMMDDTHHmmss"""
        (_hour, _minute, _seconds,
         _month, _day_of_month,  _year,
         GMT_OFFSET, _DAYLIGHT_SAVINGS_ENABLED) = self._get_time()
        date_string = "20"+str(_year).zfill(2)+"-"+str(_month).zfill(2)+\
                      "-"+str( _day_of_month).zfill(2)+"T"+str(_hour).zfill(2)+\
                      ":"+str(_minute).zfill(2)+":"+str(_seconds).zfill(2)
        return date_string


    def set_time_initializer(self, time):
        command = 'H'
        for p in time:
            command += chr(p)
        self._send_command(command)
        response = self._read_response(1)
        self._validate_command(response)

    def get_version(self):
        self.serial.write('V')
        response = self.serial.read(3)
        return ord(response[0]) + ord(response[1]) / 10.0

    def get_model(self):
        self.serial.write('m')
        response = self.serial.read(2)
        return ord(response[0])

    def echo(self, x):
        command = 'K' + chr(x)
        self._send_command(command)
        response = self._read_response(2)
        return ord(response[0])

    def alignment_complete(self):
        self._send_command('J')
        response = self._read_response(2)
        return True if ord(response[0]) == 1 else False

    def goto_in_progress(self):
        self.serial.write('L')
        response = self.serial.read(2)
        return True if int(response[0]) == 1 else False

    def cancel_goto(self):
        self._send_command('M')
        response = self._read_response(1)
        self._validate_command(response)


    def cancel_current_operation(self):
        self.cancel_goto()

    def display(self, msg):
        print(self.echo(msg))



    def goto_altaz(self, altaz):
        self.goto_azel(altaz.az.deg, altaz.el.deg)

    def is_aligned(self):
        print "not implemented"

    def set_location_lat_long(self):
        print "not implemented"
