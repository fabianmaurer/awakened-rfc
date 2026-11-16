# Fertile soil art

Generated with the built-in imagegen tool. The original RGBA PNG is retained as
`FertileSoil.png`; `tools/build_fertile_soil_art.py` exports its unchanged colours
and alpha to runtime DDS textures and builds the ground-level NIF mesh.

The feature adds +1 food on selected flat, open plains and grassland. It occupies
the normal feature slot and does not replace forests, wetlands or floodplains.
The model uses a transparent ground decal; actual terrain contouring and layering
under farms/cottages remain user-operated in-game visual checks.

## Generation prompt

Create a production-ready top-down diffuse ground-decal texture for Civilization IV's Fertile soil terrain feature. Square image with genuine transparent background. Scatter many small, irregular, softly edged patches of deep dark earthy brown humus, interwoven with fine lush muted-green grass tufts. About one third of the image should contain the soil-and-grass patches; the rest must be transparent so the existing grassland or golden plains terrain shows through. Distribute patches naturally across the tile with an irregular transparent outer margin, no large central mound, no rectangular border and no obvious repeating motif. Fine-grained, understated hand-painted strategy-game terrain detail, readable when reduced to 256 pixels. Strict orthographic overhead view, completely flat surface, even neutral diffuse lighting, no cast shadows, no directional highlights. Natural fertile earth before cultivation: no furrows, no straight lines, no crops, no plants taller than short grass, no rocks, no objects, no rivers, no text, no icons, no baked checkerboard.
