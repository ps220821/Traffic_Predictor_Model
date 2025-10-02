from datetime import timedelta
import pandas as pd
import numpy as np
import re


# Lowercase, remove punctuation, normalize whitespace for location names.
def normalize_name(s: str) -> str:
    if pd.isna(s):
        return ""
    s = str(s).lower()
    s = re.sub(r"[^\w\s]", " ", s)  # remove punctuation
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Check if two location strings share meaningful tokens (ignoring stopwords)
def has_shared_token(name_a, name_b):
    stop = {"naar", "op", "ri", "richt", "richting",
            "knooppnt", "knppnt", "afrit", "knooppunt"}
    a = {t for t in normalize_name(
        name_a).split() if t not in stop and len(t) > 2}
    b = {t for t in normalize_name(
        name_b).split() if t not in stop and len(t) > 2}
    return len(a & b) > 0


direction_mapping = {
    "A2": {"L": "southBound", "R": "northBound"},    # A2 runs north <-> south
    "A50": {"L": "southBound", "R": "northBound"},   # A50 also mainly N <-> S
    "A58": {"L": "westBound", "R": "eastBound"},     # A58 runs west <-> east
    "A67": {"L": "westBound", "R": "eastBound"},     # A67 runs west <-> east
    "N2": {"L": "southBound", "R": "northBound"}     # N2 is parallel to A2
}

# Function to map each row


def map_direction(row):
    road = row["vild_primary_road_number"]
    dir_code = row["vild_primary_direction"]
    if road in direction_mapping and dir_code in direction_mapping[road]:
        return direction_mapping[road][dir_code]
    return "unknown"


STOPWORDS = {  # Stopwords to remove (words that don't add location meaning)
    "knooppunt", "knppnt", "knooppnt", "afrit",
    "naar", "ri", "richt", "richting", "op", "bij", "van", "de", "het"
}


def normalize_ref_text(name: str) -> str:
    if pd.isna(name):
        return "empty"

    s = str(name).lower()

    s = (s.replace("knppnt", "knooppunt")
         .replace("knooppnt", "knooppunt"))
    # Replace slashes with space
    s = s.replace("/", " ")
    # Remove punctuation
    s = re.sub(r"[^\w\s]", " ", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Convert a string into a set of important keys (stopwords removed).
def to_meaningful_keys(s: str) -> set:
    if not s:
        return set()
    tokens = normalize_ref_text(s).split()
    return {t for t in tokens if t not in STOPWORDS and len(t) > 2}


# Check if an intensity record could match a jam record
def possible_match(intensity_row, jam_row):

    # 1) Same road
    if intensity_row["road_code"] != jam_row["vild_primary_road_number"]:
        return False

    # 2) Same direction
    if intensity_row["driving_direction"] != jam_row["driving_direction"]:
        return False

    # 3) Time overlap (jam must cover the measurement window)
    start_i = intensity_row["start_measurement_period"]
    end_i = intensity_row["end_measurement_period"]
    start_j = jam_row["start_time"]
    end_j = jam_row["end_time"] if pd.notna(
        jam_row["end_time"]) else start_j + timedelta(minutes=30)

    # check if jam overlaps with intensity measurement period
    if not (start_j <= end_i and end_j >= start_i):
        return False

    # 4) Location tokens overlap
    if len(intensity_row["location_tokens"] & jam_row["vild_primary_tokens"]) == 0:
        return False

    return True


def token_overlap(row):  # Check if two token sets (measurement vs jam) overlap

    a = row["location_tokens"]
    b = row["vild_primary_tokens"]
    return len(a & b) > 0
