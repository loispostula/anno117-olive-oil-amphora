"""Static checks for the mod. They prove the files are well-formed and the patch logic is
consistent; they do NOT prove the game accepts it. See README "In-game test checklist".

Upstream checks run only when UPSTREAM_DIR points to a folder holding the upstream mod ZIPs.
"""
import copy
import json
import os
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "mod"
ASSETS = MOD / "data/base/config/export/assets.xml"
sys.path.insert(0, str(ROOT / "tools"))
import package  # noqa: E402

OLIVE_PRESS, OLIVES, OLIVE_OIL, AMPHORAE, GLASS, LAVENDER, CLAY = "4831", "2072", "2149", "31700", "2117", "2071", "2086"
# Every asset this mod may touch. Sources: anno-mods/anno-117-calculator params, Taludas' patch.
PERFUME_CHAINS = ("1556002102", "1556002103")  # Unguentarium chain views, display only
PATCHED_GUIDS = {OLIVE_PRESS, "31806", "55972", OLIVE_OIL, "2778", "55961", *PERFUME_CHAINS}
PERFUMERY, LAMP_WORKSHOP, AMPHORA_WORKSHOP = "1556002101", "2100200101", "3199"
TALUDAS = "taludas-oliveoilneedsglass"
LINE_ID = "2001004149"
ICON = "data/olive-oil-amphora/ui/icon_olive_oil_amphora.png"
GAME_LANGUAGES = ("brazilian", "english", "french", "german", "italian", "japanese", "korean", "polish",
                  "russian", "simplified_chinese", "spanish", "traditional_chinese")
OP_TYPES = ("Add", "Remove", "Merge", "Replace", "Append", "Prepend")

# Shaped after the calculator data and the paths Taludas' published patch writes to. Not game data.
# The negative OasisId mimics a vanilla LineId.
VANILLA_FIXTURE = f"""<AssetList>
  <Asset><Values><Standard><GUID>{OLIVE_PRESS}</GUID></Standard>
    <FactoryBase><FactoryInputs><Item><Product>{OLIVES}</Product><Amount>1</Amount></Item></FactoryInputs>
    <FactoryOutputs><Item><Product>{OLIVE_OIL}</Product><Amount>1</Amount></Item></FactoryOutputs></FactoryBase>
  </Values></Asset>
  <Asset><Values><Standard><GUID>31806</GUID></Standard>
    <ProductionChain><Building>{OLIVE_PRESS}</Building><Tier1><Item><Building>2699</Building></Item></Tier1></ProductionChain>
  </Values></Asset>
  <Asset><Values><Standard><GUID>55972</GUID></Standard>
    <ProductionChain><Building>{OLIVE_PRESS}</Building><Tier1><Item><Building>2699</Building></Item></Tier1></ProductionChain>
  </Values></Asset>
  <Asset><Values><Standard><GUID>{OLIVE_OIL}</GUID><IconFilename>vanilla.png</IconFilename></Standard>
    <Text><OasisId>-6911555031864321364</OasisId></Text></Values></Asset>
  <Asset><Values><Standard><GUID>2778</GUID><IconFilename>vanilla.png</IconFilename></Standard></Values></Asset>
  <Asset><Values><Standard><GUID>55961</GUID><IconFilename>vanilla.png</IconFilename></Standard></Values></Asset>
</AssetList>"""

# Shape of Unguentarium 1.7's perfume chain views (1.6 has only 1556002102).
UNGUENTARIUM_CHAINS = f"""<AssetList>
  <Asset><Values><Standard><GUID>1556002102</GUID></Standard><ProductionChain><Building>{PERFUMERY}</Building><Tier1>
    <Item><Building>{OLIVE_PRESS}</Building><Tier2><Item><Building>2699</Building></Item></Tier2></Item>
    <Item><Building>2698</Building></Item>
    <Item><Building>3074</Building><Tier2><Item><Building>2958</Building></Item></Tier2></Item>
  </Tier1></ProductionChain></Values></Asset>
  <Asset><Values><Standard><GUID>1556002103</GUID></Standard><ProductionChain><Building>{PERFUMERY}</Building><Tier1>
    <Item><Building>{OLIVE_PRESS}</Building></Item><Item><Building>2698</Building></Item><Item><Building>3074</Building></Item>
  </Tier1></ProductionChain></Values></Asset>
</AssetList>"""


def fixture(*chain_guids):
    """Vanilla fixture plus the given Unguentarium chain assets."""
    doc = ET.fromstring(VANILLA_FIXTURE)
    doc.extend(a for a in ET.fromstring(UNGUENTARIUM_CHAINS) if a.findtext("Values/Standard/GUID") in chain_guids)
    return doc


