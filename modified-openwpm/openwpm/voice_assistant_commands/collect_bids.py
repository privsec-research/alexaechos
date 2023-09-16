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
import json
import time

class BidCollectionCommand(BaseCommand):
    """This command logs how many links it found on any given page"""

    def __init__(self, tranco_index, site) -> None:
        self.logger = logging.getLogger("openwpm")
        self.tranco_index = tranco_index
        self.site = site

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "BidCollectionCommand"

    def write_content(self, file_addr, list_content) -> None:
        with open(file_addr, 'w') as out_file:
            for item in list_content:
                out_file.write(json.dumps(item)) 
                out_file.write('\n')

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        GET_CPM =  "var output = [];" \
                        "function getCPM()" \
                        "{    " \
                        "    var responses = pbjs.getBidResponses();" \
                        "    var winners = pbjs.getAllWinningBids();" \
                        "    Object.keys(responses).forEach(function(adUnitCode) {" \
                        "    var response = responses[adUnitCode];" \
                        "        response.bids.forEach(function(bid) " \
                        "        {" \
                        "            output.push({" \
                        "            bid: bid," \
                        "            adunit: adUnitCode," \
                        "            adId: bid.adId," \
                        "            bidder: bid.bidder," \
                        "            time: bid.timeToRespond," \
                        "            cpm: bid.cpm," \
                        "            msg: bid.statusMessage," \
                        "            rendered: !!winners.find(function(winner) {" \
                        "                return winner.adId==bid.adId;" \
                        "            })" \
                        "            });" \
                        "        });" \
                        "    });" \
                        "}" \
                        "getCPM();" \
                        "return output;"

        GET_FORCED_CPM = """window.updated_output = [];
                            function sendAdserverRequest(responses, timeout) {
                                Object.keys(responses).forEach(function(adUnitCode) {
                                    var response = responses[adUnitCode];
                                        response.bids.forEach(function(bid) 
                                        {
                                            window.updated_output.push({
                                            bid: bid,
                                            adunit: adUnitCode,
                                            adId: bid.adId,
                                            bidder: bid.bidder,
                                            time: bid.timeToRespond,
                                            cpm: bid.cpm,
                                            msg: bid.statusMessage,
                                            });
                                        });
                                    });
                            }

                            pbjs.requestBids({
                                bidsBackHandler: sendAdserverRequest,
                                timeout: 1000
                            });
                        """
        GET_FORCED_CPM_RETURN = "return window.updated_output;"

        current_url = webdriver.current_url
        bids = []
        count = 0
        method = 'NORMAL' 
        
        try:
            bids = webdriver.execute_script(GET_CPM)

            if len(bids) == 0:                
                webdriver.execute_script(GET_FORCED_CPM)
                time.sleep(4)
                bids = webdriver.execute_script(GET_FORCED_CPM_RETURN)
                method = 'FORCED'

            if len(bids) > 0:
                file_addr = os.path.join(manager_params.data_directory, 'website_bids', str(self.visit_id) + '_' +  str(self.tranco_index) + '_' + method + '_' + self.site.replace('http://www.',''))

                self.write_content(file_addr, bids)

        except Exception as e: 
            self.logger.info("Exception occurred while running %s", str(self))
            print('EXCEPTION occurred in bid collection:', str(e))
            pass

        self.logger.info("Running %s", str(self))