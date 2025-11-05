"""
Algoritmo A* melhorado para encontrar o menor caminho em um labirinto 2D.

Melhorias:
- Tie-break por (f, h) na heap para desempate mais "informado".
- Verificação rigorosa de exatamente 1 'S' (start) e 1 'E' (end).
- g_score (sem varrer heap para atualizar nós).
- Suporte opcional a movimentos diagonais (8 direções) com heurística Octile.
- Suporte a terrenos com peso (células '2'..'9' multiplicam o custo do passo).
- Impressão alinhada do labirinto e exibição do custo total.
- Compatível com o formato anterior: 'S', 'E', '0' (livre), '1' ou '#' (obstáculo).
"""

import heapq
import math
from typing import List, Tuple, Optional, Dict, Iterable

try:
    from .view_curses import run_curses_animation  # tipo: ignore
except Exception:
    try:
        from view_curses import run_curses_animation  # fallback quando exec direto
    except Exception:
        run_curses_animation = None  # sem curses disponível


Pos = Tuple[int, int]


def is_obstacle(cell: str) -> bool:
    """Define o que é obstáculo."""
    return cell in ("1", "#")


def cell_weight(cell: str) -> float:
    """
    Retorna o peso multiplicativo do terreno:
    - '0', 'S', 'E' => 1.0
    - '2'..'9' => peso numérico
    - Qualquer outra coisa tratada como 1.0 (desde que não seja obstáculo)
    """
    if cell in ("S", "E", "0"):
        return 1.0
    if cell.isdigit():
        v = int(cell)
        if v >= 2:
            return float(v)
        return 1.0
    return 1.0


def find_unique_positions(lab: List[List[str]]) -> Tuple[Pos, Pos]:
    """
    Encontra e valida que exista exatamente 1 'S' e 1 'E'.
    Levanta ValueError se não cumprir.
    """
    starts: List[Pos] = []
    ends: List[Pos] = []
    for i, row in enumerate(lab):
        for j, c in enumerate(row):
            if c == "S":
                starts.append((i, j))
            elif c == "E":
                ends.append((i, j))

    if len(starts) != 1:
        raise ValueError(f"Esperado exatamente 1 'S', encontrado: {len(starts)}")
    if len(ends) != 1:
        raise ValueError(f"Esperado exatamente 1 'E', encontrado: {len(ends)}")

    return starts[0], ends[0]


def neighbors_4(pos: Pos) -> Iterable[Pos]:
    i, j = pos
    yield (i - 1, j)
    yield (i + 1, j)
    yield (i, j - 1)
    yield (i, j + 1)


def neighbors_8(pos: Pos) -> Iterable[Pos]:
    i, j = pos
    # ortogonais
    yield (i - 1, j)
    yield (i + 1, j)
    yield (i, j - 1)
    yield (i, j + 1)
    # diagonais
    yield (i - 1, j - 1)
    yield (i - 1, j + 1)
    yield (i + 1, j - 1)
    yield (i + 1, j + 1)


def in_bounds(lab: List[List[str]], pos: Pos) -> bool:
    i, j = pos
    return 0 <= i < len(lab) and 0 <= j < len(lab[0])


def manhattan(a: Pos, b: Pos) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def octile(a: Pos, b: Pos) -> float:
    """
    Heurística Octile (admissível para 8 direções):
    (sqrt(2)-1)*min(dx,dy) + max(dx,dy)
    """
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return (math.sqrt(2) - 1) * min(dx, dy) + max(dx, dy)


def movement_cost(from_pos: Pos, to_pos: Pos, lab: List[List[str]]) -> float:
    """
    Custo base do passo:
      - 1.0 para ortogonais
      - sqrt(2) para diagonais
    Multiplicado pelo peso do terreno da célula de destino.
    """
    di = abs(to_pos[0] - from_pos[0])
    dj = abs(to_pos[1] - from_pos[1])
    base = math.sqrt(2) if di == 1 and dj == 1 else 1.0
    dest_cell = lab[to_pos[0]][to_pos[1]]
    return base * cell_weight(dest_cell)


def reconstruct_path(came_from: Dict[Pos, Pos], current: Pos) -> List[Pos]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def a_star(
    lab: List[List[str]],
    allow_diagonals: bool = False
) -> Optional[Tuple[List[Pos], float]]:
    """
    A* com:
      - Heurística: Manhattan (4-dir) ou Octile (8-dir).
      - g_score com heap; evita varrer heap para updates.
      - Suporte a pesos em '2'..'9'.
    Retorna (caminho, custo_total) ou None.
    """
    start, goal = find_unique_positions(lab)

    # Caso trivial: S == E
    if start == goal:
        return [start], 0.0

    neigh_fn = neighbors_8 if allow_diagonals else neighbors_4
    heuristic = octile if allow_diagonals else manhattan

    # g_score e estruturas
    g_score: Dict[Pos, float] = {start: 0.0}
    came_from: Dict[Pos, Pos] = {}

    # Heap de (f, h, seq, pos) — tie-break por h; seq evita empate total
    open_heap: List[Tuple[float, float, int, Pos]] = []
    seq = 0
    h0 = heuristic(start, goal)
    heapq.heappush(open_heap, (h0, h0, seq, start))

    closed: set[Pos] = set()

    while open_heap:
        _, _, _, current = heapq.heappop(open_heap)

        if current in closed:
            continue
        closed.add(current)

        if current == goal:
            path = reconstruct_path(came_from, current)
            return path, g_score[current]

        for nb in neigh_fn(current):
            if not in_bounds(lab, nb):
                continue
            cell = lab[nb[0]][nb[1]]
            if is_obstacle(cell):
                continue

            tentative_g = g_score[current] + movement_cost(current, nb, lab)
            if tentative_g < g_score.get(nb, float("inf")):
                came_from[nb] = current
                g_score[nb] = tentative_g
                h = heuristic(nb, goal)
                f = tentative_g + h
                seq += 1
                heapq.heappush(open_heap, (f, h, seq, nb))

    return None