def op_type(op):
    found = [t for t in OP_TYPES if t in op.attrib]
    if len(found) != 1:
        raise ValueError(f"ModOp needs exactly one of {OP_TYPES}: {op.attrib}")
    return found[0]


def op_target(op, path):
    """Returns (guid, path relative to Values) for short or @GUID ModOps."""
    if "GUID" in op.attrib:
        return op.get("GUID"), path
    if path.startswith("@"):
        guid, _, rest = path[1:].partition("/")
        return guid, rest
    raise ValueError(f"Only GUID-scoped ModOps are supported: {op.attrib}")


def find_values(doc, guid):
    return next((a.find("Values") for a in doc.iter("Asset") if a.findtext("Values/Standard/GUID") == guid), None)


def select(values, path):
    return values.findall(path) if path else [values]


def condition_holds(doc, op, cond):
    negate = cond.startswith("!")
    guid, path = op_target(op, cond.lstrip("!"))
    values = find_values(doc, guid)
    return bool(values is not None and select(values, path)) != negate


def apply_modops(doc, modops, only_guids=None):
    """Minimal ModOp interpreter for the subset used here (ModOp, Group). Returns loader-style warnings."""
    warnings = []
    for node in modops:
        if node.tag == "Group":
            if condition_holds(doc, node, node.get("Condition")):
                warnings += apply_modops(doc, node, only_guids)
            continue
        if node.tag != "ModOp":
            continue
        op = node
        kind = op_type(op)
        guid, path = op_target(op, op.get(kind))
        if only_guids is not None and guid not in only_guids:
            continue
        # Positive conditions skip silently, even on a missing asset; negative ones still warn.
        cond = op.get("Condition")
        if cond and not condition_holds(doc, op, cond):
            continue
        values = find_values(doc, guid)
        if values is None:
            warnings.append(f"asset {guid} not found")
            continue
        targets = select(values, path)
        if not targets:
            warnings.append(f"{kind} {guid}/{path}: no match")
            continue
        parents = {c: p for p in values.iter() for c in p}
        for target in targets:
            if kind == "Add":
                target.extend(copy.deepcopy(list(op)))
            elif kind == "Remove":
                parents[target].remove(target)
            elif kind == "Merge":
                for child in op:
                    existing = target.find(child.tag)
                    if existing is not None:
                        target.remove(existing)
                    target.append(copy.deepcopy(child))
            else:
                raise NotImplementedError(kind)
    return warnings


def inputs(doc, guid):
    return [i.findtext("Product") for i in find_values(doc, guid).findall("FactoryBase/FactoryInputs/Item")]


def under_olive_press(doc, guid):
    return [i.findtext("Building") for i in find_values(doc, guid).findall(
        f"ProductionChain/Tier1/Item[Building='{OLIVE_PRESS}']/Tier2/Item")]


def tier1(doc, guid):
    return [i.findtext("Building") for i in find_values(doc, guid).findall("ProductionChain/Tier1/Item")]


def our_modops():
    return ET.parse(ASSETS).getroot()


def upstream_mods():
    """ModID -> list of parsed export XML roots, read from ZIPs in UPSTREAM_DIR."""
    found = {}
    folder = os.environ.get("UPSTREAM_DIR")
    if not folder:
        return found
    for zpath in Path(folder).expanduser().glob("*.zip"):
        try:
            zf = zipfile.ZipFile(zpath)
        except zipfile.BadZipFile:
            continue
        with zf:
            for name in zf.namelist():
                if name.count("/") == 1 and name.endswith("/modinfo.json"):
                    mod_id = json.loads(zf.read(name).decode("utf-8-sig"))["ModID"]
                    prefix = name.rsplit("/", 1)[0] + "/data/base/config/export/"
                    found[mod_id] = [ET.fromstring(zf.read(n)) for n in zf.namelist()
                                     if n.startswith(prefix) and n.endswith(".xml")]
    return found


