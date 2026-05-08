import asyncio
import os

from dotenv import set_key
from playwright.async_api import async_playwright


async def extract_token_via_browser() -> str:
    """Headlessly extracts the Scite token using a persistent browser session."""
    print("\n[Auth] Launching Playwright to extract Scite token...")

    user_data_dir = os.path.join(os.getcwd(), ".scite_browser_profile")
    is_first_run = not os.path.exists(user_data_dir)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=not is_first_run,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = await context.new_page()

        extracted_token = [None]

        async def intercept_request(request):
            if "api.scite.ai" in request.url:
                auth_header = request.headers.get("authorization", "")
                if auth_header.startswith("Bearer "):
                    token_candidate = auth_header.split(" ")[1]
                    # STRICT VALIDATION: Real JWTs start with "eyJ" (Base64 for '{"')
                    # and are typically very long. This ignores "null" or generic public keys.
                    if token_candidate.startswith("eyJ") and len(token_candidate) > 100:
                        extracted_token[0] = token_candidate

        page.on("request", intercept_request)

        if is_first_run:
            print(
                "\n[Action Required] First run detected. Please log in via the browser window."
            )
            print(
                "The script will automatically grab the token once you are fully logged in and a real API call fires."
            )

        # Removed "networkidle" to prevent timeout crashes during complex 2FA/SSO redirects
        # Navigating directly to the login flow to ensure it triggers correctly
        await page.goto("https://scite.ai/login", timeout=0)

        if is_first_run:
            # Keep the browser open infinitely until the STRICT token validation passes
            while extracted_token[0] is None:
                await asyncio.sleep(1)

            print(
                "\n[Auth] Valid JWT Token successfully captured! Resuming agent execution."
            )
            await asyncio.sleep(2)  # Buffer to let the dashboard finish rendering
        else:
            # If headless, navigate to search to trigger an API call
            await page.goto("https://scite.ai/search", timeout=60000)

            # Wait up to 15 seconds for the background API calls to fire and populate the token
            for _ in range(15):
                if extracted_token[0] is not None:
                    break
                await asyncio.sleep(1)

        await context.close()

        if extracted_token[0]:
            set_key(".env", "SCITE_AUTH_TOKEN", extracted_token[0])
            os.environ["SCITE_AUTH_TOKEN"] = extracted_token[0]
            return extracted_token[0]
        else:
            raise RuntimeError(
                "Failed to extract valid JWT token. SSO session may have expired. Delete '.scite_browser_profile' and try again."
            )


def invalidate_token():
    """Clears the token to force Playwright extraction on the next attempt."""
    set_key(".env", "SCITE_AUTH_TOKEN", "")
    os.environ.pop("SCITE_AUTH_TOKEN", None)
