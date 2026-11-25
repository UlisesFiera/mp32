#ifndef MP32_H
# define MP32_H

# include <string.h>

# include "esp_log.h"
# include "esp_nimble_hci.h"
# include "host/ble_hs.h"
# include "nimble/nimble_port.h"
# include "nimble/nimble_port_freertos.h"
# include "nvs_flash.h"

typedef struct  mp32_data_s 
{
    static const char   *tag;
    static const char   *name;
    static uint8_t      addr_type;
} mp32_data_t;

#endif
