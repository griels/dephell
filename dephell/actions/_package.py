from typing import List

from ..converters import PIPConverter
from ..controllers import Resolver
from ..models import Dependency


def get_packages(req: str) -> List[Dependency]:
    root = PIPConverter(lock=False).loads(req)
    return root.dependencies


def get_package(req: str) -> Dependency:
    return get_packages(req=req)[0]


def get_resolver(req: str) -> Resolver:
    return PIPConverter(lock=False).loads_resolver(req)
