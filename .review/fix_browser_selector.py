"""Small reviewed follow-up to the original hash-locked browser candidate."""
from pathlib import Path
import sys

path = Path(sys.argv[1]) / "scripts/verify_browser_workflows.py"
text = path.read_text(encoding="utf-8")
old = '                    page.get_by_label("Use the built-in sample", exact=True).check()'
new = '''                    page.get_by_text("Use the built-in sample", exact=True).click()
                    expect(page.get_by_label("Use the built-in sample", exact=True)).to_be_checked()'''
assert text.count(old) == 1
text = text.replace(old, new)
old = '''                finally:
                    browser.close()'''
new = '''                except Exception:
                    if "page" in locals() and not page.is_closed():
                        try:
                            page.screenshot(path=str(output / "failure.png"), full_page=True)
                            (output / "failure.html").write_text(page.content(), encoding="utf-8")
                            (output / "failure-text.txt").write_text(page.locator("body").inner_text(), encoding="utf-8")
                        except Exception as capture_error:
                            print(f"Failure capture unavailable: {capture_error}", file=sys.stderr)
                    raise
                finally:
                    browser.close()'''
assert text.count(old) == 1
text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
