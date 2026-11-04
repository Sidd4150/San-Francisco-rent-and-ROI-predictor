"""Download and snapshot official recent-tenancy data. No synthetic fallback."""
import argparse
import gzip
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
SOURCE_URL = 'https://data.sf.gov/resource/gdc7-dmcn.json'
SOURCE_PAGE = 'https://data.sf.gov/Housing-and-Buildings/Rent-Board-Housing-Inventory/gdc7-dmcn'
ZORI_URL = 'https://files.zillowstatic.com/research/public_csvs/zori/City_zori_uc_sfrcondomfr_sm_month.csv'
WHERE = "submission_year = '2026' AND occupancy_type = 'Occupied by non-owner' AND occupancy_or_vacancy_date_year in ('2025','2026')"
BEDROOMS = {'Studio': 0, 'One-Bedroom': 1, 'Two-Bedroom': 2, 'Three-Bedroom': 3, 'Four-Bedroom': 4, '5+': 5}
BATHROOMS = {'One bathroom': 1, 'One and a half bathrooms': 1.5, 'Two bathrooms': 2,
             'Two and a half bathrooms': 2.5, 'Three bathrooms or more': 3}
UTILITY_MAP = {'waterIncluded': 'base_rent_includes_water_sewer', 'gasIncluded': 'base_rent_includes_natural_gas',
               'electricityIncluded': 'base_rent_includes_electricity', 'refuseIncluded': 'base_rent_includes_refuse_recycling'}


def closed_band(value):
    numbers = re.fullmatch(r'\$?(\d+)-\$?(\d+)(?: Sq\.Ft)?', value or '')
    return tuple(map(int, numbers.groups())) if numbers else None


def prepare(rows):
    cleaned, excluded = [], Counter()
    for row in rows:
        rent, sqft = closed_band(row.get('monthly_rent')), closed_band(row.get('square_footage'))
        reason = None
        if row.get('submission_year') != '2026' or row.get('occupancy_type') != 'Occupied by non-owner' or row.get('occupancy_or_vacancy_date_year') not in ('2025', '2026'):
            reason = 'outside_recent_tenancy_cohort'
        elif not rent or rent[0] < 1:
            reason = 'zero_unknown_or_open_ended_rent'
        elif not sqft or sqft[0] < 251 or sqft[1] > 4000:
            reason = 'unknown_open_ended_or_small_floor_area'
        elif row.get('bathroom_count') not in BATHROOMS:
            reason = 'shared_or_unknown_bathroom'
        elif row.get('bedroom_count') not in BEDROOMS:
            reason = 'unknown_bedrooms'
        elif not row.get('point') or not row.get('block_num') or not row.get('analysis_neighborhood'):
            reason = 'missing_geography'
        if reason:
            excluded[reason] += 1
            continue
        lon, lat = row['point']['coordinates']
        if not (37.70 <= lat <= 37.84 and -122.52 <= lon <= -122.35):
            excluded['outside_sf_bounds'] += 1
            continue
        start = row.get('occupancy_or_vacancy_date', '')[:10]
        if not start or start > datetime.now(timezone.utc).date().isoformat():
            excluded['missing_or_future_tenancy_date'] += 1
            continue
        def optional_number(key, low, high):
            try:
                value = float(row.get(key, ''))
                return value if low <= value <= high else None
            except (ValueError, TypeError):
                return None
        record = dict(recordId=row['unique_id'], block=str(row['block_num']),
                      tenancyYear=int(row['occupancy_or_vacancy_date_year']), tenancyDate=start,
                      beds=BEDROOMS[row['bedroom_count']], baths=BATHROOMS[row['bathroom_count']],
                      footage=sum(sqft) / 2, latitude=lat, longitude=lon,
                      neighborhood=row['analysis_neighborhood'],
                      yearBuilt=optional_number('year_property_built', 1800, 2026),
                      buildingUnits=optional_number('unit_count', 1, 10000),
                      rentLow=rent[0], rentHigh=rent[1], rent=sum(rent) / 2)
        record.update({field: {'Y': 1, 'N': 0}.get(row.get(source)) for field, source in UTILITY_MAP.items()})
        cleaned.append(record)
    frame = pd.DataFrame(cleaned).drop_duplicates('recordId').sort_values('recordId')
    # Identical public rows can represent distinct units. Keep them, but all units
    # in the same city block are assigned to the same evaluation partition.
    return frame, dict(excluded)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-json', type=Path)
    parser.add_argument('--zori-csv', type=Path)
    args = parser.parse_args()
    if args.input_json:
        rows = json.loads(args.input_json.read_text())
    else:
        rows, offset = [], 0
        while True:
            response = requests.get(SOURCE_URL, params={'$where': WHERE, '$limit': 50000, '$offset': offset, '$order': 'unique_id'}, timeout=90)
            response.raise_for_status()
            batch = response.json()
            rows.extend(batch)
            if len(batch) < 50000:
                break
            offset += len(batch)
    frame, exclusions = prepare(rows)
    if len(frame) < 1000:
        raise RuntimeError('Insufficient real observations; existing artifacts are unchanged')
    DATA.mkdir(exist_ok=True)
    path = DATA / 'recent_tenancies.csv.gz'
    # Stable gzip output allows exact data checksums across reruns.
    with path.open('wb') as output:
        with gzip.GzipFile(filename='', mode='wb', fileobj=output, mtime=0) as compressed:
            compressed.write(frame.to_csv(index=False, float_format='%.8f').encode())
    if args.zori_csv:
        zori = pd.read_csv(args.zori_csv)
    else:
        response = requests.get(ZORI_URL, timeout=90)
        response.raise_for_status()
        from io import StringIO
        zori = pd.read_csv(StringIO(response.text))
    city = zori[(zori.RegionName == 'San Francisco') & (zori.State == 'CA')].iloc[0]
    history = [{'date': key, 'rent': round(float(value), 2)} for key, value in city.items()
               if re.fullmatch(r'\d{4}-\d{2}-\d{2}', key) and pd.notna(value)]
    market = dict(source='Zillow Observed Rent Index', source_url='https://www.zillow.com/research/data/',
                  download_url=ZORI_URL, attribution='Data provided by Zillow Group', history=history,
                  latest=history[-1], note='Citywide asking-rent index. Context only; not applied to individual predictions.')
    (DATA / 'market_context.json').write_text(json.dumps(market, indent=2) + '\n')
    metadata = dict(source='San Francisco Rent Board Housing Inventory', source_url=SOURCE_PAGE,
                    download_url=SOURCE_URL, query=WHERE, license='Open Data Commons Public Domain Dedication and License',
                    retrieved_at=datetime.now(timezone.utc).isoformat(), data_as_of=max(r.get('data_as_of', '') for r in rows),
                    raw_rows=len(rows), usable_rows=len(frame), excluded=exclusions,
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    tenancy_year_counts={str(k): int(v) for k, v in frame.tenancyYear.value_counts().items()},
                    block_count=int(frame.block.nunique()),
                    limitations=['Owner-reported occupied rents, including possible subsidized tenancies; not advertised asking rents.',
                                 'Rents and areas use closed $250 and 250-sq-ft band midpoints.',
                                 'No-rent, open-ended $7000+ rent, shared-bathroom and unsupported floor-area records are excluded.',
                                 'Coordinates are anonymized block locations. Bedrooms 5+ and bathrooms 3+ are capped at those values.'])
    (DATA / 'provenance.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == '__main__':
    main()
