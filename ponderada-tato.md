# Ponderada CC08: Do Pipeline ao Deadlock

Nome completo: Bruno Gabriel Giordano Guilherme Kadayan | D1: 2 | D2: 6 | N: 4

(considerando Bruno Gabriel como primeiro nome)


## Parte A: Problema Técnico

### A1: Arquitetura e Memória

#### 1. Plataforma H

**Dados:**
- IC = 220.000 instruções
- CPI = 1,5 ciclos por instrução
- Clock = 48 MHz = 48.000.000 Hz

A fórmula é:

$$
T = \frac{IC \times CPI}{f}
$$

Substituindo os valores:

$$
T = \frac{220.000 \times 1,5}{48.000.000}
$$

$$
T = \frac{330.000}{48.000.000} = 0,006875 \text{ s}
$$

Deixando em ms:

$$
T = 0,006875 \times 1000 = 6,875 \text{ ms}
$$

**Conclusão:**

A Plataforma H não atende ao requisito de 5 ms, pois leva 6,875 ms para processar cada amostra, passando o limite em 1,875 ms.


#### 2. Plataforma V

**Dados:**
- IC = 220.000 instruções
- Clock = 1,2 GHz = 1.200.000.000 Hz
- CPI base = 1,0
- Acessos à memória por instrução = 1,3
- Tempo de acerto na cache L1 = 1 ciclo
- Penalidade de falta = 120 ciclos
- Atraso máximo do Linux = 3 ms

**Taxa de falta na cache (m):**

A taxa de falta depende de D1:

$$
m = 3\% + (0,5\% \times D1)
$$

Trocando D1 = 2:

$$
m = 3\% + (0,5\% \times 2) = 4\%
$$

A taxa de falta fica em 4%.

**Tempo médio de acesso à memória (AMAT):**

A fórmula é:

$$
AMAT = \text{Tempo de acerto} + (m \times \text{Penalidade})
$$

Trocando os valores:

$$
AMAT = 1 + (0,04 \times 120)
$$

$$
AMAT = 1 + 4,8 = 5,8 \text{ ciclos}
$$

**CPI efetivo:**

O CPI efetivo considera os ciclos adicionais de espera causados pelas faltas na cache.

A fórmula é:

$$
CPI_{efetivo} = 1,0 + (Acessos \times m \times Penalidade)
$$

Trocando os valores:

$$
CPI_{efetivo} = 1,0 + (1,3 \times 0,04 \times 120)
$$

$$
CPI_{efetivo} = 1,0 + 6,24 = 7,24
$$

Entrão, considerando as faltas na cache a Plataforma V tem um CPI efetivo de 7,24 ciclos por instrução.

**Tempo de processamento:**

Utilizando o CPI efetivo, podemos calcular o tempo de processamento da Plataforma V:

$$
T = \frac{IC \times CPI_{efetivo}}{f}
$$

Trocando os valores:

$$
T = \frac{220.000 \times 7,24}{1.200.000.000}
$$

$$
T = \frac{1.592.800}{1.200.000.000}
$$

$$
T \approx 0,0013273 \text{ s}
$$

Convertendo para ms:

$$
T \approx 0,0013273 \times 1000 = 1,3273 \text{ ms}
$$

**Pior caso com atraso do Linux:**

O Linux pode interromper a tarefa, causando um atraso adicional de até 3 ms. Somando esse atraso ao tempo calculado:

$$
T_{pior} = T + 3 \text{ ms}
$$

$$
T_{pior} = 1,3273 + 3 = 4,3273 \text{ ms}
$$

**Conclusão:**

A Plataforma V atende ao requisito de 5 ms, pois apresenta um tempo de processamento de aproximadamente 1,327 ms. Mesmo considerando o atraso máximo de 3 ms do Linux, o tempo calculado chega a 4,327 ms, permanecendo cerca de 0,673 ms abaixo do limite estabelecido.

#### 3. Acelerador DSP

**Dados:**
- Tempo original da Plataforma H = 6,875 ms
- Parte do processamento correspondente ao filtro = 60%
- Aceleração do filtro com DSP = 5 vezes

**Cálculo do speedup global:**

Para calcular o ganho de desempenho com o DSP, utilizamos a Lei de Amdahl:

$$
Speedup = \frac{1}{(1-F)+\frac{F}{S}}
$$

Onde:
- F = fração do processamento que será acelerada (0,6)
- S = fator de aceleração dessa parte (5)

Substituindo os valores:

$$
Speedup = \frac{1}{(1-0,6)+\frac{0,6}{5}}
$$

$$
Speedup = \frac{1}{0,4+0,12}
$$

$$
Speedup = \frac{1}{0,52} \approx 1,923
$$

Portanto, o DSP torna o processamento total aproximadamente 1,92 vez mais rápido.

**Novo tempo de processamento:**

Para calcular o novo tempo, dividimos o tempo original pelo speedup:

$$
T_{novo} = \frac{T_{original}}{Speedup}
$$

Trocando os valores:

$$
T_{novo} = \frac{6,875}{1,9230769}
$$

$$
T_{novo} = 3,575 \text{ ms}
$$

**Conclusão:**

Com o acelerador DSP, a Plataforma H passa a atender ao requisito de 5 ms, reduzindo seu tempo de processamento de 6,875 ms para 3,575 ms.

Apesar de o filtro ficar 5 vezes mais rápido, o ganho total é de aproximadamente 1,92 vez, pois apenas 60% do processamento é acelerado. Os outros 40% continuam levando o mesmo tempo.

#### 4. Harvard vs. Von Neumann

A Plataforma V utiliza a arquitetura Von Neumann, na qual instruções e dados compartilham o caminho de acesso à memória, criando um gargalo. Como a DRAM é mais lenta, a cache ajuda a reduzir o tempo médio de acesso. Já a Plataforma H utiliza a arquitetura Harvard, com caminhos separados para instruções e dados, permitindo acessos simultâneos, além disso, sua SRAM interna possui acesso em apenas um ciclo, dispensando a necessidade de cache nesse cenário.


#### 5. Evidência das caches

O processador do meu computador é um Intel Core i5-1240P, da 12ª geração. A imagem abaixo mostra suas caches, conforme identificado no CPU-Z.

![Caches do computador](img/cache-cpu.png)

A cache L1 do meu processador é dividida entre instruções (L1 Instruction) e dados (L1 Data), permitindo que ambos sejam acessados por caminhos separados.

O processador utiliza uma arquitetura Harvard modificada, pois apresenta essa separação na L1, mas compartilha níveis inferiores de memória, como a cache L3 e a RAM. Assim, combina características de Harvard e Von Neumann, em vez de seguir exclusivamente uma das duas arquiteturas.

### A2 — Pipeline

[Respostas e diagramas]

### A3 — Processos e Threads

[Respostas]

### A4 — Semáforos

[Resultados dos testes, tabela e prints]

### A5 — Deadlock

[Respostas e diagramas]

## Parte B — Decisão do CTO

[Seu memorando de até uma página]
