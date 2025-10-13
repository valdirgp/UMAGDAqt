import uuid
import re
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from General.util import Util
import sys, os

class License():
    def  __init__(self, language):
        self.lang = language
        self.none = None
        self.fisical_address = self.get_mac_address()

        self.util = Util()

    # gets all info for the license request
    def create_lincense_request(self, username, instname, temp_window):
        try:
            # QFileDialog.getExistingDirectory requires a QWidget parent, so temp_window must be a QWidget
            save_file_path = QFileDialog.getExistingDirectory(temp_window, "Select Directory")
            if not save_file_path:
                return

            with open(save_file_path + '/request_license_UMAGDA.utc', 'w+', encoding="utf-8") as file:
                file.write(f'Instituição: {instname}\nNome: {username}\nID: {self.fisical_address}')

            QMessageBox.information(
                temp_window,
                self.util.dict_language[self.lang]["mgbox_success"],
                self.util.dict_language[self.lang]["mgbox_success_reqlc"]
            )
            temp_window.close()
        except Exception as error:
            QMessageBox.information(
                temp_window,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_reqlc"]
            )

    # encode fisical address
    def encode_address(self):
        equivalent_number = {'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15, 'g': 16, 'h': 17, 'i': 18, 'j': 19, 'k': 20, 'l': 21, 'm': 22
                             , 'n': 23, 'o': 24, 'p': 25, 'q': 26, 'r': 27, 's': 28, 't': 29, 'u': 30, 'v': 31, 'w': 32, 'x': 33, 'y': 34, 'z': 35}
        list_address = list(self.fisical_address)
        for i, char in enumerate(list_address):
            if char.isdigit():
                list_address[i] = str(int(char)+37)
            if char.isalpha():
                list_address[i] = str(equivalent_number[char]+37)

        return ''.join(list_address)

    # gets fisical address
    def get_mac_address(self):
        address = uuid.getnode()
        fisical_address  = ':'.join(['{:02x}'.format((address >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])
        return fisical_address
    
    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath("./")
            
        return os.path.join(base_path, relative_path)

    # validate fisical address
    def verify_fisical_adress(self):
        try:
            with open(self.resource_path('license_UMAGDA.utc'), 'r') as file:
                file_text = file.read()
                encoded_address = self.encode_address()
                if re.search(encoded_address, file_text):
                    return True
            return False
        except Exception:
            return False