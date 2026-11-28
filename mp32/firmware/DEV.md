**Flash program's documentation:**

1. esp_log.h — ESP-IDF Logging Library

2. esp_nimble_hci.h — ESP-IDF NimBLE API

3. host/ble_hs.h — Apache NimBLE Host API

4. nimble/nimble_port.h — ESP-IDF NimBLE Port API

5. nimble/nimble_port_freertos.h — ESP-IDF NimBLE FreeRTOS Integration

6. nvs_flash.h — ESP-IDF NVS Flash API

**Bluetooth types:**    
    BLE GATT: Supports bidirectional data exchange with both iOS and macOS through native APIs. No MFi certification required.

    Bluetooth Classic SPP: Useful for serial data communication with compatible computers, but not generally accessible to third-party iOS applications.

    Bluetooth Classic A2DP: Audio streaming, not general-purpose data exchange.

**What is GAP?**
GAP stands for Generic Access Profile.

In Bluetooth Classic, GAP handles things such as:
- Device discovery.
- Device visibility.
- Connection-related events.
- Authentication and pairing.
- Encryption.

So GAP is the layer responsible for how Bluetooth devices find each other and establish relationships.

**What is A2DP?**
It's the BT profile we will use for audio transmission.

**What is AVRCP?**
It's the BT profile we will use for managing controllers (play, pause, etc.).

**What is NVS?**
NVS means Non-Volatile Storage.

It's a persistent key-value storage system used by ESP-IDF components, including Bluetooth functionality.

It allows information to survive power cycles.