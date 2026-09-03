import aroeira, os
pasta = os.path.dirname(__file__)
fullpasta = os.path.join(pasta, "senha.txt")
tela = aroeira.Tela("Teste", largura= 1600, altura= 900, cor_fundo="cinza")
arquivo = open(fullpasta, "r")
check = arquivo.read()
arquivo.close()
listatarefa = []
def tarefasadc():
    listatarefa.append(tarefa.valor)
    print(listatarefa)
    tarefa.limpar()
    arospawn = 200
    for i in listatarefa:
        texto = aroeira.Texto(origem=aroeira.Ponto(100,arospawn),conteudo=f"[  ]   {i}")
        arospawn += 20
        tela.adicionar(texto)
def index():
    arquivo = open(fullpasta, "r")
    senha = arquivo.read()
    arquivo.close()
    botao = aroeira.Botao(origem=aroeira.Ponto(1400,820),ao_clicar=apagarSenha,rotulo="APAGAR SENHA")
    if login.valor == senha:
        global tarefa
        tela.remover(login)
        spawn = aroeira.Ponto(77,66)
        caixatexto = aroeira.Retangulo(origem=spawn, cor="verde", largura= 950, altura= 100)
        tarefa = aroeira.Campo(origem=aroeira.Ponto(100,90),ao_confirmar=tarefasadc)
        botao2 = aroeira.Botao(origem=aroeira.Ponto(450,100), ao_clicar=tarefasadc)
        tela.adicionar(botao2)
        tela.adicionar(tarefa)
        tela.adicionar(caixatexto)
        tela.adicionar(botao)
    else:
        caixa = aroeira.CaixaDeDialogo(titulo="Errou a senha", mensagem="Tente novamente")
        tela.mostrar_dialogo(caixa)
        login.limpar()
def criarSenha():
    arquivo = open(fullpasta, "w")
    x = registrar.valor
    arquivo.write(x)
    arquivo.close()
    tela.remover(registrar)
    tela.adicionar(login)
def apagarSenha():
    arquivo = open(fullpasta, "w")
    nada = ""
    arquivo.write(nada)
    arquivo.close()
    tela.fechar()     
def clicou(ponto):
    if ponto.x >= 110 and ponto.x <= 120 and ponto.y >= 200 and ponto.x <= 220:
         print(f"Clique em x={ponto.x}, y={ponto.y}")
login = aroeira.Campo(origem=aroeira.Ponto(230,250), rotulo="Senha",ao_confirmar=index)
registrar = aroeira.Campo(origem=aroeira.Ponto(230,250), rotulo="Definir Senha", ao_confirmar=criarSenha)
if check == "":
    tela.adicionar(registrar)
else:
    tela.adicionar(login)
tela.ao_clicar(clicou)
tela.executar()