def print_labyrinth(lab: List[List[str]]):
    """Imprime o labirinto com colunas alinhadas."""
    width = max(len(c) for row in lab for c in row)
    for row in lab:
        print(" ".join(c.rjust(width) for c in row))


def show_path(lab: List[List[str]], path: List[Pos]):
    """Imprime o labirinto com o caminho marcado por '*' (preservando S e E)."""
    vis = [row[:] for row in lab]
    for (i, j) in path:
        if vis[i][j] not in ("S", "E"):
            vis[i][j] = "*"
    print("\nLabirinto com caminho:")
    print_labyrinth(vis)


def create_example(allow_weights: bool = True) -> List[List[str]]:
    """
    Exemplo:
    - '1' / '#' = obstáculo
    - '2' (peso maior) para ilustrar custo de terreno
    """
    lab = [
        ["S", "0", "1", "0", "0"],
        ["0", "0", "1", "0", "1"],
        ["0", "0", "0", "0", "0"],
        ["1", "0", "0", "E", "1"],
    ]
    if allow_weights:
        lab[2][1] = "2"  # terreno mais "caro" (peso 2x) apenas para exemplo
    return lab


def read_user_labyrinth() -> List[List[str]]:
    """
    Lê o labirinto do usuário.
    VÁLIDOS: S, E, 0, 1, #, 2..9
    """
    print("\nCriar labirinto customizado")
    print("Legenda: S=início, E=fim, 0=livre, 1/#=obstáculo, 2..9=terreno pesado")
    while True:
        try:
            linhas = int(input("\nQuantas linhas? "))
            colunas = int(input("Quantas colunas? "))
            if linhas <= 0 or colunas <= 0:
                print("Linhas/colunas devem ser > 0.")
                continue
            break
        except ValueError:
            print("Digite números válidos.")

    lab: List[List[str]] = []
    print(f"\nDigite cada linha com {colunas} elementos separados por espaço.")
    print("Ex.: S 0 1 0 E  ou  S 0 # 0 E  ou  S 0 2 0 E")
    valid = set(list("SE0#") + [str(d) for d in range(0, 10)])
    for i in range(linhas):
        while True:
            linha = input(f"Linha {i+1}: ").strip().upper().split()
            if len(linha) != colunas:
                print(f"ERRO: precisa ter exatamente {colunas} elementos.")
                continue
            if not all(token in valid for token in linha):
                print("ERRO: use apenas S, E, 0, 1, #, 2..9.")
                continue
            lab.append(linha)
            break

    # valida S/E únicos aqui para feedback imediato
    try:
        _ = find_unique_positions(lab)
    except ValueError as e:
        print(f"Validação: {e}")
    return lab


def main():
    print("=" * 64)
    print("ALGORITMO A* – LABIRINTO (4 ou 8 direções, pesos de terreno)")
    print("=" * 64)

    while True:
        print("\nOpções:")
        print("1 - Usar labirinto de exemplo (com um terreno '2')")
        print("2 - Criar labirinto customizado")
        print("3 - Sair")

        op = input("Opção: ").strip()
        if op == "3":
            print("Encerrando...")
            return
        elif op not in ("1", "2"):
            print("Opção inválida.")
            continue

        diag_in = input("Permitir diagonais? (S/N): ").strip().upper()
        allow_diag = diag_in == "S"

        lab = create_example(True) if op == "1" else read_user_labyrinth()

        print("\nLabirinto original:")
        print_labyrinth(lab)

        print("\nExecutando A*...")
        try:
            result = a_star(lab, allow_diagonals=allow_diag)
        except ValueError as e:
            print(f"\n❌ Erro de validação: {e}")
            continue

        if result is None:
            print("\n❌ Sem solução: não há caminho entre S e E.")
        else:
            path, total_cost = result
            print(f"\n✓ Caminho encontrado com {len(path)} passos (inclui S e E).")
            print(f"Custo total acumulado: {total_cost:.3f}")
            print("\nCoordenadas do caminho:")
            for k, p in enumerate(path):
                print(f"Passo {k}: {p}")
            show_path(lab, path)

            # Visualização opcional com curses
            if run_curses_animation is not None:
                vis = input("\nVisualizar com curses em tempo real? (S/N): ").strip().upper()
                if vis == 'S':
                    try:
                        run_curses_animation(lab, path, delay_ms=120)
                    except Exception as e:
                        print(f"[curses] Falha ao iniciar visualização: {e}")
            else:
                print("\n[INFO] curses indisponível neste ambiente. Pulei a visualização.")

        print("\n" + "-" * 64)


if __name__ == "__main__":
    main()
