from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from time import sleep

ROOT_PATH = Path(__file__).parent


class ContaIterador:

    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            conta = self.contas[self._index]
            return f"""\
            Agência:\t{conta.agencia}
            Número:\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t{conta.saldo:.2f}
            """
        except IndexError:
            raise StopIteration
        finally:
            self._index += 1


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        self.indice_conta = 0

    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_dia()) >= 10:
            print('Excedeu limite de transações diario!')
            return

        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.cpf}>'


class Conta:
    def __init__(self,  numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print('\nOperação falhou! Saldo insuficiente!')

        elif valor > 0:
            self._saldo -= valor
            print('\nSaque realizado com sucesso!')
            return True
        else:
            print('\nOperação falhou!')

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print('\nDeposito realizado com sucesso!')
        else:
            print('\nAlgo deu errado!')
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes
                if transacao['tipo'] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saque = numero_saques >= self.limite_saques

        if excedeu_limite:
            print('\nOperação falhou! O valor excedeu limite de saque.')
        elif excedeu_saque:
            print('\nOperação falhou! Excedeu o numero de saques permitidos.')
        else:
            return super().sacar(valor)
        return False

    def __repr__(self):
        return f"<{self.__class__.__name__}: \
          ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"

    def __str__(self):
        return f"""\
                Agência:\t{self.agencia}
                C/C:\t{self.numero}
                Titular:\t{self.cliente.nome}
            """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })

    def gerar_relatorio(self, tipo=None):
        for transacao in self._transacoes:
            if tipo is None or transacao['tipo'].lower() == tipo.lower():
                yield transacao

    def transacoes_dia(self):
        data_atual = datetime.now().date()
        formato = "%d-%m-%Y %H:%M:%S"
        transacoes = []
        for transac in self._transacoes:
            data_transacao = datetime.strptime(transac['data'], formato).date()
            if data_atual == data_transacao:
                transacoes.append(transac)
        return transacoes


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        success = conta.sacar(self.valor)

        if success:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        success = conta.depositar(self.valor)

        if success:
            conta.historico.adicionar_transacao(self)


def log_transacao(func):
    def envelope(*args, **kwargs):
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        result = func(*args, **kwargs)
        print(f"{data_hora} - {func.__name__}")

        with open(ROOT_PATH / 'log.txt', 'a', encoding='UTF-8') as log:
            log.write(f'Hora: {data_hora} - Função: {func.__name__}'
                      ' - Args: {args}{kwargs} - Retorno: {result}\n')

        return result
    return envelope


def menu():
    print("\n-=-=-= MENU =-=-=-")
    print()
    print("[D] Depositar \n"
          "[S] Sacar \n"
          "[E] Extrato \n"
          "[NC] Nova Conta \n"
          "[LC] Listar Contas \n"
          "[NU] Novo Usuário- \n"
          "[Q] Sair")
    return input("-> ")


@log_transacao
def depositar(clientes):
    cpf = input("Digite o cpf do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('\nCliente não encontrado!')
        return

    valor = float(input("Informe o valor do deposito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def sacar(clientes):
    cpf = input("Digite o cpf do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('\nCliente não encontrado!')
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def exibir_extrato(cliente):
    cpf = input("Digite o cpf do cliente: ")
    print("Digite o tipo de operação que deseja visualizar.\n"
          "Saque [s]\n"
          "Deposito[d]")
    sigla_operacao = input('>>').lower()
    tipo_operacao = None
    if sigla_operacao == 's':
        tipo_operacao = 'saque'
    elif sigla_operacao == 'd':
        tipo_operacao = 'deposito'
    else:
        tipo_operacao = None

    cliente = filtrar_cliente(cpf, cliente)

    if not cliente:
        print('\nCliente não encontrado!')
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    try:
        print("\n================ EXTRATO ================")

        extrato = ""
        tem_transacao = False
        for transacao in conta.historico.gerar_relatorio(tipo=tipo_operacao):
            tem_transacao = True
            extrato += f"\n{transacao['data']}\n{transacao['tipo']}"
            ":  R${transacao['valor']:.2f}\n"

        if not tem_transacao:
            extrato = "Não foi realizado movimentações."

        print(extrato)
        print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
        print("\n==========================================")
    except Exception as erro:
        print(f'Valor invalido - Error: {erro}')
        return


@log_transacao
def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe usuário com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço "
                     "(logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento,
                           cpf=cpf, endereco=endereco)
    clientes.append(cliente)
    print("=== Usuário criado com sucesso! ===")


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [
        cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


@log_transacao
def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do usuário: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Usuário não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print('\nConta criada com sucesso!')


def listar_contas(contas):
    for conta in ContaIterador(contas):
        print("=" * 100)
        print(conta)


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print('\nCliente não possui contas!')
        return

    return cliente.contas[0]


def main():

    clientes = []
    contas = []

    while True:

        opcao = menu()

        if opcao.upper() == "D":
            depositar(clientes)

        elif opcao.upper() == "S":
            sacar(clientes)

        elif opcao.upper() == "E":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao.upper() == "Q":
            print(clientes)
            print(contas)
            print("Finalizando sessão...")
            sleep(0.3)
            print("Obrigado.")
            break

        else:
            print('ERRO: Digite uma opção válida!\n')


main()


def ClienteOi(x):
    return f'Oi, {x}'
