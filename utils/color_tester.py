import matplotlib.pyplot as plt

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def draw_color_squares(hex_list):
    fig, ax = plt.subplots(1, len(hex_list), figsize=(len(hex_list) * 2, 2))
    if len(hex_list) == 1:
        ax = [ax]
    for i, hex_color in enumerate(hex_list):
        rgb = hex_to_rgb(hex_color)
        ax[i].add_patch(plt.Rectangle((0, 0), 1, 1, color=[c/255 for c in rgb]))
        ax[i].set_xlim(0, 1)
        ax[i].set_ylim(0, 1)
        ax[i].axis('off')
    plt.show()

# 예시 16진수 RGB 리스트
hex_list = ['#21ACA9', '#34CDEF', '#7398C1', '#7475BB',
            '#756C86', '#ACB6B3', '#B5E045',
            '#BFA8EE', '#CB7D60', '#D2DA40', '#D87FC8', '#E35BE5',
            '#EE5444', '#EF5A68', '#F7969A', '#F8CA8F',
            '#FA942E', '#FE5B05', '#FFF600']
# hex_list = [
#     '#FF0000',  # Red
#     '#00FF00',  # Green
#     '#0000FF',  # Blue
#     '#FFFF00',  # Yellow
#     '#FF00FF',  # Magenta
#     '#00FFFF',  # Cyan
#     '#800000',  # Maroon
#     '#808000',  # Olive
#     '#008000',  # Dark Green
#     '#800080',  # Purple
#     '#008080',  # Teal
#     '#000080',  # Navy
#     '#FFA500',  # Orange
#     '#FFC0CB',  # Pink
#     '#A52A2A',  # Brown
#     '#8A2BE2',  # Blue Violet
#     '#5F9EA0',  # Cadet Blue
#     '#D2691E',  # Chocolate
#     '#FF7F50',  # Coral
#     '#6495ED',  # Cornflower Blue
#     '#DC143C',  # Crimson
#     '#00CED1',  # Dark Turquoise
#     '#FFD700',  # Gold
#     '#ADFF2F',  # Green Yellow
#     '#4B0082'   # Indigo
# ]
hex_list = ['#21ACA9', '#34CDEF','#7475BB','#756C86','#ACB6B3','#B5E045',
        '#BFA8EE', '#CB7D60','#E35BE5',
        '#EE5444', '#EF5A68', '#F7969A', '#F8CA8F', '#EDED2A']
draw_color_squares(hex_list)
