import pytest
from faker import Faker

from src import Activity


@pytest.fixture(scope="class")
def dummy_activity(request):

    fake = Faker()

    request.cls.dummy_activity = Activity(
        duration = fake.time('%S') ,
        path = fake.pystr(),
        user_id = fake.uuid4()
    )

    return request.cls.dummy_activity