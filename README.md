# Skyfellows

This simple Python script will fetch stats about all the accounts you're following on Bluesky, including when each account was last active (ie. posted something). This can be helpful for managing your Following feed and removing dormant accounts (sorting the list by last active to identify them).

## How to install & run

This has been tested on Python 3.11.5 but not extensively on other versions. Your mileage may vary. 

### 1. Install dependencies

`pip3 install -r requirements.txt`

### 2. Edit Bluesky credentials

Open `app.py` and edit Lines 61 & 62 (as shown below) with your Bluesky credentials. This will be your handle and a unique [app password that you can generate here.](https://bsky.app/settings/app-passwords)

```
# Bluesky login credentials
BLUESKY_HANDLE = "example.bsky.social"
BLUESKY_APP_PASSWORD = "xxxx-xxxx-xxxx-xxxx"
```

Once edited, save and close the `app.py` file.

### 3. Run the script

Run the script from your terminal:

`python3 app.py`

This will begin the process, which may take a while depending on how many users you follow. **Warning:** Bluesky rate limits at 5000 API requests per 5 minutes, so you may encounter errors if you follow over 1,500 accounts. This should not impact most users.

### 4. Open the follows.html page

Once the script is completed, it will tell you that it's successfully built the page and written it to `follows.html`

Find this file in the folder alongside where you stored the script and open it in your web browser. You can now sort the columns by clicking on the table headers. Enjoy!

## The MIT License (MIT)
Copyright (c) 2023 feditrends

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
