### How This Server Works

1.  **Socket Server**: It opens a TCP socket on port `1234` and listens for incoming connections. For each client that connects, it spins up a new `ClientHandler` thread. This allows multiple clients to connect simultaneously (though they will be controlling the same GPIB bus).

2.  **`GpibManager` Class**: This class is a wrapper around PyVISA. It handles the details of connecting to a specific GPIB instrument at a given address. When a client sends `++addr X`, the server creates a new `GpibManager` instance for that address.

3.  **`ClientHandler` Class**: This is the core of the emulator.
    * It receives data from the client.
    * If the command starts with `++`, it calls `handle_prologix_command`. This method has a large `if/elif` block that maps each Prologix command to a PyVISA function.
    * If the command is a standard instrument command (like `*IDN?`), it's passed directly to the `GpibManager` to be written to the instrument.