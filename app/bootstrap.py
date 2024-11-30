from punq import Container, Scope

from app.repositories.rate_repository import RateRepo
from app.routers.rate_router import RateRouter
from app.services.rate_service import RateService
from app.settings import AppConfig
from app.utils.db import Db, DbConfig


def bootstrap(app_config: AppConfig) -> Container:
    container = Container()
    container.register(AppConfig, instance=app_config)
    container.register(DbConfig, instance=app_config.bd, scope=Scope.singleton)
    container.register(Db, Db, scope=Scope.singleton)

    container.register(RateRepo)
    container.register(RateService)
    container.register(RateRouter)

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
