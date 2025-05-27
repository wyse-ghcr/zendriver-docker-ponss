import asyncio
import os
import subprocess
import requests
import zipfile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
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
    print(f"Root user: {os.geteuid() == 0}")
    browser = None
    while browser is None:
        try:
            browser = await zd.start(
                browser_args=["--enable-features=UseOzonePlatform", "--ozone-platform=wayland", "--load-extension=/app/ubo_lite"],
                no_sandbox=os.geteuid() == 0
            )
        except:
            print("Failed to start browser, retrying...")
            await asyncio.sleep(4)
    return browser

async def refresh_codes() -> None:
    print("Starting browser...")
    browser = await start_browser()
    print("Browser successfully started!")

    print("Opening login page...")
    page = await browser.get("https://www.ponss.it/account/login")
    await page.wait(0.5)
    print("Login page successfully opened!")
    username_input = await page.select("#UserName")
    password_input = await page.select("#Password")
    login_button = await page.select("form[action='/account/login'] > button[type='submit']")
    print(f"Logging in user ({os.environ["PONSS_USER"]})...")
    await username_input.send_keys(os.environ["PONSS_USER"])
    await password_input.send_keys(os.environ["PONSS_PASS"])
    await login_button.click()
    await page.wait(0.5)
    page = await browser.get("https://www.ponss.it/account/codes")
    await page.wait(0.5)
    print("User successfully logged in!")

    print("Refreshing codes...")
    await page.evaluate("window.confirm = function(msg) { return true; };")
    refresh_codes_button = await page.select("form[action='/account/updateusercodes'] > button[type='submit']")
    await refresh_codes_button.click()
    await page.wait(2)
    print("Codes refreshed!")

    print("Closing browser...")
    await browser.stop()
    print("Broser closed!")

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

    print("Scheduling jobs...")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(refresh_codes, 'cron', hour=os.environ["PONSS_REFRESH_TIME_01"].split(":")[0], minute=os.environ["PONSS_REFRESH_TIME_01"].split(":")[1], jitter=int(os.environ["JOB_JITTER"]))
    scheduler.add_job(refresh_codes, 'cron', hour=os.environ["PONSS_REFRESH_TIME_02"].split(":")[0], minute=os.environ["PONSS_REFRESH_TIME_02"].split(":")[1], jitter=int(os.environ["JOB_JITTER"]))
    scheduler.add_job(refresh_codes, 'cron', hour=os.environ["PONSS_REFRESH_TIME_03"].split(":")[0], minute=os.environ["PONSS_REFRESH_TIME_03"].split(":")[1], jitter=int(os.environ["JOB_JITTER"]))
    scheduler.add_job(refresh_codes, 'cron', hour=os.environ["PONSS_REFRESH_TIME_04"].split(":")[0], minute=os.environ["PONSS_REFRESH_TIME_04"].split(":")[1], jitter=int(os.environ["JOB_JITTER"]))
    scheduler.start()
    print("Jobs scheduled!")
    print("Zendriver Docker Ponss successfully started!")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
