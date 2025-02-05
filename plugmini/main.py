import os
import sys
from dotenv import load_dotenv
import argparse
from plugmini import SwitchBotPlugMini


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

    result, resp = SwitchBotPlugMini.execute(address, command)
    if result:
        print(result, resp)
        sys.exit(0)  # result==True, exit(0)
    else:
        print(result, resp)
        sys.exit(1)


if __name__ == "__main__":
    main()
