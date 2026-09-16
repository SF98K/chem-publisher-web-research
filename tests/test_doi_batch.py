"""Offline checks for DOI batch manifest preparation."""

import csv
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "prepare_doi_batch.py"
RECORDER = Path(__file__).parents[1] / "scripts" / "record_doi_result.py"


class DoiBatchTests(unittest.TestCase):
    def run_tool(self, source, manifest):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(source), "--output", str(manifest)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_csv_normalizes_deduplicates_and_preserves_source_row(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.csv"
            manifest = Path(directory) / "manifest.csv"
            source.write_text(
                "Title,DOI\nA,https://doi.org/10.1000/ABC.1\nB,doi:10.1000/abc.1\nC,10.5555/xyz.\nD,\n",
                encoding="utf-8",
            )
            result = self.run_tool(source, manifest)
            self.assertEqual(result.returncode, 0, result.stderr)
            with manifest.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row["doi"] for row in rows], ["10.1000/abc.1", "10.5555/xyz."])
            self.assertEqual([row["source_row"] for row in rows], ["2", "4"])
            self.assertEqual([row["status"] for row in rows], ["pending", "pending"])

    def test_xlsx_reads_doi_column_case_insensitively(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.xlsx"
            manifest = Path(directory) / "manifest.csv"
            self.write_minimal_xlsx(source)
            result = self.run_tool(source, manifest)
            self.assertEqual(result.returncode, 0, result.stderr)
            with manifest.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["doi"], "10.1038/example.2")
            self.assertEqual(rows[0]["source_row"], "2")

    def test_recorder_updates_one_manifest_row(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.csv"
            manifest = Path(directory) / "manifest.csv"
            source.write_text("doi\n10.1000/example\n", encoding="utf-8")
            pdf = Path(directory) / "example.pdf"
            pdf.write_bytes(b"%PDF-1.7\n%%EOF")
            self.assertEqual(self.run_tool(source, manifest).returncode, 0)
            result = subprocess.run(
                [
                    sys.executable, str(RECORDER), "--manifest", str(manifest),
                    "--source-row", "2", "--status", "downloaded",
                    "--publisher", "ACS Publications", "--pdf-path", str(pdf),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with manifest.open(encoding="utf-8", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["status"], "downloaded")
            self.assertEqual(row["publisher"], "ACS Publications")
            self.assertEqual(row["pdf_path"], str(pdf.resolve()))

    def test_rerun_preserves_existing_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.csv"
            manifest = Path(directory) / "manifest.csv"
            source.write_text("doi\n10.1000/example\n", encoding="utf-8")
            manifest.write_text("existing progress", encoding="utf-8")
            self.assertNotEqual(self.run_tool(source, manifest).returncode, 0)
            self.assertEqual(manifest.read_text(), "existing progress")

    def test_doi_preserves_suffix_and_encodes_url(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.csv"
            manifest = Path(directory) / "manifest.csv"
            source.write_text("doi\n10.1000/a(1)\n10.1000/a#b\n10.foo/bar\n", encoding="utf-8")
            self.assertEqual(self.run_tool(source, manifest).returncode, 0)
            with manifest.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["doi"], "10.1000/a(1)")
            self.assertEqual(rows[1]["doi_url"], "https://doi.org/10.1000/a%23b")
            self.assertEqual(rows[2]["status"], "invalid-doi")

    def test_xlsx_sparse_row_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.xlsx"
            self.write_minimal_xlsx(source)
            with zipfile.ZipFile(source) as archive:
                entries = {name: archive.read(name) for name in archive.namelist()}
            sheet = "xl/worksheets/sheet1.xml"
            entries[sheet] = entries[sheet].replace(b'r="2"', b'r="8"').replace(b'r="A2"', b'r="A8"')
            with zipfile.ZipFile(source, "w") as archive:
                for name, content in entries.items():
                    archive.writestr(name, content)
            manifest = Path(directory) / "manifest.csv"
            self.assertEqual(self.run_tool(source, manifest).returncode, 0)
            with manifest.open(encoding="utf-8") as handle:
                self.assertEqual(next(csv.DictReader(handle))["source_row"], "8")

    def test_html_cannot_be_recorded_as_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.csv"
            manifest = Path(directory) / "manifest.csv"
            source.write_text("doi\n10.1000/example\n", encoding="utf-8")
            self.assertEqual(self.run_tool(source, manifest).returncode, 0)
            before = manifest.read_bytes()
            pdf = Path(directory) / "login.pdf"
            pdf.write_text("<html>Login</html>")
            result = subprocess.run([sys.executable, str(RECORDER), "--manifest", str(manifest), "--source-row", "2", "--status", "downloaded", "--pdf-path", str(pdf)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(manifest.read_bytes(), before)

    @staticmethod
    def write_minimal_xlsx(path):
        entries = {
            "[Content_Types].xml": """<?xml version=\"1.0\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"><Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/><Default Extension=\"xml\" ContentType=\"application/xml\"/><Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/><Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/><Override PartName=\"/xl/sharedStrings.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml\"/></Types>""",
            "_rels/.rels": """<?xml version=\"1.0\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/></Relationships>""",
            "xl/workbook.xml": """<?xml version=\"1.0\"?><workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"Sheet1\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>""",
            "xl/_rels/workbook.xml.rels": """<?xml version=\"1.0\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/></Relationships>""",
            "xl/sharedStrings.xml": """<?xml version=\"1.0\"?><sst xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" count=\"2\" uniqueCount=\"2\"><si><t>doi</t></si><si><t>https://doi.org/10.1038/EXAMPLE.2</t></si></sst>""",
            "xl/worksheets/sheet1.xml": """<?xml version=\"1.0\"?><worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData><row r=\"1\"><c r=\"A1\" t=\"s\"><v>0</v></c></row><row r=\"2\"><c r=\"A2\" t=\"s\"><v>1</v></c></row></sheetData></worksheet>""",
        }
        with zipfile.ZipFile(path, "w") as archive:
            for name, content in entries.items():
                archive.writestr(name, content)


if __name__ == "__main__":
    unittest.main()
