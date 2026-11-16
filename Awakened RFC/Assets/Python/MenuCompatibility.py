"""Local, launch-time gameplay fingerprint; Python 2.4 compatible."""
import os
import sha

from CvPythonExtensions import (CyGInterfaceScreen, CyInterface, CyGame,
                                FontTypes, HitTestTypes, PopupStates, WidgetTypes)
import CvUtil

SCREEN_ID = 102
_fingerprint = None
_resolution = None


def fingerprint(root):
    global _fingerprint
    if _fingerprint is not None:
        return _fingerprint
    # Civ4's custom importer does not provide a normal filesystem __file__.
    root = os.path.normpath(os.path.abspath(root))
    paths = ["Assets/CvGameCoreDLL.dll"]
    for folder, suffixes in (("Assets/Python", (".py",)),
                             ("Assets/XML", (".xml",)),
                             ("PublicMaps", (".py", ".civbeyondswordwbsave"))):
        for directory, dirs, files in os.walk(os.path.join(root, folder)):
            dirs[:] = [name for name in dirs if not name.startswith(".")
                       and name not in ("__pycache__", "_rollback-backup")]
            for name in files:
                if os.path.splitext(name)[1].lower() in suffixes:
                    path = os.path.join(directory, name)[len(root) + 1:]
                    paths.append(path.replace("\\", "/"))
    paths.sort()
    digest = sha.new()
    try:
        for path in paths:
            handle = open(os.path.join(root, path), "rb")
            try:
                data = handle.read()
            finally:
                handle.close()
            # Git checkouts and ZIP installs can have different line endings.
            if not path.lower().endswith(".dll"):
                data = data.replace("\r\n", "\n").replace("\r", "\n")
            digest.update(path.lower() + "\0" + sha.new(data).digest())
        _fingerprint = digest.hexdigest()[:12]
    except (IOError, OSError):
        # Never present an incomplete hash as a successful compatibility check.
        _fingerprint = "?"
    return _fingerprint


def show(root):
    """Called by the native menu, independently of gameplay event updates."""
    global _resolution
    if CyGame().isPitbossHost():
        return
    screen = CyGInterfaceScreen("MenuCompatibility", SCREEN_ID)
    resolution = (screen.getXResolution(), screen.getYResolution())
    if screen.isActive() and _resolution == resolution:
        return
    _resolution = resolution
    screen.setDimensions(resolution[0] - 200, 30, 200, 28)
    screen.setPersistent(True)
    screen.showWindowBackground(False)
    screen.setRenderInterfaceOnly(False)
    screen.setLabel("CompatibilityHash", "", u"<font=1>%s</font>" % fingerprint(root),
                    CvUtil.FONT_RIGHT_JUSTIFY, 190, 0, -0.1,
                    FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
    screen.setHitTest("CompatibilityHash", HitTestTypes.HITTEST_NOHIT)
    # The second argument passes input through to the native menu.
    screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, True)


def update(delta):
    if not CyInterface().isInMainMenu():
        CyGInterfaceScreen("MenuCompatibility", SCREEN_ID).hideScreen()


def handleInput(inputClass):
    return 0
