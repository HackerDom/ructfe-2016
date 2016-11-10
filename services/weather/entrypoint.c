#include "dispatcher.h"
#include "controlserver.h"
#include "storage.h"
#include "logging.h"
#include "types.h"

int32 main()
{
	wt_init_logging("weather.log");
	wt_init_storage("weather.db");

	wt_update_forecast_data();

	wt_run_dispatcher();
}
