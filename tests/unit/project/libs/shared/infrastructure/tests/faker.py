# pylint: skip-file

from typing import Union

from faker import Faker
from faker.providers import date_time, file, geo, internet, lorem, misc, phone_number
from faker.providers.date_time import Provider as DateTimeProvider
from faker.providers.file import Provider as FileProvider
from faker.providers.geo import Provider as GeoProvider
from faker.providers.internet import Provider as InternetProvider
from faker.providers.lorem import Provider as LoremProvider
from faker.providers.misc import Provider as MiscProvider
from faker.providers.phone_number import Provider as PhoneProvider

FakerProvider = Union[
    DateTimeProvider,
    FileProvider,
    GeoProvider,
    InternetProvider,
    LoremProvider,
    MiscProvider,
    PhoneProvider,
]

FAKE = Faker()  # type: Union[Faker, FakerProvider]
FAKE.add_provider(date_time)
FAKE.add_provider(file)
FAKE.add_provider(geo)
FAKE.add_provider(internet)
FAKE.add_provider(lorem)
FAKE.add_provider(misc)
FAKE.add_provider(phone_number)
