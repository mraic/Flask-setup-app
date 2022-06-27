import pytest
from faker import Faker

from src import Sale


@pytest.fixture(scope = "class")
def dummy_sale(request):
    fake = Faker()

    request.cls.dummy_sale = Sale(
        id = fake.uuid4(),
        buyer_id = fake.uuid4(),
        property_id = fake.uuid4()
    )

    return request.cls.dummy_sale