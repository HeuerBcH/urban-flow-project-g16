#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
from typing import Dict

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = BASE_DIR
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

print(f"[INFO] Base: {BASE_DIR}")
print(f"[INFO] Processed: {PROCESSED_DIR}")

# ---------- Helpers ----------

def read_csv_safe(path: str, **kwargs) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"[AVISO] Arquivo não encontrado: {path}")
        return None
    try:
        df = pd.read_csv(path, **kwargs)
        print(f"[OK] Carregado: {os.path.basename(path)} ({df.shape[0]} linhas, {df.shape[1]} colunas)")
        return df
    except Exception as e:
        print(f"[ERRO] Falha ao carregar {path}: {e}")
        return None


def to_int_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors='coerce').astype('Int64')


def to_float_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors='coerce')


def strip_series(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip()


def normalize_time_hhmmss(x: str) -> str:
    """
    GTFS permite horas >= 24. Mantemos como texto HH:MM:SS.
    Corrige strings incompletas (ex.: '5:3' -> '05:03:00').
    """
    if pd.isna(x):
        return None
    val = str(x).strip()
    if val == "":
        return None
    # Já no formato HH:MM:SS
    if len(val.split(":")) == 3:
        hh, mm, ss = val.split(":")
    elif len(val.split(":")) == 2:
        hh, mm = val.split(":")
        ss = "00"
    else:
        # tentativa simples: números contínuos
        digits = ''.join([c for c in val if c.isdigit()])
        if len(digits) >= 4:
            hh = digits[:-4]
            mm = digits[-4:-2]
            ss = digits[-2:]
        elif len(digits) >= 2:
            hh = digits[:-2] or '0'
            mm = digits[-2:]
            ss = '00'
        else:
            return None
    try:
        hh = str(int(hh))  # permite >=24
        mm = f"{int(mm):02d}"
        ss = f"{int(ss):02d}"
        return f"{hh.zfill(2)}:{mm}:{ss}"
    except Exception:
        return None


def save_df(df: pd.DataFrame, name: str):
    if df is None:
        print(f"[AVISO] {name} está vazio, não será salvo.")
        return
    out = os.path.join(PROCESSED_DIR, name)
    df.to_csv(out, index=False, encoding='utf-8')
    print(f"[OK] Salvo: {name} ({df.shape[0]} linhas)")

# ---------- Load raw GTFS ----------
files = {
    'agency': 'agency.csv',
    'calendar': 'calendar.csv',
    'calendar_dates': 'calendar_dates.csv',
    'fare_attributes': 'fare_attributes.csv',
    'fare_rules': 'fare_rules.csv',
    'feed_info': 'feed_info.csv',
    'routes': 'routes.csv',
    'shapes': 'shapes.csv',
    'stop_times': 'stop_times.csv',
    'stops': 'stops.csv',
    'trips': 'trips.csv',
}

raw: Dict[str, pd.DataFrame] = {}
for key, fname in files.items():
    raw[key] = read_csv_safe(os.path.join(RAW_DIR, fname))

print("\n=== LIMPEZA E PADRONIZAÇÃO GTFS ===")

# ---------- agency ----------
agency = raw.get('agency')
if agency is not None and not agency.empty:
    agency = agency.copy()
    for col in ['agency_id','agency_name','agency_url','agency_timezone','agency_lang','agency_phone','agency_fare_url','agency_email']:
        if col in agency.columns:
            agency[col] = agency[col].astype(str).str.strip()
    agency = agency.drop_duplicates(subset=['agency_id'])
    print(f"[OK] agency limpo: {agency.shape}")
else:
    agency = None

# ---------- calendar ----------
calendar = raw.get('calendar')
if calendar is not None and not calendar.empty:
    calendar = calendar.copy()
    # coagir dias para 0/1
    for col in ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']:
        if col in calendar.columns:
            calendar[col] = to_int_series(calendar[col]).fillna(0).clip(0,1)
    # datas como texto YYYYMMDD mantidas ou converter para datetime
    for col in ['start_date','end_date']:
        if col in calendar.columns:
            calendar[col] = pd.to_datetime(calendar[col].astype(str), format='%Y%m%d', errors='coerce').dt.date
    calendar['service_id'] = strip_series(calendar['service_id'])
    calendar = calendar.drop_duplicates(subset=['service_id'])
    print(f"[OK] calendar limpo: {calendar.shape}")
else:
    calendar = None

# ---------- calendar_dates ----------
calendar_dates = raw.get('calendar_dates')
if calendar_dates is not None and not calendar_dates.empty:
    calendar_dates = calendar_dates.copy()
    calendar_dates['service_id'] = strip_series(calendar_dates['service_id'])
    if 'exception_type' in calendar_dates.columns:
        calendar_dates['exception_type'] = to_int_series(calendar_dates['exception_type']).fillna(0)
    if 'date' in calendar_dates.columns:
        calendar_dates['date'] = pd.to_datetime(calendar_dates['date'].astype(str), format='%Y%m%d', errors='coerce').dt.date
    calendar_dates = calendar_dates.drop_duplicates(subset=['service_id','date'])
    print(f"[OK] calendar_dates limpo: {calendar_dates.shape}")
else:
    calendar_dates = None

# ---------- routes ----------
routes = raw.get('routes')
if routes is not None and not routes.empty:
    routes = routes.copy()
    for col in ['route_id','agency_id','route_short_name','route_long_name','route_url']:
        if col in routes.columns:
            routes[col] = strip_series(routes[col])
    if 'route_type' in routes.columns:
        routes['route_type'] = to_int_series(routes['route_type'])
    routes = routes.drop_duplicates(subset=['route_id'])
    print(f"[OK] routes limpo: {routes.shape}")
else:
    routes = None

# ---------- shapes ----------
shapes = raw.get('shapes')
if shapes is not None and not shapes.empty:
    shapes = shapes.copy()
    shapes['shape_id'] = strip_series(shapes['shape_id'])
    for col in ['shape_pt_lat','shape_pt_lon']:
        if col in shapes.columns:
            shapes[col] = to_float_series(shapes[col])
    if 'shape_pt_sequence' in shapes.columns:
        shapes['shape_pt_sequence'] = to_int_series(shapes['shape_pt_sequence'])
    if 'shape_dist_traveled' in shapes.columns:
        shapes['shape_dist_traveled'] = to_float_series(shapes['shape_dist_traveled'])
    # remover duplicatas por par chave
    shapes = shapes.drop_duplicates(subset=['shape_id','shape_pt_sequence'])
    print(f"[OK] shapes limpo: {shapes.shape}")
else:
    shapes = None

# ---------- stops ----------
stops = raw.get('stops')
if stops is not None and not stops.empty:
    stops = stops.copy()
    stops['stop_id'] = strip_series(stops['stop_id'])
    for col in ['stop_name','stop_url']:
        if col in stops.columns:
            stops[col] = strip_series(stops[col])
    for col in ['stop_lat','stop_lon']:
        if col in stops.columns:
            stops[col] = to_float_series(stops[col])
    if 'location_type' in stops.columns:
        stops['location_type'] = to_int_series(stops['location_type']).fillna(0)
    stops = stops.drop_duplicates(subset=['stop_id'])
    print(f"[OK] stops limpo: {stops.shape}")
else:
    stops = None

# ---------- trips ----------
trips = raw.get('trips')
if trips is not None and not trips.empty:
    trips = trips.copy()
    for col in ['route_id','service_id','trip_id','trip_headsign','shape_id']:
        if col in trips.columns:
            trips[col] = strip_series(trips[col])
    if 'direction_id' in trips.columns:
        trips['direction_id'] = to_int_series(trips['direction_id']).fillna(0)
    trips = trips.drop_duplicates(subset=['trip_id'])
    print(f"[OK] trips limpo: {trips.shape}")
else:
    trips = None

# ---------- stop_times ----------
stop_times = raw.get('stop_times')
if stop_times is not None and not stop_times.empty:
    stop_times = stop_times.copy()
    for col in ['trip_id','stop_id']:
        if col in stop_times.columns:
            stop_times[col] = strip_series(stop_times[col])
    for tcol in ['arrival_time','departure_time']:
        if tcol in stop_times.columns:
            stop_times[tcol] = stop_times[tcol].apply(normalize_time_hhmmss)
    if 'stop_sequence' in stop_times.columns:
        stop_times['stop_sequence'] = to_int_series(stop_times['stop_sequence'])
    # remover registros sem trip_id ou stop_id
    stop_times = stop_times[stop_times['trip_id'].notna() & stop_times['stop_id'].notna()]
    # remover duplicatas
    stop_times = stop_times.drop_duplicates(subset=['trip_id','stop_sequence'])
    print(f"[OK] stop_times limpo: {stop_times.shape}")
else:
    stop_times = None

# ---------- fare_attributes ----------
fare_attributes = raw.get('fare_attributes')
if fare_attributes is not None and not fare_attributes.empty:
    fare_attributes = fare_attributes.copy()
    for col in ['fare_id','currency_type','agency_id']:
        if col in fare_attributes.columns:
            fare_attributes[col] = strip_series(fare_attributes[col])
    if 'price' in fare_attributes.columns:
        fare_attributes['price'] = to_float_series(fare_attributes['price'])
    for col in ['payment_method','transfers']:
        if col in fare_attributes.columns:
            fare_attributes[col] = to_int_series(fare_attributes[col])
    fare_attributes = fare_attributes.drop_duplicates(subset=['fare_id'])
    print(f"[OK] fare_attributes limpo: {fare_attributes.shape}")
else:
    fare_attributes = None

# ---------- fare_rules ----------
fare_rules = raw.get('fare_rules')
if fare_rules is not None and not fare_rules.empty:
    fare_rules = fare_rules.copy()
    for col in ['fare_id','route_id']:
        if col in fare_rules.columns:
            fare_rules[col] = strip_series(fare_rules[col])
    fare_rules = fare_rules.drop_duplicates(subset=['fare_id','route_id'])
    print(f"[OK] fare_rules limpo: {fare_rules.shape}")
else:
    fare_rules = None

# ---------- feed_info ----------
feed_info = raw.get('feed_info')
if feed_info is not None and not feed_info.empty:
    feed_info = feed_info.copy()
    for col in ['feed_publisher_name','feed_publisher_url','feed_lang','feed_version','feed_contact_email','feed_contact_url']:
        if col in feed_info.columns:
            feed_info[col] = strip_series(feed_info[col])
    for col in ['feed_start_date','feed_end_date']:
        if col in feed_info.columns:
            feed_info[col] = pd.to_datetime(feed_info[col].astype(str), format='%Y%m%d', errors='coerce').dt.date
    print(f"[OK] feed_info limpo: {feed_info.shape}")
else:
    feed_info = None

# ---------- Save processed ----------
save_df(agency, 'agency_clean.csv')
save_df(calendar, 'calendar_clean.csv')
save_df(calendar_dates, 'calendar_dates_clean.csv')
save_df(fare_attributes, 'fare_attributes_clean.csv')
save_df(fare_rules, 'fare_rules_clean.csv')
save_df(feed_info, 'feed_info_clean.csv')
save_df(routes, 'routes_clean.csv')
save_df(shapes, 'shapes_clean.csv')
save_df(stop_times, 'stop_times_clean.csv')
save_df(stops, 'stops_clean.csv')
save_df(trips, 'trips_clean.csv')

# ---------- Quick summary ----------
print("\n=== RESUMO ===")
for name, df in {
    'agency': agency,
    'calendar': calendar,
    'calendar_dates': calendar_dates,
    'fare_attributes': fare_attributes,
    'fare_rules': fare_rules,
    'feed_info': feed_info,
    'routes': routes,
    'shapes': shapes,
    'stop_times': stop_times,
    'stops': stops,
    'trips': trips,
}.items():
    if df is not None:
        print(f"[OK] {name}: {df.shape[0]} linhas")
    else:
        print(f"[--] {name}: não disponível")
