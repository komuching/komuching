#Grass Exclusive Bot By Komunitas Kucing Terbang..  
TESTED: UBUNTU 22.04  
Fix: Bandwith Over Usage,, Script Ini Irit Bandwith Proxy..  

#Contoh Penulisan Proxy ada di local_proxies.txt
----------------------------------

INSTALASI:

Lakukan Update:
```
sudo apt update && sudo apt upgrade -y
```

Install Python & Tools Tambahan :
```
sudo apt install python3 python3-pip -y
```
```
pip install requests loguru websockets==12.0 fake_useragent websockets_proxy
```
```
pip install -r requirements.txt
```
Siapkan ID Grass Mu Jika Ingin MEnyimpan Dan Memakainya Nanti Secara Otomatis***:
```
echo "Masukan ID Grass" > id.txt
```
***Skip Ini Jika Ingin Melakukan Input Manual..

Lanjut Gan..

Buat File local_proxies.txt***
Ini untuk daftar proxy yang akan digunakan. Contoh:
```
echo "socks5://proxy1:port" > local_proxies.txt
echo "socks5://proxy2:port" >> local_proxies.txt
```
***Bisa Ditambahkan Manual Dengan Mengedit local_proxies.txt

Langsung Gas:

```
python grass.py
```
Jika Ingin Menjalankan Bot Di Latar Belakang Lakukan:
```
screen
```
lalu:
```
python grass.py
```



Cara Mendapat ID Grass:
Login Ke https://app.getgrass.io/
Lalu Tekan F12
Console
Lalu Paste Dan Enter:
```
localStorage.getItem('userId')
```
Jika Gagal,, 
dahulukan:
```
allow pasting
```
lalu:
```
localStorage.getItem('userId')
```
