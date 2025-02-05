# references:
# [Bot BLE open API](https://github.com/OpenWonderLabs/SwitchBotAPI-BLE/blob/latest/devicetypes/bot.md)
# [Plug Mini BLE open API](https://github.com/OpenWonderLabs/SwitchBotAPI-BLE/blob/latest/devicetypes/plugmini.md)
# [Bleak doc](https://bleak.readthedocs.io/en/latest/index.html)

# related articles:
# [SwitchBotをWindows 10 から制御する](https://qiita.com/hiratarich/items/00be23735ac6001ff74b)

import sys
import asyncio
from bleak import BleakClient


class SwitchBotPlugMini:
    """SwitchBot Plug Mini の制御クラス"""

    # UUID 定義
    # [plugmini UUID](https://github.com/OpenWonderLabs/SwitchBotAPI-BLE/blob/latest/devicetypes/plugmini.md#ble-communication-packet-basic-format)
    RX_CHARACTERISTIC_UUID = "cba20002-224d-11e6-9fb8-0002a5d5c51b"
    TX_CHARACTERISTIC_UUID = "cba20003-224d-11e6-9fb8-0002a5d5c51b"

    # コマンド定義
    # [Expansion command](https://github.com/OpenWonderLabs/SwitchBotAPI-BLE/blob/latest/devicetypes/plugmini.md#0x0f-expansion-command)
    COMMANDS = {
        "off": b"\x57\x0f\x50\x01\x01\x00",
        "on": b"\x57\x0f\x50\x01\x01\x80",
        "toggle": b"\x57\x0f\x50\x01\x02\x80",
        "state": b"\x57\x0f\x51\x01",
    }
    # NOTE: The response format is same regardless of the command.
    RESPONSES = {
        b"\x01\x80": "On",
        b"\x01\x00": "Off",
    }

    @classmethod
    def generate_command(cls, operation: str) -> bytes:
        """操作に応じたコマンドを取得"""
        return cls.COMMANDS.get(operation, None)

    @classmethod
    def parse_response(cls, response: bytes) -> str:
        """応答データを解析"""
        return cls.RESPONSES.get(response, "Unknown")

    @classmethod
    async def send_command(cls, address: str, command: bytes) -> bytes:
        """
        Send a command to the BLE device and get the response

        Args:
            address (str): BLE MAC Address
            command (bytes): Command to send

        Returns:
            bytes: Response data
        """
        response = b"\x00\x00"

        def callback(sender: int, data: bytearray):
            nonlocal response
            response = bytes(data)

        # reference: https://github.com/hbldh/bleak/issues/59
        async with BleakClient(address) as client:
            await client.start_notify(cls.TX_CHARACTERISTIC_UUID, callback)
            await client.write_gatt_char(
                cls.RX_CHARACTERISTIC_UUID, command, response=True
            )
            await asyncio.sleep(0.5)
            await client.stop_notify(cls.TX_CHARACTERISTIC_UUID)

        return response

    @classmethod
    def execute(cls, address: str, operation: str):
        """SwitchBot Plug Mini を操作"""
        command = cls.generate_command(operation)
        if command is None:
            print("ERROR: operation must be <off/on/toggle/state>")
            return False, None

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(cls.send_command(address, command))
            return True, cls.parse_response(response)
        except Exception:
            print(sys.exc_info())
            return False, None
        finally:
            asyncio.set_event_loop(None)
            loop.close()
