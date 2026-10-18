# C2

## Actividad 1
Correr tests
```bash
python3 test_servidor.py localhost 8000
python3 test_client.py localhost 8000
```
Correr tests buffer
```bash
python3 test_buff_servidor.py localhost 8000
python3 test_buff_cliente.py localhost 8000
```
Correr servidor y cliente
```bash
python3 servidor.py localhost 8000 > recibido.txt
python3 cliente.py localhost 8000 < archivotest.txt
```
Con modo DEBUG
```bash
DEBUG=1 python3 servidor.py localhost 8000 > recibido.txt
DEBUG=1 python3 cliente.py localhost 8000 < archivotest.txt
```
## Actividad 2
Correr tests
```bash
python3 test_server2.py localhost 8000 
python3 test_client2.py localhost 8000
```

Correr servidor y cliente
```bash
python3 servidorCopia.py localhost 8000 > recibido.txt
python3 clienteCopia.py localhost 8000 < testarchivo.txt
```
Con modo DEBUG
```bash
DEBUG=1 python3 servidorCopia.py localhost 8000 > recibido.txt
DEBUG=1 python3 clienteCopia.py localhost 8000 < testarchivo.txt
```
Tests CC
```bash 
DEBUG=1 TIMEOUT=0.5 python3 servidorCopia.py localhost 8000 > recibido2.bin
DEBUG=1 TIMEOUT=0.5 CC=1 python3 clienteCopia.py localhost 8000 < archivo100.bin
```



