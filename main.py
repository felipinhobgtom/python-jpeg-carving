import argparse
import logging
import platform
from datetime import datetime
from pathlib import Path

# variaveis
buf_size = 512
start_magic_byte = b"\xff\xd8\xff\xe0"  # inicio da assinatura JPEG
end_magic_byte = b"\xff\xd9"  # fim da assinatura JPEG
# verificacao de sistema operacional
is_windows = platform.system() == "Windows"


def read_bytes(device: str, output: Path):
    recovered = 0
    offset = 0

    # criando e garantindo que o diretorio eh valido
    output.mkdir(parents=True, exist_ok=True)

    if is_windows:
        file_disk = open(rf"\\.\{device}", "rb")     # raw f-string evita o warning
    else:
        file_disk = open(device, "rb")

    # o arg passado aqui eh o tamanho do buffer
    byte = file_disk.read(buf_size)

    while byte:
        logging.debug("Processando bloco %s (tamanho %s bytes)",
                      offset, len(byte))
        # retorna o offset/indice do inicio dos bytes
        found = byte.find(start_magic_byte)
        if found >= 0:
            logging.info("JPEG encontrado no offset: %s",
                         hex(found + (buf_size * offset)))
            file_recovered = open(output / f"{recovered}.jpg", 'wb')

            # retorna o offset/indice do inicio dos bytes
            # o segundo arg eh pra especificar onde vai comecar
            found_end = byte.find(end_magic_byte, found)

            if found_end >= 0:
                # aq eh um slice cabuloso
                file_recovered.write(byte[found:found_end+2])
                file_recovered.close()
                logging.info("JPEG escrito: %s.jpg", recovered)
                recovered += 1
            else:
                file_recovered.write(byte[found:])
                last_ff = byte.endswith(b"\xff")
                while True:
                    byte = file_disk.read(buf_size)
                    offset += 1

                    if not byte:
                        file_recovered.close()
                        break

                    if last_ff and byte.startswith(b"\xd9"):
                        file_recovered.write(b"\xd9")
                        file_recovered.close()
                        logging.info("JPEG escrito: %s.jpg", recovered)
                        recovered += 1
                        break

                    end_magic_find = byte.find(end_magic_byte)
                    if end_magic_find >= 0:
                        file_recovered.write(byte[:end_magic_find+2])
                        file_recovered.close()
                        logging.info("JPEG escrito: %s.jpg", recovered)
                        recovered += 1
                        break
                    else:
                        file_recovered.write(byte)
                        last_ff = (byte.endswith(b"xff"))

        offset += 1
        byte = file_disk.read(buf_size)
    file_disk.close()
    logging.info("Varredura finalizada; total de JPEGs recuperados: %s",
                 recovered)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("device", default=None,
                   help="disco que sera usado para iterar nos bytes")
    p.add_argument("output", default=None,
                   help="path onde vai ficar os arquivos recuperados")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format=f"{datetime.now().isoformat(
        )} %(levelname)s %(name)s: %(message)s"
    )

    logging.info("Iniciando varredura no device %s; output em %s",
                 args.device, args.output)

    read_bytes(args.device, Path(args.output))


if __name__ == "__main__":
    main()
