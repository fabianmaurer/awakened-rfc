// External x86 dump writer. No CRT or game hooks; called only for owned runs.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

extern "C" __declspec(dllimport) LPWSTR* WINAPI CommandLineToArgvW(LPCWSTR, int*);
typedef BOOL (WINAPI *WriteDump)(HANDLE, DWORD, HANDLE, DWORD, void*, void*, void*);

extern "C" void observerDumpMain()
{
    int count = 0;
    LPWSTR* args = CommandLineToArgvW(GetCommandLineW(), &count);
    if (args == NULL || count != 3) ExitProcess(ERROR_INVALID_PARAMETER);
    DWORD pid = 0;
    for (const wchar_t* digit = args[1]; *digit; ++digit)
    {
        if (*digit < L'0' || *digit > L'9') ExitProcess(ERROR_INVALID_PARAMETER);
        pid = pid * 10 + (*digit - L'0');
    }
    if (pid == 0) ExitProcess(ERROR_INVALID_PARAMETER);
    HMODULE library = LoadLibraryW(L"dbghelp.dll");
    if (library == NULL) ExitProcess(GetLastError());
    WriteDump writeDump = (WriteDump)GetProcAddress(library, "MiniDumpWriteDump");
    if (writeDump == NULL) ExitProcess(GetLastError());
    HANDLE process = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_DUP_HANDLE, FALSE, pid);
    if (process == NULL) ExitProcess(GetLastError());
    HANDLE file = CreateFileW(args[2], GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) ExitProcess(GetLastError());
    // Includes native x86 contexts/stacks, TEBs and indirect stack memory.
    BOOL result = writeDump(process, pid, file, 0x1960, NULL, NULL, NULL);
    DWORD error = result ? ERROR_SUCCESS : GetLastError();
    CloseHandle(file);
    CloseHandle(process);
    LocalFree(args);
    ExitProcess(error ? error : (result ? 0 : ERROR_WRITE_FAULT));
}
