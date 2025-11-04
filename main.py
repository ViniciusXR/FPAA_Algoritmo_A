"""
Algoritmo A* para encontrar o menor caminho em um labirinto 2D entre dois pontos, 
evitando obstáculos e considerando os custos dos movimentos. 
"""

import heapq
from typing import List, Tuple, Optional


class Node:
    """Representa um nó no algoritmo A*"""
    def __init__(self, position: Tuple[int, int], g_cost: int, h_cost: int, parent: Optional['Node'] = None):
        self.position = position  # (linha, coluna)
        self.g_cost = g_cost      # Custo do caminho do início até este nó
        self.h_cost = h_cost      # Heurística (estimativa até o destino)
        self.f_cost = g_cost + h_cost  # Custo total
        self.parent = parent      # Nó pai para reconstruir o caminho
    
    def __lt__(self, other):
        """Comparação para a fila de prioridade"""
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        """Comparação de igualdade baseada na posição"""
        return self.position == other.position
    
    def __hash__(self):
        """Hash baseado na posição para usar em sets"""
        return hash(self.position)


def heuristica_manhattan(pos_atual: Tuple[int, int], pos_final: Tuple[int, int]) -> int:
    """
    Calcula a distância de Manhattan entre duas posições.
    h(n) = |x_atual - x_final| + |y_atual - y_final|
    """
    return abs(pos_atual[0] - pos_final[0]) + abs(pos_atual[1] - pos_final[1])


def encontrar_posicoes(labirinto: List[List[str]]) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
    """
    Encontra as posições inicial (S) e final (E) no labirinto.
    Retorna: (posicao_inicial, posicao_final)
    """
    pos_inicial = None
    pos_final = None
    
    for i in range(len(labirinto)):
        for j in range(len(labirinto[i])):
            if labirinto[i][j] == 'S':
                pos_inicial = (i, j)
            elif labirinto[i][j] == 'E':
                pos_final = (i, j)
    
    return pos_inicial, pos_final


def obter_vizinhos(posicao: Tuple[int, int], labirinto: List[List[str]]) -> List[Tuple[int, int]]:
    """
    Retorna as posições vizinhas válidas (cima, baixo, esquerda, direita).
    """
    linha, coluna = posicao
    linhas = len(labirinto)
    colunas = len(labirinto[0])
    vizinhos = []
    
    # Movimentos possíveis: cima, baixo, esquerda, direita
    movimentos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for movimento in movimentos:
        nova_linha = linha + movimento[0]
        nova_coluna = coluna + movimento[1]
        
        # Verifica se está dentro dos limites
        if 0 <= nova_linha < linhas and 0 <= nova_coluna < colunas:
            # Verifica se não é um obstáculo
            if labirinto[nova_linha][nova_coluna] != '1':
                vizinhos.append((nova_linha, nova_coluna))
    
    return vizinhos


def reconstruir_caminho(no_final: Node) -> List[Tuple[int, int]]:
    """
    Reconstrói o caminho do início ao fim seguindo os nós pais.
    """
    caminho = []
    no_atual = no_final
    
    while no_atual is not None:
        caminho.append(no_atual.position)
        no_atual = no_atual.parent
    
    caminho.reverse()
    return caminho


def algoritmo_a_estrela(labirinto: List[List[str]]) -> Optional[List[Tuple[int, int]]]:
    """
    Implementa o algoritmo A* para encontrar o menor caminho no labirinto.
    
    Retorna:
        - Lista de coordenadas do caminho se encontrado
        - None se não houver caminho possível
    """
    # Validar se S e E existem no labirinto
    pos_inicial, pos_final = encontrar_posicoes(labirinto)
    
    if pos_inicial is None:
        print("Erro: Ponto inicial 'S' não encontrado no labirinto!")
        return None
    
    if pos_final is None:
        print("Erro: Ponto final 'E' não encontrado no labirinto!")
        return None
    
    # Inicializar estruturas de dados
    fila_aberta = []  # Fila de prioridade (heap)
    conjunto_aberto = set()  # Para verificação rápida se um nó está na fila
    conjunto_fechado = set()  # Nós já explorados
    
    # Criar nó inicial
    no_inicial = Node(
        position=pos_inicial,
        g_cost=0,
        h_cost=heuristica_manhattan(pos_inicial, pos_final)
    )
    
    heapq.heappush(fila_aberta, no_inicial)
    conjunto_aberto.add(pos_inicial)
    
    # Loop principal do A*
    while fila_aberta:
        # Pegar o nó com menor f_cost
        no_atual = heapq.heappop(fila_aberta)
        conjunto_aberto.remove(no_atual.position)
        
        # Verificar se chegamos ao destino
        if no_atual.position == pos_final:
            return reconstruir_caminho(no_atual)
        
        # Adicionar ao conjunto fechado
        conjunto_fechado.add(no_atual.position)
        
        # Explorar vizinhos
        for pos_vizinho in obter_vizinhos(no_atual.position, labirinto):
            # Ignorar se já foi explorado
            if pos_vizinho in conjunto_fechado:
                continue
            
            # Calcular custos para o vizinho
            g_cost_vizinho = no_atual.g_cost + 1  # Custo de movimento sempre 1
            h_cost_vizinho = heuristica_manhattan(pos_vizinho, pos_final)
            
            # Criar nó vizinho
            no_vizinho = Node(
                position=pos_vizinho,
                g_cost=g_cost_vizinho,
                h_cost=h_cost_vizinho,
                parent=no_atual
            )
            
            # Se o vizinho já está na fila aberta, verificar se encontramos um caminho melhor
            if pos_vizinho in conjunto_aberto:
                # Procurar o nó na fila
                encontrado = False
                for i, no_na_fila in enumerate(fila_aberta):
                    if no_na_fila.position == pos_vizinho:
                        if no_vizinho.g_cost < no_na_fila.g_cost:
                            # Encontramos um caminho melhor, atualizar o nó
                            fila_aberta[i] = no_vizinho
                            heapq.heapify(fila_aberta)
                        encontrado = True
                        break
            else:
                # Adicionar novo nó à fila aberta
                heapq.heappush(fila_aberta, no_vizinho)
                conjunto_aberto.add(pos_vizinho)
    
    # Se saímos do loop sem encontrar o destino, não há caminho
    return None


