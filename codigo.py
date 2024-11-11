import cv2
import numpy as np
import os
import hashlib
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken


def embed_text(image_path, text, output_path):
    image = cv2.imread(image_path)
    data = list(image.flatten())

    # Adicionar delimitador e converter texto para binário
    text = text + '%%'  # Delimitar o texto
    text_bin = ''.join(format(ord(c), '08b') for c in text)

    # Verificar se o texto cabe na imagem
    if len(text_bin) > len(data):
        raise ValueError("Texto muito grande para ser embutido nesta imagem.")

    # Embutir o texto nos bits menos significativos dos pixels
    for i in range(len(text_bin)):
        data[i] = (data[i] & ~1) | int(text_bin[i])  

    # Reformatar a imagem e salvar
    new_image = np.array(data).reshape(image.shape)
    cv2.imwrite(output_path, new_image)

def retrieve_text(image_path):
    image = cv2.imread(image_path)
    data = list(image.flatten())

    text_bin = ''
    for pixel in data:
        text_bin += str(pixel & 1)

    # Dividir o texto binário em bytes e converter
    text_bytes = [text_bin[i:i+8] for i in range(0, len(text_bin), 8)]

    text = ''
    for b in text_bytes:
        try:
            char = chr(int(b, 2))
            text += char
            if text.endswith('%%'):  # Interromper ao encontrar o delimitador
                break
        except ValueError:
            break  # Parar se um valor não puder ser convertido

    return text.split('%%')[0]  


# Funções de Hash
def generate_hash(image_path):
    with open(image_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    return file_hash

# Criptografia
def generate_key():
    return Fernet.generate_key()

def encrypt_message(key, message):
    fernet = Fernet(key)
    encrypted = fernet.encrypt(message.encode())
    return encrypted

def decrypt_message(key, encrypted_message):
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_message).decode()
    return decrypted

# Menu Principal
def menu():
    key = generate_key()  
    encrypted_message = None  # Variável para armazenar mensagem criptografada

    while True:
        print("\nMenu de Opções:")
        print("(1) Embutir texto em uma imagem")
        print("(2) Recuperar texto de uma imagem")
        print("(3) Gerar hash das imagens")
        print("(4) Encriptar mensagem")
        print("(5) Decriptar mensagem")
        print("(S) Sair")

        choice = input("Escolha uma opção: ")

        if choice in ['S', 's']:
            print("Saindo do programa.")
            break
        elif choice == '1':
            image_path = input("Caminho da imagem: ")
            text = input("Texto a ser embutido: ")
            output_path = input("Caminho da imagem de saída: ")
            embed_text(image_path, text, output_path)
            print("Texto embutido na imagem.")
        elif choice == '2':
            image_path = input("Caminho da imagem: ")
            retrieved_text = retrieve_text(image_path)
            print("Texto recuperado:", retrieved_text)
        elif choice == '3':
            original_image_path = input("Caminho da imagem original: ")
            altered_image_path = input("Caminho da imagem alterada: ")
            original_hash = generate_hash(original_image_path)
            altered_hash = generate_hash(altered_image_path)
            print("Hash original:", original_hash)
            print("Hash alterado:", altered_hash)
        elif choice == '4':
            message = input("Mensagem a ser encriptada: ")
            encrypted_message = encrypt_message(key, message)
            print("Mensagem encriptada:", encrypted_message)
        elif choice == '5':
            if encrypted_message:
                try:
                    decrypted_message = decrypt_message(key, encrypted_message)
                    print("Mensagem decriptada:", decrypted_message)
                except InvalidToken:
                    print("Erro: Token inválido! A chave de criptografia pode estar incorreta.")
            else:
                print("Erro: Nenhuma mensagem encriptada encontrada.")
        else:
            print("Opção inválida! Tente novamente.")


menu()