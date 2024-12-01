from punq import Container, Scope

from app.repositories.tariff_repository import TariffRepo
from app.routers.rate_router import TariffRouter
from app.services.tariff_service import TariffService
from app.settings import AppConfig
from app.utils.db import Db, DbConfig


def bootstrap(app_config: AppConfig) -> Container:
    container = Container()
    container.register(AppConfig, instance=app_config)
    container.register(DbConfig, instance=app_config.bd, scope=Scope.singleton)
    container.register(Db, Db, scope=Scope.singleton)

    container.register(TariffRepo)
    container.register(TariffService)
    container.register(TariffRouter)

    # container.register(TaskRepo)
    # container.register(TasksServie)
    # container.register(TaskRouter)
    #
    # container.register(ProductRepo)
    # container.register(ProductService)
    # container.register(ProductRouter)
    #
    # container.register(UserRepo)
    # container.register(UserService)
    # container.register(UserRouter)
    #
    # container.register(AuthRouter)

    return container