def exibir_labirinto_com_caminho(labirinto: List[List[str]], caminho: List[Tuple[int, int]]):
    """
    Exibe o labirinto com o caminho destacado usando '*'.
    """
    # Criar cópia do labirinto para não modificar o original
    labirinto_visual = [linha[:] for linha in labirinto]
    
    # Marcar o caminho (exceto S e E)
    for pos in caminho:
        linha, coluna = pos
        if labirinto_visual[linha][coluna] not in ['S', 'E']:
            labirinto_visual[linha][coluna] = '*'
    
    # Exibir o labirinto
    print("\nLabirinto com o caminho destacado:")
    for linha in labirinto_visual:
        print(' '.join(linha))


def criar_labirinto_exemplo() -> List[List[str]]:
    """
    Cria um labirinto de exemplo para teste.
    """
    return [
        ['S', '0', '1', '0', '0'],
        ['0', '0', '1', '0', '1'],
        ['0', '0', '0', '0', '0'],
        ['1', '0', '0', 'E', '1']
    ]


def ler_labirinto_usuario() -> List[List[str]]:
    """
    Permite ao usuário criar um labirinto customizado.
    """
    print("\nCriar labirinto customizado")
    print("Legenda: S = início, E = fim, 0 = livre, 1 = obstáculo")
    
    while True:
        try:
            linhas = int(input("\nQuantas linhas terá o labirinto? "))
            colunas = int(input("Quantas colunas terá o labirinto? "))
            
            if linhas <= 0 or colunas <= 0:
                print("O número de linhas e colunas deve ser maior que zero!")
                continue
            
            break
        except ValueError:
            print("Por favor, digite um número válido!")
    
    labirinto = []
    print(f"\nDigite cada linha do labirinto ({colunas} elementos separados por espaço):")
    print("Exemplo: S 0 1 0 E")
    
    for i in range(linhas):
        while True:
            linha_str = input(f"Linha {i + 1}: ").strip().upper()
            elementos = linha_str.split()
            
            if len(elementos) != colunas:
                print(f"Erro: Você deve digitar exatamente {colunas} elementos!")
                continue
            
            # Validar elementos
            valido = True
            for elem in elementos:
                if elem not in ['S', 'E', '0', '1']:
                    print(f"Erro: '{elem}' não é válido. Use apenas S, E, 0 ou 1!")
                    valido = False
                    break
            
            if valido:
                labirinto.append(elementos)
                break
    
    return labirinto


def main():
    """
    Função principal do programa.
    """
    print("=" * 60)
    print("ALGORITMO A* - ROBÔ DE RESGATE EM LABIRINTO")
    print("=" * 60)
    
    while True:
        print("\nEscolha uma opção:")
        print("1 - Usar labirinto de exemplo")
        print("2 - Criar labirinto customizado")
        print("3 - Sair")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == '1':
            labirinto = criar_labirinto_exemplo()
        elif opcao == '2':
            labirinto = ler_labirinto_usuario()
        elif opcao == '3':
            print("\nEncerrando programa...")
            break
        else:
            print("Opção inválida! Tente novamente.")
            continue
        
        # Exibir labirinto original
        print("\nLabirinto original:")
        for linha in labirinto:
            print(' '.join(linha))
        
        # Executar o algoritmo A*
        print("\nExecutando algoritmo A*...")
        caminho = algoritmo_a_estrela(labirinto)
        
        # Exibir resultado
        if caminho is None:
            print("\n❌ Sem solução: Não há caminho possível entre S e E!")
        else:
            print(f"\n✓ Caminho encontrado com {len(caminho)} passos!")
            print("\nCoordenadas do caminho:")
            for i, pos in enumerate(caminho):
                print(f"Passo {i}: {pos}")
            
            exibir_labirinto_com_caminho(labirinto, caminho)
        
        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()