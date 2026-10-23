#ifndef ARFC_REPORTING_H
#define ARFC_REPORTING_H

// Opt in with ARFC_ENABLE_REPORTING=1 in the legacy Makefile environment/settings.
#ifndef ARFC_ENABLE_REPORTING
#define ARFC_ENABLE_REPORTING 0
#endif
#if ARFC_ENABLE_REPORTING != 0 && ARFC_ENABLE_REPORTING != 1
#error ARFC_ENABLE_REPORTING must be 0 or 1
#endif

#endif
