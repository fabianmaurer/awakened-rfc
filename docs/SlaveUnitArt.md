# Slave unit models

Slave units use their own NIF files and art definitions. Each group contains
three figures of variant A and two of variant B, with different earth-tone
material tints and slightly different scales. Irregular formations offset
their positions and allow more variation in facing direction.

All eight tiers share the base slave's bare-chested body, hair, face and
rough clothing. The mesh is skinned to each weapon donor's skeleton, with
rebuilt inverse bind matrices; it is not a rigid attachment. This preserves
walking, fighting, firing and death animations without adding regular uniforms.

| Tier | Equipment and animation rig |
| --- | --- |
| Unarmed | Warrior rig, with the club removed. |
| Bronze | Middle Eastern axeman's axe and animations. |
| Iron | Swordsman's sword and animations, without the shield or armor. |
| Maces | Standard Maceman's flail, including its skinned chain and ball, and matching animations. |
| Muskets | American Revolution militia musket and firing animations. |
| Rifles | Dawn of Civilization Armed Pioneer's long firearm and Oromo animations. |
| Infantry | Standard Infantry's Springfield rifle and matching animations. |
| Modern | Standard Marine's automatic rifle, animated magazine and matching animations. |

Weapons remain parented to their original animated nodes, including
detachable magazines and any falling-weapon copy. Rest-pose retargeting fits the shared body to each
rig's proportions. Unit combat stats, promotion rules, upkeep and upgrade
prices are unaffected.

## Sources and attribution

- Firaxis: Civilization IV, Warlords and Beyond the Sword unit models and
  animations, including the American Revolution militia.
- Dawn of Civilization by Daniel Guenther / Leoreth: Armed Pioneer model and
  its bundled textures, taken from the locally installed mod. Its broader art
  contributor credits and MIT license are retained in
  [credits](../art/slaves/Dawn-of-Civilization-Credits.txt) and
  [license](../art/slaves/Dawn-of-Civilization-LICENSE.md).
- RFC MP Plus modifications: custom material variants, removal of the unarmed
  unit's club, body retargeting and irregular formations.

## Rebuild and preview

The build reads local game and DoC assets without modifying those installations.
Their paths are configured near the top of `tools/build_slave_art.py`.

```powershell
.\.venv-art\Scripts\python.exe -m pip install -r art/slaves/requirements.txt
.\.venv-art\Scripts\python.exe tools/build_slave_art.py
.\.venv-art\Scripts\python.exe tools/preview_slave_art.py
```

The static [preview](../art/slaves/preview.png) shows bind poses, not animated
in-game stances. The game supplies idle, walking and combat animations. In-game
visual validation is still required.

`tools/update_slave_unit_line.py` reapplies these mesh groups when regenerating
slave gameplay XML, so it does not replace the custom models with regular troops.
