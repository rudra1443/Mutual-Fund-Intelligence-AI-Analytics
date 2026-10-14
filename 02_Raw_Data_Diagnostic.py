from pathlib import Path
import re
import pandas as pd

# =====================================================
# FULL RAW FILE DIAGNOSTIC
# Scans every TXT file; does not modify raw data
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "data"
OUTPUT_FOLDER = PROJECT_ROOT / "output"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

TARGET_PATTERN = re.compile(r"\bMULTI[\s-]*CAP\b", re.IGNORECASE)


def read_text_file(path):
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return path.read_text(encoding=encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
        except OSError as error:
            return None
    return None


def analyse_file(path):
    text = read_text_file(path)

    result = {
        "File": path.name,
        "Folder": path.parent.name,
        "Relative_Path": str(path.relative_to(PROJECT_ROOT)),
        "Bytes": path.stat().st_size,
        "Total_Lines": 0,
        "Header_Found": False,
        "Parsed_Data_Rows": 0,
        "MultiCap_Rows": 0,
        "Direct_Growth_MultiCap_Rows": 0,
        "First_Target_Date": "",
        "Last_Target_Date": "",
        "Sample_Target_Schemes": "",
        "Status": "",
        "Error": "",
    }

    if text is None:
        result["Status"] = "READ_ERROR"
        return result

    lines = [
        line.strip().lstrip("\ufeff")
        for line in text.splitlines()
        if line.strip()
    ]

    result["Total_Lines"] = len(lines)

    # Find the actual AMFI column header, even if
    # category/title lines appear before it.
    header_index = None

    for index, line in enumerate(lines):
        upper = line.upper()

        if "SCHEME CODE" in upper and "NAV NAME" in upper:
            header_index = index
            result["Header_Found"] = True
            break

    # Scan all relevant lines for semicolon-separated records.
    # Expected AMFI data row:
    # Code;NAV Name;Plan;Option;ISIN;ISIN;NAV;Date

    scan_lines = (
        lines[header_index + 1:]
        if header_index is not None
        else lines
    )

    parsed_rows = []
    target_names = []
    target_dates = []
    direct_growth_count = 0

    for line in scan_lines:
        cells = [value.strip() for value in line.split(";")]

        # Need at least 8 columns and a numeric scheme code.
        if len(cells) < 8:
            continue

        if not re.fullmatch(r"\d+", cells[0]):
            continue

        result["Parsed_Data_Rows"] += 1
        parsed_rows.append(cells)

        scheme_name = cells[1]
        combined = " ".join(cells[:4]).upper()

        # Match Multi Cap / Multicap only.
        # Does not match Mid Cap or Multi Asset.
        if not TARGET_PATTERN.search(scheme_name):
            continue

        result["MultiCap_Rows"] += 1

        if scheme_name and scheme_name not in target_names:
            target_names.append(scheme_name)

        # Plan and option may appear in separate columns.
        if (
            "DIRECT" in combined
            and "GROWTH" in combined
            and "IDCW" not in combined
        ):
            direct_growth_count += 1

            if len(cells) >= 8:
                target_dates.append(cells[7])

    result["Direct_Growth_MultiCap_Rows"] = direct_growth_count

    valid_dates = pd.to_datetime(
        pd.Series(target_dates, dtype="string"),
        errors="coerce",
        dayfirst=True
    ).dropna()

    if not valid_dates.empty:
        result["First_Target_Date"] = (
            valid_dates.min().strftime("%Y-%m-%d")
        )
        result["Last_Target_Date"] = (
            valid_dates.max().strftime("%Y-%m-%d")
        )

    result["Sample_Target_Schemes"] = " || ".join(target_names[:10])

    if result["Parsed_Data_Rows"] == 0:
        result["Status"] = "NO_PARSEABLE_NAV_ROWS"
    elif result["MultiCap_Rows"] == 0:
        result["Status"] = "MULTICAP_NOT_FOUND"
    elif direct_growth_count == 0:
        result["Status"] = "DIRECT_GROWTH_NOT_CONFIRMED"
    else:
        result["Status"] = "TARGET_ROWS_FOUND"

    if not result["Header_Found"]:
        result["Error"] = "STANDARD_HEADER_NOT_FOUND"

    return result


# Scan ALL TXT files; do not filter AMC folders.
txt_files = sorted(
    path for path in DATA_FOLDER.rglob("*")
    if path.is_file() and path.suffix.lower() == ".txt"
)

print("=" * 75)
print("FULL MUTUAL FUND RAW DATA DIAGNOSTIC")
print("=" * 75)
print("Project:", PROJECT_ROOT)
print("Data folder:", DATA_FOLDER)
print("TXT files found:", len(txt_files))

results = []

for number, path in enumerate(txt_files, start=1):
    item = analyse_file(path)
    results.append(item)

    print(
        f"[{number}/{len(txt_files)}] "
        f"{item['File']} | "
        f"Rows={item['Parsed_Data_Rows']} | "
        f"MultiCap={item['MultiCap_Rows']} | "
        f"DirectGrowth={item['Direct_Growth_MultiCap_Rows']} | "
        f"{item['Status']}"
    )

report = pd.DataFrame(results)

report_path = OUTPUT_FOLDER / "Raw_Data_Diagnostic_Report.csv"
report.to_csv(report_path, index=False, encoding="utf-8-sig")

print("\n" + "=" * 75)
print("DIAGNOSTIC SUMMARY")
print("=" * 75)
print("Files scanned:", len(results))

if not report.empty:
    print("\nStatus counts:")
    print(report["Status"].value_counts().to_string())

    print("\nFiles with issues:")
    issue_rows = report[
        report["Status"] != "TARGET_ROWS_FOUND"
    ]

    if issue_rows.empty:
        print("None")
    else:
        print(
            issue_rows[
                [
                    "File",
                    "Parsed_Data_Rows",
                    "MultiCap_Rows",
                    "Direct_Growth_MultiCap_Rows",
                    "Status",
                    "Error",
                ]
            ].to_string(index=False)
        )

print("\nReport saved to:")
print(report_path)
print("=" * 75)