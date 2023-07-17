from time import sleep
import os


def menu():
    print("-=-=-= MENU =-=-=-")
    print()
    print("[D] Depositar \n"
          "[S] Sacar \n"
          "[E] Extrato \n"
          "[NC] Nova Conta \n"
          "[LC] Listar Contas \n"
          "[NU] Novo Usuário- \n"
          "[Q] Sair")
    return input("-> ")

def depositar(saldo, valor, extrato):
    if valor > 0:
        saldo += valor
        extrato += f'Depósito: R$ {valor:.2f}\n'
        print('Depósito realizado com sucesso!\n')
    else:
        print("Operação falhou! Digite um valor válido.\n")
    sleep(1)
    os.system('cls')
    return saldo, extrato

def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    
    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques >= limite_saques

    if excedeu_saldo:
        print('Saldo insuficiente.\n')
    elif excedeu_limite:
        print('Valor digitado excede limite de saque.\n')
    elif excedeu_saques:
        print('Excedeu o limite de saques.\n')
    elif valor > 0:
        saldo -= valor
        extrato += f'Saque: R$ {valor:.2f}\n'
        numero_saques += 1
        print('Saque realizado com sucesso!\n')
    else:
        print("Operação falhou! Digite um valor válido.\n")
    sleep(1)
    os.system("cls")
    return saldo, extrato

def exibir_extrato(saldo, /, *, extrato):
    print("\n================ EXTRATO ================")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo:\t\tR$ {saldo:.2f}")
    print("==========================================")

def criar_usuario(usuarios):
    cpf = input("Informe o CPF (somente número): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("\n@@@ Já existe usuário com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    usuarios.append({"nome": nome, "data_nascimento": data_nascimento, "cpf": cpf, "endereco": endereco})

    print("=== Usuário criado com sucesso! ===")  

def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario["cpf"] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def criar_conta(agencia, numero_conta, usuarios):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("\n=== Conta criada com sucesso! ===")
        return {"agencia": agencia, "numero_conta": numero_conta, "usuario": usuario}

    print("\n@@@ Usuário não encontrado, fluxo de criação de conta encerrado! @@@")

def listar_contas(contas):
    for conta in contas:
        linha = f"Agência: {conta['agencia']}\nC/C: {conta['numero_conta']}\nTitular: {conta['usuario']['nome']}\n"
                
        
        print("=" * 100)
        print((linha))


def main():
    
    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0
    LIMITE_SAQUES = 3
    AGENCIA = "0001"
    usuarios = []
    contas = []

    while True:

        
        opcao = menu()

        
        if opcao.upper() == "D":
            valor = float(input("Valor a ser depositado: "))  

            saldo, extrato = depositar(saldo, valor, extrato) 
            
            
        elif opcao.upper() == "S":
            valor = float(input("Valor a ser sacado: "))
            
            saldo, extrato = sacar(saldo=saldo, valor=valor, extrato=extrato, limite=limite, numero_saques=numero_saques, limite_saques=LIMITE_SAQUES)


        elif opcao.upper() == "E":
            os.system("cls")
            exibir_extrato(saldo, extrato=extrato)

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            conta = criar_conta(AGENCIA, numero_conta, usuarios)

            if conta:
                contas.append(conta)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao.upper() == "Q":
            print("Finalizando sessão...")
            sleep(0.3)
            print("Obrigado.")
            break

        else:
            print('ERRO: Digite uma opção válida!\n')


main()      
            