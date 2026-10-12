#!/usr/bin/env python3
"""Inspect extracted Anno 117 vanilla assets.xml for amphora and olive oil IDs."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def main(path):
    root = ET.parse(path).getroot()
    for asset in root.iter('Asset'):
        name = asset.findtext('./Values/Standard/Name') or ''
        guid = asset.findtext('./Values/Standard/GUID') or ''
        if any(term in name.lower() for term in ('amphor', 'olive', 'oil press', 'potter')):
            inputs = [(x.findtext('Product'), x.findtext('Amount')) for x in asset.findall('./Values/FactoryBase/FactoryInputs/Item')]
            outputs = [(x.findtext('Product'), x.findtext('Amount')) for x in asset.findall('./Values/FactoryBase/FactoryOutputs/Item')]
            print(f'{guid}: {name} | inputs={inputs} outputs={outputs}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python tools/inspect_assets.py /path/to/assets.xml')
    main(Path(sys.argv[1]))
