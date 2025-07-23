import openhtf as htf
from openhtf.output.servers import station_server
from openhtf.output.web_gui import web_launcher
from openhtf.plugs import user_input
from openhtf.util.configuration import CONF

from devices import *
from adapters import ProtocolAdapter
from test import phase_factory


class TestRunner:
    def __init__(self, test_config: dict, adapter: ProtocolAdapter):
        self.test_config = test_config
        self.adapter = adapter
        self.instrument = None

    def connect_instrument(self):
        device_class: Instrument = globals()[self.test_config['device']]
        self.instrument = device_class(name=self.test_config['name'], adapter=self.adapter)
        self.instrument.setup()  # Setup the instrument if needed
        print(f'Connected to {self.instrument}')

    def run_test(self, host='localhost', port=10000):
        # Generate the list of phase functions from the configuration.
        Instrument_function = getattr(self.instrument, self.test_config['function'])
        dynamic_phases = [phase_factory(Instrument_function, step.get('comment'), step.get('params'), step.get('measurement')) for step in self.test_config['steps']]
        test = htf.Test(
            *dynamic_phases,
            test_name=self.test_config['name'],
        )
        CONF.load(station_server_port=str(port))
        with station_server.StationServer() as server:
            web_launcher.launch(f'http://{host}:{port}')
            test.add_output_callbacks(server.publish_final_state)
            test.execute(test_start=user_input.prompt_for_test_start())
