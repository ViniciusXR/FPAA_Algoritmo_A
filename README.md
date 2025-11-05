## Alunos
* Cristiano Nunes Pires Junior
* Joey Clapton Maciel Barbosa Santos
* Sthel Felipe Torres
* Vinicius Xavier Ramalho

# PathFinder - Algoritmo A* no Labirinto 2D

Implementação do Algoritmo A* para encontrar o menor caminho entre `S` (start) e `E` (end) em um labirinto 2D. Suporta movimentos em 4 direções (padrão) e opcionalmente em 8 direções (ponto extra), além de pesos de terreno (ponto extra).

---

## 🧐 O que é?

O A* combina o custo acumulado do caminho (`g(n)`) com uma estimativa admissível da distância até o objetivo (`h(n)`), escolhendo expandir o nó com menor `f(n) = g(n) + h(n)`.

- Movimentos válidos (requisito): cima, baixo, esquerda, direita (4-direções)
- Custo de movimento (requisito): 1 por passo
- Heurística (requisito): Distância de Manhattan
- Extensões implementadas (opcionais):
  - Movimentos diagonais (8-direções) com heurística Octile e custo √2
  - Pesos de terreno nas células `2..9` (multiplicam o custo do passo)

---

## 🔍 Como o algoritmo funciona (linha por linha)

Referências ao `main.py`:

- 141-146: Localiza `S` e `E` e trata o caso trivial (`S == E`)
- 147-149: Define vizinhança e heurística: Manhattan (4-dir) ou Octile (8-dir)
- 150-159: Inicializa `g_score`, `came_from` e a fila de prioridade (`heap`) com o nó inicial
- 162-171: Loop principal: extrai melhor `f`, fecha o nó, checa se é o objetivo e reconstrói caminho
- 173-179: Gera vizinhos válidos, respeitando limites e obstáculos
- 180-187: Relaxa arestas: atualiza `g_score`, `came_from`, recomputa `f` e empilha no `heap`
- 189: Retorna `None` caso não exista caminho ("Sem solução")

Observações:
- Obstáculos aceitos: `1` ou `#`
- Entradas válidas: `S`, `E`, `0`, `1`, `#`, `2..9`
- Pesos de terreno e diagonais são opcionais e desabilitáveis na interface

---

## ⚙️ Como Executar o Projeto

### Pré-requisitos
- Python 3.8+ (recomendado)

### Execução
```bash
cd FPAA/TP-04
python3 main.py
# ou
python main.py
```

Siga o menu interativo:
- Opção 1: labirinto de exemplo
- Opção 2: criar labirinto customizado
- Escolha se permite diagonais (S/N). Para cumprir o requisito base, use N.

---

## ✅ Conformidade com os Requisitos

- Leitura do labirinto: entrada via exemplo ou input do usuário (226-266)
- Heurística Manhattan (requisito): usada quando diagonais estão desabilitadas (147-149, 93-95)
- Movimentos 4-direções (requisito): vizinhança por `neighbors_4` quando diagonais estão desabilitadas (66-71, 147)
- Custo de cada movimento 1 (requisito): atendido quando diagonais e pesos não são usados (116-118 com `0`/`S`/`E`/`0` ⇒ peso 1)
- Validação de S e E existem e são únicos: (44-63) — caso inválido lança erro de validação
- Sem solução: retorna `None` e imprime mensagem apropriada (189; 302-304)
- Exibição: lista de coordenadas do caminho e labirinto com caminho destacado por `*` (305-311 e 199-206)

Pontos extra implementados (opcionais):
- Diagonais (74-85) + heurística Octile (97-105) + custo √2 (116)
- Pesos `2..9` multiplicativos no custo (27-41, 107-119)

Dica: para aderir estritamente ao requisito de custo 1, execute com diagonais = N e não use pesos no labirinto (apenas `S`, `E`, `0`, `1`/`#`).

---

## 🧪 Exemplos

### Exemplo 1 (padrão 4-direções, sem diagonais)
Entrada (Opção 1, N):
```
S 0 1 0 0
0 0 1 0 1
0 2 0 0 0
1 0 0 E 1
```
Saída (resumo):
```
✓ Caminho encontrado com 7 passos (inclui S e E).
Custo total acumulado: 7.000
Coordenadas:
(0, 0) → (1, 0) → (2, 0) → (2, 1) → (3, 1) → (3, 2) → (3, 3)
Labirinto com caminho:
S 0 1 0 0
* 0 1 0 1
* * 0 0 0
1 * * E 1
```
Obs.: O custo foi 7 porque a célula `(2,1)` tem peso `2` (ponto extra). Se não quiser ponderação, não use dígitos `2..9` no labirinto.

### Exemplo 2 (sem solução)
```
S 0 # 0 0
0 0 # 0 #
0 # # # 0
# 0 0 E #
```
Saída:
```
❌ Sem solução: não há caminho entre S e E.
```

---

## 📁 Estrutura do Projeto

```
FPAA/TP-04/
├── main.py          # Implementação do A* (4-dir e extras opcionais)
├── task.md          # Enunciado do trabalho
└── README.md        # Documentação
```

---

## 📚 Referências
- Hart, Nilsson, Raphael (1968) — A Formal Basis for the Heuristic Determination of Minimum Cost Paths
- Heurísticas em grids: Manhattan e Octile
- Notas de aula (FPAA) sobre busca informada e A*
