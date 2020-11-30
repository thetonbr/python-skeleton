from aiocli.commander import Application, run_app

from project.apps.cli.controllers.example.example_router import example_router
from project.apps.settings import container, env

app = Application(
    name=env(key='name', typ=str),
    version=env(key='version', typ=str),
    on_startup=[lambda _: container()],  # to avoid event_loop issues with third parties
    on_shutdown=[lambda _: container().get('services.shutdown')()],
)

app.include_router(example_router)


def main() -> None:
    run_app(app)
