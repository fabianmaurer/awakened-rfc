"""Local exception UI; never queue a popup or change synchronized game state.

Compatible with the game's Python 2.4 interpreter.
"""
import os
import sys
import tempfile
import traceback

import CvUtil
from CvPythonExtensions import *

SCREEN_ID = 101
_muted = False
_handling = False
_log_path = None
help_widget = None
_last_error = None
_repeat_count = 0


def screen():
    return CyGInterfaceScreen("AwakenedDebugExceptions", SCREEN_ID)


def dismiss():
    global _muted
    _muted = True
    screen().hideScreen()


def shortcut(key, ctrl, shift):
    if ctrl and shift and key == int(InputTypes.KB_F12):
        dismiss()
        return True
    return False


def _log(message):
    global _log_path
    # A writable location even when the mod is installed under Program Files.
    # Keep a dedicated log because sending stderr to the engine creates popups.
    if _log_path is None:
        _log_path = os.path.join(tempfile.gettempdir(), "AwakenedRFC-PythonErrors.log")
    handle = open(_log_path, "ab")
    try:
        handle.write(message.encode("utf-8", "replace"))
    finally:
        handle.close()


def exceptHook(errorType, value, tb):
    global _handling, _last_error, _repeat_count
    message = u"".join([CvUtil.convertToUnicode(line) for line in
                        traceback.format_exception(errorType, value, tb)])
    frame = tb
    while frame is not None:
        if frame.tb_frame.f_code.co_name == "updateHelpStrings":
            message += u"Last hovered widget: %s\n" % (help_widget,)
            break
        frame = frame.tb_next
    # Tooltip failures can recur on every frame. Keep the first full traceback
    # and exponentially spaced repeat counts rather than flooding both logs.
    logged_message = message
    if message == _last_error:
        _repeat_count += 1
        if _repeat_count & (_repeat_count - 1):
            logged_message = None
        else:
            logged_message = u"Previous exception repeated %d times.\n" % _repeat_count
    else:
        _last_error = message
        _repeat_count = 0
    if logged_message is not None:
        sys.stdout.write(logged_message.encode("utf-8", "replace"))
        try:
            _log(logged_message)
        except Exception:
            pass  # The engine debug stream still has the traceback.
    if _handling or _muted or not CvUtil.SHOWEXCEPTIONS:
        return
    _handling = True
    try:
        _show(message)
    finally:
        _handling = False


def _show(message):
    try:
        if CyGame().isPitbossHost() or CyGame().isObserverAutoPlay():
            return
        ui = screen()
        if ui.isActive():
            return  # Keep the first traceback visible; do not queue more dialogs.
        text = CyTranslator()
        width = min(760, ui.getXResolution() - 40)
        height = min(540, ui.getYResolution() - 40)
        ui.setDimensions((ui.getXResolution() - width) / 2,
                         (ui.getYResolution() - height) / 2, width, height)
        ui.setRenderInterfaceOnly(True)
        ui.showWindowBackground(False)
        ui.addPanel("ErrorPanel", "", "", True, False, 0, 0, width, height,
                    PanelStyles.PANEL_STYLE_MAIN)
        ui.setLabel("ErrorTitle", "", text.getText("TXT_KEY_DEBUG_ERROR_TITLE", ()),
                    CvUtil.FONT_CENTER_JUSTIFY, width / 2, 18, 0,
                    FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        # Escape markup in tracebacks before passing them to the engine renderer.
        body = message.replace(u"<", u"[").replace(u">", u"]")[-12000:]
        ui.addMultilineText("ErrorTraceback", body, 20, 55, width - 40, height - 170,
                            WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
        ui.addMultilineText("ErrorHint", text.getText("TXT_KEY_DEBUG_ERROR_HINT", ()),
                            20, height - 105, width - 40, 50,
                            WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
        ui.setButtonGFC("DismissErrors", text.getText("TXT_KEY_DEBUG_ERROR_DISMISS", ()),
                        "", width / 2 - 140, height - 48, 280, 30,
                        WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)
        ui.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
    except Exception:
        # An error in diagnostic UI must not recursively create engine popups.
        sys.stdout.write("Awakened RFC: could not display exception window.\n")


def handleInput(inputClass):
    if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CHARACTER:
        if inputClass.getData() in (int(InputTypes.KB_ESCAPE), int(InputTypes.KB_RETURN)):
            dismiss()
            return 1
        if shortcut(inputClass.getData(), inputClass.isCtrlKeyDown(), inputClass.isShiftKeyDown()):
            return 1
    if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and
            inputClass.getFunctionName() == "DismissErrors"):
        dismiss()
        return 1
    return 0


def update(delta):
    pass


def install():
    # CvAppInterface also assigns this hook during initialization.
    CvUtil.myExceptHook = exceptHook
    sys.excepthook = exceptHook
