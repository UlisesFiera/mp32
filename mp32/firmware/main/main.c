
#include "mp32.h"

#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_bt_device.h"
#include "esp_bt_defs.h"
#include "esp_bt_gap.h"
#include "esp_bt_api.h"
#include "esp_a2dp_api.h"
#include "esp_gap_ble_api.h"
#include "esp_gatts_api.h"

static void init_bluetooth(void)
{
	esp_bt_controller_config_t bt_cfg =
		BT_CONTROLLER_INIT_CONFIG_DEFAULT();

	ESP_ERROR_CHECK(esp_bt_controller_init(&bt_cfg));

	ESP_ERROR_CHECK(
		esp_bt_controller_enable(ESP_BT_MODE_BTDM));

	ESP_ERROR_CHECK(esp_bluedroid_init());
	ESP_ERROR_CHECK(esp_bluedroid_enable());
}

void app_main(void)
{
	ESP_ERROR_CHECK(nvs_flash_init());

	init_bluetooth();

	// Register BLE callbacks and initialize your BLE GATT server.

	// Register Classic Bluetooth callbacks and initialize A2DP.
}
