# Civic button artwork

Current icons are exported at 64 x 64 pixels with Pillow. Most are drawn directly
at that size; Republic, Dictatorship, Legitimacy and Military reuse scenes from the first artwork
set with darker, subdued colors. Labor uses imagegen paintings preserved in
`labor-imagegen/`; rebuilding uses these saved sources without new generation.
The original RFC civic atlas supplies the rounded corner alpha mask.

The five Government icons are drawn directly at 64 x 64 pixels by
`draw_government.py`, without an image generation service:

- Tribal System: an antlered elder and cloaked council around a forest hearth.
- Monarchy: an empty royal throne in a torchlit vaulted hall.
- Republic: a Roman senator in a white toga addressing the assembly.
- Dictatorship: a stern uniformed ruler in front of crimson banners, without armor.
- Democracy: a citizen's hand casting a ballot in a torchlit public square.

Government uses a dark fantasy palette, weathered materials, contrasting
firelight, and a mix of figures, architecture, and objects.
Religion is exported by `draw_religion.py`, with the compositions defined
in `religion_scenes.py`:

- Ancestor Cult: weathered wooden ancestor mask, feathers, beads, offerings and smoking incense in a dark grove.
- State Religion: richly vested cleric holding an ornate sacred book.
- Holy State: monumental gilded sanctuary with crimson state banners and a processional stair.
- Tolerance: cross, crescent, Star of David and Dharma wheel in four equal corners,
  representing equal state toleration without implying agreement between religions.
- State Atheism: a leather-bound Bible burning on an iron grate, representing suppression of religion.

State Religion reuses a preserved first-set portrait with subdued colors and
richer gold highlights. The other four scenes are drawn directly at 64px.

Run `.venv-art/Scripts/python.exe art/civics/draw_religion.py` to rebuild
only that column and its `religion-pixel-preview.png` contact sheet.

Military reuses the first set's detailed scenes, with subdued colors matching
the other portrait icons. `draw_military.py` exports the preserved 64px sources:

- Warrior Society: warrior with a spear and round shield.
- Militia: defender with a spear and wooden shield before town walls.
- Knighthood: armored rider with lance and horse.
- Professional Army: uniformed soldier with a musket.
- Conscription: recruiter handing a weapon to a civilian.

Run `.venv-art/Scripts/python.exe art/civics/draw_military.py` to rebuild
only that column and its `military-pixel-preview.png` contact sheet.

Labor uses five separate paintings created with the built-in imagegen tool.
`draw_labor.py` downsamples the saved `labor-imagegen/*.png` sources with Lanczos
and applies the original atlas alpha before exporting 64px DXT3 buttons.
`labor-imagegen/prompts.json` preserves the complete generation prompts.

- Self Sufficiency: a woman picking a ripe apple from a tree, with a gathering basket.
- Slavery: weathered iron manacles and chains on damp stone.
- Serfdom: wheat sheaf and iron sickle before fields and a distant manor.
- Planned Economy: folded crimson hammer-and-sickle flag above an industrial skyline.
- Market Economy: striped market awning, goods, wooden counter and gold coins.

Run `.venv-art/Scripts/python.exe art/civics/draw_labor.py` to rebuild
only that column and its `labor-pixel-preview.png` contact sheet.
The earlier procedural drawing functions remain available as artwork history;
the exporter uses the saved paintings.

Legitimacy is exported by `draw_legitimacy.py` from the preserved first-set
64px sources in `references/`, with the same subdued colors as the Government
portraits:

- Despotism: ancient ruler gripping a jeweled scepter.
- Theocracy: a priest performing a blessing.
- Plutocracy: wealthy merchant presenting gold coins.
- Nationalism: citizen carrying a wind-blown banner.
- Rule of Law: judge with scales and an open law book.

Run `.venv-art/Scripts/python.exe art/civics/draw_legitimacy.py` to rebuild
only that column and its `legitimacy-pixel-preview.png` contact sheet.

Run `.venv-art/Scripts/python.exe art/civics/draw_government.py` from the
workspace root to recreate their DXT3 textures, PNG sources, and
`government-pixel-preview.png`. The preview shows the compressed game assets.
The drawn scenes are defined in `dark_government.py`; `reuse_government.py`
grades the two preserved 64px portraits in `references/` (from commit `3581b08`).
Its Monarchy scene incorporates
the throne from `draw_monarchy.py`. All five buttons use the
original atlas's rounded corner alpha, with no added gold frame.
`draw_symbolic_civics.py` retains the earlier symbolic drawing functions for
reference; its exporter now invokes the four current category scripts instead.

To rebuild the complete set, run from the workspace root:

```powershell
.\.venv-art\Scripts\python.exe art/civics/draw_government.py
.\.venv-art\Scripts\python.exe art/civics/draw_symbolic_civics.py
```

The symbolic drawing script invokes the Legitimacy, Labor, Military and Religion exporters,
so a complete rebuild retains their current artwork. This writes the native-size `*-pixel.png` sources, the game DDS files,
`symbolic-civics-preview.png`, and the compact `preview.png` contact sheet.
Both contact sheets show the actual compressed game assets. Copy changed DDS
files to the installed mod after rebuilding the artwork.

Game assets are in `Awakened RFC/Assets/Art/Interface/Buttons/Civics/RFCMP`:
64 x 64 pixels, DXT3 DDS, with the original atlas's rounded corner alpha mask.
The civic XML uses direct DDS paths for both the civic screen and Civilopedia.
`preview.png` shows the final icons by civic column at an enlarged pixel scale.

`prepare_icons.py` and `generation.json` describe the earlier image-generation
workflow. Running that converter overwrites the symbolic buttons with its input
images. Run both drawing scripts afterward to restore the current set.
