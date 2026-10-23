# Arabian and successor banners

Generated with the built-in imagegen tool; design prompts are in `prompts.json`.
The four `*-source.png` files retain the original generated artwork.
`banner-preview.png` shows decoded RGB with an approximate horizontal squeeze.
In-game feedback confirmed that the earlier horizontal compression made the
emblems too thin. The complete square sources are now fitted to 128 x 96 inside
each 128 x 128 texture, with extended background above and below. This widens
the artwork relative to its height without cropping the emblems. The exact
in-game appearance still needs user confirmation.
Rebuild all five new banners with
`.venv-art/Scripts/python.exe tools/build_banner_textures.py`.

Runtime textures live under `Awakened RFC/Assets/Art/Interface/TeamColor` as
`FlagDECAL_Arabia.dds`, `FlagDECAL_Abbasid.dds`, `FlagDECAL_Fatimid.dds`, and
`FlagDECAL_Umayyad.dds`. Each is 128 x 128, DXT3, without mipmaps, with alpha
zero throughout. Civ4 uses alpha as a team-color mask; white alpha hides the
artwork. Civilization art definitions enable full-color (white-flag) rendering.

These are distinct game designs inspired by martial and regional ornament,
rather than claims to reproduce exact historical flags.
