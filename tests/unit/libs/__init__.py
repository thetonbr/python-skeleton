# pylint: skip-file

from typing import Union

from faker import Faker
from faker.providers import internet, lorem, date_time, misc
from faker.providers.date_time import Provider as DateTimeProvider
from faker.providers.internet import Provider as InternetProvider
from faker.providers.lorem import Provider as LoremProvider
from faker.providers.misc import Provider as MiscProvider

from unittest_data_provider import data_provider

FAKE = Faker()  # type: Union[Faker, InternetProvider, LoremProvider, DateTimeProvider, MiscProvider]
FAKE.add_provider(internet)
FAKE.add_provider(lorem)
FAKE.add_provider(date_time)
FAKE.add_provider(misc)
