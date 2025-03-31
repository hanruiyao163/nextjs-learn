from PIL import Image
from io import BytesIO


def show_graph_image(graph):
    image = graph.get_graph().draw_mermaid_png()
    Image.open(BytesIO(image)).show()



