from pathlib import Path
import pandas as pd


# ============================================================
# MUTUAL FUND PERFORMANCE INTELLIGENCE
# RAW DATA AUDIT - FINAL VERSION
# ============================================================

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Main folders
DATA_FOLDER = PROJECT_ROOT / "data"
OUTPUT_FOLDER = PROJECT_ROOT / "output"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# AMC IDENTIFICATION
# ============================================================

AMC_KEYWORDS = {
    "SBI": "SBI",
    "HDFC": "HDFC",
    "ICICI": "ICICI",
    "NIPPON": "NIPPON",
    "KOTAK": "KOTAK",
    "ADITYA": "ADITYA_BIRLA",
    "BIRLA": "ADITYA_BIRLA",
    "AXIS": "AXIS",
    "UTI": "UTI"
}


def identify_amc(file_path):

    text = str(file_path).upper()

    for keyword, amc_name in AMC_KEYWORDS.items():

        if keyword in text:
            return amc_name

    return "UNKNOWN"


# ============================================================
# READ AMFI TXT FILE
# ============================================================

def read_amfi_file(file_path):

    encodings = [
        "utf-8",
        "utf-8-sig",
        "latin1"
    ]

    for encoding in encodings:

        try:

            df = pd.read_csv(
                file_path,
                sep=";",
                dtype=str,
                encoding=encoding,
                on_bad_lines="skip"
            )

            df.columns = [
                str(column).strip()
                for column in df.columns
            ]

            return df

        except Exception:
            continue

    return None


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(columns, keyword):

    for column in columns:

        if keyword in str(column).upper():

            return column

    return None


# ============================================================
# FIND ALL TXT FILES
# ============================================================

txt_files = sorted(
    DATA_FOLDER.rglob("*.txt")
)


print()
print("=" * 80)
print("MUTUAL FUND RAW DATA AUDIT")
print("=" * 80)

print()
print(f"Project Folder : {PROJECT_ROOT}")
print(f"Data Folder    : {DATA_FOLDER}")
print(f"TXT Files Found: {len(txt_files)}")
print()


# ============================================================
# NO FILE CHECK
# ============================================================

if len(txt_files) == 0:

    print("ERROR: No TXT files found.")
    print()
    print("Expected structure:")
    print("data/")
    print("   AMC folders")
    print("   raw/")
    print("       TXT files")
    print()

    raise SystemExit


# ============================================================
# AUDIT STORAGE
# ============================================================

audit_results = []


total_raw_rows = 0
total_multicap_rows = 0
total_direct_growth_rows = 0
total_invalid_nav = 0
total_duplicate_rows = 0


# ============================================================
# PROCESS EVERY FILE
# ============================================================

