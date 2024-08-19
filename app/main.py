import asyncio
import time


from iot.devices import HueLightDevice, SmartSpeakerDevice, SmartToiletDevice
from iot.message import Message, MessageType
from iot.service import IOTService


async def main() -> None:
    # create an IOT service
    service = IOTService()

    # create and register a few devices
    hue_light = HueLightDevice()
    speaker = SmartSpeakerDevice()
    toilet = SmartToiletDevice()

    hue_light_registering = service.register_device(hue_light)
    speaker_registering = service.register_device(speaker)
    toilet_id_registering = service.register_device(toilet)

    hue_light_id, speaker_id, toilet_id = await asyncio.gather(
        hue_light_registering, speaker_registering, toilet_id_registering
    )

    # create a few programs
    # wake up programms
    speaker_tasks = service.create_tasks(
        [
            Message(speaker_id, MessageType.SWITCH_ON),
            Message(
                speaker_id,
                MessageType.PLAY_SONG,
                "Rick Astley - Never Gonna Give You Up",
            ),
        ]
    )
    hue_light_tasks = service.create_tasks(
        [
            Message(hue_light_id, MessageType.SWITCH_ON),
        ]
    )
    await service.run_parallel(
        service.run_sequence(*speaker_tasks), *hue_light_tasks
    )

    # sleep programms
    hue_light_tasks = service.create_tasks(
        [
            Message(hue_light_id, MessageType.SWITCH_OFF),
        ]
    )
    speaker_tasks = service.create_tasks(
        [
            Message(speaker_id, MessageType.SWITCH_OFF),
        ]
    )
    toilet_tasks = service.create_tasks(
        [
            Message(toilet_id, MessageType.FLUSH),
            Message(toilet_id, MessageType.CLEAN),
        ]
    )
    await service.run_parallel(
        service.run_sequence(*toilet_tasks), *hue_light_tasks, *speaker_tasks
    )

    # unregistering
    hue_light_unregistering = service.unregister_device(hue_light_id)
    speaker_unregistering = service.unregister_device(speaker_id)
    toilet_id_unregistering = service.unregister_device(toilet_id)

    await asyncio.gather(
        hue_light_unregistering, speaker_unregistering, toilet_id_unregistering
    )


if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main())
    end = time.perf_counter()

    print("Elapsed:", end - start)
