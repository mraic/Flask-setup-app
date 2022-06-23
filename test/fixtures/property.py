import pytest
from faker import Faker

from src import Property


@pytest.fixture(scope="class")
def dummy_property(request):
    fake = Faker()

    request.cls.dummy_property = Property(
        address = fake.address(),
        price = fake.random_int(min=1, max=95000),
        living_area = fake.random_int(min=1, max=100),
        owner_id = fake.uuid4()
    )

    return request.cls.dummy_property