for file_number, file_path in enumerate(txt_files, start=1):

    print(
        f"[{file_number}/{len(txt_files)}] "
        f"Checking: {file_path.name}"
    )

    # --------------------------------------------------------
    # BASIC INFO
    # --------------------------------------------------------

    amc = identify_amc(file_path)

    result = {

        "File_Name": file_path.name,

        "Relative_Path": str(
            file_path.relative_to(PROJECT_ROOT)
        ),

        "AMC": amc,

        "Total_Rows": 0,

        "MultiCap_Rows": 0,

        "Direct_Growth_Rows": 0,

        "First_Date": "",

        "Last_Date": "",

        "Invalid_NAV_Rows": 0,

        "Duplicate_Rows": 0,

        "Status": "CHECK"

    }


    # --------------------------------------------------------
    # READ FILE
    # --------------------------------------------------------

    df = read_amfi_file(file_path)


    if df is None:

        result["Status"] = "READ_ERROR"

        audit_results.append(result)

        continue


    # --------------------------------------------------------
    # REMOVE EMPTY ROWS
    # --------------------------------------------------------

    df = df.dropna(
        how="all"
    ).copy()


    result["Total_Rows"] = len(df)

    total_raw_rows += len(df)


    # --------------------------------------------------------
    # FIND IMPORTANT COLUMNS
    # --------------------------------------------------------

    nav_name_col = find_column(
        df.columns,
        "NAV NAME"
    )

    nav_value_col = find_column(
        df.columns,
        "NET ASSET VALUE"
    )

    date_col = None

    for column in df.columns:

        upper_column = str(column).upper().strip()

        if upper_column == "DATE":

            date_col = column
            break


    # --------------------------------------------------------
    # COLUMN VALIDATION
    # --------------------------------------------------------

    if nav_name_col is None:

        result["Status"] = "NAV_NAME_COLUMN_MISSING"

        audit_results.append(result)

        continue


    # --------------------------------------------------------
    # CLEAN NAV NAME
    # --------------------------------------------------------

    df[nav_name_col] = (
        df[nav_name_col]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )


    # ========================================================
    # MULTI CAP DETECTION
    # ========================================================

    # Handles both:
    #
    # MULTI CAP FUND
    # MULTICAP FUND
    #
    # This is important because AMC naming differs.

    multi_cap_mask = (
        df[nav_name_col]
        .str.contains(
            "MULTI CAP FUND",
            regex=False,
            na=False
        )
        |
        df[nav_name_col]
        .str.contains(
            "MULTICAP FUND",
            regex=False,
            na=False
        )
    )


    multi_cap_df = df[
        multi_cap_mask
    ].copy()


    result["MultiCap_Rows"] = len(
        multi_cap_df
    )

    total_multicap_rows += len(
        multi_cap_df
    )


    # ========================================================
    # DIRECT + GROWTH DETECTION
    # ========================================================

    direct_mask = (
        multi_cap_df[nav_name_col]
        .str.contains(
            "DIRECT PLAN",
            regex=False,
            na=False
        )
    )


    growth_mask = (
        multi_cap_df[nav_name_col]
        .str.contains(
            "GROWTH",
            regex=False,
            na=False
        )
    )


    direct_growth_df = multi_cap_df[
        direct_mask & growth_mask
    ].copy()


    result["Direct_Growth_Rows"] = len(
        direct_growth_df
    )

    total_direct_growth_rows += len(
        direct_growth_df
    )


    # ========================================================
    # DATE ANALYSIS
    # ========================================================

    if (
        date_col is not None
        and len(direct_growth_df) > 0
    ):

        dates = pd.to_datetime(
            direct_growth_df[date_col],
            errors="coerce",
            dayfirst=True
        )


        valid_dates = dates.dropna()


        if len(valid_dates) > 0:

            result["First_Date"] = (
                valid_dates
                .min()
                .strftime("%Y-%m-%d")
            )

            result["Last_Date"] = (
                valid_dates
                .max()
                .strftime("%Y-%m-%d")
            )


    # ========================================================
    # NAV VALIDATION
    # ========================================================

    if (
        nav_value_col is not None
        and len(direct_growth_df) > 0
    ):

        nav_values = pd.to_numeric(

            direct_growth_df[nav_value_col]
            .astype(str)
            .str.replace(
                ",",
                "",
                regex=False
            )
            .str.strip(),

            errors="coerce"
        )


        invalid_nav_mask = (
            nav_values.isna()
            |
            (nav_values <= 0)
        )


        invalid_count = int(
            invalid_nav_mask.sum()
        )


        result["Invalid_NAV_Rows"] = (
            invalid_count
        )


        total_invalid_nav += (
            invalid_count
        )


    # ========================================================
    # DUPLICATE CHECK
    # ========================================================

    duplicate_columns = []


    if date_col is not None:

        duplicate_columns.append(
            date_col
        )


    if nav_name_col is not None:

        duplicate_columns.append(
            nav_name_col
        )


    if (
        len(duplicate_columns) >= 2
        and len(direct_growth_df) > 0
    ):

        duplicate_count = int(
            direct_growth_df
            .duplicated(
                subset=duplicate_columns,
                keep=False
            )
            .sum()
        )


        result["Duplicate_Rows"] = (
            duplicate_count
        )


        total_duplicate_rows += (
            duplicate_count
        )


    # ========================================================
    # FINAL STATUS
    # ========================================================

    if result["Direct_Growth_Rows"] == 0:

        result["Status"] = (
            "NO_DIRECT_GROWTH_MULTICAP"
        )


    elif result["Invalid_NAV_Rows"] > 0:

        result["Status"] = (
            "INVALID_NAV"
        )


    else:

        result["Status"] = "PASS"


    audit_results.append(result)


# ============================================================
# CREATE DATAFRAME
# ============================================================

audit_df = pd.DataFrame(
    audit_results
)


# ============================================================
# SAVE REPORT
# ============================================================

audit_file = (
    OUTPUT_FOLDER
    /
    "Raw_Data_Audit_Report.csv"
)


audit_df.to_csv(
    audit_file,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)

print()
print(
    f"Total TXT Files        : {len(txt_files)}"
)

print(
    f"Total Raw Rows         : {total_raw_rows:,}"
)

print(
    f"Total MultiCap Rows    : {total_multicap_rows:,}"
)

print(
    f"Total Direct Growth    : {total_direct_growth_rows:,}"
)

print(
    f"Invalid NAV Rows       : {total_invalid_nav:,}"
)

print(
    f"Duplicate Rows         : {total_duplicate_rows:,}"
)


# ============================================================
# STATUS SUMMARY
# ============================================================

print()
print("=" * 80)
print("STATUS SUMMARY")
print("=" * 80)

status_summary = (
    audit_df[
        "Status"
    ]
    .value_counts()
)


for status, count in status_summary.items():

    print(
        f"{status:<35} : {count}"
    )


# ============================================================
# AMC SUMMARY
# ============================================================

print()
print("=" * 80)
print("AMC SUMMARY")
print("=" * 80)


amc_summary = (
    audit_df
    .groupby("AMC")
    .agg(

        Files=(
            "File_Name",
            "count"
        ),

        Raw_Rows=(
            "Total_Rows",
            "sum"
        ),

        MultiCap_Rows=(
            "MultiCap_Rows",
            "sum"
        ),

        Direct_Growth_Rows=(
            "Direct_Growth_Rows",
            "sum"
        ),

        Invalid_NAV=(
            "Invalid_NAV_Rows",
            "sum"
        ),

        Duplicate_Rows=(
            "Duplicate_Rows",
            "sum"
        )

    )
    .reset_index()
)


print(
    amc_summary.to_string(
        index=False
    )
)


# ============================================================
# FILE REPORT
# ============================================================

print()
print("=" * 80)
print("FILE STATUS")
print("=" * 80)


for _, row in audit_df.iterrows():

    print(
        f"{row['AMC']:<15} | "
        f"{row['File_Name']:<45} | "
        f"{row['Status']}"
    )


# ============================================================
# FINAL REPORT LOCATION
# ============================================================

print()
print("=" * 80)

print(
    "Report created:"
)

print(
    audit_file
)

print()
print(
    "NEXT: Open Raw_Data_Audit_Report.csv"
)

print("=" * 80)