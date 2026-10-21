"""Build capability only; ordinary games never import the reporting machinery."""
from CvPythonExtensions import CyGame

ENABLED = CyGame().isReportingEnabled()
