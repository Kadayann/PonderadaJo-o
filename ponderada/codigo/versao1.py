"""A4 - Versão 1: produtor-consumidor sem sincronização.

A thread do sensor produz 20.000 identificadores e a thread do motor os retira
de um buffer circular com quatro posições. O buffer, seus índices e o contador
``ocupadas`` não são protegidos: o ``sleep(0)`` entre a leitura e a escrita do
contador torna a condição de corrida observável.
"""

from collections import Counter
import threading
import time


N = 4
TOTAL = 20_000
TIMEOUT_SEM_PROGRESSO = 1.0

buffer = [None] * N
ocupadas = 0
proxima_escrita = 0
proxima_leitura = 0
produzidas = 0
consumidas: list[int] = []
leituras_invalidas = 0

encerrar = threading.Event()
produtor_terminou = threading.Event()
travou = threading.Event()


def produtor() -> None:
    """Produz os identificadores de 0 a ``TOTAL - 1``.

    A função não recebe parâmetros nem retorna valor. Ela usa espera ocupada
    quando o contador indica buffer cheio. A atualização deliberadamente não
    atômica de ``ocupadas`` é a região de corrida pedida no enunciado.
    """

    global ocupadas, proxima_escrita, produzidas

    for amostra in range(TOTAL):
        while ocupadas >= N and not encerrar.is_set():
            time.sleep(0)
        if encerrar.is_set():
            break

        buffer[proxima_escrita] = amostra
        proxima_escrita = (proxima_escrita + 1) % N

        valor_lido = ocupadas
        time.sleep(0)
        ocupadas = valor_lido + 1
        produzidas += 1

    produtor_terminou.set()


def consumidor() -> None:
    """Retira amostras do buffer e detecta um segundo sem progresso.

    A função não recebe parâmetros nem retorna valor. Leituras de posições
    vazias são contabilizadas separadamente. Quando ainda há trabalho indicado
    pelo produtor, contador ou buffer e nenhuma amostra válida chega durante um
    segundo, a execução é marcada como travada e encerrada de forma controlada.
    """

    global ocupadas, proxima_leitura, leituras_invalidas

    ultimo_progresso = time.monotonic()

    while not encerrar.is_set():
        if ocupadas <= 0:
            ha_item_real = any(item is not None for item in buffer)
            if produtor_terminou.is_set() and not ha_item_real:
                break
            if time.monotonic() - ultimo_progresso >= TIMEOUT_SEM_PROGRESSO:
                travou.set()
                encerrar.set()
                break
            time.sleep(0)
            continue

        amostra = buffer[proxima_leitura]
        buffer[proxima_leitura] = None
        proxima_leitura = (proxima_leitura + 1) % N

        valor_lido = ocupadas
        time.sleep(0)
        ocupadas = valor_lido - 1

        if isinstance(amostra, int):
            consumidas.append(amostra)
            ultimo_progresso = time.monotonic()
        else:
            leituras_invalidas += 1

        if len(consumidas) >= TOTAL:
            break

        sem_item_real = not any(item is not None for item in buffer)
        if produtor_terminou.is_set() and sem_item_real:
            break
        if time.monotonic() - ultimo_progresso >= TIMEOUT_SEM_PROGRESSO:
            travou.set()
            encerrar.set()
            break


def calcular_metricas() -> dict[str, int]:
    """Calcula métricas a partir das frequências dos identificadores.

    Retorna um dicionário com quantidade de leituras válidas, identificadores
    únicos, perdas entre as amostras efetivamente produzidas, duplicações e
    identificadores fora da faixa produzida.
    """

    frequencias = Counter(consumidas)
    ids_validos = {
        identificador
        for identificador in frequencias
        if 0 <= identificador < produzidas
    }
    fora_da_faixa = sum(
        frequencia
        for identificador, frequencia in frequencias.items()
        if identificador not in ids_validos
    )
    duplicadas = sum(frequencias[identificador] - 1 for identificador in ids_validos)

    return {
        "consumidas": len(consumidas),
        "unicas": len(ids_validos),
        "perdidas": produzidas - len(ids_validos),
        "duplicadas": duplicadas,
        "fora_da_faixa": fora_da_faixa,
        "frequencia_minima": min((frequencias[i] for i in ids_validos), default=0),
        "frequencia_maxima": max((frequencias[i] for i in ids_validos), default=0),
    }


def main() -> None:
    """Executa a simulação, aguarda as threads e imprime o relatório final.

    A função não recebe parâmetros nem retorna valor. Um limite externo evita
    que um erro no mecanismo de detecção mantenha o processo preso.
    """

    inicio = time.perf_counter()
    thread_produtor = threading.Thread(target=produtor, name="sensor", daemon=True)
    thread_consumidor = threading.Thread(target=consumidor, name="motor", daemon=True)

    thread_produtor.start()
    thread_consumidor.start()
    thread_produtor.join(timeout=10.0)
    thread_consumidor.join(timeout=2.0)

    if thread_produtor.is_alive() or thread_consumidor.is_alive():
        travou.set()
        encerrar.set()
        thread_produtor.join(timeout=1.0)
        thread_consumidor.join(timeout=1.0)

    tempo_total = time.perf_counter() - inicio
    metricas = calcular_metricas()

    print("Versão 1 — sem sincronização")
    print(f"Buffer (N): {N}")
    print(f"Amostras previstas: {TOTAL}")
    print(f"Amostras produzidas: {produzidas}")
    print(f"Amostras consumidas: {metricas['consumidas']}")
    print(f"IDs únicos válidos consumidos: {metricas['unicas']}")
    print(f"Amostras perdidas: {metricas['perdidas']}")
    print(f"Amostras duplicadas: {metricas['duplicadas']}")
    print(f"Leituras inválidas: {leituras_invalidas}")
    print(f"IDs consumidos fora da faixa produzida: {metricas['fora_da_faixa']}")
    print(
        "Frequência mínima/máxima dos IDs válidos: "
        f"{metricas['frequencia_minima']}/{metricas['frequencia_maxima']}"
    )
    print(f"Travou: {'SIM' if travou.is_set() else 'NÃO'}")
    print(f"Tempo total (s): {tempo_total:.6f}")


if __name__ == "__main__":
    main()
