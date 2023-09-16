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

from openwpm.storage.storage_controller import DataSocket
from openwpm.storage.storage_providers import TableName

class BidStatusCollectionCommand(BaseCommand):
    """This command logs how many links it found on any given page"""

    def __init__(self, tranco_index, site) -> None:
        self.logger = logging.getLogger("openwpm")
        self.tranco_index = tranco_index
        self.site = site

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "BidStatusCollectionCommand"

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        PBJS_VERSION = "var version = '';" \
                        "function pbjsVersion() " \
                        "{" \
                        "    try" \
                        "    {" \
                        "        version = pbjs.version;" \
                        "        " \
                        "    }" \
                        "    catch(err)" \
                        "    {" \
                        "        " \
                        "    }" \
                        "}" \
                        "pbjsVersion();" \
                        "return version;"

        current_url = webdriver.current_url
        pbjs_version = ''
        prebid_status = 0

        try:
            pbjs_version = webdriver.execute_script(PBJS_VERSION)

            if pbjs_version != '':
                prebid_status = 1

        except Exception as e: 
            self.logger.info("Exception occured while running %s", str(self))
            pass

        self.logger.info("Running %s", str(self))

        sock = DataSocket(manager_params.storage_controller_address)
        sock.store_record(
            TableName("prebid_status"),
            self.visit_id,
            {
                "visit_id": self.visit_id,
                "browser_id": self.browser_id,
                "tranco_index": self.tranco_index,
                "site_url": self.site,
                "prebid_version": pbjs_version,
                "prebid_status": prebid_status
            },
        )
        sock.close()
