import os
from traceback import print_exception
from django.contrib.auth.models import User

import csv

from ..models import Usuarios

backupPrincipal = "principalBackupUsuarios.csv"

# Coloca todos usuarios que estao no banco de dados no csv backup
def atualizaBackupUsuarios():
    try:
        directory = os.path.dirname(__file__)  # puxa dir que ele esta
        file_path = os.path.join(directory, backupPrincipal) # faz o path absoluto

        usuarios = Usuarios.objects.all()

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'nome', 'email', 'senha'])

            for user in usuarios:
                writer.writerow([user.id_usuario, user.nome, user.email, user.senha])

        print(f"Backup feito: {backupPrincipal}")
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)

#percorre o backup principal e verifica se todos os usuarios estao no banco de dados
def verificaIntegridadeUsuarios():
    try:
        directory = os.path.dirname(__file__)
        file_path = os.path.join(directory, backupPrincipal)
        if not os.path.exists(file_path):
            print("Arquivo de backup de usuarios principal nao existe...")
            with open(file_path, 'w') as file:
                file.write("")  # Cria um arquivo vazio
            atualizaBackupUsuarios()
            print(f"O arquivo {file_path} de backup principal foi criado.")

        usuarios = Usuarios.objects.all()

        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                usuario_id = row[0]
                nome = row[1]

                if not usuarios.filter(nome=nome).exists() or not usuarios.filter(id_usuario=usuario_id).exists():
                    print("Banco de dados corrompido: restaurando usuarios do backup local...")
                    restaurarBancoDeDadosUsuarios()
                    atualizaBackupUsuarios()
                    return
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)

def restaurarBancoDeDadosUsuarios():
    try:
        directory = os.path.dirname(__file__)  # puxa dir que ele esta
        file_path = os.path.join(directory, backupPrincipal)  # faz o path absoluto
        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                nome = row[1]
                email = row[2]
                senha = row[3]
                Usuarios( nome, email, senha).save()
                user_django = User(username=nome, email=email)  # cadastra user padrao do django
                user_django.set_password(senha)
                user_django.save()
            print("Banco de dados restaurado com sucesso")

    except Exception as e:
        print_exception(type(e), e, e.__traceback__)