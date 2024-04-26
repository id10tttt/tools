import aiohttp
import asyncio
from aiohttp_socks import ChainProxyConnector
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class LoopError(Exception):

    def __init__(self, message):
        super().__init__(message)


HEAD = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

TIMEOUT = aiohttp.ClientTimeout(
    total=90,
    connect=0,
    sock_connect=60,
    sock_read=90
)


async def get_request(url, cookies=None, proxy_list=None, save_cookies=False):
    try:
        async with aiohttp.ClientSession(headers=HEAD, cookie_jar=aiohttp.CookieJar(unsafe=True), cookies=cookies,
                                         timeout=TIMEOUT,
                                         connector=ChainProxyConnector.from_urls(
                                             proxy_list) if proxy_list else None) as sess:
            logger.info("GET %s" % url)
            if save_cookies:
                async with sess.get(url) as resp:
                    return await resp.text(), sess.cookie_jar
            else:
                async with sess.get(url) as resp:
                    return await resp.text()
    except asyncio.exceptions.CancelledError:
        raise LoopError("Asyncio loop had been closed before request could finish.")


async def post_request(url, data, proxy_list=None):
    try:
        async with aiohttp.ClientSession(headers=HEAD, timeout=TIMEOUT,
                                         cookie_jar=aiohttp.CookieJar(unsafe=True),
                                         connector=ChainProxyConnector.from_urls(
                                             proxy_list) if proxy_list else None) as sess:
            logger.info("POST %s" % url)
            async with sess.post(url, data=data) as resp:
                return await resp.text(), sess.cookie_jar
    except asyncio.exceptions.CancelledError:
        raise LoopError("Asyncio loop had been closed before request could finish.")
