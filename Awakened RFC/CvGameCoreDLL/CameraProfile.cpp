#include "CvGameCoreDLL.h"
#include "CameraProfile.h"

#if ARFC_ENABLE_REPORTING
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

namespace {
    const int BIN_COUNT = 3500; // 70 seconds at 20 ms, beyond the launcher's limit.
    const int ENTRY_COUNT = 4096;
    const LONG CONTROL_MAGIC = 0x43414d31;
    struct Control { volatile LONG command; LONG magic; };
    struct Timing { unsigned int samples; __int64 ticks, maximum; };
    struct Entry {
        unsigned int hash; int metric, parent; void* caller;
        char key[128]; Timing timing;
    };
    const char* names[] = {
        "CvGlobals.getDefineINT", "CvGlobals.getDefineFLOAT", "CvGlobals.getDefineSTRING", "CvGlobals.getInfoTypeForString",
        "CvGame.getScriptData", "CvPlot.getScriptData", "CvMap.updateVisibility", "CvMap.updateSymbols",
        "CvMap.updateSymbolVisibility", "CvMap.updateFog", "CvPlot.updateSymbolDisplay", "CvPlot.updateSymbolVisibility",
        "CvPlot.updateVisibility", "CvPlot.updateSymbols", "CvPlot.updateFeatureSymbol", "CvPlot.updateFeatureSymbolVisibility",
        "CvPlot.getVisibleImprovementState", "CvPlot.getVisibleBonusState", "CvPlot.shouldUsePlotBuilder",
        "CvPlot.isLayoutDirty", "CvPlot.isFlagDirty", "CvGame.updateColoredPlots", "CvGame.updateBlockadedPlots", "CvGame.update"
    };
    bool initialized = false, started = false;
    Control* control = NULL;
    HANDLE mapping = NULL;
    DWORD owner = 0;
    char output[MAX_PATH] = "";
    __int64 frequency = 0, epoch = 0;
    int parent = -1, depth = 0;
    unsigned int calls[CAMERA_METRIC_COUNT] = {0};
    unsigned int droppedEntries = 0;
    Timing* bins = NULL;
    Entry* entries = NULL;

