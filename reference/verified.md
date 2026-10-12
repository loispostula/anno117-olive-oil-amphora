# Evidence

Status legend: **confirmed** = read in a primary source; **hypothesis** = inferred, needs an in-game test.

## Vanilla GUIDs

Source: [anno-mods/anno-117-calculator](https://github.com/anno-mods/anno-117-calculator) `js/params-base.js`, generated from game assets.

| GUID | Asset | Fact | Status |
|---|---|---|---|
| `31700` | Good Amphorae | producers `3199` (Roman), `55962` (Albion) | confirmed |
| `4831` | Production Household Roman Olive Oil (Olive Press) | input `2072` olives, output `2149`, cycle 90 | confirmed |
| `2149` | Good Olive Oil | producer `4831` only, icon `data/ui/fhd/base/icon_content/production_goods/icon_3d_olive_oil_goods.png` | confirmed |
| `2778` / `55961` | Need Roman / Roman Celtic Household Olive Oil | same icon as `2149` | confirmed |
| `2777` / `55960` | Need Roman / Roman Celtic Household Amphorae | needProduct `31700` | confirmed |
| `3199` | Roman Amphorae workshop | inputs clay `2086` + resin `31695` | confirmed |
| `55962` | Roman Celtic Amphorae workshop | inputs mud `2102` + resin `31695` | confirmed |
| `2970` / `31752` | Roman Clay Pit / Roman Resin | producers of `2086` / `31695` | confirmed |
| `5848` / `31761` | Mud producer / Roman Celtic Resin | producers of `2102` / `31695` | confirmed |
| `3074` | Production Heavy Roman Glass (Glass Smelter) | input silica `2091`, output `2117` | confirmed |
| `31806` / `55972` | Olive oil production chains (Latium / Albion) | have `ProductionChain/Tier1` | confirmed via Taludas' patch |

Vanilla references to `2149`: producer `4831`, needs `2778` and `55961`, product filter `37670`. Nothing else in the calculator data, which covers production only (not quests, items or costs).

No vanilla factory consumes a product that is also a household need (scanned all `factories[].inputs` against `needs[].needProduct`).

## Upstream mods (local ZIPs)

| Mod | File | Fact |
|---|---|---|
| `unguentarium-khayi` 1.6 | `unguentarium.include.xml` | factory `1556002101` inputs `2149`, `2117`, `2071`; output `1556002100`; chain `1556002102` Tier1 `4831`, `3074`, `2698` |
| `unguentarium-khayi` 1.7 | `unguentarium.include.xml` | same factory inputs and output as 1.6; perfume chain Tier1 reordered; new Albion perfume chain `1556002103` (Tier1 `4831`, `2698`, `3074`), trigger `1556002104`, construction menu `41327`, pool `50606`; new text `1556002204`. No asset or LineId shared with this mod |
| `roman-night-lamps-koopas` 1.2.0 | `assets.xml` | factory `2100200101` inputs `2086`, `2149`; output `2100200100`; chain `2100200202` Tier1 `4831`, `2970` |
| `taludas-oliveoilneedsglass` 1.0.0 (declared Incompatible) | `assets.xml` | `Add="@4831/FactoryBase/FactoryInputs"` glass `2117` (StorageAmount 3); adds `3074` to `31806` and `55972` Tier1; Glass Smelter rebalance; trigger `1999100012` |

Upstream LineIds in use: `2001000010`, `2001000011` (lamps), `2001000020`–`2001000022` (perfume). This mod uses `2001004149`.

Neither required mod patches `4831`, `31806`, `55972`, `2149`, `2778` or `55961` (checked by `UpstreamTests`).

## Mod loader

Source: [jakobharder/anno-mod-loader docs](https://jakobharder.github.io/anno-mod-loader/) (`docs/modinfo.md`, `loading-order.md`, `modops/*.md`, `changes-117.md`).

- `"Anno": 8` required for Anno 117; `Difficulty` mandatory (`cheat|easier|unchanged|harder`).
- `Dependencies.Require`: missing mod → log warning. `Dependencies.LoadAfter`: listed mods load first, no warning if absent. `Dependencies.Incompatible`: active listed mod → log warning.
- Asset names use `Values/Text/OasisId` → LineId. Texts are added with `<ModOp Add="/TextExport/Texts[1]">` in `data/base/config/gui/texts_<language>.xml`. Personal LineId range: 2.001.000.000 – 2.001.009.999.
- Short ModOps: `GUID="x" Add="Path"` where the path skips `/Values/`. `Condition` is relative to the GUID, `!` negates.
- `Merge` adds or replaces child nodes, never removes.
- Assets path: `data/base/config/export/assets.xml`. Mods folder: `<user>/Anno 117/mods/`. Log: `<user documents>/Anno 117/mods/mod-loader.log`.

## Hypotheses

- Amphorae work as a factory input without extra config. Basis: product records have no end-product flag. Both required mods consume `2149`, which is also a household-need good.
- A loose 256×256 PNG under `data/<mod>/ui/` renders as a product icon. Basis: Unguentarium (256×256) and Oil Lamp (120×120) both ship one this way.
