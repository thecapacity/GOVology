#!/usr/bin/env python3
"""Quick CSV diff tool using pandas - written with some (but not all) help from Claude"""
import sys
import pandas as pd


def check_columns(file1, file2):
    df1 = pd.read_csv(file1, nrows=0)  # just headers
    df2 = pd.read_csv(file2, nrows=0)

    cols1, cols2 = set(df1.columns), set(df2.columns)
    if cols1 != cols2:
        print("⚠️  Column mismatch — will compare on common columns only")
        if cols1 - cols2:
            print(f"  Only in {file1}: {cols1 - cols2}")
        if cols2 - cols1:
            print(f"  Only in {file2}: {cols2 - cols1}")
    else:
        print(f"✅ Columns match ({len(cols1)} columns)")

def load(filepath):
    df = pd.read_csv(filepath, dtype=str, index_col="initial_domain", keep_default_na=False)
    df = df[~df.index.duplicated(keep="first")]
    return df

def diff_csvs(file1, file2, details=False):
    df_old = load(file1)
    df_new = load(file2)

    # Align to common columns if there's a mismatch
    common_cols = df_old.columns.intersection(df_new.columns)
    df_old = df_old[common_cols]
    df_new = df_new[common_cols]

    for name in df_old.index.difference(df_new.index):
        print(f"❌ DELETED: {name}")

    for name in df_new.index.difference(df_old.index):
        print(f"✅ ADDED:   {name}")

    if details:
        for name in df_old.index.intersection(df_new.index):
            old_row, new_row = df_old.loc[name], df_new.loc[name]
            for field in old_row.index[old_row != new_row]:
                print(f"⚠️  CHANGED [{name}] {field}: {old_row[field]!r} → {new_row[field]!r}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python csv_diff.py file1.csv file2.csv")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]
    print(f"Checking files: {file1} and {file2}\n")

    if check_columns(file1, file2):
        diff_csvs(file1, file2)
