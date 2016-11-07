#include "client/linux/handler/exception_handler.h"
#include <stdio.h>


//
static bool dumpCallback( const google_breakpad::MinidumpDescriptor& descriptor, void* context, bool succeeded ) {
  printf("%s", descriptor.path());
  fflush (stdout);
  return succeeded;
}


//
void _EQUAL();
void _0();
void _1();
void _2();
void _3();
void _4();
void _5();
void _6();
void _7();
void _8();
void _9();
void _A();
void _B();
void _C();
void _D();
void _E();
void _F();
void _G();
void _H();
void _I();
void _J();
void _K();
void _L();
void _M();
void _N();
void _O();
void _P();
void _Q();
void _R();
void _S();
void _T();
void _U();
void _V();
void _W();
void _X();
void _Y();
void _Z();
void _a();
void _b();
void _c();
void _d();
void _e();
void _f();
void _g();
void _h();
void _i();
void _j();
void _k();
void _l();
void _m();
void _n();
void _o();
void _p();
void _q();
void _r();
void _s();
void _t();
void _u();
void _v();
void _w();
void _x();
void _y();
void _z();


//
typedef void (*VoidFunc)();
VoidFunc g_funcPtrs[] = 
    { &_0, &_1, &_2, &_3, &_4, &_5, &_6, &_7, &_8, &_9, 
      &_A, &_B, &_C, &_D, &_E, &_F, &_G, &_H, &_I, &_J, 
      &_K, &_L, &_M, &_N, &_O, &_P, &_Q, &_R, &_S, &_T, 
      &_U, &_V, &_W, &_X, &_Y, &_Z, 
  	  &_a, &_b, &_c, &_d, &_e, &_f, &_g, &_h, &_i, &_j, 
      &_k, &_l, &_m, &_n, &_o, &_p, &_q, &_r, &_s, &_t, 
      &_u, &_v, &_w, &_x, &_y, &_z, &_EQUAL };


//
int g_flagSymbolIdx = 0;
const int FLAG_LEN = 32;
char* g_flagPtr = nullptr;      

//
#define PROCESS_SYMBOL()\
	char localStorage[ 256 ] = { 0 };\
	if( g_flagSymbolIdx == 16 ){\
		strcpy( localStorage, "HERE IS THE REST OF YOUR FLAG=" );\
		int len = strlen( localStorage );\
		strncpy( localStorage + len, &g_flagPtr[ g_flagSymbolIdx ], 16 );\
		memset( g_flagPtr, 0, FLAG_LEN );\
		volatile int* ptr = 0;\
		*ptr = 0;\
	}\
	\
	char symbol = g_flagPtr[ g_flagSymbolIdx ];\
	int funcIdx = 0;\
	if( isdigit( symbol ) )\
		funcIdx = symbol - 0x30;\
	if( isalpha( symbol ) )\
		if( symbol < 0x5B )\
			funcIdx = symbol - 0x41 + 10;\
		else\
			funcIdx = symbol - 0x61 + 36;\
	if( symbol == '=' ) \
		funcIdx = sizeof( g_funcPtrs ) / sizeof( VoidFunc ) - 1;\
	\
	g_flagSymbolIdx++;\
	g_funcPtrs[ funcIdx ]();


//
void _EQUAL(){ PROCESS_SYMBOL() }
void _0(){ PROCESS_SYMBOL() }
void _1(){ PROCESS_SYMBOL() }
void _2(){ PROCESS_SYMBOL() }
void _3(){ PROCESS_SYMBOL() }
void _4(){ PROCESS_SYMBOL() }
void _5(){ PROCESS_SYMBOL() }
void _6(){ PROCESS_SYMBOL() }
void _7(){ PROCESS_SYMBOL() }
void _8(){ PROCESS_SYMBOL() }
void _9(){ PROCESS_SYMBOL() }
void _A(){ PROCESS_SYMBOL() }
void _B(){ PROCESS_SYMBOL() }
void _C(){ PROCESS_SYMBOL() }
void _D(){ PROCESS_SYMBOL() }
void _E(){ PROCESS_SYMBOL() }
void _F(){ PROCESS_SYMBOL() }
void _G(){ PROCESS_SYMBOL() }
void _H(){ PROCESS_SYMBOL() }
void _I(){ PROCESS_SYMBOL() }
void _J(){ PROCESS_SYMBOL() }
void _K(){ PROCESS_SYMBOL() }
void _L(){ PROCESS_SYMBOL() }
void _M(){ PROCESS_SYMBOL() }
void _N(){ PROCESS_SYMBOL() }
void _O(){ PROCESS_SYMBOL() }
void _P(){ PROCESS_SYMBOL() }
void _Q(){ PROCESS_SYMBOL() }
void _R(){ PROCESS_SYMBOL() }
void _S(){ PROCESS_SYMBOL() }
void _T(){ PROCESS_SYMBOL() }
void _U(){ PROCESS_SYMBOL() }
void _V(){ PROCESS_SYMBOL() }
void _W(){ PROCESS_SYMBOL() }
void _X(){ PROCESS_SYMBOL() }
void _Y(){ PROCESS_SYMBOL() }
void _Z(){ PROCESS_SYMBOL() }
void _a(){ PROCESS_SYMBOL() }
void _b(){ PROCESS_SYMBOL() }
void _c(){ PROCESS_SYMBOL() }
void _d(){ PROCESS_SYMBOL() }
void _e(){ PROCESS_SYMBOL() }
void _f(){ PROCESS_SYMBOL() }
void _g(){ PROCESS_SYMBOL() }
void _h(){ PROCESS_SYMBOL() }
void _i(){ PROCESS_SYMBOL() }
void _j(){ PROCESS_SYMBOL() }
void _k(){ PROCESS_SYMBOL() }
void _l(){ PROCESS_SYMBOL() }
void _m(){ PROCESS_SYMBOL() }
void _n(){ PROCESS_SYMBOL() }
void _o(){ PROCESS_SYMBOL() }
void _p(){ PROCESS_SYMBOL() }
void _q(){ PROCESS_SYMBOL() }
void _r(){ PROCESS_SYMBOL() }
void _s(){ PROCESS_SYMBOL() }
void _t(){ PROCESS_SYMBOL() }
void _u(){ PROCESS_SYMBOL() }
void _v(){ PROCESS_SYMBOL() }
void _w(){ PROCESS_SYMBOL() }
void _x(){ PROCESS_SYMBOL() }
void _y(){ PROCESS_SYMBOL() }
void _z(){ PROCESS_SYMBOL() }


//
void StartFlagProcessing()
{
	PROCESS_SYMBOL()
}


//
void Execute() // dummy fucntion
{

}


//
int main( int argc, char* argv[] ) {
  google_breakpad::MinidumpDescriptor descriptor("dumps");
  google_breakpad::ExceptionHandler eh(descriptor, NULL, dumpCallback, NULL, true, -1);

  g_flagSymbolIdx = 0;
  g_flagPtr = argv[ 1 ];
  StartFlagProcessing();

  return 0;
}
