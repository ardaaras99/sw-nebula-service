from datetime import datetime

from pydantic import BaseModel

from sw_nebula_service.engine import Engine


class TestNode(BaseModel):
    field_1: str
    field_2: str | None = None
    field_3: int
    field_4: int | None = None
    field_5: float
    field_6: float | None = None
    field_7: bool
    field_8: bool | None = None
    field_9: datetime
    field_10: datetime | None = None


class PersonNode(BaseModel):
    name: str
    age: int
    gender: str
    email: str
    phone: str
    address: str


def insert_n_random_nodes(engine: Engine, name_space: str, num_nodes: int):
    import random

    for i in range(num_nodes):
        node = TestNode(
            field_1=f"test_{i}",
            field_2=None,
            field_3=i,
            field_4=None,
            field_5=random.random(),  # noqa: S311
            field_6=None,
            field_7=random.choice([True, False]),  # noqa: S311
            field_8=None,
            field_9=datetime.now(),
            field_10=None,
        )
        person_node = PersonNode(
            name=f"person_{i}",
            age=random.randint(18, 100),  # noqa: S311
            gender=random.choice(["male", "female"]),  # noqa: S311
            email=f"person_{i}@example.com",
            phone=f"1234567890{i}",
            address=f"address_{i}",
        )
        engine.vertex_manager.insert_vertex(name_space=name_space, node=node, vid=i)
        engine.vertex_manager.insert_vertex(name_space=name_space, node=person_node, vid=i + 100)
