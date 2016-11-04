#include "client/linux/handler/exception_handler.h"
#include <stdio.h>


//
static bool dumpCallback( const google_breakpad::MinidumpDescriptor& descriptor, void* context, bool succeeded ) {
  printf("%s", descriptor.path());
  fflush (stdout);
  return succeeded;
}


//
int main( int argc, char* argv[] ) {
  google_breakpad::MinidumpDescriptor descriptor("./");
  google_breakpad::ExceptionHandler eh(descriptor, NULL, dumpCallback, NULL, true, -1);

  volatile int* ptr = 0;
  *ptr = 0;

  return 0;
}

