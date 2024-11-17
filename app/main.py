import asyncio
import os
import subprocess

import zendriver as zd


async def start_browser() -> zd.Browser:
    browser = await zd.start(
        # use wayland for rendering instead of default X11 backend
        browser_args=["--enable-features=UseOzonePlatform", "--ozone-platform=wayland"],
    )
    return browser


async def get_browserscan_bot_detection_results(page: zd.Tab) -> str:
    element = await page.find_element_by_text("Test Results:")
    if (
        element is None
        or element.parent is None
        or not isinstance(element.parent.children[-1], zd.Element)
    ):
        return "element not found"

    return element.parent.children[-1].text


async def main() -> None:
    print(f"Zendriver Docker demo (zendriver {zd.__version__})")
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

    print("Visiting https://www.browserscan.net/bot-detection")
    page = await browser.get("https://www.browserscan.net/bot-detection")

    print("Getting test results...\n")
    result = await get_browserscan_bot_detection_results(page)
    if result == "Normal":
        print(f"Test passed! Result: {result}")
    else:
        print(
            f"Test failed! ({result=}) Check browser window with VNC viewer to see what happened."
        )

    print(
        (
            "\nDemo complete.\n"
            "- Try using a VNC viewer to visit the Docker container's built-in VNC server at http://localhost:5910.\n"
            "- VNC allows for easy debugging and inspection of the browser window.\n"
            "- For some tasks which may not be fully possible to automate, it can also be used to manually interact with the browser.\n\n"
            "When you are done, press Ctrl+C to exit the demo."
        )
    )
    await asyncio.Future()  # wait forever


if __name__ == "__main__":
    asyncio.run(main())