class StaticTests(unittest.TestCase):
    def test_assets_xml_structure(self):
        root = our_modops()
        self.assertEqual(root.tag, "ModOps")
        self.assertTrue(list(root))
        for node in root:
            self.assertIn(node.tag, ("ModOp", "Group"))
            if node.tag == "Group":
                self.assertRegex(node.get("Condition", ""), r"^@\d+$", "groups only guard on an asset existing")
                self.assertTrue(all(op.tag == "ModOp" for op in node))
        for op in root.iter("ModOp"):
            self.assertIn("GUID", op.attrib, "use GUID-scoped ModOps only")
            op_type(op)

    def test_patch_scope_is_exactly_the_expected_assets(self):
        touched = {op.get("GUID") for op in our_modops().iter("ModOp")}
        self.assertEqual(touched, PATCHED_GUIDS)
        self.assertNotIn(PERFUMERY, touched)
        self.assertNotIn(LAMP_WORKSHOP, touched)

    def test_modinfo(self):
        info = json.loads((MOD / "modinfo.json").read_text(encoding="utf-8"))
        self.assertEqual(info["Anno"], 8)
        self.assertRegex(info["Version"], r"^\d+\.\d+\.\d+$")
        self.assertRegex(info["ModID"], r"^[a-z0-9-]+$")
        self.assertIn(info["Difficulty"], {"cheat", "easier", "unchanged", "harder"})
        for key in ("ModName", "Category", "Description"):
            self.assertTrue(info[key]["English"])
        deps = info["Dependencies"]
        self.assertEqual(deps["Require"], [])
        self.assertEqual(deps["Optional"], ["unguentarium-khayi", "roman-night-lamps-koopas"])
        self.assertTrue(set(deps["Require"] + deps["Optional"]) <= set(deps["LoadAfter"]), "dependencies must load first")
        self.assertEqual(deps["Incompatible"], [TALUDAS])
        self.assertNotIn(TALUDAS, deps["Optional"] + deps["LoadAfter"])
        self.assertTrue((MOD / info["AssetsPath"]).is_file())

    def test_icons_exist_and_are_png(self):
        icons = {e.text for e in our_modops().iter("IconFilename")}
        self.assertTrue(icons)
        for icon in icons:
            path = MOD / icon
            self.assertTrue(path.is_file(), icon)
            head = path.read_bytes()[:24]
            self.assertEqual(head[:8], b"\x89PNG\r\n\x1a\n", icon)
            width, height = int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
            self.assertEqual((width, height), (256, 256), icon)

    def test_icon_path_is_namespaced(self):
        for e in our_modops().iter("IconFilename"):
            self.assertTrue(e.text.startswith("data/olive-oil-amphora/"), e.text)

    def test_texts_for_every_game_language(self):
        oasis = [e.text for e in our_modops().iter("OasisId")]
        self.assertEqual(oasis, [LINE_ID])
        gui = MOD / "data/base/config/gui"
        self.assertEqual(sorted(p.name for p in gui.iterdir()), sorted(f"texts_{l}.xml" for l in GAME_LANGUAGES))
        for lang in GAME_LANGUAGES:
            root = ET.parse(gui / f"texts_{lang}.xml").getroot()
            ops = list(root)
            self.assertEqual([op.get("Add") for op in ops], ["/TextExport/Texts[1]"], lang)
            texts = [(t.findtext("LineId"), t.findtext("Text")) for t in ops[0].findall("Text")]
            self.assertEqual(len(texts), 1, lang)
            self.assertEqual(texts[0][0], LINE_ID, lang)
            self.assertTrue(texts[0][1].strip(), lang)

    def test_line_id_in_personal_range(self):
        self.assertTrue(2_001_000_000 <= int(LINE_ID) <= 2_001_009_999)


class PatchSimulationTests(unittest.TestCase):
    def setUp(self):
        self.doc = fixture(*PERFUME_CHAINS)

    def assert_final_state(self):
        self.assertEqual(sorted(inputs(self.doc, OLIVE_PRESS)), sorted([OLIVES, AMPHORAE]))
        self.assertNotIn("3074", tier1(self.doc, "31806"))
        self.assertNotIn("3074", tier1(self.doc, "55972"))
        self.assertEqual(tier1(self.doc, "31806").count("3199"), 1)
        self.assertEqual(tier1(self.doc, "55972").count("55962"), 1)
        for guid in (OLIVE_OIL, "2778", "55961", OLIVE_PRESS, "31806", "55972"):
            icons = find_values(self.doc, guid).findall("Standard/IconFilename")
            self.assertEqual([i.text for i in icons], [ICON])
        self.assertEqual([e.text for e in find_values(self.doc, OLIVE_OIL).findall("Text/OasisId")], [LINE_ID])
        self.assertEqual([o.findtext("Product") for o in find_values(self.doc, OLIVE_PRESS).findall(
            "FactoryBase/FactoryOutputs/Item")], [OLIVE_OIL], "output GUID must stay 2149")
        for guid in PERFUME_CHAINS:
            if find_values(self.doc, guid) is not None:
                self.assertEqual(under_olive_press(self.doc, guid).count(AMPHORA_WORKSHOP), 1, guid)

    def test_vanilla(self):
        self.assertEqual(apply_modops(self.doc, our_modops()), [])
        self.assert_final_state()

    def test_perfume_chains(self):
        apply_modops(self.doc, our_modops())
        self.assertEqual(under_olive_press(self.doc, "1556002102"), ["2699", AMPHORA_WORKSHOP])
        self.assertEqual(under_olive_press(self.doc, "1556002103"), [AMPHORA_WORKSHOP])

    def test_unguentarium_1_6_without_albion_chain(self):
        self.doc = fixture("1556002102")
        self.assertEqual(apply_modops(self.doc, our_modops()), [])
        self.assert_final_state()

    def test_without_unguentarium(self):
        self.doc = fixture()
        self.assertEqual(apply_modops(self.doc, our_modops()), [])
        self.assert_final_state()

    def test_idempotent(self):
        apply_modops(self.doc, our_modops())
        self.assertEqual(apply_modops(self.doc, our_modops()), [])
        self.assert_final_state()


