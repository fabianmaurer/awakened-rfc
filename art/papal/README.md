# Papal banner

Created with the built-in imagegen tool. `banner-source.png` is the generated
source; `banner-preview.png` approximates the reported in-game horizontal squeeze:
`Awakened RFC/Assets/Art/Interface/TeamColor/FlagDECAL_Papal.dds`.
The DDS uses DXT3 compression, no mipmaps, and an entirely black alpha channel
(zero). With the Papal player's white-flag rendering setting, this displays the
texture's RGB artwork. A white alpha channel masks the entire artwork with the
team color. The PNG preview shows RGB only because alpha is a Civ4 color mask.
The complete artwork is fitted to 128 x 96 inside the 128 x 128 DDS, with
extended background above and below. This widens its proportions to counter
the horizontal squeeze reported in-game, without cropping the emblem. The
earlier 96 x 128 correction went in the wrong direction.
Rebuild with `.venv-art/Scripts/python.exe tools/build_banner_textures.py`.
See the [Civ4 flag tutorial](https://forums.civfanatics.com/threads/how-to-create-flags-for-civ4-for-dummys.315966/).

Prompt:

> Create a production game texture: a flat square heraldic banner for the Papal States in Civilization IV, medieval heraldry style, bold and legible when downscaled to 128x128 pixels. Deep crimson red field, centered large crossed keys of Saint Peter, one gold and one ivory silver, teeth at the top, round ring handles at the bottom, a small white and gold three-tier papal tiara above their crossing. Symmetric heraldic emblem with thick clear silhouettes, restrained dark outlines. Emblem occupies central 75% of image, generous red margins. Flat solid colors only, no fabric, no shadows, no 3D, no folds, no pole, no lettering, no border. Full square texture with opaque crimson background.
