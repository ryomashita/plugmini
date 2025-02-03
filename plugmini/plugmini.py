# references
# https://qiita.com/hiratarich/items/00be23735ac6001ff74b
# https://github.com/OpenWonderLabs/SwitchBotAPI-BLE/blob/latest/devicetypes/plugmini.md
# https://masahito.hatenablog.com/entry/2021/10/02/095828
# https://bleak.readthedocs.io/en/latest/index.html
# https://github.com/hbldh/bleak/issues/59

import os
import sys
import binascii
import asyncio
from bleak import BleakClient
from dotenv import load_dotenv
import argparse


def switchbotplugmini(address, operation):
    """! switchbotplugmini brief.
    Turn Off, Turn On, Toggle, Read State the SwitchBot Plug Mini
    @param address  : BLE MAC Address
    @param operation: turnoff/turnon/toggle/readstate
    @return         : result(True/False)
                      resp(RESP message(0x0100:Off, 0x0180:On) or 0x0000)
    """

    # RX characteristic UUID of the message from the Terminal to the Device
    RX_CHARACTERISTIC_UUID = "cba20002-224d-11e6-9fb8-0002a5d5c51b"
    # TX characteristic UUID of the message from the Device to the Terminal
    TX_CHARACTERISTIC_UUID = "cba20003-224d-11e6-9fb8-0002a5d5c51b"

    result = True
    resp = b"\x00\x00"

    def callback(sender: int, data: bytearray):
        # print(f"{sender}: {data}")
        nonlocal resp
        resp = data

    async def run(loop):
        async with BleakClient(address, loop=loop) as client:
            await client.start_notify(TX_CHARACTERISTIC_UUID, callback)
            await client.write_gatt_char(
                RX_CHARACTERISTIC_UUID, bytearray(command), response=True
            )
            await asyncio.sleep(0.5)
            await client.stop_notify(TX_CHARACTERISTIC_UUID)

    if operation == "off":
        command = b"\x57\x0f\x50\x01\x01\x00"
    elif operation == "on":
        command = b"\x57\x0f\x50\x01\x01\x80"
    elif operation == "toggle":
        command = b"\x57\x0f\x50\x01\x02\x80"
    elif operation == "state":
        command = b"\x57\x0f\x51\x01"
    else:
        print("ERROR, <off/on/toggle/state>")
        return False, resp

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run(loop))
    except Exception:
        print(sys.exc_info())
        result = False
    finally:
        asyncio.set_event_loop(None)
        loop.close()
        return result, resp


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Control SwitchBot Plug Mini over BLE."
    )
    parser.add_argument(
        "command",
        choices=["off", "on", "toggle", "state"],
        help="Command to execute",
    )
    parser.add_argument(
        "address",
        nargs="?",
        default=os.getenv("PLUGMINI_MAC_ADDRESS"),
        help="BLE MAC Address",
    )

    args = parser.parse_args()

    if args.address is None:
        parser.error(
            "MAC address must be provided as an argument or via the PLUGMINI_MAC_ADDRESS environment variable."
        )

    return args


def main():
    load_dotenv()

    args = parse_arguments()
    address = args.address
    command = args.command

    result, resp = switchbotplugmini(address, command)
    if result:
        if resp == b"\x01\x80":
            print(result, binascii.hexlify(resp), "on")
        elif resp == b"\x01\x00":
            print(result, binascii.hexlify(resp), "off")
        else:
            print(result, binascii.hexlify(resp))
        sys.exit(0)  # result==True, exit(0)
    else:
        print(result, binascii.hexlify(resp))
        sys.exit(1)


if __name__ == "__main__":
    main()
