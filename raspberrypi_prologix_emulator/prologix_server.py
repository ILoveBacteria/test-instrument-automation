#
# Raspberry Pi Prologix GPIB-Ethernet Emulator
#
# This script runs on a Raspberry Pi with a GPIB interface
# (e.g., using gpib_bitbang with linux-gpib). It listens for
# network connections and emulates the command set of a
# Prologix GPIB-Ethernet controller.
#
# It allows a remote computer to control GPIB instruments
# connected to the Raspberry Pi using standard Prologix commands.
#
# Author: Gemini
# Version: 1.0
#
# Installation on Raspberry Pi:
# 1. Ensure linux-gpib and the gpib_bitbang driver are installed and configured.
# 2. Install PyVISA and the pyvisa-py backend:
#    pip install pyvisa pyvisa-py
# 3. Save this script as prologix_server.py
# 4. Run from the terminal: python3 prologix_server.py
#

import socket
import threading
import pyvisa
import logging

# --- Configuration ---
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 1234       # The standard Prologix port
GPIB_INTERFACE = 'GPIB0' # The VISA resource name for your GPIB interface

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GpibManager:
    """
    Manages the connection to a single GPIB instrument via PyVISA.
    This class handles opening, closing, and interacting with the instrument.
    """
    def __init__(self, interface, address):
        self.rm = pyvisa.ResourceManager('@py') # Use the pyvisa-py backend
        self.instrument = None
        self.address = address
        self.interface = interface
        self.connect()

    def connect(self):
        """Opens a connection to the GPIB instrument."""
        try:
            resource_name = f"{self.interface}::{self.address}::INSTR"
            self.instrument = self.rm.open_resource(resource_name)
            # Set a reasonable timeout for instrument communication
            self.instrument.timeout = 2000 # 2 seconds
            logging.info(f"Successfully connected to GPIB device at address {self.address}")
        except pyvisa.errors.VisaIOError as e:
            logging.error(f"Failed to connect to GPIB device at address {self.address}: {e}")
            self.instrument = None

    def close(self):
        """Closes the connection to the instrument."""
        if self.instrument:
            self.instrument.close()
            logging.info(f"Closed connection to GPIB device at address {self.address}")

    def write(self, command):
        """Writes a command to the instrument."""
        if self.instrument:
            self.instrument.write(command)
        else:
            raise ConnectionError("GPIB instrument not connected.")

    def read(self, num_bytes=1024):
        """Reads data from the instrument."""
        if self.instrument:
            return self.instrument.read()
        else:
            raise ConnectionError("GPIB instrument not connected.")

    def query(self, command):
        """Writes a command and reads the response."""
        if self.instrument:
            return self.instrument.query(command)
        else:
            raise ConnectionError("GPIB instrument not connected.")

    def clear(self):
        """Sends a device clear (DCL) signal."""
        if self.instrument:
            self.instrument.clear()
        else:
            raise ConnectionError("GPIB instrument not connected.")
            
    @property
    def service_request_status(self):
        """Checks the status of the SRQ line."""
        if self.instrument:
            # The status byte is a pyvisa attribute
            return self.instrument.stb
        return 0


