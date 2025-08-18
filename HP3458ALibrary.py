from devices import HP3458A


class HP3458ALibrary:
    def __init__(self, resource, **kwargs):
        self.device = HP3458A(resource, **kwargs)

    def setup_device(self):
        """Setup the HP3458A device."""
        self.device.setup()

    def configure_dcv(self, mrange=None):
        """Configure device for DC voltage measurement."""
        self.device.conf_function_DCV(mrange=mrange)

    def get_reading(self, trig=True):
        """Get a single reading from the device."""
        return self.device.get_reading(trig=trig)

    def reset_device(self):
        """Reset the device."""
        self.device.reset()
