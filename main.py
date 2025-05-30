import asyncio
from services.factory import ServiceFactory


async def main():
    calendar_service = ServiceFactory.create_calendar_service()
    ui = await ServiceFactory.create_user_interface(calendar_service)

    try:
        await ui.start()
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(ui, 'stop'):
            await ui.stop()


if __name__ == '__main__':
    asyncio.run(main())
