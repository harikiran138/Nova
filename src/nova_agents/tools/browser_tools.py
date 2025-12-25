from typing import Dict, Any, Optional
from .base import BaseTool

class BrowserTool(BaseTool):
    """
    Deep web browsing using Playwright (Headless Chromium).
    Allows navigation, clicking, typing, and content extraction.
    """
    
    def __init__(self):
        self._browser = None
        self._page = None
        self._playwright = None

    @property
    def name(self) -> str:
        return "browser.browse"

    @property
    def description(self) -> str:
        return "browser.browse(action, url=None, selector=None, text=None) - Actions: 'visit', 'click', 'type', 'scroll', 'back', 'screenshot'. Navigate the real web."

    def _ensure_browser(self):
        from playwright.sync_api import sync_playwright
        if not self._playwright:
            self._playwright = sync_playwright().start()
        if not self._browser:
            self._browser = self._playwright.chromium.launch(headless=True)
            self._page = self._browser.new_page()
            # Set user agent to avoid basic blocks
            self._page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

    def execute(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "visit")
        url = kwargs.get("url")
        selector = kwargs.get("selector")
        text = kwargs.get("text")
        
        try:
            self._ensure_browser()
            
            if action == "visit":
                if not url: return {"success": False, "error": "Missing url"}
                self._page.goto(url, timeout=30000)
                title = self._page.title()
                content = self._page.inner_text("body")[:2000] # Snippet
                return {"success": True, "result": f"Visited: {title}\nSummary: {content}..."}
            
            elif action == "click":
                if not selector: return {"success": False, "error": "Missing selector"}
                self._page.click(selector, timeout=5000)
                return {"success": True, "result": f"Clicked {selector}"}
                
            elif action == "type":
                if not selector or not text: return {"success": False, "error": "Missing selector or text"}
                self._page.fill(selector, text)
                return {"success": True, "result": f"Typed '{text}' into {selector}"}
                
            elif action == "scroll":
                self._page.evaluate("window.scrollBy(0, 500)")
                return {"success": True, "result": "Scrolled down"}
            
            elif action == "screenshot":
                path = "screenshot.png"
                self._page.screenshot(path=path)
                return {"success": True, "result": f"Screenshot saved to {path}"}
                
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            # Restart browser on fatal error
            if "Target closed" in str(e) or "Session closed" in str(e):
                self._close()
            return {"success": False, "error": str(e)}

    def _close(self):
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    def __del__(self):
        self._close()
