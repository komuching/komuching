import asyncio
import random
import ssl
import json
import time
import uuid
import requests
import shutil
import sys
from loguru import logger
from websockets_proxy import Proxy, proxy_connect
from fake_useragent import UserAgent

# Fungsi untuk menampilkan header ASCII text sederhana
def print_header():
    header = """
888           8888888888       .d8888b.  
888           888             d88P  Y88b 
888           888             888    888 
888           8888888         888        
888           888             888  88888 
888           888             888    888 
888           888             Y88b  d88P 
88888888      888              "Y8888P88 
                                         
                                         
                                         
    """
    print(header)

user_agent = UserAgent(os='windows', platforms='pc', browsers='chrome')
random_user_agent = user_agent.random

async def connect_to_wss(socks5_proxy, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))
    logger.info(f"ID perangkat yang dihasilkan: {device_id} untuk proxy: {socks5_proxy}")

    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)  # Waktu tunggu acak kecil sebelum mencoba koneksi
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

            logger.info(f"Mencoba menghubungkan ke {uri} melalui proxy {socks5_proxy}")
            
            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=server_hostname,
                                     extra_headers=custom_headers) as websocket:
                
                logger.info(f"Berhasil terhubung ke server WebSocket di {uri} melalui proxy {socks5_proxy}")

                # Fungsi send_ping dengan interval 5 detik untuk debugging
                async def send_ping():
                    while True:
                        send_message = json.dumps({"action": "PING"})  # Data minimal untuk pesan PING
                        logger.debug(f"Mengirim pesan PING: {send_message}")
                        await websocket.send(send_message)
                        logger.info(f"Berhasil Ping ke proxy {socks5_proxy}")
                        await asyncio.sleep(5)  # Mengurangi frekuensi PING menjadi 5 detik untuk diagnosis

                await asyncio.sleep(1)
                asyncio.create_task(send_ping())

                while True:
                    response = await websocket.recv()
                    logger.info(f"Pesan mentah yang diterima: {response}")  # Log semua respons dari server
                    message = json.loads(response)
                    logger.info(f"Pesan yang diurai: {message}")

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
                        logger.debug(f"Mengirim respons AUTH: {auth_response}")
                        await websocket.send(json.dumps(auth_response))

                    # Mengirim respons PONG dengan data minimal
                    elif message.get("action") == "PONG":
                        pong_response = {"origin_action": "PONG"}
                        logger.debug(f"Mengirim respons PONG: {pong_response}")
                        await websocket.send(json.dumps(pong_response))

        except Exception as e:
            logger.error(f"Terjadi kesalahan dalam loop koneksi: {e}")
            logger.error(f"Gagal dengan proxy: {socks5_proxy}. Menunggu 15 detik sebelum mencoba lagi.")
            await asyncio.sleep(15)  # Tunggu 15 detik sebelum mencoba kembali koneksi dengan proxy yang sama
            continue  # Lanjutkan loop dan coba koneksi ulang setelah delay

async def main():
    # Tampilkan header saat memulai
    print_header()

    # Pilihan untuk input user ID
    print("Pilih metode input ID pengguna:")
    print("1. Input manual")
    print("2. Gunakan ID yang disimpan di id.txt")

    choice = input("Masukkan pilihan (1 atau 2): ")
    if choice == "1":
        user_id = input("Silakan masukkan ID pengguna Anda: ")
    elif choice == "2":
        try:
            with open("id.txt", "r") as file:
                user_id = file.read().strip()
                logger.info(f"ID pengguna berhasil dimuat dari id.txt: {user_id}")
        except FileNotFoundError:
            logger.error("File id.txt tidak ditemukan. Harap buat file atau pilih opsi 1 untuk input manual.")
            sys.exit(1)
    else:
        logger.error("Pilihan tidak valid. Masukkan 1 atau 2.")
        sys.exit(1)

    # Load proxies from file and start connection tasks
    with open('local_proxies.txt', 'r') as file:
        local_proxies = file.read().splitlines()
    
    tasks = []
    for proxy in local_proxies:
        tasks.append(asyncio.ensure_future(connect_to_wss(proxy, user_id)))

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    # Mengatur level log ke DEBUG untuk log detail
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    asyncio.run(main())
