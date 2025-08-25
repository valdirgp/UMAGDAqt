from matplotlib.backend_tools import ToolToggleBase
from General.util import Util

class CustomPltOptions(ToolToggleBase):
    default_keymap = 'm'  # Atalho de teclado para ativar/desativar
    description = 'Inform data collected'  # Descrição da ferramenta
    image = Util.resource_path("images/info_icon.ico")  # Caminho para o ícone (deve funcionar em PyQt5)

    def __init__(self, *args, inform_graph, **kwargs):
        self.inform_graph = inform_graph
        super().__init__(*args, **kwargs)

    def trigger(self, *args, **kwargs):
        self.inform_graph()