class PackageTests(unittest.TestCase):
    def test_reproducible_zip(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            za, zb = package.build(Path(a)), package.build(Path(b))
            self.assertEqual(za.read_bytes(), zb.read_bytes())
            with zipfile.ZipFile(za) as zf:
                names = zf.namelist()
        tops = {n.split("/", 1)[0] for n in names}
        self.assertEqual(len(tops), 1)
        top = tops.pop()
        self.assertIn(f"{top}/modinfo.json", names)
        self.assertIn(f"{top}/data/base/config/export/assets.xml", names)
        self.assertIn(f"{top}/{ICON}", names)
        self.assertIn(f"{top}/data/base/config/gui/texts_french.xml", names)


@unittest.skipUnless(os.environ.get("UPSTREAM_DIR"), "set UPSTREAM_DIR to a folder with the upstream mod ZIPs")
class UpstreamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mods = upstream_mods()

    def factory_inputs(self, mod_id, guid):
        for root in self.mods[mod_id]:
            values = find_values(root, guid)
            if values is not None:
                return [i.findtext("Product") for i in values.findall("FactoryBase/FactoryInputs/Item")]
        self.fail(f"{guid} not defined by {mod_id}")

    def patched_guids(self, mod_id):
        guids = set()
        for root in self.mods[mod_id]:
            for op in root.iter("ModOp"):
                guids.add(op.get("GUID"))
                for attr in OP_TYPES:
                    m = re.match(r"@(\d+)", op.get(attr, ""))
                    if m:
                        guids.add(m.group(1))
        return guids - {None}

    def test_perfume_recipe_untouched(self):
        self.assertIn("unguentarium-khayi", self.mods)
        self.assertEqual(self.factory_inputs("unguentarium-khayi", PERFUMERY), [OLIVE_OIL, GLASS, LAVENDER])

    def test_lamp_recipe_untouched(self):
        self.assertIn("roman-night-lamps-koopas", self.mods)
        self.assertEqual(self.factory_inputs("roman-night-lamps-koopas", LAMP_WORKSHOP), [CLAY, OLIVE_OIL])

    def test_no_patch_conflicts_with_supported_mods(self):
        for mod_id in ("unguentarium-khayi", "roman-night-lamps-koopas"):
            # Unguentarium locks its own chain views; our display patch on them is checked against its real files.
            self.assertEqual(self.patched_guids(mod_id) & (PATCHED_GUIDS - set(PERFUME_CHAINS)), set(), mod_id)

    def test_perfume_chain_patch_on_real_unguentarium(self):
        doc = ET.fromstring("<AssetList/>")
        doc.extend(copy.deepcopy(a) for r in self.mods["unguentarium-khayi"] for a in r.iter("Asset"))
        self.assertEqual(apply_modops(doc, our_modops(), only_guids=set(PERFUME_CHAINS)), [])
        self.assertEqual(under_olive_press(doc, "1556002102").count(AMPHORA_WORKSHOP), 1)
        if find_values(doc, "1556002103") is not None:
            self.assertEqual(under_olive_press(doc, "1556002103"), [AMPHORA_WORKSHOP])

    def test_line_id_not_used_upstream(self):
        for mod_id, roots in self.mods.items():
            ids = {e.text for r in roots for e in r.iter("OasisId")}
            self.assertNotIn(LINE_ID, ids, mod_id)

    def test_upstream_text_line_ids(self):
        """Upstream text files live outside export/; read them straight from the ZIPs."""
        for zpath in Path(os.environ["UPSTREAM_DIR"]).expanduser().glob("*.zip"):
            try:
                with zipfile.ZipFile(zpath) as zf:
                    for name in zf.namelist():
                        if "/data/base/config/gui/texts_" in name and name.endswith(".xml"):
                            ids = {e.text for e in ET.fromstring(zf.read(name)).iter("LineId")}
                            self.assertNotIn(LINE_ID, ids, f"{zpath.name}:{name}")
            except zipfile.BadZipFile:
                continue


if __name__ == "__main__":
    unittest.main()
