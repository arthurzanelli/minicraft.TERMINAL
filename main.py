# MINECRAFT TERMINAL - versão simples para estudar
# Como jogar: digite w, a, s, d (e aperte Enter) para andar. Digite o para sair.
import csv #todo (porque precisamos de blibiotecas e variaveis para nosso codigo ficar fluido)
import os
import random
global frases
frases = int(0)
crefttable = False  #todo (variável global para indicar se o jogador tem uma mesa de trabalho)
criaturas = {
    "vaca": "01010",
    "porco": "01010",
    "ovelha": "01010",
    "galinha": "01010",
    "zumbi": "30222",
    "esqueleto": "24222",
    "aranha": "20102",
}
SPAWNS_POR_BLOCO = {
    "vazio": ["vaca", "porco", "ovelha", "galinha"],
    "arvore": ["vaca", "porco", "ovelha", "galinha"],
    "caverna": ["zumbi", "esqueleto", "aranha"],
}
SPAWNS_POR_BIOMA = {
    "floresta": ["vaca", "porco", "ovelha", "galinha"],
    "deserto": ["zumbi", "aranha"],
    "planície": ["vaca", "porco", "ovelha", "galinha", "zumbi"],
    "montanha": ["esqueleto", "aranha", "zumbi"],
    "pântano": ["zumbi", "aranha", "vaca"],
}
#* (Primeiro dígito: ataque curto; segundo: ataque à distância; terceiro: vida;)
#* (quarto: pacificidade; quinto: artefatos.)
#* (Nomes dos arquivos onde o jogo guarda os dados)
PASTA_JOGO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_JOGADORES = os.path.join(PASTA_JOGO, "players.csv")
ARQUIVO_MAPA = os.path.join(PASTA_JOGO, "cordenadas.csv")
ARQUIVO_INVENTARIO = os.path.join(PASTA_JOGO, "inventario.csv")
ARQUIVO_BIOMA = os.path.join(PASTA_JOGO, "bioma.txt")
ARQUIVO_BAU = os.path.join(PASTA_JOGO, "bau.csv")
INVENTARIO_USUARIO_ATUAL = ""
hp = 20
fome = 20
força = 1
TAMANHO_MAPA = 100  # o mundo tem 100 x 100 blocos
ORDEM_BIOMAS = ["floresta", "deserto", "planície", "montanha", "pântano"]
CONFIGURACAO_BIOMAS = {
    "floresta": {"árvores": 0.50, "cavernas": 0.10},
    "deserto": {"árvores": 0.00, "cavernas": 0.10},
    "planície": {"árvores": 0.20, "cavernas": 0.40},
    "montanha": {"árvores": 0.10, "cavernas": 0.45},
    "pântano": {"árvores": 0.50, "cavernas": 0.15},
}
ALTURA_BIOMA = TAMANHO_MAPA // len(ORDEM_BIOMAS)


def clear_screen():# todo (deletar as coisas do terminal)
    """Limpa a tela no Windows ou em outros sistemas."""
    os.system("cls" if os.name == "nt" else "clear")

def substring(texto: str, inicio: int, fim: int) -> str:
    """
    Extrai uma substring de 'texto' entre os índices 'inicio' e 'fim'.
    O índice 'fim' é não inclusivo (como no fatiamento padrão do Python).
    
    Args:
        texto (str): Texto de entrada.
        inicio (int): Índice inicial (inclusive).
        fim (int): Índice final (exclusivo).
    
    Returns:
        str: Substring extraída ou string vazia se índices inválidos.
    """
    # Validação de tipos
    if not isinstance(texto, str):
        raise TypeError("O parâmetro 'texto' deve ser uma string.")
    if not isinstance(inicio, int) or not isinstance(fim, int):
        raise TypeError("Os parâmetros 'inicio' e 'fim' devem ser inteiros.")

    # Ajuste de limites para evitar IndexError
    tamanho = len(texto)
    if inicio < 0:
        inicio = 0
    if fim > tamanho:
        fim = tamanho
    if inicio >= fim:
        return ""  # Nenhuma substring válida

    return texto[inicio:fim]

