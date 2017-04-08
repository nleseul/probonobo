import struct
import subprocess

from distutils.version import LooseVersion
from enum import IntEnum
from io import BytesIO
from PIL import Image


class AndroidKeyCode(IntEnum):
    ANDROID_KEYCODE_BACK = 4
    ANDROID_KEYCODE_MENU = 82
    ANDROID_KEYCODE_POWER = 26


class AndroidDevice:

    has_exec_out = False

    def connect(self):

        subprocess.run(["adb", "start-server"])

        version_output = subprocess.run(["adb", "version"], stdout=subprocess.PIPE).stdout.decode('utf-8')
        version = LooseVersion(version_output.partition('\n')[0].strip()[29:])
        self.has_exec_out = version >= LooseVersion('1.0.36')

        devices_output = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE).stdout.decode('utf-8')

        if '\tdevice' not in devices_output:
            raise DeviceException("No devices found!")

    def disconnect(self):
        subprocess.run(["adb", "kill-server"])

    def is_in_power_save(self):
        check_awake_result = subprocess.run(["adb", "shell", "dumpsys power | grep 'Display Power' | cut -c22-"],
                                            stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        return check_awake_result != 'ON'

    def power_save_on(self):
        if not self.is_in_power_save():
            self.press_key(AndroidKeyCode.ANDROID_KEYCODE_POWER)

    def power_save_off(self):
        if self.is_in_power_save():
            self.press_key(AndroidKeyCode.ANDROID_KEYCODE_POWER)
            self.press_key(AndroidKeyCode.ANDROID_KEYCODE_MENU)

    def press_key(self, key):
        subprocess.run(["adb", "shell", ("input keyevent " + repr(int(key)))])

    def select_at_coord(self, coord):
        subprocess.run(["adb", "shell", ("input tap " + ' '.join(repr(int(v)) for v in coord))])

    def drag(self, start, end, duration=1):
        command = ("input swipe " + ' '.join(repr(int(v)) for v in (start + end)) + ' ' + repr(int(duration * 1000)))
        subprocess.run(["adb", "shell", command])

    def get_screenshot(self):
        return self.__load_raw_screenshot()

    def get_screenshot_bytes(self):
        raw_screenshot = self.__get_screenshot_bytes(False)
        header = raw_screenshot[0:12]
        rgba_data = raw_screenshot[12:]
        width, height, format = struct.unpack('<III', header)
        return rgba_data, width, height, format

    def __load_raw_screenshot(self):
        bytes, width, height, format = self.get_screenshot_bytes()
        image = Image.frombytes('RGBA', (width, height), bytes)
        return image

    def __load_png_screenshot(self, bytes):
        image = Image.open(BytesIO(bytes))
        return image

    def __get_screenshot_bytes(self, get_png):
        if (self.has_exec_out):
            result = subprocess.run(["adb", "exec-out", "screencap" + (" -p" if get_png else "")], stdout=subprocess.PIPE)
        else:
            result = subprocess.run(["adb", "shell", "screencap" + (" -p" if get_png else "")], stdout=subprocess.PIPE)
        data = result.stdout

        return data

