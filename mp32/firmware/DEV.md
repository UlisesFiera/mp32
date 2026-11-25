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