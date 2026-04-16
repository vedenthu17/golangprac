import tkinter as tk
import math, copy

X, O, E = "X", "O", "_"

# ── Node ─────────────────────────────────────────────────────────────────────
class Node:
    def __init__(self, label=""):
        self.label = label
        self.children = []
        self.x = self.y = 0
        self.pruned = self.best = False

# ── Board helpers ─────────────────────────────────────────────────────────────
def evaluate(b):
    lines = [b[r] for r in range(3)] + \
            [[b[r][c] for r in range(3)] for c in range(3)] + \
            [[b[i][i] for i in range(3)], [b[i][2-i] for i in range(3)]]
    for ln in lines:
        if ln[0] == ln[1] == ln[2] != E:
            return 10 if ln[0] == X else -10
    return 0

def has_moves(b):
    return any(b[i][j] == E for i in range(3) for j in range(3))

# ── Minimax with Alpha-Beta ───────────────────────────────────────────────────
stats = {"nodes": 0, "pruned": 0}

def minimax(b, is_max, alpha, beta, parent):
    stats["nodes"] += 1
    node = Node("\n".join("".join(r) for r in b))
    parent.children.append(node)

    score = evaluate(b)
    if score or not has_moves(b):
        return score

    best_child = None
    best = -math.inf if is_max else math.inf

    for i in range(3):
        for j in range(3):
            if b[i][j] != E:
                continue
            b[i][j] = X if is_max else O
            val = minimax(b, not is_max, alpha, beta, node)
            b[i][j] = E

            if (is_max and val > best) or (not is_max and val < best):
                best, best_child = val, node.children[-1]

            if is_max:
                alpha = max(alpha, best)
            else:
                beta = min(beta, best)

            if beta <= alpha:
                stats["pruned"] += 1
                p = Node("✂")
                p.pruned = True
                node.children.append(p)
                break
        else:
            continue
        break

    if best_child:
        best_child.best = True
        node.best = True
    return best

# ── Layout ────────────────────────────────────────────────────────────────────
HGAP, VGAP = 52, 70

def subtree_width(n):
    return max(1, sum(subtree_width(c) for c in n.children))

def layout(n, depth=0, left=0):
    w = subtree_width(n)
    n.x = left + w * HGAP // 2
    n.y = depth * VGAP + 40
    cur = left
    for c in n.children:
        cw = subtree_width(c)
        layout(c, depth + 1, cur)
        cur += cw * HGAP

# ── Draw ──────────────────────────────────────────────────────────────────────
COLORS = {"edge": "#555", "pruned_edge": "#e05", "best_edge": "#0c6",
          "node": "#c8d8f0", "pruned_node": "#fbb", "best_node": "#8ed",
          "root": "#ffd966"}

def draw_tree(cv, n):
    for ch in n.children:
        color = COLORS["pruned_edge"] if ch.pruned else (COLORS["best_edge"] if ch.best else COLORS["edge"])
        cv.create_line(n.x, n.y, ch.x, ch.y, fill=color, width=2 if ch.best else 1)
        draw_tree(cv, ch)

    fill = COLORS["pruned_node"] if n.pruned else (COLORS["best_node"] if n.best else COLORS["node"])
    if n.label == "ROOT":
        fill = COLORS["root"]
    r = 11
    cv.create_oval(n.x-r, n.y-r, n.x+r, n.y+r, fill=fill, outline="#333", width=1)
    cv.create_text(n.x, n.y, text=n.label if n.pruned else "", font=("Arial", 7, "bold"))

