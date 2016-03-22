#!/usr/bin/python

import serial



class TelescopeError(Exception):
    def __init__(self, msg):
        self.msg = msg

class TelescopeAlignmentNotSet(TelescopeError):
    def __ini__(self):
        msg = "Telescope alignment not set"
        super(TelescopeAlignmentNotSet, self).__init__(msg)


class NexStar:
    
    def __init__(self, device):
        self.serial = serial.Serial(device, baudrate=9600, timeout=1)
        self.DIR_AZIMUTH = 0
        self.DIR_ELEVATION = 1

    @staticmethod
    def _validate_command(response):
        assert response == '#', 'Command failed'

    @staticmethod
    def _precise_to_degrees(string):
        return int(string, 16) / 2.**32 * 360.

    @staticmethod
    def _degrees_to_precise(degrees):
        print "_degrees_to_precise(%s)"%degrees
        rounded = round(degrees / 360. * 2.**32)
        print "_rounded_off %s"%rounded
        return '%08X' % rounded

    def _get_position(self, command):
        self.serial.write(command)
        response = self.serial.read(18)
        print response
        return (self._precise_to_degrees(response[:8]),
                self._precise_to_degrees(response[9:17]))

    @staticmethod
    def _convert_radec_to_atlaz(_ra, _dec):
        pass

    def get_azel(self):
        return self._get_position('z')
        
    def get_radec(self):
        return self._get_position('e') 

    def _goto_command(self, char, values):
        command = (char + self._degrees_to_precise(values[0]) + ',' +
                   self._degrees_to_precise(values[1]))
        print command
        self.serial.write(command)
        response = self.serial.read(1)
        self._validate_command(response)

    def safe_goto_azel(self, az, el):
        if not self.alignment_complete():
            raise TelescopeAlignmentNotSet
        if el > 90.0:
            raise TelescopeError("elevation larger than 90 degrees not allowed")
        if az >= 360.0:
            az = 0.0
        self.goto_azel(az, el)

    def goto_azel(self, az, el):
        print "going to %s %s" %(az, el)
        self._goto_command('b', (az, el))
    def DetermineRaDecAreSafe(self, az, el):
        '''Checks if ra and dec are safe for telescope

        Based on the location this function should determine if the
        given Right Assention and Declination are safe for the telescope
        to point to. (we don't want pointing at floor :) '''
        return True

    def safe_goto_radec(self, ra, dec):
        if not self.alignment_complete():
            raise TelescopeAlignmentNotSet
        if not self.DetermineRaDecAreSafe(ra,dec):
            raise TelescopeError("Ra: %s, Dec: %s are not safe at current location" %
                                 (ra, dec))
        self.goto_radec(ra, dec)

    def goto_radec(self, ra, dec):
        print "goto: %s %s "%(ra,dec)
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
        self.serial.write('w')
        response = self.serial.read(9)
        lat = ()
        for char in response[:4]:
            lat = lat + (ord(char),)
        _long = ()
        for char in response[4:-1]:
            _long = _long + (ord(char),)
        ns_char = 'N' if lat[3] == 0 else 'S'
        ew_char = 'E' if _long[3] == 0 else 'W'
        print(str(lat[0]) + ' ' + str(lat[1]) + "'" + str(lat[2]) +
              '" ' + ns_char + ', ' +
              str(_long[0]) + ' ' + str(_long[1]) + "'" + str(_long[2]) +
              '" ' + ew_char)
        return lat, _long

    def set_location(self, lat, lon):
        command = 'W'
        for p in lat:
            command += chr(p)
        for p in lon:
            command += chr(p)
        self.serial.write(command)
        response = self.serial.read(1)
        self._validate_command(response)

    def get_time(self):
        self.serial.write('h')
        response = self.serial.read(9)
        time = ()
        for char in response[:-1]:
            time = time + (ord(char),)
        return time

    def set_time(self, time):
        command = 'H'
        for p in time:
            command += chr(p)
        self.serial.write(command)
        response = self.serial.read(1)
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
        self.serial.write(command)
        response = self.serial.read(2)
        return ord(response[0])

    def alignment_complete(self):
        self.serial.write('J')
        response = self.serial.read(2)
        return True if ord(response[0]) == 1 else False

    def goto_in_progress(self):
        self.serial.write('L')
        response = self.serial.read(2)
        return True if int(response[0]) == 1 else False

    def cancel_goto(self):
        self.serial.write('M')
        response = self.serial.read(1)
        self._validate_command(response)
