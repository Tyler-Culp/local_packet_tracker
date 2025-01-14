from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io


class GraphBuilder:
    def __init__(self, data: dict):
        self.type = "scatter"
        self.data = data
        self.color = "blue"
        self.title = "Sent Packet Times"
        self.xTitle = "Time"
        self.yTitle = "Packet Count"


    def withType(self, type: str):
        self.type = type
        return self  # Return self to enable method chaining

    def withColor(self, color: str):
        self.color = color
        return self  # Return self to enable method chaining
    
    def withTitle(self, title: str):
        self.title = title
        return self  # Return self to enable method chaining
    
    def withXTitle(self, xTitle: str):
        self.xTitle = xTitle
        return self  # Return self to enable method chaining

    def withYTitle(self, yTitle: str):
        self.yTitle = yTitle
        return self  # Return self to enable method chaining
    
    def build(self):
        return makeGraph(self)


def makeGraph(graphBuilder: GraphBuilder):
    graphToMake = graphBuilder.type
    color = graphBuilder.color
    title = graphBuilder.title
    xTitle = graphBuilder.xTitle
    yTitle = graphBuilder.yTitle
    data = graphBuilder.data

    xAxis = list(data.keys())
    yAxis = list(data.values())

    fig, ax = plt.subplots(figsize=(13, 13))

    match graphToMake:
        case "bar":
            bars = ax.bar(xAxis, yAxis, color=color, align="center")
            ax.bar_label(bars)
            plt.subplots_adjust(bottom=0.4)
            plt.xticks(rotation=90)
        case "scatter":
            plt.scatter(xAxis, yAxis, color=color, s=50)
            plt.xticks(rotation=75)
        

    plt.xlabel(xTitle)
    plt.ylabel(yTitle)
    plt.title(f"{title}")

    img = io.BytesIO()
    FigureCanvas(fig).print_png(img)
    img.seek(0) # Moves back to first byte of image
    print("Graph has been built!")
    return img

def makeGraphObject(graphBuilder: GraphBuilder):
    data = graphBuilder.data

    xAxis = list(data.keys())
    yAxis = list(data.values())

    return {
        "xAxis": xAxis,
        "yAxis": yAxis,
        "type": graphBuilder.type,
        "color": graphBuilder.color,
        "title": graphBuilder.title,
        "xTitle": graphBuilder.xTitle,
        "yTitle": graphBuilder.yTitle
    }