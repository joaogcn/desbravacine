import json
import os
import imdb
import pwinput

ia = imdb.IMDb()

def clean_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def carregar_dados():
    try:
        with open("dados.json", "r") as arquivo:
            dados = json.load(arquivo)
        return dados
    except FileNotFoundError:
        return {'usuarios': {}, 'avaliacoes': [], 'favoritos': {}}

def salvar_dados(dados):
    with open("dados.json", "w") as arquivo:
        json.dump(dados, arquivo, indent=2)

dados = carregar_dados()
usuario_atual = None

def registrar_usuario():
    nome_usuario = input("Digite um nome de usuário: ")
    if nome_usuario in dados['usuarios']:
        clean_terminal()
        print("Nome de usuário já existe. Escolha outro nome de usuário.")
        return
    senha = pwinput.pwinput("Digite uma senha: ")
    dados['usuarios'][nome_usuario] = senha
    salvar_dados(dados)
    clean_terminal()
    print("Registro de usuário bem-sucedido.")

def fazer_login():
    global usuario_atual
    nome_usuario = input("Digite seu nome de usuário: ")
    senha = pwinput.pwinput("Digite sua senha: ")
    if nome_usuario in dados['usuarios'] and dados['usuarios'][nome_usuario] == senha:
        usuario_atual = nome_usuario
        clean_terminal()
        print(f"Bem-vindo, {nome_usuario}!")
    else:
        clean_terminal()
        print("Nome de usuário ou senha inválidos.")

def excluir_avaliacao():
    if usuario_atual is None:
        clean_terminal()
        print("Você precisa fazer login para excluir uma avaliação.")
        return
    
    avaliacoes_usuario_atual = [avaliacao for avaliacao in dados['avaliacoes'] if avaliacao['Usuario'] == usuario_atual]

    if avaliacoes_usuario_atual:
        clean_terminal()
        print("Suas avaliações:")
        for i, avaliacao in enumerate(avaliacoes_usuario_atual, start=1):
            print(f"{i}. Avaliação:")
            print(f"Usuário: {avaliacao['Usuario']}")
            print(f"Filme: {avaliacao['Filme']} ")
            print(f"Nota: {avaliacao['Nota']}")
            print(f"Comentário: {avaliacao['Comentario']}")
            print(f"Favorito: {avaliacao['Favorito']}")
            print()

        avaliacao_a_excluir = int(input("Digite o número da avaliação a ser excluída (0 para cancelar): "))

        if 1 <= avaliacao_a_excluir <= len(avaliacoes_usuario_atual):
            avaliacao_a_excluir -= 1
            del dados['avaliacoes'][dados['avaliacoes'].index(avaliacoes_usuario_atual[avaliacao_a_excluir])]
            salvar_dados(dados)
            clean_terminal()
            print("Avaliação excluída com sucesso.")
        else:
            clean_terminal()
            print("Número de avaliação inválido.")
    else:
        clean_terminal()
        print("Nenhuma avaliação encontrada para o seu usuário.")

def pesquisar_filme():
    nome_filme = input("Digite o nome do filme: ")
    try:
        filmes = ia.search_movie(nome_filme)
        if not filmes:
            clean_terminal()
            print("Nenhum filme encontrado.")
            return None
        for idx, filme in enumerate(filmes):
            filmeselecionado = ia.get_movie(filme.getID())
            title = filme['title']
            year = filme.get('year', 'Desconhecido')
            diretores = filmeselecionado.get('director', [{'name': 'Desconhecido'}])
            diretores_nomes = ", ".join(diretor['name'] for diretor in diretores)
            print(f"{idx + 1}. {title} ({year}) Diretor: {diretores_nomes}")
            if idx == 4:
                break
        escolha = int(input("Escolha o filme (pelo número): "))
        escolha = escolha - 1
        if 0 <= escolha < len(filmes):
            filme_selecionado = ia.get_movie(filmes[escolha].getID())
            return filme_selecionado
        else:
            clean_terminal()
            print("Escolha inválida.")
            return None
    except:
        clean_terminal()
        print(f"Erro ao pesquisar o filme")
        return None

def info_filme():
    if usuario_atual is None:
        clean_terminal()
        print("Você precisa fazer login para avaliar um filme.")
        return
    filme = pesquisar_filme()
    title = filme['title']
    year = filme['year']
    rating = filme['rating']
    directors = filme['directors']
    casting = filme['cast']
    plot = filme.data['plot']
    clean_terminal()
    print(f'\n{title} - {year}')
    print(f'Nota: {rating}')
    diretores = ", ".join(map(str,directors))
    print(f'Diretor(es):{diretores}')
    ator = ", ".join(map(str,casting))
    print(f'\nAtor(es): {ator}')
    print(f'\nSinopse: {plot[0]}')

