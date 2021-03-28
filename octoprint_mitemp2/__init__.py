# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import octoprint.settings
import octoprint.filemanager
import octoprint.plugin

#from .MiTemperature2.LYWSD03MMC import LYWSD03MMC

class MiTemperature2Plugin(octoprint.plugin.SettingsPlugin,
                           octoprint.plugin.TemplatePlugin,
                           octoprint.plugin.StartupPlugin):

    # def initialize(self):
    #     if self._settings.get(["command", "mac_address", "seconds", "temp", "humidity", "bat_voltage", "bat_level"]) is None:
    #         self._logger.error("Some data not defined, plugin won't be able to work")
    #         return False

	##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        # default settings here
        return dict(
            # config
            command="./LYWSD03MMC.py -d A4:C1:38:2D:86:49 -r -b -c 1 --callback sendToFile.sh",
            mac_address="A4:C1:38:2D:86:49",
            seconds=60,
            # values from device
            temp=0,
            humidity=0,
            bat_voltage=0,
            bat_level=0
        )

    def on_settings_save(self, data):
        # default save function
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

    def on_settings_load(self):
        return dict(octoprint.plugin.SettingsPlugin.on_settings_load(self))

    ##~~ TemplatePlugin mixin

    def get_template_configs(self):
        return [
            dict(type="navbar", template="mitemp2_navbar.jinja2", custom_bindings=True),
            dict(type="settings", template="mitemp2_settings.jinja2", custom_bindings=True, name="Xiaomi MiTemperature2")
        ]

    ##~~ SoftwareUpdate hook

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

    def update_device_details(self):
        pass

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