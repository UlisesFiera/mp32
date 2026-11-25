
#include "mp32.h"

static const char *TAG = "MP32_BT";

static void gap_callback(
	esp_bt_gap_cb_event_t event,
	esp_bt_gap_cb_param_t *param)
{
	switch (event)
	{
		case ESP_BT_GAP_CONFIG_EIR_DATA_EVT:
			ESP_LOGI(TAG, "EIR configuration completed");
			break;
		case ESP_BT_GAP_AUTH_CMPL_EVT:
			ESP_LOGI(TAG, "Authentication completed: status=%d, name=%s",
					param->auth_cmpl.stat,
					param->auth_cmpl.device_name);
			break;
		case ESP_BT_GAP_ENC_CHG_EVT:
			ESP_LOGI(TAG, "Encryption changed: status=%d, enabled=%d",
					param->enc_chg.enc_mode,
					param->enc_chg.enc_mode);
			break;
		case ESP_BT_GAP_ACL_CONN_CMPL_STAT_EVT:
			ESP_LOGI(TAG, "ACL connection completed");
			break;
		case ESP_BT_GAP_ACL_DISCONN_CMPL_STAT_EVT:
			ESP_LOGI(TAG, "ACL connection disconnected");
			break;
		default:
			ESP_LOGI(TAG, "Unhandled GAP event: %d", event);
			break;
	}
}

static void init_bluetooth(void)
{
	esp_bt_controller_config_t	bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();

	ESP_ERROR_CHECK(esp_bt_controller_init(&bt_cfg));
	ESP_ERROR_CHECK(esp_bt_controller_enable(ESP_BT_MODE_BTDM));
	ESP_ERROR_CHECK(esp_bluedroid_init());
	ESP_ERROR_CHECK(esp_bluedroid_enable());
	ESP_ERROR_CHECK(esp_bt_gap_register_callback(gap_callback));
	ESP_ERROR_CHECK(esp_bt_gap_set_device_name("MP32"));
	ESP_ERROR_CHECK(esp_bt_gap_set_scan_mode(ESP_BT_CONNECTABLE, ESP_BT_GENERAL_DISCOVERABLE));
	ESP_LOGI(TAG, "Bluetooth Classic initialized");
	ESP_LOGI(TAG, "Device name: MP32");
}

void app_main(void)
{
	ESP_ERROR_CHECK(nvs_flash_init());
	init_bluetooth();
	while (1)
	{
		vTaskDelay(pdMS_TO_TICKS(1000));
	}
}
