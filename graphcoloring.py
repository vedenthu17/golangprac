import tkinter as tk
import math


def is_valid(node, color, assignment, graph):
    for neighbor in graph[node]:
        if neighbor in assignment and assignment[neighbor] == color:
            return False
    return True

def solve(graph, colors, assignment={}):
    if len(assignment) == len(graph):
        return assignment

    for node in graph:
        if node not in assignment:
            break

    for color in colors:
        if is_valid(node, color, assignment, graph):
            assignment[node] = color
            result = solve(graph, colors, assignment)
            if result:
                return result
            del assignment[node]

    return None


 
def get_graph(text):
    graph = {}
    edges = text.split(",")

    for e in edges:
        u, v = e.strip().split("-")

        graph.setdefault(u, []).append(v)
        graph.setdefault(v, []).append(u)

    return graph


 
def draw(graph, solution):
    canvas.delete("all")

    nodes = list(graph.keys())
    n = len(nodes)

    pos = {}
    for i in range(n):
        angle = 2 * math.pi * i / n
        x = 250 + 150 * math.cos(angle)
        y = 250 + 150 * math.sin(angle)
        pos[nodes[i]] = (x, y)

    # edges
    for u in graph:
        for v in graph[u]:
            canvas.create_line(*pos[u], *pos[v])

    # nodes
    for node in nodes:
        x, y = pos[node]
        color = solution[node]
        canvas.create_oval(x-20, y-20, x+20, y+20, fill=color)
        canvas.create_text(x, y, text=node, fill="white")


 
def run():
    try:
        graph = get_graph(entry.get())
        colors = ["red", "green", "blue"]

        ans = solve(graph, colors, {})

        if ans:
            label.config(text=str(ans))
            draw(graph, ans)
        else:
            label.config(text="No solution")

    except:
        label.config(text="Invalid input")


 
root = tk.Tk()
root.title("Graph Coloring")

tk.Label(root, text="Edges (A-B, B-C):").pack()

entry = tk.Entry(root, width=30)
entry.pack()

tk.Button(root, text="Solve", command=run).pack()

canvas = tk.Canvas(root, width=500, height=500, bg="white")
canvas.pack()

label = tk.Label(root, text="")
label.pack()

root.mainloop()