def avaliar_filme():
    if usuario_atual is None:
        clean_terminal()
        print("Você precisa fazer login para avaliar um filme.")
        return
    filme = pesquisar_filme()
    if filme:
        avaliacao_existente = [avaliacao for avaliacao in dados['avaliacoes'] if avaliacao['Usuario'] == usuario_atual and avaliacao['Filme'] == f"{filme['title']} ({filme['year']})"]

        if avaliacao_existente:
            clean_terminal()
            print("Avaliação existente. Atualizando opções:\n")
            print(f"Avaliação anterior:\n{avaliacao_existente[0]}")
            print()

            nota = input("Dê uma nova nota para o filme (0-10): ")
            comentario = input("Escreva um novo comentário: ")
            favorito = input("Este filme é um dos seus favoritos? (sim/não): ").strip().lower()

            avaliacao_existente[0]['Nota'] = nota
            avaliacao_existente[0]['Comentario'] = comentario
            avaliacao_existente[0]['Favorito'] = favorito

            salvar_dados(dados)
            clean_terminal()
            print("Avaliação atualizada com sucesso.")
        else:
            nota = input("Dê uma nota para o filme (0-10): ")
            try:
                nota = float(nota)
                if 0 <= nota <= 10:
                    comentario = input("Escreva um comentário: ")
                    favorito = input("Este filme é um dos seus favoritos? (sim/não): ").strip().lower()
                    if favorito == "sim":
                        salvar_filme_favorito(filme)
                    nova_avaliacao = {
                        'Usuario': usuario_atual,
                        'Filme': f"{filme['title']} ({filme['year']})",
                        'Nota': nota,
                        'Comentario': comentario,
                        'Favorito': favorito
                    }
                    dados['avaliacoes'].append(nova_avaliacao)
                    salvar_dados(dados)
                    clean_terminal()
                    print("Avaliação salva com sucesso.")
                else:
                    clean_terminal()
                    print("A nota deve estar entre 0 e 10.")
            except ValueError:
                clean_terminal()
                print("A nota deve ser um valor numérico.")

def salvar_filme_favorito(filme):
    if usuario_atual is None:
        clean_terminal()
        print("Você precisa fazer login para marcar um filme como favorito.")
        return

    filme_str = f"{filme['title']} ({filme['year']})"
    
    if usuario_atual not in dados['favoritos']:
        dados['favoritos'][usuario_atual] = [filme_str]
    else:
        dados['favoritos'][usuario_atual].append(filme_str)

    try:
        salvar_dados(dados)
        clean_terminal()
        print("Filme marcado como favorito.")
    except:
        clean_terminal()
        print(f"Erro ao salvar filme como favorito")

def visualizar_favoritos():
    if usuario_atual is None:
        clean_terminal()
        print("Você precisa fazer login para visualizar seus filmes favoritos.")
        return

    favoritos_usuario = dados['favoritos'].get(usuario_atual, [])

    if favoritos_usuario:
        clean_terminal()
        print(f"Filmes favoritos de {usuario_atual}:\n")
        for favorito in favoritos_usuario:
            print(favorito)
    else:
        clean_terminal()
        print("Nenhum filme favorito encontrado para o usuário.")

def visualizar_avaliacoes():
    try:
        avaliacoes = dados['avaliacoes']
        if avaliacoes:
            clean_terminal()
            print("Avaliações existentes:\n")
            for avaliacao in avaliacoes:
                print(f"Usuário: {avaliacao['Usuario']}")
                print(f"Filme: {avaliacao['Filme']}")
                print(f"Nota: {avaliacao['Nota']}")
                print(f"Comentário: {avaliacao['Comentario']}")
                print(f"Favorito: {avaliacao['Favorito']}")
                print()
        else:
            clean_terminal()
            print("Nenhuma avaliação encontrada.")
    except:
        clean_terminal()
        print(f"Erro ao visualizar as avaliações")

while True:
    print("\n------------- DesbravaCine ------------")
    print("1. Registrar um novo usuário")
    print("2. Fazer login")
    if usuario_atual:
        print("3. Pesquisar informações sobre um filme")
        print("4. Avaliar filme ou série")
        print("5. Visualizar avaliações existentes")
        print("6. Excluir uma avaliação")
        print("7. Visualizar filmes e séries favoritas")
    print("\nPara sair, digite Sair.")
    print("---------------------------------------\n")
    opcao = input("Escolha a opção: ")
    opcao = opcao.capitalize()
    print()
    if opcao == "1":
        registrar_usuario()
    elif opcao == "2":
        fazer_login()
    elif opcao == "3" and usuario_atual:
        info_filme()
    elif opcao == "4" and usuario_atual:
        avaliar_filme()
    elif opcao == "5" and usuario_atual:
        visualizar_avaliacoes()
    elif opcao == "6" and usuario_atual:
        excluir_avaliacao()
    elif opcao == "7" and usuario_atual:
        visualizar_favoritos()
    elif opcao == "Sair":
        break
    else:
        print("Opção inválida. Tente novamente.")
