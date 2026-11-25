#ifndef MP32_H
# define MP32_H
 
# include <string.h>

# include "freertos/FreeRTOS.h"
# include "freertos/task.h"

# include "esp_log.h"
# include "esp_err.h"

# include "esp_bt.h"
# include "esp_bt_main.h"
# include "esp_bt_device.h"
# include "esp_bt_defs.h"
# include "esp_gap_bt_api.h"
# include "esp_a2dp_api.h"
# include "esp_gap_ble_api.h"
# include "esp_gatts_api.h"
# include "nvs_flash.h"

typedef struct mp32_data_s
{
    const char *tag;
    const char *name;
    uint8_t addr_type;
} mp32_data_t;

#endif
