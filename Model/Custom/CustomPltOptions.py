from matplotlib.backend_tools import ToolToggleBase
from General.util import Util

class CustomPltOptions(ToolToggleBase):
    default_keymap = 'm'  # keyboard shortcut
    description = 'Inform data collected'
    # O matplotlib aceita PNG para ícones em Qt, então use o PNG
    image = Util.resource_pathGeneral("images/info_icon.png")

    def __init__(self, *args, inform_graph, **kwargs):
        self.inform_graph = inform_graph
        super().__init__(*args, **kwargs)

    def trigger(self, *args, **kwargs):
        self.inform_graph()