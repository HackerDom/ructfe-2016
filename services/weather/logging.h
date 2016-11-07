#pragma once

void wt_init_logging(const char *filename);

void wt_log_info(const char *format, ...);
void wt_log_warn(const char *format, ...);
void wt_log_error(const char *format, ...);