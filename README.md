# DIY Home Assistant Devices

Version-controlled configuration for DIY ESPHome devices and their related Home Assistant configuration.

## Layout

- `esphome/devices/`: one ESPHome YAML file per device, named for the device (for example, `workshop-sensor.yaml`).
- `home-assistant/packages/`: optional Home Assistant package YAML for device-specific helpers, automations, or template entities.
- `esphome/devices/secrets.yaml`: local-only secrets for the device configs in that folder; ignored by Git.
- `home-assistant/secrets.yaml`: local-only Home Assistant secrets; ignored by Git.

Keep each device's configuration and its matching Home Assistant package easy to find by using the same device name in both directories. Commit configuration changes here, but keep credentials, tokens, and private keys in local secrets files and reference them with `!secret`.

## Adding a device

1. Add its ESPHome configuration under `esphome/devices/`.
2. Add a Home Assistant package under `home-assistant/packages/` only if the device needs configuration beyond ESPHome's automatic entity discovery.
3. Validate the ESPHome YAML with ESPHome before deploying it, then commit the configuration changes.

This repository is a source-control workspace, not a live Home Assistant configuration directory. Copy or deploy files to your Home Assistant/ESPHome installation using the workflow you already use.

## Testing the Kitchen Device

The test uses temporary dummy secrets, so it does not need your local `secrets.yaml` and never reads real credentials.

```powershell
python -m unittest discover -s tests -v
```

The test runs `esphome config` to validate the configuration without compiling or uploading firmware. To build firmware separately, run `esphome compile esphome/devices/kitchen.yaml`. To flash and view logs, use `esphome run esphome/devices/kitchen.yaml` only when you are ready to update the physical device.

To run the isolated firmware compile using temporary dummy secrets, set the opt-in flag first:

```powershell
$env:ESPHOME_TEST_COMPILE = "1"
python -m unittest discover -s tests -v
Remove-Item Env:ESPHOME_TEST_COMPILE
```

This compile may download the ESP-IDF toolchain. It does not upload firmware.

## Voice Assistant and Announcements

After the device is connected to Home Assistant, assign it to the Kitchen area and select an Assist pipeline in the device's Voice Assistant settings. The pipeline supplies speech-to-text, the conversation agent, and text-to-speech; weather answers also require a Home Assistant weather entity.

The `Kitchen Speaker` media player supports Home Assistant announcements to this device. This provides one-way announcements, not a live two-way intercom; coordinating a room-to-room call requires additional Home Assistant automation and audio routing.