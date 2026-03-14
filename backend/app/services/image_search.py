"""Image/logo search via social URL scraping — no external API keys required."""
import asyncio
import httpx
from bs4 import BeautifulSoup
from app.services.storage import upload_from_url

HEADERS = {"User-Agent": "Socii-CRM/1.0 (contact-image-search)"}
TIMEOUT = 10


async def _fetch_og_image(url: str) -> str | None:
    """Extract og:image meta tag from a URL."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=TIMEOUT) as client:
            r = await client.get(url, headers=HEADERS)
            r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
        if tag:
            return tag.get("content")
    except Exception:
        pass
    return None


async def _fetch_favicon(website_url: str) -> str | None:
    """Try /favicon.ico then <link rel=icon>."""
    try:
        base = website_url.rstrip("/")
        favicon_url = f"{base}/favicon.ico"
        async with httpx.AsyncClient(follow_redirects=True, timeout=TIMEOUT) as client:
            r = await client.get(favicon_url, headers=HEADERS)
            if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                return favicon_url
            # Try HTML link tag
            r2 = await client.get(website_url, headers=HEADERS)
            soup = BeautifulSoup(r2.text, "html.parser")
            icon = soup.find("link", rel=lambda v: v and "icon" in v)
            if icon and icon.get("href"):
                href = icon["href"]
                if href.startswith("http"):
                    return href
                return f"{base}{href}"
    except Exception:
        pass
    return None


async def search_contact_images(contact) -> list[str]:
    """
    Return candidate image URLs by scraping social profile URLs.
    contact is a Contact SQLModel instance.
    """
    tasks = []
    if contact.linkedin_url:
        tasks.append(_fetch_og_image(contact.linkedin_url))
    if contact.twitter_url:
        tasks.append(_fetch_og_image(contact.twitter_url))
    if contact.github_url:
        tasks.append(_fetch_og_image(contact.github_url))
    if contact.instagram_url:
        tasks.append(_fetch_og_image(contact.instagram_url))
    if contact.website_url:
        tasks.append(_fetch_og_image(contact.website_url))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    candidates = [r for r in results if isinstance(r, str) and r]
    return list(dict.fromkeys(candidates))  # deduplicate, preserve order


async def search_company_logo(company) -> list[str]:
    """
    Return candidate logo URLs for a company.
    """
    tasks = []
    if company.website_url:
        tasks.append(_fetch_og_image(company.website_url))
        tasks.append(_fetch_favicon(company.website_url))
    if company.linkedin_url:
        tasks.append(_fetch_og_image(company.linkedin_url))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    candidates = [r for r in results if isinstance(r, str) and r]
    return list(dict.fromkeys(candidates))


async def import_image_from_url(image_url: str, storage_path: str) -> tuple[str, str]:
    """Download, process and store an image from a URL. Returns (public_url, storage_path)."""
    return await upload_from_url(image_url, storage_path)
