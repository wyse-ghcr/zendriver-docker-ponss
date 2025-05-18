import asyncio
import os
import subprocess
import requests
import zipfile
import schedule
import time
import random

import zendriver as zd


async def start_browser() -> zd.Browser:
    if not os.path.isdir("ubo_lite"):
        print("Downloading latest uBlock Origin Lite release...")
        resp = requests.get("https://api.github.com/repos/uBlockOrigin/uBOL-home/releases/latest")
        data = resp.json()
        for element in data["assets"]:
            if "chromium" in element["browser_download_url"]:
                ubo_lite_zip_resp = requests.get(element["browser_download_url"])
                with open("ubo_lite.zip", "wb") as file:
                    file.write(ubo_lite_zip_resp.content)
        os.mkdir("ubo_lite")
        ubo_lit_zip = zipfile.ZipFile("ubo_lite.zip")
        ubo_lit_zip.extractall("ubo_lite")
        ubo_lit_zip.close()
        print("uBlock Origin Lite successfully downloaded and unzipped!")
    browser = await zd.start(
        browser_args=["--enable-features=UseOzonePlatform", "--ozone-platform=wayland", "--load-extension=/app/ubo_lite"],
    )
    return browser

async def refresh_codes(page) -> None:
    delay = random.randint(1, 3600)
    print(f"Refreshing codes in {delay/60} min...")
    await asyncio.sleep(delay)
    refresh_codes_button = await page.select("form[action='/account/updateusercodes'] > button[type='submit']")
    await refresh_codes_button.click()
    print("Codes refreshed!")

def run_refresh_codes(page) -> None:
    asyncio.create_task(refresh_codes(page))

async def main() -> None:
    print(f"Zendriver Docker Ponss Starting (zendriver {zd.__version__})")
    chrome_version = " ".join(
        (
            subprocess.run(
                ["google-chrome-stable", "--version"], stdout=subprocess.PIPE
            )
            .stdout.decode("utf-8")
            .split(" ")[:3]
        )
    )
    print(
        f"{chrome_version} {os.uname().machine} ({os.uname().sysname} {os.uname().release})\n"
    )

    print("Starting browser...")
    browser = await start_browser()
    print("Browser successfully started!")

    print("Opening login page...")
    page = await browser.get("https://www.ponss.it/account/login")
    await asyncio.sleep(0.5)
    print("Login page successfully opened!")
    username_input = await page.select("#UserName")
    password_input = await page.select("#Password")
    login_button = await page.select("form[action='/account/login'] > button[type='submit']")
    print(f"Logging in user ({os.environ["PONSS_USER"]})...")
    await username_input.send_keys(os.environ["PONSS_USER"])
    await password_input.send_keys(os.environ["PONSS_PASS"])
    await login_button.click()
    await asyncio.sleep(0.5)
    print("User successfully logged in!")
    page = await browser.get("https://www.ponss.it/account/codes")
    await asyncio.sleep(0.5)
    await page.evaluate("window.confirm = function(msg) { return true; };")
    print("Scheduling jobs...")
    schedule.every().day.at(os.environ["PONSS_REFRESH_TIME_01"]).do(run_refresh_codes, page)
    schedule.every().day.at(os.environ["PONSS_REFRESH_TIME_02"]).do(run_refresh_codes, page)
    schedule.every().day.at(os.environ["PONSS_REFRESH_TIME_03"]).do(run_refresh_codes, page)
    schedule.every().day.at(os.environ["PONSS_REFRESH_TIME_04"]).do(run_refresh_codes, page)
    print("Jobs scheduled!")

    print("Zendriver Docker Ponss successfully started!")

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
