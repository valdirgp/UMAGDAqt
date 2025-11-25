from PIL import Image

nome = "globo"
# Abre o PNG
img = Image.open(f"General/images/{nome}.png")

# Converte para múltiplas resoluções (recomendado para ícones)
tamanhos = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

# Salva como .ico com múltiplas resoluções
img.save(f"General/images/{nome}.ico", sizes=tamanhos)
