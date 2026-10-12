# Anno 117 — Olive Oil in Amphorae (experimental)

Compatibility project for **Unguentarium – Roman Perfumery** (`unguentarium-khayi`, tested source 1.6) and **Roman Oil Lamp Maker** (`roman-night-lamps-koopas`, source 1.2.0).

## Intended chains

- Olive oil: **olives + amphora → olive oil** (new amphora-and-olives icon)
- Perfume: **olive oil + lavender + glass → perfume** (unchanged)
- Oil lamps: unchanged

## Current status

**NOT PLAYABLE YET.** The XML file is a deliberately inert placeholder; no GUID is guessed. The supplied image is a **preview**, not yet registered as an in-game product icon.

Confirmed from supplied Unguentarium archive: perfume factory `1556002101`, olive oil product `2149`, glass product `2117`, lavender product `2071`. Confirmed from supplied lamp mod: its factory consumes olive oil product `2149`.

## Missing information

1. Amphora commodity GUID from the vanilla game.
2. Vanilla olive-oil production building GUID and its current FactoryInputs.
3. Vanilla olive-oil product asset and its icon configuration.
4. Verify that the amphora can be used as a FactoryInput, and test in game.

Extract vanilla assets from `maindata/config.rda` with a compatible RDA extraction tool; provide `data/base/config/export/assets.xml` to finish. No game purchase is necessary on the development machine.

## Repository layout

- `mod/`: eventual installable mod structure (currently a placeholder)
- `mod/data/compat/ui/olive_oil_amphora.png`: generated 256×256 concept icon
- `tools/inspect_assets.py`: find relevant assets in vanilla XML
- `reference/`: notes on third-party mods (their files are not redistributed)

## Licensing

Third-party mod files are intentionally excluded. Generated artwork is supplied for use in this compatibility project. Anno and its names belong to their respective owners.
