from PyQt5.QtWidgets import QApplication, QMessageBox
import random as rd
import re
import os
import sys

# gets fisical id from archive
def get_address():
    try:
        with open('./request_license_UMAGDA.utc', 'r', encoding="utf-8") as file:
            splited_file = file.read().split('\n')
            for line in splited_file:
                if re.search('ID', line):
                    return line.split()[1]
    except FileNotFoundError:
        QMessageBox.information(None, 'ERRO', 'É necessário um arquivo request na mesma pasta')
        return None

# encode id
def encode_address(fisical_address):
    try:
        equivalent_number = {
            'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15, 'g': 16, 'h': 17, 'i': 18,
            'j': 19, 'k': 20, 'l': 21, 'm': 22, 'n': 23, 'o': 24, 'p': 25, 'q': 26, 'r': 27,
            's': 28, 't': 29, 'u': 30, 'v': 31, 'w': 32, 'x': 33, 'y': 34, 'z': 35
        }
        list_address = list(fisical_address.lower())
        for i, char in enumerate(list_address):
            if char.isdigit():
                list_address[i] = str(int(char)+37)
            elif char.isalpha():
                list_address[i] = str(equivalent_number[char]+37)
        return ''.join(list_address)
    except Exception:
        QMessageBox.information(None, 'ERRO', 'Não foi possível gerar máscara de endereço')
        return None

# appends or creates a list with people that have access to the program
def generate_list_people():
    try:
        with open('./request_license_UMAGDA.utc', 'r', encoding="utf-8") as file:
            splited_file = file.read().split('\n')
            for line in splited_file:
                if re.search('Instituição', line):
                    institution = line.split()[1]
                if re.search('Nome', line):
                    name = line.split()[1]

        people_list_path = os.path.join('people_access_UMAGDA.txt')
        with open(people_list_path, 'a+', encoding="utf-8") as file:
            file.write(f'Nome: {name}   Instituição: {institution}\n')
        return True
    except FileNotFoundError:
        QMessageBox.information(None, 'ERRO', 'É necessário um arquivo request na mesma pasta')
        return False

# creates numbers archive with encoded id in the middle
def create_license_archive():
    try:
        fisical_address = get_address()
        if fisical_address is None:
            return

        encoded_address = encode_address(fisical_address)
        if encoded_address is None:
            return

        rd.seed()
        address_position = rd.randint(0, 5000)

        with open('license_UMAGDA.utc', 'w+', encoding="utf-8") as file:
            encoded_numbers = [str(rd.randint(1000, 9999)) for _ in range(0, 5000)]
            encoded_numbers.insert(address_position, encoded_address)
            encoded_numbers = ':'.join(encoded_numbers)
            file.write(encoded_numbers)

        if not generate_list_people():
            return

        QMessageBox.information(None, 'Ação concluída', 'Licença gerada com sucesso')
    except Exception:
        QMessageBox.information(None, 'ERRO', 'Não foi possível gerar licença')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    create_license_archive()
    sys.exit()
