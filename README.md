# Anno 117: Olive Oil in Amphorae

Compatibility mod for Anno 117: Pax Romana. Olive oil is pressed into amphorae and becomes the **Olive Oil Amphora**, so glass is only needed once, in the perfume chain.

**Status: tested in game on 0.1.2 with Unguentarium 1.7** (Roman Oil Lamp Maker not tested yet). See [In-game test checklist](#in-game-test-checklist).

## Production chains

| Building | With this mod |
|---|---|
| Olive Press `4831` | Olives + **Amphorae** → **Olive Oil Amphora** |
| Unguentarium `1556002101` | Olive Oil Amphora + Glass + Lavender → Perfume (recipe unchanged) |
| Oil Lamp Workshop `2100200101` | Clay + Olive Oil Amphora → Oil Lamp (recipe unchanged) |

The Olive Oil Amphora is the vanilla olive oil product (`2149`), renamed and given an amphora icon (transparent background, like vanilla goods). The Olive Press and the olive oil production chain tabs use the same icon. The GUID is kept on purpose:

- Roman and Albion residents keep their olive oil need (`2778`, `55961`). Those needs get the amphora icon too.
- Perfume and oil lamps keep consuming `2149`; their recipes are not patched.
- Warehouses, trade and existing saves keep working.

The new name uses LineId `2001004149` and ships in all 12 game languages. French, English and German are proofread. The other languages are best-effort translations.

## Compatibility

| Mod | ModID | Version checked | Relation |
|---|---|---|---|
| Unguentarium – Roman Perfumery (khayi) | `unguentarium-khayi` | 1.6, 1.7 | Required, loads before |
| Roman Oil Lamp Maker (Koopas) | `roman-night-lamps-koopas` | 1.2.0 | Required, loads before |
| Olive Oil Needs Glass (Taludas) | `taludas-oliveoilneedsglass` | 1.0.0 | **Incompatible** |

- Recipes of the required mods are not patched. The only upstream assets touched are Unguentarium's perfume chain views (`1556002102`, and `1556002103` from 1.7), which get the Amphorae Workshop under the Olive Press. Display only. A missing required mod only produces a warning in `mod-loader.log`.
- This mod replaces Taludas' "Olive Oil Needs Glass". Together they would give olive oil both glass and amphorae. Disable Taludas' mod. It declares itself `SafeToRemove`.
- Any other mod that changes Olive Press `4831` inputs or the olive oil product text may conflict.

## Installation

1. Download `olive-oil-amphora-compat-<version>.zip` from the GitHub Releases or mod.io.
2. Extract it into `<user>/Anno 117/mods/` (for example `Documents/Anno 117/mods/`), so you get `mods/[Gameplay] Olive Oil in Amphorae/modinfo.json`.
3. Install and enable the required mods. Disable "Olive Oil Needs Glass" (Taludas).
4. Start the game and enable the mod.

Existing saves: olive presses that are already built need amphorae from the moment the mod is enabled.

## In-game test checklist

Run with Unguentarium and Roman Oil Lamp Maker enabled and Taludas' mod disabled. Results from the first test (0.1.2, Unguentarium 1.7) in brackets.

- [ ] `<user documents>/Anno 117/mods/mod-loader.log` has no warnings or errors that mention `olive-oil-amphora-compat`. (log not sent yet)
- [x] Olive Press info panel shows two inputs: Olives and Amphorae. No glass.
- [x] An Olive Press with olives and amphorae in reach produces "Olive Oil Amphora".
- [x] An Olive Press without amphorae stops and reports a missing input.
- [x] The product is named "Amphore d'huile d'olive" / "Olive Oil Amphora", with the amphora icon, in the warehouse, the trade screen and the residence needs panel, in Latium and Albion.
- [x] Residences still consume amphorae and olive oil amphorae (both household needs work).
- [x] Latium olive oil production chain view lists the Amphorae Workshop (with Clay Pit and Resin).
- [x] Albion olive oil production chain view lists the Albion Amphorae Workshop (not buildable there, as in vanilla).
- [ ] Olive oil build menu tab and the Olive Press show the amphora icon. (fixed in 0.1.3, failed in 0.1.2)
- [ ] Unguentarium perfume chain views (Latium and Albion) show the amphora icon on the Olive Press and the Amphorae Workshop under it. (fixed in 0.1.3, failed in 0.1.2)
- [ ] Unguentarium needs Olive Oil Amphora + Glass + Lavender and produces perfume.
- [ ] Oil Lamp Workshop needs Clay + Olive Oil Amphora and produces oil lamps. (not tested, mod not used)
- [x] An existing save loads, and its olive presses switch to the new recipe.
- [ ] With Taludas' mod also enabled, `mod-loader.log` reports the incompatibility.

## Unresolved issues

- **Partially tested in game.** See the checklist. Roman Oil Lamp Maker and the loader log are still unchecked.
- **Amphorae as a factory input.** Confirmed in game: the Olive Press consumes amphorae and stops without them.
- **Vanilla XML shape.** The GUIDs come from game data exported by [anno-117-calculator](https://github.com/anno-mods/anno-117-calculator). The XML paths (`FactoryBase/FactoryInputs`, `ProductionChain/Tier1`) are the ones Taludas' published mod patches. `Values/Text/OasisId` is the pattern Unguentarium uses for its products. The raw vanilla `assets.xml` has not been inspected.
- **LineId range.** `2001004149` sits in the shared personal range (2.001.000.000 – 2.001.009.999). Reserve a range on [GuidRanges](https://github.com/anno-mods/GuidRanges) before a wide public release.
- **Input storage.** The Olive Press stores 3 amphorae (`StorageAmount`, same as Taludas' glass). The vanilla value for olives is unknown.
- **Perfume chain views.** Only the Amphorae Workshop is added under the Olive Press (no Clay Pit / Resin level below it).

## Development

Requires Python 3.10+ and nothing else.

```sh
python3 -m unittest discover -s tests -v       # static checks + patch simulation
UPSTREAM_DIR=~/Downloads python3 -m unittest discover -s tests   # + checks against the upstream mod ZIPs
python3 tools/package.py                       # reproducible ZIP in dist/
```

Upstream checks read the ZIPs in `UPSTREAM_DIR` (matched by the `ModID` in each `modinfo.json`). They verify that the perfume and lamp recipes match, that the required mods patch none of our assets, and that no upstream text uses our LineId.

### What the tests prove

| Proven statically | Needs the game |
|---|---|
| XML well-formed, only GUID-scoped ModOps | The loader accepts every ModOp |
| Patch touches exactly 6 expected assets | Vanilla assets have these exact paths |
| Result is olives + amphorae, output stays `2149`, idempotent | The factory consumes amphorae |
| Name text in all 12 languages, LineId free upstream | The name shows in the UI |
| modinfo fields, Require ⊆ LoadAfter, Taludas incompatible | Load order in a real mod set |
| Icon files exist, PNG 256×256 | The icon renders |
| Reproducible ZIP | |

### CI and releases

`.github/workflows/ci.yml`:

- Push / PR: run tests, build the ZIP, upload it as the `mod-zip` artifact.
- Tag `vX.Y.Z` (must equal `Version` in `mod/modinfo.json`): create a GitHub Release with the ZIP, then upload it to mod.io.

mod.io upload runs only when these are set in the repository settings:

| Kind | Name | Value |
|---|---|---|
| Variable | `MODIO_GAME_ID` | numeric Anno 117 game ID on mod.io |
| Variable | `MODIO_MOD_ID` | numeric ID of a mod page you own |
| Secret | `MODIO_TOKEN` | mod.io OAuth token with write scope |
| Secret | `MODIO_DOMAIN` | API subdomain from mod.io/me/access, `<this>.modapi.io` (`api.mod.io` is deprecated) |

Create the mod.io page manually first (logo: `media/modio-logo.png`). `MODIO_TOKEN` must be an OAuth 2 access token with read+write scope from mod.io/me/access: an API key is read-only and cannot upload. Release flow: bump `Version` in `mod/modinfo.json`, commit, tag `v<version>`, push the tag.

## Layout

```
mod/                    installable mod (packaged into the ZIP)
  modinfo.json
  data/base/config/export/assets.xml
  data/base/config/gui/texts_*.xml      name "Olive Oil Amphora", 12 languages
  data/olive-oil-amphora/ui/icon_olive_oil_amphora.png
tests/test_mod.py       static checks, patch simulation, upstream checks
tools/package.py        reproducible ZIP builder
reference/verified.md   sources and evidence for every GUID and assumption
media/modio-logo.png    mod.io listing image, 1920×1080 (not in the ZIP)
media/modio-chains.png  mod.io gallery image: production chains
```

## Licensing

[MIT](LICENSE), including the olive oil amphora icon. Third-party mod files are not redistributed. The mod.io images in `media/` show game goods icons and the Unguentarium and Oil Lamp icons; those belong to their owners and are not covered by the MIT license. Anno and its names belong to their respective owners.