# ── AI move ───────────────────────────────────────────────────────────────────
def ai_move():
    stats["nodes"] = stats["pruned"] = 0
    root_node = Node("ROOT")
    best_val, move = math.inf, None

    for i in range(3):
        for j in range(3):
            if board[i][j] != E:
                continue
            board[i][j] = O
            val = minimax(copy.deepcopy(board), True, -math.inf, math.inf, root_node)
            board[i][j] = E
            if val < best_val:
                best_val, move = val, (i, j)

    # Fit tree to canvas
    layout(root_node)
    bbox_w = max((n.x for row in [root_node] for n in _all_nodes(root_node)), default=1200)
    bbox_h = max((n.y for n in _all_nodes(root_node)), default=600)

    cv.delete("all")
    # Scale to fit
    cw, ch = max(bbox_w + 60, 1200), max(bbox_h + 60, 600)
    cv.config(scrollregion=(0, 0, cw, ch))
    draw_tree(cv, root_node)

    cv.create_text(10, 10, anchor="nw", text=f"Nodes: {stats['nodes']}  Pruned: {stats['pruned']}",
                   font=("Courier", 10, "bold"), fill="#222")
    # Legend
    for idx, (lbl, col) in enumerate([("Best path", COLORS["best_node"]),
                                       ("Pruned", COLORS["pruned_node"]),
                                       ("Normal", COLORS["node"])]):
        cx = cw - 130
        cv.create_oval(cx, 12+idx*18, cx+12, 24+idx*18, fill=col, outline="#333")
        cv.create_text(cx+18, 18+idx*18, anchor="w", text=lbl, font=("Courier", 9))

    if move:
        i, j = move
        board[i][j] = O
        buttons[i][j].config(text=O, fg="#c0392b", state="disabled")
    check_game_over()

def _all_nodes(n):
    yield n
    for c in n.children:
        yield from _all_nodes(c)

# ── Game logic ────────────────────────────────────────────────────────────────
def check_game_over():
    s = evaluate(board)
    if s == 10:
        status_var.set("X wins! 🎉")
    elif s == -10:
        status_var.set("O wins!")
    elif not has_moves(board):
        status_var.set("Draw!")
    else:
        status_var.set("Your turn (X)")

def player_move(i, j):
    if board[i][j] != E or evaluate(board) or not has_moves(board):
        return
    board[i][j] = X
    buttons[i][j].config(text=X, fg="#2980b9", state="disabled")
    status_var.set("AI thinking…")
    root.after(100, ai_move)

def reset():
    global board
    board = [[E]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            buttons[i][j].config(text="", state="normal")
    cv.delete("all")
    status_var.set("Your turn (X)")

# ── UI ────────────────────────────────────────────────────────────────────────
board = [[E]*3 for _ in range(3)]
root = tk.Tk()
root.title("Tic-Tac-Toe  ·  Alpha-Beta Visualizer")
root.configure(bg="#1e1e2e")

top = tk.Frame(root, bg="#1e1e2e")
top.pack(side="top", fill="x", padx=10, pady=6)

game_frame = tk.Frame(top, bg="#1e1e2e")
game_frame.pack(side="left")

buttons = [[None]*3 for _ in range(3)]
for i in range(3):
    for j in range(3):
        b = tk.Button(game_frame, text="", width=4, height=2,
                      font=("Courier", 22, "bold"), bg="#2a2a3e", fg="white",
                      activebackground="#44446e", relief="flat", bd=0,
                      command=lambda i=i, j=j: player_move(i, j))
        b.grid(row=i, column=j, padx=3, pady=3)
        buttons[i][j] = b

ctrl = tk.Frame(top, bg="#1e1e2e")
ctrl.pack(side="left", padx=20)

status_var = tk.StringVar(value="Your turn (X)")
tk.Label(ctrl, textvariable=status_var, font=("Courier", 12), bg="#1e1e2e", fg="#cdd6f4").pack(pady=4)
tk.Button(ctrl, text="↺  New Game", font=("Courier", 11, "bold"), bg="#89b4fa", fg="#1e1e2e",
          relief="flat", padx=12, pady=4, command=reset).pack()

cv_frame = tk.Frame(root, bg="#1e1e2e")
cv_frame.pack(fill="both", expand=True, padx=6, pady=4)

cv = tk.Canvas(cv_frame, bg="#f8f8ff", highlightthickness=0)
cv.pack(side="left", fill="both", expand=True)

vsb = tk.Scrollbar(cv_frame, orient="vertical", command=cv.yview)
vsb.pack(side="right", fill="y")
hsb = tk.Scrollbar(root, orient="horizontal", command=cv.xview)
hsb.pack(fill="x")
cv.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)

root.mainloop()
