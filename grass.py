import asyncio
import random
import ssl
import json
import time
import uuid
import requests
import shutil
import sys  # Tambahkan ini untuk menggunakan sys
from loguru import logger
from websockets_proxy import Proxy, proxy_connect
from fake_useragent import UserAgent

user_agent = UserAgent(os='windows', platforms='pc', browsers='chrome')
random_user_agent = user_agent.random

# Set untuk menyimpan proxy yang gagal, agar tidak dicoba kembali
failed_proxies = set()

async def connect_to_wss(socks5_proxy, user_id):
    # Jika proxy sudah ada di daftar failed_proxies, hentikan fungsi ini
    if socks5_proxy in failed_proxies:
        logger.warning(f"Skipping failed proxy: {socks5_proxy}")
        return

    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))
    logger.info(f"Generated device_id: {device_id} for proxy: {socks5_proxy}")
    
    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)
            custom_headers = {
                "User-Agent": random_user_agent,
                "Origin": "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi"
            }
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            urilist = ["wss://proxy.wynd.network:4444/", "wss://proxy.wynd.network:4650/"]
            uri = random.choice(urilist)
            server_hostname = "proxy.wynd.network"
            proxy = Proxy.from_url(socks5_proxy)

            logger.info(f"Attempting to connect to {uri} via proxy {socks5_proxy}")
            
            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=server_hostname,
                                     extra_headers=custom_headers) as websocket:
                
                logger.info(f"Connected to WebSocket server at {uri} via proxy {socks5_proxy}")

                # Fungsi send_ping dengan interval 5 detik untuk debugging
                async def send_ping():
                    while True:
                        send_message = json.dumps({"action": "PING"})  # Data minimal untuk pesan PING
                        logger.debug(f"Sending PING message: {send_message}")
                        await websocket.send(send_message)
                        await asyncio.sleep(5)  # Mengurangi frekuensi PING menjadi 5 detik untuk diagnosis

                await asyncio.sleep(1)
                asyncio.create_task(send_ping())

                while True:
                    response = await websocket.recv()
                    logger.info(f"Received raw message: {response}")  # Log semua respons dari server
                    message = json.loads(response)
                    logger.info(f"Parsed message: {message}")

                    # Mengirim respons AUTH dengan data minimal yang diperlukan
                    if message.get("action") == "AUTH":
                        auth_response = {
                            "id": message["id"],
                            "origin_action": "AUTH",
                            "result": {
                                "browser_id": device_id,
                                "user_id": user_id,
                                "user_agent": custom_headers['User-Agent'],
                                "timestamp": int(time.time()),
                                "device_type": "extension",
                                "version": "4.26.2",
                                "extension_id": "lkbnfiajjmbhnfledhphioinpickokdi"
                            }
                        }
                        logger.debug(f"Sending AUTH response: {auth_response}")
                        await websocket.send(json.dumps(auth_response))

                    # Mengirim respons PONG dengan data minimal
                    elif message.get("action") == "PONG":
                        pong_response = {"origin_action": "PONG"}
                        logger.debug(f"Sending PONG response: {pong_response}")
                        await websocket.send(json.dumps(pong_response))

        except Exception as e:
            logger.error(f"Error in connection loop: {e}")
            logger.error(f"Failed with proxy: {socks5_proxy}")
            failed_proxies.add(socks5_proxy)  # Tambahkan proxy ke daftar failed_proxies
            await asyncio.sleep(5)  # Retry connection setelah 5 detik jika terjadi error
            break  # Hentikan loop jika proxy gagal

async def main():
    _user_id = input('Please Enter your user ID: ')
    with open('local_proxies.txt', 'r') as file:
        local_proxies = file.read().splitlines()
    
    tasks = []
    for proxy in local_proxies:
        if proxy not in failed_proxies:
            tasks.append(asyncio.ensure_future(connect_to_wss(proxy, _user_id)))

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    # Mengatur level log ke INFO untuk mengurangi jumlah log yang dicatat
    import sys  # Pastikan sys diimpor
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")  # Atur level log ke DEBUG untuk melihat detail log
    asyncio.run(main())
