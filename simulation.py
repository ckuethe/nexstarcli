import telescopes


class Telescope(telescopes.BaseTelescope):
    def goto_altaz(self, altaz):
        pass

    def is_aligned(self):
        pass

    def get_radec(self):
        pass

    def get_altaz(self):
        pass

    def cancel_current_operation(self):
        pass

    def get_location(self):
        pass

    def set_earth_location(self, latlong):
        pass

    def goto_radec(self, radec):
        pass

    def get_time(self):
        pass

    def display(self, msg):
        pass

    def set_time(self, time):
        pass

    def _send_command(self, cmd):
        pass
