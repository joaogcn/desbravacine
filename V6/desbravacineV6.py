import imdb
import pwinput
import os
ia = imdb.IMDb()

def clean_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def carregar_dados_usuarios():
    usuarios = {}
    try:
        with open("usuarios.txt", "r") as arquivo:
            linhas = arquivo.readlines()
            for i in range(0, len(linhas), 2):
                nome_usuario = linhas[i].strip()
                senha = linhas[i + 1].strip()
                usuarios[nome_usuario] = senha
        return usuarios
    except FileNotFoundError:
        return {}

def salvar_dados_usuarios(usuarios):
    with open("usuarios.txt", "w") as arquivo:
        for nome_usuario, senha in usuarios.items():
            arquivo.write(nome_usuario + "\n")
            arquivo.write(senha + "\n")

usuarios = carregar_dados_usuarios()
usuario_atual = None

def registrar_usuario():
    nome_usuario = input("Digite um nome de usuário: ")
    if nome_usuario in usuarios:
        clean_terminal()
        print("Nome de usuário já existe. Escolha outro nome de usuário.")
        return
    senha = pwinput.pwinput("Digite uma senha: ")
    usuarios[nome_usuario] = senha
    salvar_dados_usuarios(usuarios)
    clean_terminal()
    print("Registro de usuário bem-sucedido.")

def fazer_login():
    global usuario_atual #esse global ai é pra poder acessar a variavel fora da funcao. foi o unico metodo que consegui achar.
    nome_usuario = input("Digite seu nome de usuário: ")
    senha = pwinput.pwinput("Digite sua senha: ")
    if nome_usuario in usuarios and usuarios[nome_usuario] == senha:
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
    
    try:
        with open("avaliacoes.txt", "r") as arquivo:
            avaliacoes = arquivo.readlines()
        
        if avaliacoes:
            clean_terminal()
            print("Suas avaliações:")
            avaliacoes_usuario_atual = []
            avaliacao_atual = []
            for i, linha in enumerate(avaliacoes):
                if linha.strip() == f"Usuário: {usuario_atual}":
                    avaliacao_atual.append(linha)
                    for _ in range(4):
                        avaliacao_atual.append(avaliacoes[i + 1])
                        i += 1
                    avaliacoes_usuario_atual.append(avaliacao_atual)
                    avaliacao_atual = []

            if avaliacoes_usuario_atual:
                for i, avaliacao in enumerate(avaliacoes_usuario_atual):
                    num_avaliacao = i + 1
                    print(f"{num_avaliacao}. Avaliação:")
                    for linha in avaliacao:
                        print(linha.strip())
                    print()
                
                avaliacao_a_excluir = int(input("Digite o número da avaliação a ser excluída (0 para cancelar): "))
                
                if 1 <= avaliacao_a_excluir <= len(avaliacoes_usuario_atual):
                    avaliacao_a_excluir -= 1
                    indice_inicial = avaliacoes.index(avaliacoes_usuario_atual[avaliacao_a_excluir][0])
                    del avaliacoes[indice_inicial:indice_inicial + 5] 

                    with open("avaliacoes.txt", "w") as arquivo:
                        arquivo.writelines(avaliacoes)
                    clean_terminal()
                    print("Avaliação excluída com sucesso.")
                else:
                    clean_terminal()
                    print("Número de avaliação inválido.")
            else:
                clean_terminal()
                print("Nenhuma avaliação encontrada para o seu usuário.")
        else:
            clean_terminal()
            print("Nenhuma avaliação encontrada para o seu usuário.")
    except:
        clean_terminal()
        print(f"Erro ao excluir a avaliação")

def pesquisar_filme():
    nome_filme = input("Digite o nome do filme: ")
    try:
        filmes = ia.search_movie(nome_filme) #utiliza a lib pra acessar o imdb e pesquisar o filme, retorna as informações necessarias.
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
        nota = input("Dê uma nota para o filme (0-10): ")
        try:
            nota = float(nota)
            if 0 <= nota <= 10:
                comentario = input("Escreva um comentário: ")
                favorito = input("Este filme é um dos seus favoritos? (sim/não): ").strip().lower()
                if favorito == "sim":
                    salvar_filme_favorito(filme)
                try:
                    with open("avaliacoes.txt", "a") as arquivo:
                        arquivo.write(f"Usuário: {usuario_atual}\n")
                        arquivo.write(f"Filme: {filme['title']} ({filme['year']})\n")
                        arquivo.write(f"Nota: {nota}\n")
                        arquivo.write(f"Comentário: {comentario}\n")
                        arquivo.write(f"Favorito: {favorito}\n\n")
                    print("Avaliação salva com sucesso.")
                except:
                    clean_terminal()
                    print(f"Erro ao salvar a avaliação")
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

    filme_str = f"Usuário: {usuario_atual}, Filme: {filme['title']} ({filme['year']})\n"

    try:
        with open("favoritos.txt", "a") as arquivo:
            arquivo.write(filme_str)
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

    try:
        with open("favoritos.txt", "r") as arquivo:
            favoritos = arquivo.readlines()
            if favoritos:
                clean_terminal()
                print(f"Filmes favoritos de {usuario_atual}:\n")
                for favorito in favoritos:
                    if favorito.startswith(f"Usuário: {usuario_atual}"):
                        print(favorito.strip())
                if not any(favorito.startswith(f"Usuário: {usuario_atual}") for favorito in favoritos):
                    print("Nenhum filme favorito encontrado para o usuário.")
            else:
                clean_terminal()
                print("Nenhum filme favorito encontrado.")
    except FileNotFoundError:
        clean_terminal()
        print("Nenhum filme favorito encontrado.")
    except:
        clean_terminal()
        print(f"Erro ao visualizar os filmes favoritos")

def visualizar_avaliacoes():
    try:
        with open("avaliacoes.txt", "r") as arquivo:
            avaliacoes = arquivo.read()
            if avaliacoes:
                clean_terminal()
                print("Avaliações existentes:\n")
                print(avaliacoes)
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
    if usuario_atual != None:
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
    elif opcao == "3" and usuario_atual != None:
        info_filme()
    elif opcao == "4" and usuario_atual != None:
        avaliar_filme()
    elif opcao == "5" and usuario_atual != None:
        visualizar_avaliacoes()
    elif opcao == "6" and usuario_atual != None:
        excluir_avaliacao()
    elif opcao == "7" and usuario_atual != None:
        visualizar_favoritos()
    elif opcao == "Sair":
        break
    else:
        print("Opção inválida. Tente novamente.")
