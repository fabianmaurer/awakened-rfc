#ifndef ARFC_CAMERA_PROFILE_H
#define ARFC_CAMERA_PROFILE_H
#include "Reporting.h"

#if ARFC_ENABLE_REPORTING
// VC7.1 intrinsic: retain the caller even when the executable omits x86 frames.
extern "C" void* _ReturnAddress(void);
#pragma intrinsic(_ReturnAddress)

enum CameraMetric {
    CAMERA_DEFINE_INT, CAMERA_DEFINE_FLOAT, CAMERA_DEFINE_STRING, CAMERA_INFO_TYPE,
    CAMERA_GAME_SCRIPT, CAMERA_PLOT_SCRIPT,
    CAMERA_MAP_VISIBILITY, CAMERA_MAP_SYMBOLS, CAMERA_MAP_SYMBOL_VISIBILITY,
    CAMERA_MAP_FOG, CAMERA_PLOT_SYMBOL_DISPLAY, CAMERA_PLOT_SYMBOL_VISIBILITY,
    CAMERA_PLOT_VISIBILITY, CAMERA_PLOT_SYMBOLS, CAMERA_PLOT_FEATURE,
    CAMERA_PLOT_FEATURE_VISIBILITY, CAMERA_PLOT_IMPROVEMENT, CAMERA_PLOT_BONUS,
    CAMERA_PLOT_BUILDER, CAMERA_PLOT_LAYOUT_DIRTY, CAMERA_PLOT_FLAG_DIRTY,
    CAMERA_COLORED_PLOTS, CAMERA_BLOCKADED_PLOTS, CAMERA_GAME_UPDATE,
    CAMERA_METRIC_COUNT
};

class CameraProfileScope {
public:
    CameraProfileScope(CameraMetric metric, const char* key, void* caller);
    ~CameraProfileScope();
private:
    int m_previous, m_metric, m_entry, m_bin;
    __int64 m_start;
};
#define CAMERA_PROFILE(metric) CameraProfileScope cameraScope(metric, NULL, _ReturnAddress())
#define CAMERA_LOOKUP(metric, key) CameraProfileScope cameraScope(metric, key, _ReturnAddress())
#else
#define CAMERA_PROFILE(metric)
#define CAMERA_LOOKUP(metric, key)
#endif
#endif
