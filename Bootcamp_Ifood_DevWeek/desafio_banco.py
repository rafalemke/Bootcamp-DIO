from time import sleep
import os

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3


while True:

    sleep(0.3)
    print("-=-=-= MENU =-=-=-")
    print()
    print("[D] Depositar \n"
          "[S] Sacar \n"
          "[E] Extrato \n"
          "[Q] Sair")
    opcao = input("Digite uma opção: ")

    
    if opcao.upper() == "D":
        valor = float(input("Valor a ser depositado: "))   
        if valor > 0:
            saldo += valor
            extrato += f'Depósito: R$ {valor:.2f}\n'
            print('Depósito realizado com sucesso!\n')
        else:
            print("Operação falhou! Digite um valor válido.\n")
        sleep(2)
        os.system('cls')
        
    elif opcao.upper() == "S":
        valor = float(input("Valor a ser sacado: "))
        if valor > 0 and valor < saldo and numero_saques < LIMITE_SAQUES:
            saldo -= valor
            extrato += f'Saque: R$ {valor:.2f}\n'
            numero_saques += 1
            print('Saque realizado com sucesso!\n')
        elif valor > saldo:
            print('Saldo insuficiente.\n')
        elif  numero_saques >= LIMITE_SAQUES:
            print('Excedeu o limite de saques.\n')
        else:
            print("Operação falhou! Digite um valor válido.\n")
        sleep(2)
        os.system("cls")


    elif opcao.upper() == "E":
        os.system("cls")
        print("-=-=-=-= EXTRATO =-=-=-=-")
        print()
        print(extrato)
        print()
        print("-----------------------")
        print(f'SALDO: {saldo:.2f}')

    elif opcao.upper() == "Q":
        print("Finalizando sessão...")
        sleep(0.3)
        print("Obrigado.")
        break

    else:
        print('ERRO: Digite uma opção válida!\n')

    
        