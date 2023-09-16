""" This file aims to demonstrate how to write custom commands in OpenWPM

Steps to have a custom command run as part of a CommandSequence

1. Create a class that derives from BaseCommand
2. Implement the execute method
3. Append it to the CommandSequence
4. Execute the CommandSequence

"""
import logging

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket

import os 
from pathlib import Path

class IframeScreenshotCommand(BaseCommand):
    """This command logs how many links it found on any given page"""

    def __init__(self, tranco_index, site) -> None:
        self.logger = logging.getLogger("openwpm")
        self.tranco_index = tranco_index
        self.site = site

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "IframeScreenshotCommand"

    def write_content(self, file_addr, list_content) -> None:
        with open(file_addr, 'w') as out_file:
            for item in list_content:
                out_file.write(item + '\n') 

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:  
        iframe_elements = webdriver.find_elements_by_tag_name('iframe')

        base_file_addr = os.path.join(manager_params.data_directory, 'website_iframe_screenshots', str(self.visit_id) + '_' +  str(self.tranco_index) + '_' + self.site.replace('http://www.',''))

        Path(os.path.join(base_file_addr)).mkdir(parents=True, exist_ok=True)
        iframe_screenshot_logs = []

        for idx, iframe in enumerate(iframe_elements):
            try:
                iframe.screenshot(os.path.join(base_file_addr, str(idx) + '.png'))
                iframe_screenshot_logs.append(str(idx) + ',' + iframe.get_attribute("src"))
            except Exception as ex:
                pass
            
        self.logger.info("Successfully logged " + str(len(iframe_screenshot_logs))  + " iframe screenshots out of " + str(len(iframe_elements)))

        self.write_content(os.path.join(base_file_addr,'iframe_screenshot_logs.csv'), iframe_screenshot_logs)

        if len(iframe_elements) == 0:
            self.logger.info("No iframes found for %s", self.site)
        else:
            self.logger.info("iframe screenshots logged on %s", self.site)