    unsigned int stride(int metric) {
        if (metric <= CAMERA_INFO_TYPE || metric == CAMERA_PLOT_LAYOUT_DIRTY || metric == CAMERA_PLOT_FLAG_DIRTY) return 64;
        if (metric >= CAMERA_PLOT_SYMBOL_DISPLAY && metric <= CAMERA_PLOT_BUILDER) return 16;
        return 1;
    }
    void initialize() {
        initialized = true;
        char name[128];
        DWORD length = GetEnvironmentVariableA("ARFC_CAMERA_PROFILE_CONTROL", name, sizeof(name));
        if (!length || length >= sizeof(name)) return;
        length = GetEnvironmentVariableA("ARFC_CAMERA_PROFILE_LOG", output, sizeof(output));
        if (!length || length >= sizeof(output)) return;
        mapping = OpenFileMappingA(FILE_MAP_ALL_ACCESS, FALSE, name);
        if (!mapping) return;
        control = (Control*)MapViewOfFile(mapping, FILE_MAP_ALL_ACCESS, 0, 0, sizeof(Control));
        if (!control || control->magic != CONTROL_MAGIC) {
            if (control) UnmapViewOfFile(control);
            CloseHandle(mapping); mapping = NULL; control = NULL; return;
        }
        LARGE_INTEGER value;
        if (!QueryPerformanceFrequency(&value)) { control = NULL; return; }
        frequency = value.QuadPart;
        bins = (Timing*)calloc(BIN_COUNT * CAMERA_METRIC_COUNT, sizeof(Timing));
        entries = (Entry*)calloc(ENTRY_COUNT, sizeof(Entry));
        if (!bins || !entries) { control->command = -1; control = NULL; return; }
        owner = GetCurrentThreadId();
    }
    void add(Timing& target, __int64 ticks) {
        ++target.samples; target.ticks += ticks;
        if (ticks > target.maximum) target.maximum = ticks;
    }
    void flush() {
        FILE* file = fopen(output, "w");
        if (!file) { control->command = -1; return; }
        fprintf(file, "# camera_profile_v1,pid=%lu,thread=%lu,frequency=%I64d,module_base=0x%08lx,dropped_entries=%u\n",
            GetCurrentProcessId(), owner, frequency, (unsigned long)GetModuleHandleA("CvGameCoreDLL.dll"), droppedEntries);
        fprintf(file, "record,metric,parent,key,caller,bin_start_ms,calls,samples,sample_stride,total_sample_ms,max_sample_ms\n");
        for (int metric = 0; metric < CAMERA_METRIC_COUNT; ++metric) {
            fprintf(file, "calls,%s,,,,,%u,,%u,,\n", names[metric], calls[metric], stride(metric));
            for (int bin = 0; bin < BIN_COUNT; ++bin) {
                Timing& t = bins[bin * CAMERA_METRIC_COUNT + metric];
                if (t.samples) fprintf(file, "bin,%s,,,,%d,,%u,%u,%.6f,%.6f\n", names[metric], bin * 20,
                    t.samples, stride(metric), 1000.0 * t.ticks / frequency, 1000.0 * t.maximum / frequency);
            }
        }
        for (int i = 0; i < ENTRY_COUNT; ++i) {
            Entry& e = entries[i]; if (!e.hash) continue;
            fprintf(file, "site,%s,%s,\"%s\",0x%08lx,,,%u,%u,%.6f,%.6f\n", names[e.metric],
                e.parent < 0 ? "external" : names[e.parent], e.key, (unsigned long)e.caller,
                e.timing.samples, stride(e.metric), 1000.0 * e.timing.ticks / frequency, 1000.0 * e.timing.maximum / frequency);
        }
        if (fclose(file) != 0) control->command = -1;
        else control->command = 3; // Acknowledge only after the CSV is closed.
    }
    int entryFor(int metric, int callerParent, const char* key, void* caller) {
        unsigned int hash = ((unsigned int)caller >> 4) ^ (metric * 16777619U) ^ (callerParent + 1);
        const char* text = key ? key : "";
        for (const char* p = text; *p; ++p) hash = (hash ^ (unsigned char)*p) * 16777619U;
        if (!hash) hash = 1;
        int index = hash & (ENTRY_COUNT - 1);
        for (int count = 0; count < ENTRY_COUNT; ++count, index = (index + 1) & (ENTRY_COUNT - 1)) {
            Entry& e = entries[index];
            if (!e.hash) {
                e.hash = hash; e.metric = metric; e.parent = callerParent; e.caller = caller;
                strncpy(e.key, text, sizeof(e.key) - 1);
                // Keep the diagnostic CSV valid even for unexpected user strings.
                for (char* p = e.key; *p; ++p) if (*p == '"' || *p == '\r' || *p == '\n') *p = '_';
                return index;
            }
            if (e.hash == hash && e.metric == metric && e.parent == callerParent && e.caller == caller) return index;
        }
        ++droppedEntries; return -1;
    }
}

CameraProfileScope::CameraProfileScope(CameraMetric metric, const char* key, void* caller) :
    m_previous(-2), m_metric(metric), m_entry(-1), m_bin(-1), m_start(0) {
    if (!initialized) initialize();
    if (!control || GetCurrentThreadId() != owner) return;
    if (control->command == 2 && depth == 0) { flush(); return; }
    if (control->command != 1) return;
    if (!started) {
        LARGE_INTEGER value; QueryPerformanceCounter(&value); epoch = value.QuadPart; started = true;
    }
    m_previous = parent; ++depth;
    if (metric >= CAMERA_MAP_VISIBILITY) parent = metric;
    unsigned int count = ++calls[metric];
    // Scramble the counter so repeated key/callback order cannot alias a fixed stride.
    unsigned int selection = count * 2654435761U;
    if (stride(metric) == 64 && (selection >> 26) != 0) return;
    if (stride(metric) == 16 && (selection >> 28) != 0) return;
    m_entry = entryFor(metric, m_previous, key, caller);
    LARGE_INTEGER value; QueryPerformanceCounter(&value); m_start = value.QuadPart;
    m_bin = (int)((m_start - epoch) * 50 / frequency);
    if (m_bin >= BIN_COUNT) m_bin = -1;
}

CameraProfileScope::~CameraProfileScope() {
    if (m_previous == -2) return;
    if (m_start) {
        LARGE_INTEGER value; QueryPerformanceCounter(&value);
        __int64 ticks = value.QuadPart - m_start;
        if (m_bin >= 0) add(bins[m_bin * CAMERA_METRIC_COUNT + m_metric], ticks);
        if (m_entry >= 0) add(entries[m_entry].timing, ticks);
    }
    parent = m_previous; --depth;
}
#endif
