# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import subprocess
import os
import pathlib
import time

import octoprint.settings
import octoprint.filemanager
import octoprint.plugin

from octoprint.util import RepeatedTimer
from octoprint.events import Events, eventManager

from octoprint_mitemp2 import stringUtils
from octoprint_mitemp2.CachedSettings import CachedSettings

#from .MiTemperature2.LYWSD03MMC import LYWSD03MMC

class MiTemperature2Plugin(octoprint.plugin.StartupPlugin,
                           octoprint.plugin.TemplatePlugin,
                           octoprint.plugin.SettingsPlugin,
                           octoprint.plugin.EventHandlerPlugin):

    ## Requires StartupPlugin
    def on_after_startup(self):
        self._logger.info("MiTemperature2 started! (MAC: %s)" % self._settings.get(["mac_address"]))
        self._start_repeat_timer()

	## Requires SettingsPlugin
    def get_settings_defaults(self):
        # default settings here
        return dict(
            # config
            command=str(pathlib.Path(__file__).parent.absolute()) + "/MiTemperature2/LYWSD03MMC.py",
            args="-r -b -c 1 --callback sendToFile.sh",
            mac_address="A4:C1:38:2D:86:49",
            seconds="60",
            # values from device
            temp="0",
            humidity="0",
            bat_voltage="0",
            bat_level="0"
        )

    ## Requires SettingsPlugin
    # def on_settings_save(self, data):
    #     # default save function
    #     octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
    #     # refresh cached settings
    #     self._cachedSettings.updateSettings(self._settings)
    #     self._update_device_data("Saved values")

    ## Requires SettingsPlugin
    # def on_settings_load(self):
    #     return dict(octoprint.plugin.SettingsPlugin.on_settings_load(self))

    ## Requires TemplatePlugin
    def get_template_configs(self):
        return [
            dict(type="navbar", template="mitemp2_navbar.jinja2", custom_bindings=True),
            dict(type="settings", template="mitemp2_settings.jinja2", custom_bindings=True, name="Xiaomi MiTemperature2")
        ]

    ## SoftwareUpdate hook
    def get_update_information(self, *args, **kwargs):
        return dict(
            mitemp2 = dict(
                displayName=self._plugin_name,
                displayVersion=self._plugin_version,
                # version check: github repository
                type="github_release",
                current=self._plugin_version,
                user="shawe",
                repo="octoprint_mitemp2",
                # update method: pip
                pip="https://github.com/shawe/octoprint-mitemp2/archive/{target}.zip"
            )
        )

    def _get_command_reply(self):
        cmd = self._settings.get(["command"])
        args = " " + self._settings.get(["args"]) + " -d " + self._settings.get(["mac_address"])

        proc = subprocess.Popen(
            cmd + " " + args,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        msg = 'through stdin to stdout\n'.encode('utf-8')
        stdout_value, stderr_value = proc.communicate(msg)
        output = repr(stdout_value.decode('utf-8'))

        output = output.split("\n")
        output = output[0].split('\\')
        res = []

        for line in output:
            res.append(line)

        return res

    def _get_device_values(self):
        res = self._get_command_reply()
        results = []

        for i in range(1, len(res) - 1):
            line = res[i]
            line = line.split(' ')
            results.append(line)

        res = {
            "temperature": results[0][1],
            "humidity": results[1][1],
            "bat_voltage": results[2][2],
            "bat_level": results[3][2]
        }

        return res

    def _update_device_details(self):
        reply = self._get_device_values()
        self._logger.info("Nuevos datos: %s" % str(reply))
        return reply

    def _update_device_data(self, updateReason=""):
        update = self._update_device_details()

        # store new values
        self._settings.set(["temperature"], update["temperature"])
        self._settings.set(["humidity"], update["humidity"])
        self._settings.set(["bat_voltage"], update["bat_voltage"])
        self._settings.set(["bat_level"], update["bat_level"])

        # prepare clientMessage
        clientMessageDict = dict()
        currentValueDict = {
            "[mac_address]": self._settings.get(["mac_address"]),
            "[temperature]": self._settings.get(["temperature"]),
            "[humidity]": self._settings.get(["humidity"]),
            "[bat_voltage]": self._settings.get(["bat_voltage"]),
            "[bat_level]": self._settings.get(["bat_level"])
        }
        navBarMessagePattern="MiTemp2 <span>[mac_address]</span> <span>[temperature] ºC</span> <span>[humidity] %</span> <span>[bat_voltage] V</span> <span>([bat_level] %)</span>"
        navBarMessage = stringUtils.multiple_replace(navBarMessagePattern, currentValueDict)
        clientMessageDict.update( {'navBarMessage' : navBarMessage } )
        self._plugin_manager.send_plugin_message(self._identifier, clientMessageDict)

    def _interval(self):
        return int(self._settings.get(["seconds"]))

    def _start_repeat_timer(self):
        self._repeat_timer = RepeatedTimer(self._interval(), self._update_device_data("Repeat timer"))
        self._repeat_timer.start()
        self._logger.info("MiTemperature2 every %s seconds" % str(self._interval()))

__plugin_identifier__ = "mitemp2"
__plugin_package__ = "octoprint_%s" % __plugin_identifier__
__plugin_name__ = "Xiaomi MiTemperature2"
__plugin_version__ = "0.1.0"
__plugin_description__ = "Shows data from Xiaomi MiTemperature2"
__plugin_author__ = "Francesc Pineda Segarra"
__plugin_author_email__ = "francesc.pineda.segarra@gmail.com"
__plugin_url__ = "https://github.com/shawe/octoprint-mitemp2"
__plugin_license__ = "AGPLv3"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = MiTemperature2Plugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }