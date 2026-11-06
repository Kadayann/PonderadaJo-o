# Ponderada CC08

Implementação da questão A4 com um produtor, um consumidor e um buffer circular de quatro posições. Os programas usam Python 3 e somente a biblioteca padrão, principalmente o módulo `threading`.

## Execução

Na raiz deste repositório, execute:

```bash
python codigo/versao1.py
python codigo/versao2.py
python codigo/versao3.py
```

Se esta pasta estiver armazenada com o nome `ponderada` e os comandos forem executados a partir do diretório pai, os caminhos equivalentes são:

```bash
python ponderada/codigo/versao1.py
python ponderada/codigo/versao2.py
python ponderada/codigo/versao3.py
```

Cada programa usa 20.000 amostras previstas e um buffer com `N = 4`. A versão 1 não sincroniza o buffer, a versão 2 usa os semáforos na ordem correta e a versão 3 reproduz de forma controlada o deadlock causado pela ordem invertida.

Os resultados das nove execuções estão em `img/versao1_teste1.txt` até `img/versao3_teste3.txt`. As capturas reais do terminal estão em `img/versao1.png`, `img/versao2.png` e `img/versao3.png`.
