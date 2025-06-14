"""
Asynchronous Web Crawler Example
Demonstrates async programming patterns and potential concurrency issues
for comprehensive code review testing.
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import ssl
import time
import weakref
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import aiofiles
import aiohttp

# ISSUE: Hardcoded configuration
MAX_CONCURRENT_REQUESTS = 50  # ISSUE: May overwhelm target servers
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
DELAY_BETWEEN_REQUESTS = 0.1  # ISSUE: Fixed delay, not adaptive
USER_AGENT = "AsyncCrawler/1.0"  # ISSUE: Non-descriptive user agent


@dataclass
class CrawlResult:
    url: str
    status_code: int
    content_length: int
    response_time: float
    content_type: str
    links_found: List[str] = field(default_factory=list)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CrawlStats:
    urls_crawled: int = 0
    urls_failed: int = 0
    total_bytes: int = 0
    start_time: float = field(default_factory=time.time)

    def get_rate(self) -> float:
        elapsed = time.time() - self.start_time
        return self.urls_crawled / elapsed if elapsed > 0 else 0


class RateLimiter:
    """Simple rate limiter - ISSUES: Not distributed, memory-based only"""

    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)  # ISSUE: Memory grows indefinitely

    async def can_request(self, domain: str) -> bool:
        now = time.time()
        # ISSUE: No cleanup of old entries
        domain_requests = self.requests[domain]

        # Remove old requests
        cutoff = now - self.time_window
        domain_requests[:] = [req_time for req_time in domain_requests if req_time > cutoff]

        if len(domain_requests) >= self.max_requests:
            return False

        domain_requests.append(now)
        return True

    async def wait_if_needed(self, domain: str):
        while not await self.can_request(domain):
            await asyncio.sleep(0.1)  # ISSUE: Fixed polling interval


class URLQueue:
    """URL queue with priority and duplicate detection"""

    def __init__(self, max_size: int = 10000):
        self.queue = asyncio.Queue(maxsize=max_size)
        self.seen_urls = set()  # ISSUE: Memory grows indefinitely
        self.priority_urls = asyncio.Queue()
        # ISSUE: No persistence of queue state

    async def add_url(self, url: str, priority: bool = False):
        url_hash = hashlib.md5(url.encode()).hexdigest()

        # ISSUE: Thread-safety issues with set operations
        if url_hash in self.seen_urls:
            return False

        self.seen_urls.add(url_hash)

        try:
            if priority:
                await self.priority_urls.put(url, timeout=1)
            else:
                await self.queue.put(url, timeout=1)
            return True
        except asyncio.TimeoutError:
            # ISSUE: Silent failure when queue is full
            return False

    async def get_url(self) -> Optional[str]:
        try:
            # Check priority queue first
            return await self.priority_urls.get(timeout=0.1)
        except asyncio.TimeoutError:
            try:
                return await self.queue.get(timeout=0.1)
            except asyncio.TimeoutError:
                return None


class ContentProcessor:
    """Process crawled content - ISSUES: No proper error handling"""

    def __init__(self):
        # ISSUE: Regex compiled repeatedly
        self.link_pattern = re.compile(r'href=[\'"]?([^\'" >]+)', re.IGNORECASE)
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    def extract_links(self, content: str, base_url: str) -> List[str]:
        """Extract links from HTML content"""

        links = []
        # ISSUE: Basic regex parsing instead of proper HTML parser
        matches = self.link_pattern.findall(content)

        for match in matches:
            try:
                # ISSUE: No validation of URL format
                absolute_url = urljoin(base_url, match)
                links.append(absolute_url)
            except Exception:
                # ISSUE: Silent failure
                continue

        return links

    def extract_emails(self, content: str) -> List[str]:
        """Extract email addresses from content"""
        # ISSUE: Simple regex may miss complex email formats
        return self.email_pattern.findall(content)

    def get_content_hash(self, content: str) -> str:
        """Generate content hash for duplicate detection"""
        return hashlib.sha256(content.encode()).hexdigest()


class AsyncWebCrawler:
    """Main crawler class with multiple architectural issues"""

    def __init__(self, start_urls: List[str], max_depth: int = 3):
        self.start_urls = start_urls
        self.max_depth = max_depth
        self.url_queue = URLQueue()
        self.rate_limiter = RateLimiter(max_requests=10, time_window=60)
        self.content_processor = ContentProcessor()

        # ISSUE: Global state management
        self.crawl_stats = CrawlStats()
        self.results = []  # ISSUE: All results stored in memory
        self.active_sessions = weakref.WeakSet()  # ISSUE: May not work as expected

        # ISSUE: No proper session management
        self.session = None
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def create_session(self) -> aiohttp.ClientSession:
        """Create HTTP session - ISSUES: No proper configuration"""

        # ISSUE: Allowing insecure SSL
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(
            limit=100,  # ISSUE: Fixed connection pool size
            limit_per_host=20,
            ssl=ssl_context,
        )

        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

        headers = {
            "User-Agent": USER_AGENT,
            # ISSUE: No proper headers for politeness
        }

        session = aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers)

        self.active_sessions.add(session)
        return session

    async def fetch_url(self, session: aiohttp.ClientSession, url: str, depth: int) -> Optional[CrawlResult]:
        """Fetch a single URL with retry logic"""

        domain = urlparse(url).netloc
        await self.rate_limiter.wait_if_needed(domain)

        # ISSUE: No respect for robots.txt

        for attempt in range(MAX_RETRIES):
            async with self.semaphore:  # ISSUE: Semaphore per request, not per domain
                try:
                    start_time = time.time()

                    # ISSUE: No request deduplication during retry
                    async with session.get(url) as response:
                        content = await response.text()
                        response_time = time.time() - start_time

                        result = CrawlResult(
                            url=url,
                            status_code=response.status,
                            content_length=len(content),
                            response_time=response_time,
                            content_type=response.headers.get("content-type", ""),
                        )

                        if response.status == 200:
                            # Extract links for further crawling
                            if depth < self.max_depth:
                                links = self.content_processor.extract_links(content, url)
                                result.links_found = links

                                # ISSUE: No filtering of link types (images, css, js)
                                for link in links[:10]:  # ISSUE: Arbitrary limit
                                    await self.url_queue.add_url(link)

                        return result

                except asyncio.TimeoutError:
                    result = CrawlResult(
                        url=url,
                        status_code=0,
                        content_length=0,
                        response_time=REQUEST_TIMEOUT,
                        content_type="",
                        error=f"Timeout on attempt {attempt + 1}",
                    )

                    if attempt == MAX_RETRIES - 1:
                        return result

                    # ISSUE: Fixed exponential backoff
                    await asyncio.sleep(2**attempt)

                except Exception as e:
                    # ISSUE: Generic exception handling
                    result = CrawlResult(
                        url=url,
                        status_code=0,
                        content_length=0,
                        response_time=0,
                        content_type="",
                        error=str(e),
                    )

                    if attempt == MAX_RETRIES - 1:
                        return result

                    await asyncio.sleep(1)

        return None

    async def worker(self, session: aiohttp.ClientSession, worker_id: int):
        """Worker coroutine to process URLs from queue"""

        logging.info(f"Worker {worker_id} started")

        while True:
            url = await self.url_queue.get_url()
            if url is None:
                # ISSUE: Workers may exit prematurely
                await asyncio.sleep(1)
                continue

            try:
                # ISSUE: No depth tracking per URL
                result = await self.fetch_url(session, url, depth=0)

                if result:
                    self.results.append(result)  # ISSUE: Not thread-safe

                    # Update stats
                    if result.error:
                        self.crawl_stats.urls_failed += 1
                    else:
                        self.crawl_stats.urls_crawled += 1
                        self.crawl_stats.total_bytes += result.content_length

                    # ISSUE: No rate limiting between requests
                    await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

            except Exception as e:
                # ISSUE: Worker exceptions not properly handled
                logging.error(f"Worker {worker_id} error: {e}")
                continue

    async def save_results(self, filename: str):
        """Save crawl results to file"""

        # ISSUE: No file locking or atomic writes
        try:
            async with aiofiles.open(filename, "w") as f:
                # ISSUE: Loading all results into memory for JSON serialization
                results_dict = [
                    {
                        "url": r.url,
                        "status_code": r.status_code,
                        "content_length": r.content_length,
                        "response_time": r.response_time,
                        "content_type": r.content_type,
                        "links_found": r.links_found,
                        "error": r.error,
                        "timestamp": r.timestamp,
                    }
                    for r in self.results
                ]

                await f.write(json.dumps(results_dict, indent=2))

        except Exception as e:
            # ISSUE: File save errors not properly handled
            logging.error(f"Failed to save results: {e}")

    async def monitor_progress(self):
        """Monitor crawling progress"""

        while True:
            await asyncio.sleep(10)  # ISSUE: Fixed monitoring interval

            rate = self.crawl_stats.get_rate()
            logging.info(
                f"Progress: {self.crawl_stats.urls_crawled} URLs crawled, "
                f"{self.crawl_stats.urls_failed} failed, "
                f"Rate: {rate:.2f} URLs/sec, "
                f"Total bytes: {self.crawl_stats.total_bytes}"
            )

            # ISSUE: No graceful shutdown mechanism
            if self.crawl_stats.urls_crawled + self.crawl_stats.urls_failed > 1000:
                break

    async def crawl(self, num_workers: int = 10) -> List[CrawlResult]:
        """Main crawling method"""

        logging.info(f"Starting crawl with {num_workers} workers")

        # Initialize URLs
        for url in self.start_urls:
            await self.url_queue.add_url(url, priority=True)

        # Create session
        self.session = await self.create_session()

        try:
            # Start workers
            workers = [asyncio.create_task(self.worker(self.session, i)) for i in range(num_workers)]

            # Start progress monitor
            monitor_task = asyncio.create_task(self.monitor_progress())

            # ISSUE: No proper task coordination
            await asyncio.sleep(60)  # ISSUE: Fixed crawl duration

            # ISSUE: Abrupt task cancellation
            for worker in workers:
                worker.cancel()

            monitor_task.cancel()

            # ISSUE: No graceful cleanup waiting
            await asyncio.gather(*workers, return_exceptions=True)

        finally:
            # ISSUE: Session cleanup may not happen properly
            if self.session:
                await self.session.close()

        logging.info(f"Crawl completed. {len(self.results)} results collected")
        return self.results


# ISSUE: Global configuration variables
CRAWL_CONFIG = {
    "start_urls": [
        "https://httpbin.org",
        "https://jsonplaceholder.typicode.com",
        "https://httpstat.us",  # ISSUE: Using test endpoints
    ],
    "max_depth": 2,
    "num_workers": 5,
    "output_file": "/tmp/crawl_results.json",
}


class CrawlerManager:
    """High-level crawler management - ISSUES: Poor resource management"""

    def __init__(self):
        self.active_crawlers = []  # ISSUE: No proper lifecycle management
        self.results_cache = {}  # ISSUE: Unbounded cache

    async def run_crawl_session(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a complete crawl session"""

        crawler = AsyncWebCrawler(start_urls=config["start_urls"], max_depth=config.get("max_depth", 3))

        self.active_crawlers.append(crawler)  # ISSUE: Memory leak

        try:
            start_time = time.time()
            results = await crawler.crawl(config.get("num_workers", 10))

            # Save results
            if "output_file" in config:
                await crawler.save_results(config["output_file"])

            # ISSUE: Not calculating comprehensive metrics
            session_stats = {
                "total_urls": len(results),
                "successful_urls": len([r for r in results if not r.error]),
                "failed_urls": len([r for r in results if r.error]),
                "total_bytes": sum(r.content_length for r in results),
                "duration": time.time() - start_time,
                "average_response_time": (sum(r.response_time for r in results) / len(results) if results else 0),
            }

            return session_stats

        except Exception as e:
            # ISSUE: Generic exception handling
            logging.error(f"Crawl session failed: {e}")
            raise
        finally:
            # ISSUE: No proper cleanup
            pass


async def main():
    """Main function with multiple issues"""

    # ISSUE: No proper logging configuration
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    manager = CrawlerManager()

    try:
        # ISSUE: No command-line argument parsing
        stats = await manager.run_crawl_session(CRAWL_CONFIG)

        print("Crawl Session Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    except KeyboardInterrupt:
        logging.info("Crawl interrupted by user")
    except Exception as e:
        # ISSUE: Generic top-level exception handling
        logging.error(f"Crawl failed: {e}")
        raise
    finally:
        # ISSUE: No cleanup of resources
        pass


if __name__ == "__main__":
    # ISSUE: No proper async context management
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Application failed: {e}")
        # ISSUE: No proper exit codes
