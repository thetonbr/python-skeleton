from asyncio.events import get_event_loop
from os import getenv

TEST_LOOP = get_event_loop()

BEFORE_SCENARIO_SETUP = getenv('BEFORE_SCENARIO_SETUP', '1')
AFTER_SCENARIO_CLEAN = getenv('AFTER_SCENARIO_CLEAN', '1')
