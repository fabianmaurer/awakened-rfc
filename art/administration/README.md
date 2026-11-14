# Administration icon

`sealed-ledger.png` is the approved source for the administration font glyph.
It was generated with the built-in image generator: a warm ivory parchment
ledger with three dark record marks and a red wax seal, in a simple hand-painted
Civilization IV HUD style, on a transparent background.

Run `tools/build_administration_icon.py` with the existing Pillow environment
to resize and pack it into the administration `MAP_CHAR` slot in both GameFont
atlases. The other glyphs and font spacing markers remain unchanged.
