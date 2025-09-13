from test import parse_test_file, TestRunner
from adapters import PrologixGPIBEthernet


def main():
    test_config = parse_test_file('scenario.yaml', 'test/schema.json')
    adapter = PrologixGPIBEthernet(
        '192.168.1.101', 
        address=test_config['address'], 
        prologix_read_timeout=0.5, 
        socket_read_timeout=15
    )
    runner = TestRunner(test_config, adapter)
    runner.connect_instrument()
    runner.run_test()


if __name__ == '__main__':
    main()
