import asyncio
from services.factory import ServiceFactory


async def main():
    # Создаем сервис календаря
    calendar_service = ServiceFactory.create_calendar_service()

    # Создаем пользовательский интерфейс
    ui = await ServiceFactory.create_user_interface(calendar_service)

    # Запускаем
    await ui.start()


if __name__ == '__main__':
    asyncio.run(main())