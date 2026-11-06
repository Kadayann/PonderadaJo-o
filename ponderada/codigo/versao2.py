"""A4 - Versão 2: produtor-consumidor com três semáforos.

Usa o padrão de buffer limitado com ``vazio``, ``cheio`` e ``mutex`` para que
as 20.000 amostras atravessem um buffer circular de quatro posições sem perdas.
"""

from collections import Counter
import threading
import time


N = 4
TOTAL = 20_000
TIMEOUT_EXECUCAO = 10.0

buffer = [None] * N
proxima_escrita = 0
proxima_leitura = 0
produzidas = 0
consumidas: list[int] = []
leituras_invalidas = 0

vazio = threading.Semaphore(N)
cheio = threading.Semaphore(0)
mutex = threading.Semaphore(1)


def produtor() -> None:
    """Produz ``TOTAL`` identificadores no buffer circular.

    A função não recebe parâmetros nem retorna valor. Para cada amostra, espera
    uma posição em ``vazio``, adquire ``mutex``, escreve e então sinaliza
    ``cheio``. Essa ordem nunca espera por espaço mantendo o mutex ocupado.
    """

    global proxima_escrita, produzidas

    for amostra in range(TOTAL):
        vazio.acquire()
        mutex.acquire()
        try:
            buffer[proxima_escrita] = amostra
            proxima_escrita = (proxima_escrita + 1) % N
            produzidas += 1
        finally:
            mutex.release()
        cheio.release()


def consumidor() -> None:
    """Consome exatamente ``TOTAL`` posições sinalizadas pelo produtor.

    A função não recebe parâmetros nem retorna valor. Ela espera ``cheio``,
    protege a retirada com ``mutex`` e libera uma posição em ``vazio``. Uma
    posição vazia seria contabilizada como inválida, embora não deva ocorrer.
    """

    global proxima_leitura, leituras_invalidas

    for _ in range(TOTAL):
        cheio.acquire()
        mutex.acquire()
        try:
            amostra = buffer[proxima_leitura]
            buffer[proxima_leitura] = None
            proxima_leitura = (proxima_leitura + 1) % N
        finally:
            mutex.release()
        vazio.release()

        if isinstance(amostra, int):
            consumidas.append(amostra)
        else:
            leituras_invalidas += 1


def calcular_metricas() -> dict[str, int]:
    """Valida identificadores e frequências e retorna as métricas do teste."""

    frequencias = Counter(consumidas)
    ids_validos = {i for i in frequencias if 0 <= i < produzidas}
    fora_da_faixa = sum(
        frequencia
        for identificador, frequencia in frequencias.items()
        if identificador not in ids_validos
    )
    duplicadas = sum(frequencias[i] - 1 for i in ids_validos)

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
    """Executa as duas threads e imprime métricas calculadas pelos IDs."""

    inicio = time.perf_counter()
    thread_produtor = threading.Thread(target=produtor, name="sensor", daemon=True)
    thread_consumidor = threading.Thread(target=consumidor, name="motor", daemon=True)

    thread_produtor.start()
    thread_consumidor.start()
    thread_produtor.join(timeout=TIMEOUT_EXECUCAO)
    thread_consumidor.join(timeout=TIMEOUT_EXECUCAO)

    travou = thread_produtor.is_alive() or thread_consumidor.is_alive()
    tempo_total = time.perf_counter() - inicio
    metricas = calcular_metricas()

    print("Versão 2 — sincronização correta com semáforos")
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
    print(f"Travou: {'SIM' if travou else 'NÃO'}")
    print(f"Tempo total (s): {tempo_total:.6f}")


if __name__ == "__main__":
    main()
