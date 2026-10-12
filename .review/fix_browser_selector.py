"""Reviewed browser harness corrections; no application checks are skipped."""
from pathlib import Path
import sys

path = Path(sys.argv[1]) / "scripts/verify_browser_workflows.py"
if not path.exists():
    # The old utility workflow invokes this once before applying the candidate.
    # There is nothing to edit until the candidate file exists.
    raise SystemExit(0)
text = path.read_text(encoding="utf-8")
def replace(old, new):
    global text
    assert text.count(old) == 1, old
    text = text.replace(old, new)
replace('                    page.get_by_label("Use the built-in sample", exact=True).check()', '''                    page.get_by_text("Use the built-in sample", exact=True).click()
                    expect(page.get_by_label("Use the built-in sample", exact=True)).to_be_checked()
                    settled()''')
replace('                    def tab(name):', '''                    def settled():
                        # Observe the real frontend lifecycle, not an arbitrary sleep
                        # or a replacement data-loading path. Require a stable idle
                        # interval so a queued rerun cannot discard the next upload.
                        page.evaluate("window.__reviewIdleSince = null")
                        page.wait_for_function("""() => {
                            const app = document.querySelector('[data-testid="stApp"]');
                            const idle = app && app.dataset.testConnectionState === 'CONNECTED'
                                && app.dataset.testScriptState === 'notRunning';
                            if (!idle) { window.__reviewIdleSince = null; return false; }
                            if (window.__reviewIdleSince === null) window.__reviewIdleSince = performance.now();
                            return performance.now() - window.__reviewIdleSince >= 600;
                        }""", timeout=30000)
                        expect(page.get_by_test_id("stException")).to_have_count(0)
                    def upload(label, file):
                        settled()
                        widget = page.get_by_test_id("stFileUploader").filter(
                            has=page.get_by_text(label, exact=True))
                        widget.locator('input[type="file"]').set_input_files(file)
                        expect(widget.get_by_text(file.name, exact=True)).to_be_visible()
                        settled()
                        expect(widget.get_by_text(file.name, exact=True)).to_be_visible()
                    def tab(name):''')
replace('                        page.get_by_role("tab", name=name, exact=True).click()', '''                        settled()
                        page.get_by_role("tab", name=name, exact=True).click()''')
replace('                        page.get_by_role("option", name=value, exact=True).click()', '''                        page.get_by_role("option", name=value, exact=True).click()
                        expect(widget.get_by_role("combobox")).to_have_value(value)
                        settled()''')
text = text.replace('page.locator(\'input[type="file"]\').nth(0).set_input_files(inputs / "invalid.csv")', 'upload("CSV or Excel", inputs / "invalid.csv")')
replace('page.locator(\'input[type="file"]\').nth(0).set_input_files(inputs / "current.xlsx")', 'upload("CSV or Excel", inputs / "current.xlsx")')
replace('                    select("Worksheet", "Current")', '''                    select("Worksheet", "Current")
                    expect(page.get_by_text("Source: current.xlsx", exact=False)).to_contain_text("sheet: Current")
                    settled()''')
replace('page.locator(\'input[type="file"]\').nth(1).set_input_files(inputs / "baseline.xlsx")', 'upload("Previous baseline (optional)", inputs / "baseline.xlsx")')
replace('page.locator(\'input[type="file"]\').nth(2).set_input_files(inputs / "rules.json")', 'upload("Load a RowSpect rule profile", inputs / "rules.json")')
replace('page.locator(\'input[type="file"]\').nth(2).set_input_files(downloads / "profile.json")', 'upload("Load a RowSpect rule profile", downloads / "profile.json")')
replace('''                finally:
                    browser.close()''', '''                except Exception:
                    import traceback
                    (output / "failure-traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")
                    if "page" in locals() and not page.is_closed():
                        try:
                            page.screenshot(path=str(output / "failure.png"), full_page=True)
                            (output / "failure.html").write_text(page.content(), encoding="utf-8")
                            (output / "failure-text.txt").write_text(page.locator("body").inner_text(), encoding="utf-8")
                        except Exception as capture_error:
                            print(f"Failure capture unavailable: {capture_error}", file=sys.stderr)
                    raise
                finally:
                    browser.close()''')
compile(text, str(path), "exec")
path.write_text(text, encoding="utf-8")
