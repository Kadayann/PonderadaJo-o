"""A4 - Versão 3: ordem incorreta dos semáforos e deadlock real.

O produtor adquire ``mutex`` antes de aguardar ``vazio``. Para tornar a falha
reproduzível, ele começa sozinho, enche as quatro posições e bloqueia na quinta
inserção ainda segurando o mutex. Só então o consumidor é iniciado. Um monitor
confirma um segundo sem progresso e libera o bloqueio apenas para encerrar.
"""

from collections import Counter
import threading
import time


N = 4
TOTAL = 20_000
TIMEOUT_SEM_PROGRESSO = 1.0

buffer = [None] * N
proxima_escrita = 0
proxima_leitura = 0
produzidas = 0
consumidas: list[int] = []
leituras_invalidas = 0

vazio = threading.Semaphore(N)
cheio = threading.Semaphore(0)
mutex = threading.Semaphore(1)

encerrar = threading.Event()
produtor_bloqueado_em_vazio = threading.Event()
consumidor_bloqueado_em_mutex = threading.Event()


def produtor() -> None:
    """Produz amostras usando propositalmente ``mutex`` antes de ``vazio``.

    A função não recebe parâmetros nem retorna valor. Depois de produzir ``N``
    itens, informa ao monitor que a próxima espera ocorrerá com ``vazio`` igual
    a zero e faz o bloqueio real mantendo ``mutex``. O token injetado pelo
    monitor, após a comprovação do deadlock, serve somente ao encerramento.
    """

    global proxima_escrita, produzidas

    for amostra in range(TOTAL):
        mutex.acquire()
        if produzidas == N:
            produtor_bloqueado_em_vazio.set()
        vazio.acquire()
        if produtor_bloqueado_em_vazio.is_set():
            produtor_bloqueado_em_vazio.clear()

        if encerrar.is_set():
            mutex.release()
            break

        buffer[proxima_escrita] = amostra
        proxima_escrita = (proxima_escrita + 1) % N
        produzidas += 1
        mutex.release()
        cheio.release()


def consumidor() -> None:
    """Tenta consumir itens e evidencia a espera circular do deadlock.

    A função não recebe parâmetros nem retorna valor. Após obter ``cheio``, ela
    registra que precisa do ``mutex`` já mantido pelo produtor. Se o monitor
    tiver solicitado encerramento, a posição não é contabilizada como consumo.
    """

    global proxima_leitura, leituras_invalidas

    for _ in range(TOTAL):
        cheio.acquire()
        consumidor_bloqueado_em_mutex.set()
        mutex.acquire()
        consumidor_bloqueado_em_mutex.clear()

        if encerrar.is_set():
            mutex.release()
            break

        amostra = buffer[proxima_leitura]
        buffer[proxima_leitura] = None
        proxima_leitura = (proxima_leitura + 1) % N
        mutex.release()
        vazio.release()

        if isinstance(amostra, int):
            consumidas.append(amostra)
        else:
            leituras_invalidas += 1


def aguardar_deadlock() -> tuple[bool, bool]:
    """Observa a espera circular e retorna ``(travou, ciclo_observado)``.

    O monitor exige que produtor e consumidor estejam nos dois waits opostos e
    que os contadores de progresso permaneçam iguais por um segundo. Ao confirmar
    o travamento, solicita encerramento e libera um token de ``vazio`` para que
    o produtor solte ``mutex`` e ambas as threads possam terminar.
    """

    inicio_sem_progresso = time.monotonic()
    progresso_anterior = (produzidas, len(consumidas))
    ciclo_observado = False

    while time.monotonic() - inicio_sem_progresso < TIMEOUT_SEM_PROGRESSO:
        ciclo_atual = (
            produtor_bloqueado_em_vazio.is_set()
            and consumidor_bloqueado_em_mutex.is_set()
        )
        ciclo_observado = ciclo_observado or ciclo_atual
        progresso_atual = (produzidas, len(consumidas))
        if progresso_atual != progresso_anterior:
            progresso_anterior = progresso_atual
            inicio_sem_progresso = time.monotonic()
        time.sleep(0.005)

    travou = ciclo_observado and progresso_anterior == (produzidas, len(consumidas))
    if travou:
        encerrar.set()
        vazio.release()
    return travou, ciclo_observado


def calcular_metricas() -> dict[str, int]:
    """Valida identificadores e frequências e retorna as métricas do teste."""

    frequencias = Counter(consumidas)
    ids_validos = {i for i in frequencias if 0 <= i < produzidas}
    duplicadas = sum(frequencias[i] - 1 for i in ids_validos)
    fora_da_faixa = sum(
        frequencia
        for identificador, frequencia in frequencias.items()
        if identificador not in ids_validos
    )
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
    """Monta a intercalação controlada, detecta o deadlock e relata métricas."""

    inicio = time.perf_counter()
    thread_produtor = threading.Thread(target=produtor, name="sensor", daemon=True)
    thread_consumidor = threading.Thread(target=consumidor, name="motor", daemon=True)

    thread_produtor.start()
    cenario_pronto = produtor_bloqueado_em_vazio.wait(timeout=2.0)
    thread_consumidor.start()
    travou, ciclo_observado = aguardar_deadlock()

    if not travou:
        encerrar.set()
        vazio.release()
        cheio.release()
    thread_produtor.join(timeout=2.0)
    thread_consumidor.join(timeout=2.0)

    if thread_produtor.is_alive() or thread_consumidor.is_alive():
        travou = True

    tempo_total = time.perf_counter() - inicio
    metricas = calcular_metricas()

    print("Versão 3 — ordem incorreta dos semáforos")
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
    print(f"Buffer cheio antes de iniciar o consumidor: {'SIM' if cenario_pronto else 'NÃO'}")
    print(f"Espera circular observada: {'SIM' if ciclo_observado else 'NÃO'}")
    print(f"Travou: {'SIM' if travou else 'NÃO'}")
    print(f"Tempo total (s): {tempo_total:.6f}")


if __name__ == "__main__":
    main()
