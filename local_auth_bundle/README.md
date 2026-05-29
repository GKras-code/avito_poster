# Avito Local Auth Bundle

Recommended Windows flow:

1. Run `AvitoLocalAuth.exe`.
2. Log in to Avito in the opened browser.
3. Return to the window and press Enter.
4. Upload `avito_auth_bundle.zip` to the website.

If the exe has not been built yet, fallback developer flow:

1. Install Python 3.11 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Run the script:
   `python avito_local_auth.py`

The script first tries local Microsoft Edge or Google Chrome. Only if they are unavailable it falls back to Playwright Chromium.