# On Raspberry-Pi server
# sudo ip link set can0 up type can bitrate 500000 restart-ms 100
# python -m can_remote --interface=socketcan --channel=can0 --bitrate=500000

import can
import time


def main():
    # Use SocketCAN interface
    bus = can.Bus('ws://localhost:54701/',
              interface='remote',
              bitrate=500000,
              receive_own_messages=True)

    # Send a CAN frame
    try:
        bus.send(can.Message(arbitration_id=0x064, data=[0x01, 0xAA], is_extended_id=False))
        time.sleep(0.5)
        bus.send(can.Message(arbitration_id=0x064, data=[0x02, 0xAA], is_extended_id=False))
        time.sleep(0.5)
        bus.send(can.Message(arbitration_id=0x064, data=[0x03, 0xAA], is_extended_id=False))
        print("Message sent on {}".format(bus.channel_info))
    except can.CanError:
        print("Message NOT sent")

    # Receive a frame (blocking, timeout=1s)
    # print("Listening on CAN bus...")
    # for msg in bus:
    #     print(msg)
    bus.shutdown()

if __name__ == "__main__":
    main()
