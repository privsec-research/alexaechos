from pathlib import Path

# from custom_command import LinkCountingCommand
from openwpm.voice_assistant_commands.collect_bid_status import BidStatusCollectionCommand
from openwpm.voice_assistant_commands.collect_iframe_screenshots import IframeScreenshotCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.commands.browser_commands import ScreenshotFullPageCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager
from openwpm.storage.leveldb import LevelDbProvider

# The list of sites that we wish to crawl
NUM_BROWSERS = 10


def read_file(file_addr):
    with open(file_addr) as f:
        content = f.readlines()
    return content

sites = read_file('tranco_09072021_10K.csv')

# Loads the default ManagerParams
# and NUM_BROWSERS copies of the default BrowserParams

manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
browser_params = [BrowserParams(display_mode="headless") for _ in range(NUM_BROWSERS)]

# Update browser configuration (use this for per-browser settings)
for browser_param in browser_params:
    # Record HTTP Requests and Responses
    browser_param.http_instrument = False
    # Record cookie changes
    browser_param.cookie_instrument = False
    # Record Navigations
    browser_param.navigation_instrument = False
    # Record JS Web API calls
    browser_param.js_instrument = False
    # Record the callstack of all WebRequests made
    browser_param.callstack_instrument = False
    # Record DNS resolution
    browser_param.dns_instrument = False
    browser_param.tp_cookies = "always"
    browser_param.bot_mitigation = False
    browser_param.display_mode = "headless"


# Update TaskManager configuration (use this for crawl-wide settings)
manager_params.data_directory = Path("./prebid_status/")
manager_params.log_path = Path("./prebid_status/openwpm.log")


# Commands time out by default after 60 seconds
with TaskManager(
    manager_params,
    browser_params,
    SQLiteStorageProvider(Path("./prebid_status/crawl-data.sqlite")),
    LevelDbProvider(db_path="./prebid_status/content.ldb"),
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
        )

        # print('printing visit_id', manager)
        # Start by visiting the page
        command_sequence.append_command(GetCommand(url=site, sleep=10), timeout=60)
        
        command_sequence.append_command(BidStatusCollectionCommand(tranco_index, site))
        # Run commands across all browsers (simple parallelization)
        manager.execute_command_sequence(command_sequence)
