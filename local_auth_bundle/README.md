# Avito Local Auth Bundle

1. Install Python 3.11 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Install Chromium for Playwright:
   `python -m playwright install chromium`
5. Run the script:
   `python avito_local_auth.py`
6. Log in to Avito in the opened browser.
7. Return to the terminal and press Enter.
8. Upload the created `avito_auth_bundle.zip` file to the website.

The script saves only reusable session files:
- `avito_storage_state.json`
- `avito_cookies.json`