from pathlib import Path

import os

# from custom_command import LinkCountingCommand
from openwpm.voice_assistant_commands.collect_bids import BidCollectionCommand
from openwpm.voice_assistant_commands.collect_iframe_screenshots import IframeScreenshotCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.commands.browser_commands import ScreenshotFullPageCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager
from openwpm.storage.leveldb import LevelDbProvider


NUM_BROWSERS = 1

CURRENT_PERSONA = os.environ['PERSONA']

def read_file(file_addr):
    with open(file_addr) as f:
        content = f.readlines()
    return content

sites = read_file('top_websites/top_prebid_websites.csv')[:200]

# Loads the default ManagerParams
# and NUM_BROWSERS copies of the default BrowserParams

manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
browser_params = [BrowserParams(display_mode="headless") for _ in range(NUM_BROWSERS)]

# Update browser configuration (use this for per-browser settings)
for browser_param in browser_params:
    # Record HTTP Requests and Responses
    browser_param.http_instrument = True
    # Record cookie changes
    browser_param.cookie_instrument = True
    # Record Navigations
    browser_param.navigation_instrument = True
    # Record JS Web API calls
    browser_param.js_instrument = True
    # Record the callstack of all WebRequests made
    browser_param.callstack_instrument = True
    # Record DNS resolution
    browser_param.dns_instrument = False
    browser_param.tp_cookies = "always"
    browser_param.bot_mitigation = True
    browser_param.display_mode = "native"
    browser_param.save_content = "image,sub_frame,main_frame"

    browser_param.seed_tar = Path('personas/' + CURRENT_PERSONA + '.tar.gz')

# Update TaskManager configuration (use this for crawl-wide settings)

Path('./' + CURRENT_PERSONA + '/website_bids/').mkdir(parents=True, exist_ok=True)
Path('./' + CURRENT_PERSONA + '/website_iframe_screenshots/').mkdir(parents=True, exist_ok=True)

manager_params.data_directory = Path('./' + CURRENT_PERSONA + '/')
manager_params.log_path = Path('./' + CURRENT_PERSONA + '/openwpm.log')


# Commands time out by default after 60 seconds
with TaskManager(
    manager_params,
    browser_params,
    SQLiteStorageProvider(Path('./' + CURRENT_PERSONA + '/crawl-data.sqlite')),
    LevelDbProvider(db_path='./' + CURRENT_PERSONA + '/content.ldb'),
) as manager:
    # Visits the sites
    for item in sites:
        tranco_index, site = item.strip().split(',')
        site = 'http://www.' + site
        tranco_index = int(tranco_index)

        def callback(success: bool, val: str = site) -> None:
            print(
                f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
            )

        # Parallelize sites over all number of browsers set above.
        command_sequence = CommandSequence(
            site,
            site_rank=tranco_index,
            callback=callback,
            reset=True,
        )

        command_sequence.append_command(GetCommand(url=site, sleep=30), timeout=60)

        # Bid collection command
        command_sequence.append_command(BidCollectionCommand(tranco_index, site))

        # Fullscreen screenshot command
        command_sequence.append_command(ScreenshotFullPageCommand('_' + str(tranco_index) + '_' + site.replace('http://www.','')))

        # Iframe screenshot command
        command_sequence.append_command(IframeScreenshotCommand(tranco_index, site))
        
        
        # Run commands across all browsers (simple parallelization)
        manager.execute_command_sequence(command_sequence)