class ClientHandler(threading.Thread):
    """
    Handles a single client connection, parsing commands and interacting
    with the GpibManager.
    """
    def __init__(self, connection, address):
        threading.Thread.__init__(self)
        self.conn = connection
        self.addr = address
        self.gpib_manager = None
        self.current_gpib_address = 1 # Default GPIB address
        self.auto_read = 0 # Prologix 'auto' mode state

    def run(self):
        """Main loop to handle client communication."""
        logging.info(f"New connection from {self.addr}")
        try:
            self.gpib_manager = GpibManager(GPIB_INTERFACE, self.current_gpib_address)
            
            while True:
                data = self.conn.recv(1024)
                if not data:
                    break # Client disconnected
                
                command = data.decode('utf-8').strip()
                logging.info(f"Received from {self.addr}: '{command}'")

                # Check if it's a Prologix command
                if command.startswith('++'):
                    self.handle_prologix_command(command)
                else:
                    self.handle_instrument_command(command)

        except (ConnectionResetError, BrokenPipeError):
            logging.warning(f"Client {self.addr} disconnected unexpectedly.")
        except Exception as e:
            logging.error(f"An error occurred with client {self.addr}: {e}")
        finally:
            if self.gpib_manager:
                self.gpib_manager.close()
            self.conn.close()
            logging.info(f"Connection with {self.addr} closed.")

    def send_response(self, response):
        """Sends a response back to the client."""
        # Ensure response ends with a newline for client compatibility
        if not response.endswith('\n'):
            response += '\n'
        self.conn.sendall(response.encode('utf-8'))

    def handle_instrument_command(self, command):
        """Process a standard SCPI command for the instrument."""
        if not self.gpib_manager or not self.gpib_manager.instrument:
            self.send_response("Error: No GPIB device connected.")
            return
            
        try:
            self.gpib_manager.write(command)
            # If auto-read is enabled and it's a query, read the response
            if self.auto_read and '?' in command:
                response = self.gpib_manager.read()
                self.send_response(response)
        except Exception as e:
            error_msg = f"Error communicating with instrument: {e}"
            logging.error(error_msg)
            self.send_response(error_msg)

    def handle_prologix_command(self, command):
        """Parses and executes a Prologix '++' command."""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:]

        try:
            # --- Address and Communication ---
            if cmd == '++addr':
                if args:
                    new_address = int(args[0])
                    if 0 <= new_address <= 30:
                        self.current_gpib_address = new_address
                        # Re-initialize the GPIB manager for the new address
                        if self.gpib_manager:
                            self.gpib_manager.close()
                        self.gpib_manager = GpibManager(GPIB_INTERFACE, self.current_gpib_address)
                    else:
                        self.send_response("Error: Invalid GPIB address.")
                else:
                    self.send_response(str(self.current_gpib_address))

            elif cmd == '++auto':
                if args:
                    self.auto_read = int(args[0])
                else:
                    self.send_response(str(self.auto_read))

            elif cmd == '++read':
                response = self.gpib_manager.read()
                self.send_response(response)

            # --- GPIB Bus Control ---
            elif cmd == '++clr':
                self.gpib_manager.clear()

            elif cmd == '++trg':
                # PyVISA does not have a direct broadcast trigger.
                # This would need to be implemented if specific instruments require it.
                logging.warning("++trg command is not fully implemented.")
                self.send_response("OK")

            elif cmd == '++ifc':
                 # Interface Clear (IFC) is typically handled by the VISA backend
                 # during resource management. A manual trigger is not standard in PyVISA.
                logging.warning("++ifc is handled by VISA backend, not manually triggered.")
                self.send_response("OK")
            
            elif cmd == '++loc':
                self.gpib_manager.instrument.control_ren(pyvisa.constants.RENLineOperation.deassert)
                
            elif cmd == '++llo':
                self.gpib_manager.instrument.control_ren(pyvisa.constants.RENLineOperation.assert_and_deassert)

            # --- Status and Polling ---
            elif cmd == '++srq':
                stb = self.gpib_manager.service_request_status
                # The SRQ line is active if bit 6 is set
                is_srq_active = 1 if (stb & 64) else 0
                self.send_response(str(is_srq_active))

            elif cmd == '++spoll':
                # Serial poll the currently addressed device
                stb = self.gpib_manager.instrument.read_stb()
                self.send_response(str(stb))
                
            # --- Configuration (Acknowledged but may not change backend behavior) ---
            elif cmd in ['++mode', '++eos', '++eoi', '++read_tmo_ms']:
                 # These settings are managed by the client or are defaults in PyVISA.
                 # We acknowledge them to maintain compatibility.
                 logging.info(f"Acknowledged command: {command}")
                 # You can add logic here if specific behavior is needed.
                 self.send_response("OK")

            # --- Informational ---
            elif cmd == '++ver':
                self.send_response("Raspberry Pi Prologix Emulator v1.0")

            else:
                self.send_response(f"Error: Unknown command '{cmd}'")

        except Exception as e:
            error_msg = f"Error processing command '{command}': {e}"
            logging.error(error_msg)
            self.send_response(error_msg)


def start_server():
    """Starts the main TCP socket server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    logging.info(f"Prologix Emulator Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        handler = ClientHandler(conn, addr)
        handler.start()

if __name__ == "__main__":
    start_server()