def obter_bioma(x, y):
    """Devolve o bioma da região fixa em que o bloco está."""
    indice = min(y // ALTURA_BIOMA, len(ORDEM_BIOMAS) - 1)
    return ORDEM_BIOMAS[indice]


def interpretar_construcao_do_jogador(descricao):# todo (a interpretação de pedidos na ia)
    """Interpreta o pedido em linguagem natural e sugere uma construção."""
    descricao = descricao.lower().strip()

    construcoes = {#* para pradonizae as construções e compor a resposta da IA
        "casa": (("moradia", "casa", "abrigo", "lar", "quarto"), {"madeira": 12, "tábua": 6}),
        "ponte": (("ponte", "atravessar", "rio", "passarela"), {"tábua": 8}),
        "muralha": (("muralha", "parede", "defesa", "proteger", "forte"), {"pedra": 20}),
        "torre": (("torre", "vigia", "mirante", "observatório"), {"pedra": 12, "madeira": 8}),
    }
    materiais_do_jogo = {#* para filtrar os itens da construção
        "madeira", "tábua", "pedra", "ferro", "ouro",
        "diamante", "carvão", "amestista", "esmeralda",
    }

    for construcao, (palavras, materiais) in construcoes.items():
        if any(palavra in descricao for palavra in palavras):
            tamanho = next((numero for numero in range(1, 6) if str(numero) in descricao), 1)
            if any(palavra in descricao for palavra in ("pequena", "pequeno")):#
                tamanho = 1
            elif any(palavra in descricao for palavra in ("grande", "gigante")):
                tamanho = 3
            fatores = {"madeira": 3 if tamanho > 1 else 0, "tábua": 2 if tamanho > 1 else 0,
                       "pedra": 4 if tamanho > 1 else 0}
            materiais = {
                item: quantidade + fatores.get(item, 0) * (tamanho - 1)
                for item, quantidade in materiais.items()
            }
            #todo (pode-se dizer na construção se é grande ou pequena para criar uma construção)
            materiais_pedidos = [
                material for material in materiais_do_jogo
                if material in descricao
            ]
            if materiais_pedidos:
                materiais = {#* (precisamos ter uma quantidade de blocos por tamanho. 30 é ideal)
                    material: (30 * tamanho if material in ("pedra", "ferro") else 10 * tamanho)
                    for material in materiais_pedidos
                }
            return construcao, materiais, tamanho

    return None, None, 1



# ---------------------------------------------------------------
# JOGADORES (login e XP)
# ---------------------------------------------------------------
def carregar_jogadores():#todo (lê o csv e devolve um dicionario)
    jogadores = {}
    if os.path.exists(ARQUIVO_JOGADORES):
        with open(ARQUIVO_JOGADORES, encoding="utf-8-sig") as arquivo:
            for linha in csv.DictReader(arquivo):
                xp_salvo = linha.get("xp")
                try:
                    xp = int(xp_salvo) if xp_salvo and xp_salvo.strip() else 0
                except (TypeError, ValueError):
                    xp = 0
                jogadores[linha["username"]] = {
                    "senha": linha["password"],
                    "xp": xp,
                }
    return jogadores




def salvar_jogadores(jogadores):
    """Escreve todos os jogadores no players.csv."""
    with open(ARQUIVO_JOGADORES, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["username", "password", "xp"])
        for nome, dados in jogadores.items():
            escritor.writerow([nome, dados["senha"], dados["xp"]])


def fazer_login(jogadores):#? (fazer login)
    global frases
    """Pergunta nome e senha. Cria a conta se for novo. Devolve o nome (ou None)."""
    print("================================")
    print("      MINECRAFT TERMINAL alpha 3.1! better comands edition")
    print("================================")
    avisos = input("Deseja ver os avisos do jogo? (s/n) ").strip().lower()
    if avisos in ("s", "sim"):
        print("\nAvisos:")
        print("demo alpha 3.1: better commands edition")
        print("alpha 3.0: table in the base")
        print("ultima atualização: 4 de novenbro de 2026")
        print("BATALHAS ENCREMENTADAS!: alpha 2.1")
        print("IA REVOLUTIONN: adicionado ia para interpretar pedidos de construção:alpha 2.0")
        print("PRIMEIRA VERSÃO: alpha 1.0")
    nome = input("Digite seu nome de usuário: ").strip()
    senha = input("Digite sua senha: ").strip()
    print("Login realizado com sucesso!")
    if nome in jogadores:
        if jogadores[nome]["senha"] != senha:
            print("Senha incorreta.")
            return None

        print("Bem-vindo de volta, " + nome + "!")
        frases += 7
    else:
        print("Olá, " + nome + "! Sua conta foi criada.")
        frases += 6
        jogadores[nome] = {"senha": senha, "xp": 0}
        salvar_jogadores(jogadores)
    return nome











# ---------------------------------------------------------------
# INVENTÁRIO
# ---------------------------------------------------------------























def carregar_inventario(username): #todo (carregar o inventario)
    """Lê somente os itens do usuário informado."""
    inventario = {}
    if os.path.exists(ARQUIVO_INVENTARIO):
        with open(ARQUIVO_INVENTARIO, encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)
            campos = leitor.fieldnames or []
            formato_antigo = "username" not in campos
            inventario_migrado = False
            for linha in leitor:
                if formato_antigo:
                    nome_usuario = username
                    inventario_migrado = True
                else:
                    nome_usuario = linha.get("username", "").strip()
                if nome_usuario != username:
                    continue
                quantidade = linha.get("quantidade")
                if quantidade is None or not quantidade.strip():
                    continue
                try:
                    inventario[linha["item"]] = int(quantidade)
                except (TypeError, ValueError):
                    continue
            if inventario_migrado and inventario:
                salvar_inventario(inventario, username)
    return inventario


def salvar_inventario(inventario, username=None):#todo (salva o inventario)
    global INVENTARIO_USUARIO_ATUAL
    if username is None:
        username = INVENTARIO_USUARIO_ATUAL

    linhas = []
    if os.path.exists(ARQUIVO_INVENTARIO):
        with open(ARQUIVO_INVENTARIO, encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)
            if "username" in (leitor.fieldnames or []):
                for linha in leitor:
                    if linha.get("username", "").strip() != username:
                        linhas.append({
                            "username": linha.get("username", "").strip(),
                            "item": linha["item"],
                            "quantidade": linha["quantidade"],
                            "peso": linha.get("peso", linha["quantidade"]),
                        })

    with open(ARQUIVO_INVENTARIO, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["username", "item", "quantidade", "peso"])
        for linha in linhas:
            escritor.writerow([
                linha["username"],
                linha["item"],
                linha["quantidade"],
                linha["peso"],
            ])
        for item, quantidade in inventario.items():
            escritor.writerow([username, item, quantidade, quantidade])


def carregar_bau(username):#todo (vê o báu e carrega ele)
    itens = {}
    if not os.path.exists(ARQUIVO_BAU):
        return itens

    with open(ARQUIVO_BAU, encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            if linha.get("username", "").strip() != username:
                continue
            try:
                quantidade = int(linha["quantidade"])
            except (TypeError, ValueError):
                continue
            itens[linha["item"]] = quantidade
    return itens


def salvar_coisa_no_bau(username, itens):
    """Salva somente o baú do usuário, preservando os demais usuários."""
    linhas = []
    if os.path.exists(ARQUIVO_BAU):
        with open(ARQUIVO_BAU, encoding="utf-8") as arquivo:
            for linha in csv.DictReader(arquivo):
                if linha.get("username", "").strip() != username:
                    linhas.append(linha)

    with open(ARQUIVO_BAU, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["username", "item", "quantidade"])
        for linha in linhas:
            escritor.writerow([linha["username"], linha["item"], linha["quantidade"]])
        for item, quantidade in itens.items():
            if quantidade > 0:
                escritor.writerow([username, item, quantidade])


def mostrar_inventario(inventario):#? salva coisas no báu 
    global frases
    if len(inventario) == 0:
        print("Inventário vazio.")
    for item, quantidade in inventario.items():
        print("-", item, "x", quantidade)
    frases += 1


def adicionar_item(inventario, item, quantidade):
    global frases
    inventario[item] = inventario.get(item, 0) + quantidade
    salvar_inventario(inventario)
    print("Você coletou", quantidade, item + "(s).")
    frases += 1

def remover_item(inventario, item, quantidade):
    global frases
    if item not in inventario:
        print("Você não tem", item)
        frases += 1
    elif quantidade > inventario[item]:
        print("Você só tem", inventario[item], item)
        frases += 1
    else:
        inventario[item] = inventario[item] - quantidade
        if inventario[item] == 0:
            del inventario[item]  # acabou, tira da lista
        salvar_inventario(inventario)
        print("Você removeu", quantidade, item + "(s).")
        frases += 1










# ---------------------------------------------------------------
# MAPA
# ---------------------------------------------------------------

















def criar_mapa():#todo (Cria um mundo novo. O mapa é um dicionário: (x, y) -> nome da estrutura. + criaturas)
    mapa = {}
    for x in range(TAMANHO_MAPA):
        for y in range(TAMANHO_MAPA):
            mapa[(x, y)] = "vazio"

    blocos_por_arvore = 4

    for indice, bioma in enumerate(ORDEM_BIOMAS):#todo cria os biomas
        y_minimo = indice * ALTURA_BIOMA
        y_maximo = min((indice + 1) * ALTURA_BIOMA, TAMANHO_MAPA)
        configuracao = CONFIGURACAO_BIOMAS[bioma]
        blocos_da_regiao = TAMANHO_MAPA * (y_maximo - y_minimo)
        blocos_arvores = int(blocos_da_regiao * configuracao["árvores"])
        blocos_cavernas = int(blocos_da_regiao * configuracao["cavernas"])

        candidatos_arvores = [
            (x, y)
            for x in range(TAMANHO_MAPA)
            for y in range(y_minimo, y_maximo - blocos_por_arvore + 1)
        ]
        random.shuffle(candidatos_arvores)

        arvores_colocadas = 0
        quantidade_arvores = blocos_arvores // blocos_por_arvore
        if quantidade_arvores == 0:
            posicoes_livres = [
                (x, y)
                for x in range(TAMANHO_MAPA)
                for y in range(y_minimo, y_maximo)
                if mapa[(x, y)] == "vazio"
            ]
            random.shuffle(posicoes_livres)
            for x, y in posicoes_livres[:blocos_cavernas]:
                mapa[(x, y)] = "caverna"
            continue

        for x, y in candidatos_arvores:
            blocos = [(x, y + parte) for parte in range(blocos_por_arvore)]
            if all(mapa[bloco] == "vazio" for bloco in blocos):
                for bloco in blocos:
                    mapa[bloco] = "árvore"
                arvores_colocadas += 1
            if arvores_colocadas >= quantidade_arvores:
                break

        posicoes_livres = [
            (x, y)
            for x in range(TAMANHO_MAPA)
            for y in range(y_minimo, y_maximo)
            if mapa[(x, y)] == "vazio"
        ]
        random.shuffle(posicoes_livres)
        for x, y in posicoes_livres[:blocos_cavernas]:
            mapa[(x, y)] = "caverna"
    return mapa

def salvar_mapa(mapa):#todo (salva o mapa)
    with open(ARQUIVO_MAPA, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["x", "y", "estrutura"])
        for (x, y), estrutura in mapa.items():
            escritor.writerow([x, y, estrutura])


def salvar_bioma(bioma):
    with open(ARQUIVO_BIOMA, "w", encoding="utf-8") as arquivo:
        arquivo.write(bioma)


def carregar_bioma():
    if os.path.exists(ARQUIVO_BIOMA):
        with open(ARQUIVO_BIOMA, encoding="utf-8") as arquivo:
            bioma = arquivo.read().strip()
        if bioma in CONFIGURACAO_BIOMAS:
            return bioma

    bioma = random.choice(list(CONFIGURACAO_BIOMAS))
    salvar_bioma(bioma)
    return bioma


def carregar_mapa():
    """Lê o mapa do arquivo. Se não existir, cria um novo."""
    if not os.path.exists(ARQUIVO_MAPA):
        mapa = criar_mapa()
        salvar_mapa(mapa)
        return mapa

    mapa = {}
    with open(ARQUIVO_MAPA, encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            x_mapa = linha.get("x")
            y_mapa = linha.get("y")
            estrutura = linha.get("estrutura")
            if not x_mapa or not y_mapa or not estrutura:
                continue
            # no arquivo antigo aparece "árvore\1" e "caverna\13": pegamos só o nome
            nome = estrutura.split("\\")[0]
            try:
                mapa[(int(x_mapa), int(y_mapa))] = nome
            except (TypeError, ValueError):
                continue

    mapa_valido = True
    for indice, bioma in enumerate(ORDEM_BIOMAS):#todo (enumerate para percorrer a lista e repetir até quando achar o termo)
        y_minimo = indice * ALTURA_BIOMA
        y_maximo = min((indice + 1) * ALTURA_BIOMA, TAMANHO_MAPA)
        configuracao = CONFIGURACAO_BIOMAS[bioma]
        blocos_regiao = TAMANHO_MAPA * (y_maximo - y_minimo)
        blocos_arvores = sum(
            estrutura == "árvore"
            for (x, y), estrutura in mapa.items()
            if y_minimo <= y < y_maximo
        )
        blocos_cavernas = sum(
            estrutura == "caverna" or estrutura in ("zumbi", "esqueleto", "aranha")
            for (x, y), estrutura in mapa.items()
            if y_minimo <= y < y_maximo
        )
        quantidade_arvores = blocos_arvores // 4
        quantidade_arvores_esperada = (int(blocos_regiao * configuracao["árvores"]) // 4)
        if (quantidade_arvores != quantidade_arvores_esperada
                or blocos_cavernas != int(blocos_regiao * configuracao["cavernas"])):
            mapa_valido = False

    if not mapa_valido:
        mapa = criar_mapa()
        salvar_mapa(mapa)
    return mapa


# ---------------------------------------------------------------
# O JOGO
# ---------------------------------------------------------------












def fazer_acao(mapa, x, y, inventario, xp):#? (açôes paradas: pra o jogador escolher o que ele quer fazer no bloco dele)
   
    global frases
    estrutura = mapa[(x, y)]
    if estrutura in criaturas:
        return gerar_criatura(mapa, x, y, inventario, xp)
    if estrutura == "base:baú":
        usar_bau(INVENTARIO_USUARIO_ATUAL, inventario)
        return xp

    # a primeira opção muda de acordo com o bloco
    if estrutura == "árvore":
        primeira = "quebrar madeira"
    elif estrutura == "caverna":
        primeira = "minerar pedra"
    else:
        primeira = "cavar"

    if estrutura == "vazio":
        print("1 - " + primeira + " | 2 - visão de cima | 3 - jogar item fora | 4 - construir | Enter - voltar")
        frases += 1
    else:
        print("1 - " + primeira + " | 2 - visão de cima | 3 - jogar item fora | Enter - voltar")
    opcao = input(" ")
    frases += 2
    #? sequencia de opções de jogador
    if opcao == "1":
        if estrutura == "árvore":
            adicionar_item(inventario, "madeira", random.randint(1, 7))
            xp = int(xp) + 5
            print("+5 XP")
        elif estrutura == "caverna":
            adicionar_item(inventario, "pedra", random.randint(1, 5))
            xp = int(xp) + 5
            print("+5 XP")

            #? (sorte: além da pedra, pode aparecer um minério (de 1 a 100))
            #? (mecanica de sorte)
            sorte = random.randint(1, 100)
            if sorte == 1:  # 1% de chance
                adicionar_item(inventario, "diamante", 1)
                xp = xp + 50
                print("DIAMANTE! +50 XP")
                frases += 1
            elif sorte <= 9:  # 8% de chance
                adicionar_item(inventario, "ouro", 1)
                xp = xp + 20
                print("Você achou ouro! +20 XP")
                frases += 1
            elif sorte <= 29:  # 20% de chance
                adicionar_item(inventario, "ferro", 1)
                xp = xp + 10
                print("Você achou ferro! +10 XP")
                frases += 1
            elif sorte <= 59:  # 30% de chance
                adicionar_item(inventario, "carvão", 1)
                xp = xp + 5
                print("Você achou carvão! +5 XP")
                frases += 1
            elif sorte <= 69:  # 10% de chance
                adicionar_item(inventario, "amestista", 1)
                xp = xp + 15
                print("Você achou amestista! +15 XP")
                frases += 1
            elif sorte <= 79:  # 10% de chance
                adicionar_item(inventario, "esmeralda", 1)
                xp = xp + 25
                print("Você achou esmeralda! +25 XP")
                frases += 1
        else:  # vazio: 21% de chance de achar uma caverna
            sorte = random.randint(1, 100)
            if sorte <= 21:
                mapa[(x, y)] = "caverna"
                salvar_mapa(mapa)
                print("Você cavou e achou uma caverna!")
                frases += 1
            else:
                print("Você não encontrou nada.")
                frases += 1
    elif opcao == "2":
        desenhar_visao(mapa, x, y)
    elif opcao == "3":
        item = input("Qual item? ")
        frases += 1
        quantidade = input("Quantos? ")
        frases += 1
        if quantidade.isdigit():
            remover_item(inventario, item, int(quantidade))
        else:
            print("Digite um número valido.")
            frases += 1
    elif opcao == "5":
        if estrutura != "vazio":
            print("Você só pode construir em um bloco vazio.")
            return xp
        
        #? pedido de ia

        pedido = input("Descreva para a IA o que você deseja construir: ").strip()
        if "craft table" in pedido.lower() or "mesa de trabalho" in pedido.lower():
            base_usos(mapa, x, y, inventario, "mesa de trabalho")
            return xp
        elif "fornalha" in pedido.lower():
            base_usos(mapa, x, y, inventario, "fornalha")
            return xp
        elif "porta" in pedido.lower():
            base_usos(mapa, x, y, inventario, "porta")
            return xp
        elif "baú" in pedido.lower() or "bau" in pedido.lower():
            base_usos(mapa, x, y, inventario, "baú")
            return xp
        if not pedido:
            print("Você não descreveu nenhuma construção.")
            return xp

        construcao, materiais, tamanho = interpretar_construcao_do_jogador(pedido)
        if construcao is None:#? não conseguiu o resultado
            print("A IA não conseguiu identificar uma construção conhecida nesse pedido.")
            print("Tente mencionar: casa, ponte, muralha ou torre.")
            frases += 2
            return xp

        print(f"A IA entendeu: {construcao} (tamanho {tamanho}).")
        print("Materiais necessários:", ", ".join(
            f"{quantidade} {item}" for item, quantidade in materiais.items()
        ))
        if not all(inventario.get(item, 0) >= quantidade for item, quantidade in materiais.items()):
            print("Você não tem os materiais necessários.")
            frases += 1
            for item, quantidade in materiais.items():
                faltando = quantidade - inventario.get(item, 0)
                if faltando > 0:
                    print(f"Faltam {faltando} {item}(s).")
                    frases += 1
            return xp

        confirmar_construcao = input("Confirmar construção? (s/n): ").strip().lower()
        frases += 1
        if confirmar_construcao not in ("s", "sim"):
            print("Construção cancelada.")
            frases += 1
            return xp

        for item, quantidade in materiais.items():
            remover_item(inventario, item, quantidade)
        mapa[(x, y)] = "construção:" + construcao
        salvar_mapa(mapa)
        xp += 10
        print(f"Você construiu uma {construcao}! +10 XP")
        frases += 1
        return xp

    return xp

def andar(mapa, x, y):
    """Pergunta a direção e devolve a nova posição (x, y)."""
    global frases
    direcao = input("Direção (w = cima, s = baixo, a = esquerda, d = direita): ").lower()
    frases += 1
    novo_x = x
    novo_y = y
    if direcao == "w":
        novo_y = y + 1
    elif direcao == "s":
        novo_y = y - 1
    elif direcao == "a":
        novo_x = x - 1
    elif direcao == "d":
        novo_x = x + 1
    else:
        print("Direção inválida.")
        frases += 1
        return x, y

    # só anda se o bloco existir no mapa
    if (novo_x, novo_y) not in mapa:
        print("Você chegou ao limite do mapa.")
        frases += 1
        return x, y
    return novo_x, novo_y


def desenhar_visao(mapa, x, y):#? desenha a visão do jogador
    """Desenha na tela os blocos ao redor do jogador (visto de cima)."""
    global frases
    alcance = 5  # quantos blocos enxergamos para cada lado
    simbolos = {#* pontos de onde as pessoas estão
        "vazio": " ", "árvore": "T", "caverna": "/",
        "bichos": "@"
    }

    # o y maior fica em cima, por isso a linha começa do topo e desce
    for linha_y in range(y + alcance, y - alcance - 1, -1):
        linha = ""
        for coluna_x in range(x - alcance, x + alcance + 1):
            if coluna_x == x and linha_y == y:
                linha = linha + "[]"  # o jogador
            elif (coluna_x, linha_y) in mapa:
                estrutura = mapa[(coluna_x, linha_y)]
                simbolo = "@" if estrutura in criaturas else simbolos.get(estrutura, " ")
                linha = linha + simbolo + " "
        print(linha)
    print("[] você | T árvore | / caverna | @ criatura ou animal")
    frases += 5

def executar_turno_ia(mapa, x_jogador, y_jogador, xp):
    """Executa o comportamento das criaturas uma vez a cada ação do jogador."""
    global frases
    criaturas_no_mapa = [
        (pos_x, pos_y, estrutura)
        for (pos_x, pos_y), estrutura in mapa.items()
        if estrutura in criaturas
    ]

    for pos_x, pos_y, criatura in criaturas_no_mapa:
        distancia = abs(pos_x - x_jogador) + abs(pos_y - y_jogador)
        pacificidade = substring(criaturas[criatura], 3, 4)

        if porta_protege_area(mapa, x_jogador, y_jogador):
            continue

        if pacificidade == "2" and distancia <= 4:
            direcao_x = 1 if pos_x < x_jogador else -1 if pos_x > x_jogador else 0
            direcao_y = 1 if pos_y < y_jogador else -1 if pos_y > y_jogador else 0
            novo_x = pos_x + direcao_x
            novo_y = pos_y + direcao_y
            if mapa.get((novo_x, novo_y)) == "vazio":
                del mapa[(pos_x, pos_y)]
                mapa[(novo_x, novo_y)] = criatura
                pos_x, pos_y = novo_x, novo_y
                print(f"{criatura.capitalize()} está vindo em sua direção!")
                frases += 1
            if abs(pos_x - x_jogador) + abs(pos_y - y_jogador) <= 1:
                dano = int(substring(criaturas[criatura], 0, 1))
                global hp
                hp -= dano
                print(f"O(A) {criatura} atacou você! -{dano} HP ({hp} restantes).")
                frases += 1
        else:
            direcao = random.choice(((0, 1), (0, -1), (-1, 0), (1, 0), (0, 0)))
            novo_x = pos_x + direcao[0]
            novo_y = pos_y + direcao[1]
            if mapa.get((novo_x, novo_y)) == "vazio":
                del mapa[(pos_x, pos_y)]
                mapa[(novo_x, novo_y)] = criatura
                frases += 1

        salvar_mapa(mapa)

    if random.randint(1, 100) <= 8 and len(criaturas_no_mapa) < 12:
        posicoes = [
            (pos_x, pos_y)
            for pos_x in range(max(0, x_jogador - 4), min(TAMANHO_MAPA, x_jogador + 5))
            for pos_y in range(max(0, y_jogador - 4), min(TAMANHO_MAPA, y_jogador + 5))
            if mapa.get((pos_x, pos_y)) in SPAWNS_POR_BLOCO
            and abs(pos_x - x_jogador) + abs(pos_y - y_jogador) >= 2
        ]
        if posicoes:
            pos_x, pos_y = random.choice(posicoes)
            bloco = mapa[(pos_x, pos_y)]
            criaturas_do_bloco = SPAWNS_POR_BLOCO[bloco].copy()
            criaturas_do_bioma = SPAWNS_POR_BIOMA[obter_bioma(pos_x, pos_y)]
            criaturas_possiveis = [
                nome for nome in criaturas_do_bloco
                if nome in criaturas_do_bioma
            ]
            if not criaturas_possiveis:
                criaturas_possiveis = criaturas_do_bloco
            criatura = random.choice(criaturas_possiveis)
            mapa[(pos_x, pos_y)] = criatura
            salvar_mapa(mapa)
            print(f"Uma {criatura} apareceu em um bloco de {bloco}.")
            frases += 1

    if hp <= 0:
        print("Você morreu! Seu progresso de XP será perdido.")
        frases += 1
        return 0

    return xp

#? coisas na batalha
def jogar(nome, jogadores):
    global frases, INVENTARIO_USUARIO_ATUAL
    xp = jogadores[nome]["xp"]
    if xp is None:
        xp = 0
    INVENTARIO_USUARIO_ATUAL = nome
    inventario = carregar_inventario(nome)
    mapa = carregar_mapa()
    x = 50
    y = 50

    print("\nVocê entrou no mundo!")
    frases += 1
    while True:
        print("\nPosição: (" + str(x) + ", " + str(y) + ")  XP: " + str(xp))
        print("Bioma: " + obter_bioma(x, y))
        print("Você está em: " + mapa[(x, y)])
        print("1 - andar | 2 - fazer uma ação | 3 - inventário | 4 - creafting | 5 - sair")
        escolha = input("O que deseja fazer? ")
        frases += 1
        if escolha == "1":
            x, y = andar(mapa, x, y)
            frases += 1
        elif escolha == "2":
            xp = fazer_acao(mapa, x, y, inventario, xp)
            if xp is None:
                xp = 0
            frases += 1
        elif escolha == "3":
            mostrar_inventario(inventario)
        elif escolha == "4":
            craft(inventario, mapa)
        elif escolha == "5":
            break
        else:
            print("Opção inválida.")

        xp = executar_turno_ia(mapa, x, y, xp)
        if xp is None:
            xp = 0

    # ao sair, salva o XP
    jogadores[nome]["xp"] = xp
    salvar_jogadores(jogadores)
    print("Seu XP final:", xp)
    print("Progresso salvo!")



#---------------------------------------------------------------
# CRAFTING
#---------------------------------------------------------------

def confirmar(texto):
    resposta = input(texto + " (s/n): ").strip().lower()
    return resposta in ("s", "sim")


def tem_mesa_de_trabalho(mapa):
    return any(estrutura == "base:mesa de trabalho" for estrutura in mapa.values())


def craft(inventario, mapa=None):#? crafting de todas as coisas
    """Mostra receitas disponíveis e cria o item escolhido."""
    global frases
    if mapa is None:
        mapa = {}
    while True:#?  receitas de crafting
        tem_mesa = (inventario.get("mesa de trabalho", 0) > 0
                    or tem_mesa_de_trabalho(mapa))

        print("\nReceitas de crafting:")
        print("1 - Mesa de trabalho: 4 tábuas")
        print("2 - Graveto: 2 tábuas")
        print("3 - Tábuas: 1 madeira (gera 4 tábuas)")
        frases += 4
        if tem_mesa:
            print("4 - Porta: 6 tábuas")
            print("5 - Picareta: 2 gravetos e 3 tábuas")
            print("6 - Fornalha: 8 pedras")
            print("7 - Baú: 8 tábuas")
            frases += 2
        print("0 - voltar")
        frases += 1
        escolha = input("Escolha uma receita: ").strip()

        if escolha == "1" and inventario.get("tábua", 0) >= 4:
            if confirmar("Criar uma mesa de trabalho?"):
                remover_item(inventario, "tábua", 4)
                adicionar_item(inventario, "mesa de trabalho", 1)
                print("Você criou uma mesa de trabalho!")
                frases += 1
        elif escolha == "2" and inventario.get("tábua", 0) >= 2:
            if confirmar("Criar um graveto?"):
                remover_item(inventario, "tábua", 2)
                adicionar_item(inventario, "graveto", 1)
                print("Você criou um graveto!")
                frases += 1
        elif escolha == "3" and inventario.get("madeira", 0) >= 1:
            if confirmar("Criar 4 tábuas?"):
                remover_item(inventario, "madeira", 1)
                adicionar_item(inventario, "tábua", 4)
                print("Você criou 4 tábuas!")
                frases += 1
        elif escolha == "4" and tem_mesa and inventario.get("tábua", 0) >= 6:
            if confirmar("Criar uma porta?"):
                remover_item(inventario, "tábua", 6)
                adicionar_item(inventario, "porta", 1)
                print("Você criou uma porta!")
                frases += 1
        elif escolha == "5" and tem_mesa and inventario.get("graveto", 0) >= 2 and inventario.get("tábua", 0) >= 3:
            if confirmar("Criar uma picareta?"):
                remover_item(inventario, "graveto", 2)
                remover_item(inventario, "tábua", 3)
                adicionar_item(inventario, "picareta", 1)
                print("Você criou uma picareta!")
                frases += 1
        elif escolha == "6" and tem_mesa and inventario.get("pedra", 0) >= 8:
            if confirmar("Criar uma fornalha?"):
                remover_item(inventario, "pedra", 8)
                adicionar_item(inventario, "fornalha", 1)
                print("Você criou uma fornalha!")
                frases += 1
        elif escolha == "7" and tem_mesa and inventario.get("tábua", 0) >= 8:
            if confirmar("Criar um baú?"):
                remover_item(inventario, "tábua", 8)
                adicionar_item(inventario, "baú", 1)
                print("Você criou um baú!")
                frases += 1
        elif escolha == "0":
            return
        else:
            print("Opção inválida ou você não tem os materiais necessários.")
            frases += 1
def gerar_criatura(mapa, x, y, inventario, xp):#todo (gerar cada criatura num bloco)
    global hp, força, frases
    """Interage com uma criatura que já está ocupando o bloco atual."""
    criatura = mapa[(x, y)]
    if criatura not in criaturas:
        return xp
    if porta_protege_area(mapa, x, y):
        print("Uma porta fechada bloqueou o ataque nesta área de 2 x 2.")
        mapa[(x, y)] = "vazio"
        salvar_mapa(mapa)
        return xp

    pacificidade = int(substring(criaturas[criatura], 3, 4))
    if pacificidade == 1:
        acao = input(f"Deseja derrotar a {criatura}? (s/n): ").strip().lower()
        frases += 1
        if acao not in ("s", "sim"):
            print(f"A {criatura} continua no bloco.")
            return xp

        recompensas = {
            "vaca": [("couro", 1, 2), ("carne crua", 1, 3)],
            "porco": [("bacon cru", 1, 3)],
            "ovelha": [("lã", 1, 2), ("carne crua", 1, 3)],
            "galinha": [("pena", 1, 3), ("carne crua", 1, 2)],
        }
        for item, minimo, maximo in recompensas[criatura]:
            adicionar_item(inventario, item, random.randint(minimo, maximo))
        mapa[(x, y)] = "vazio"
        salvar_mapa(mapa)
        xp += 10
        print(f"Você derrotou a {criatura}! +10 XP")
        return xp

    vida = int(substring(criaturas[criatura], 2, 3))
    dano_curto = int(substring(criaturas[criatura], 0, 1))
    dano_distancia = int(substring(criaturas[criatura], 1, 2))
    print(f"\n=== BATALHA: {criatura.upper()} ===")
    print(f"Sua vida: {hp} | Vida da criatura: {vida} | Ataque seu: {força}")
    while vida > 0 and hp > 0:
        acao = input("1 - atacar | 2 - defender | 3 - fugir: ").strip()
        frases += 1
        if acao == "3":
            print(f"Você fugiu da {criatura}.")
            return xp
        if acao == "2":
            reducao = max(1, (dano_curto + 1) // 2)
            dano_recebido = random.randint(1, reducao)
            hp -= dano_recebido
            print(f"Você se defendeu. -{dano_recebido} HP ({hp} restantes).")
        elif acao == "1":
            dano = força + random.randint(0, 1)
            vida -= dano
            print(f"Você causou {dano} de dano! Vida da {criatura}: {max(vida, 0)}.")
            if vida <= 0:
                break
            dano_recebido = dano_distancia if criatura == "esqueleto" else dano_curto
            if random.randint(1, 100) <= 20:
                print("Ataque esquivado! Você não sofreu dano.")
            else:
                hp -= dano_recebido
                print(f"A {criatura} atacou. -{dano_recebido} HP ({hp} restantes).")
        else:
            print("Escolha 1, 2 ou 3.")
            continue

        if hp <= 0:
            break

    if vida <= 0:
        mapa[(x, y)] = "vazio"
        salvar_mapa(mapa)
        recompensas = {
            "zumbi": [("carne podre", 1, 2)],
            "esqueleto": [("osso", 1, 2), ("flecha", 1, 3)],
            "aranha": [("teia", 1, 2)],
        }
        for item, minimo, maximo in recompensas[criatura]:
            adicionar_item(inventario, item, random.randint(minimo, maximo))
        xp += 20
        print(f"Você venceu! +20 XP")
        return xp

    print("Você morreu! Seu progresso de XP será perdido.")
    inventario.clear()
    salvar_inventario(inventario)
    mapa[(x, y)] = "vazio"
    salvar_mapa(mapa)
    return 0

def porta_protege_area(mapa, x, y):
    """Impede monstros em uma área de 2 x 2 ao redor de uma porta."""
    for (porta_x, porta_y), estrutura in mapa.items():
        if estrutura != "base:porta":
            continue
        if porta_x <= x <= porta_x + 1 and porta_y <= y <= porta_y + 1:
            return True
    return False


def usar_bau(username, inventario):
    while True:
        bau = carregar_bau(username)
        print("\nBaú:")
        if not bau:
            print("O baú está vazio.")
        else:
            for item, quantidade in bau.items():
                print("-", item, "x", quantidade)
        print("1 - guardar item | 2 - pegar item | 0 - fechar")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            item = input("Qual item guardar? ").strip()
            quantidade = input("Quantos? ").strip()
            if not quantidade.isdigit() or int(quantidade) <= 0:
                print("Digite uma quantidade válida.")
                continue
            quantidade = int(quantidade)
            if inventario.get(item, 0) < quantidade:
                print("Você não tem essa quantidade.")
                continue
            remover_item(inventario, item, quantidade)
            bau[item] = bau.get(item, 0) + quantidade
            salvar_coisa_no_bau(username, bau)
            print("Item guardado no baú.")
        elif escolha == "2":
            item = input("Qual item pegar? ").strip()
            quantidade = input("Quantos? ").strip()
            if not quantidade.isdigit() or int(quantidade) <= 0:
                print("Digite uma quantidade válida.")
                continue
            quantidade = int(quantidade)
            if bau.get(item, 0) < quantidade:
                print("O baú não tem essa quantidade.")
                continue
            bau[item] -= quantidade
            if bau[item] == 0:
                del bau[item]#todo (deletando o item do bau)
            salvar_coisa_no_bau(username, bau)
            adicionar_item(inventario, item, quantidade)
            print("Item retirado do baú.")
        elif escolha == "0":
            return
        else:
            print("Opção inválida.")


def base_usos(mapa, x, y, inventario, coisacolocavel):#? fazendo a carregação da base com itens
    global frases
    mesa = input(f"Deseja colocar uma {coisacolocavel} na base? (s/n) ").strip().lower()
    if mesa in ("s", "sim"):
        if inventario.get(coisacolocavel, 0) > 0:
            remover_item(inventario, coisacolocavel, 1)
            nome_estrutura = "base:" + coisacolocavel
            mapa[(x, y)] = nome_estrutura
            salvar_mapa(mapa)
            print(f"Você colocou a {coisacolocavel} na base.")
            frases += 1
        else:
            print(f"Você não tem uma {coisacolocavel} para colocar na base.")
            frases += 1
    else:
        print(f"Você decidiu não colocar a {coisacolocavel} na base.")
        frases += 1
    






















# ---------------------------------------------------------------
# PROGRAMA PRINCIPAL (é aqui que tudo começa)
# ---------------------------------------------------------------







if frases >= 50:
    clear_screen()
jogadores = carregar_jogadores()
nome = fazer_login(jogadores)
if nome:
    jogar(nome, jogadores)
