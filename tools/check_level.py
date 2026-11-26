#!/usr/bin/env python3
"""Prueft, ob ein Fischteich-Raetsel genau eine Loesung hat.

Schiffe: Wels 4, Hecht 3, Barsch 2, Rotfeder 1 (je als gerade Linie).
Regeln: Schiffe stehen in gerader Linie und beruehren sich nicht einmal
diagonal. Raetsel = Zeilenzahlen / Spaltenzahlen + Text-Hinweise.
"""
from itertools import product

N = 5
SHIPS = [("Wels", 4), ("Hecht", 3), ("Barsch", 2), ("Rotfeder", 1)]


def placements(length):
    out = []
    for r, c in product(range(N), repeat=2):
        if c + length <= N:
            out.append({(r, c + i) for i in range(length)})
        if r + length <= N and length > 1:
            out.append({(r + i, c) for i in range(length)})
    return out


def compatible(a, b):
    for (r1, c1) in a:
        for (r2, c2) in b:
            if abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1:
                return False
    return True


def row_counts(cells):
    return tuple(sum(1 for r, _ in cells if r == i) for i in range(N))


def col_counts(cells):
    return tuple(sum(1 for _, c in cells if c == i) for i in range(N))


def solve(puzzle):
    """puzzle: dict mit row (5 Zahlen oder None), col (5), clues[shipname]->fn."""
    options = {name: placements(length) for name, length in SHIPS}
    results = []

    wels_list = options["Wels"]
    hecht_list = [p for p in options["Hecht"]]  # Orientation filter applied later
    bars_list = options["Barsch"]
    rot_list = options["Rotfeder"]

    for wels, hecht, barsch, rot in product(wels_list, hecht_list, bars_list, rot_list):
        fleet = {"Wels": wels, "Hecht": hecht, "Barsch": barsch, "Rotfeder": rot}
        all_cells = wels | hecht | barsch | rot
        if len(all_cells) != 10:
            continue
        pairs = [(wels, hecht), (wels, barsch), (wels, rot),
                 (hecht, barsch), (hecht, rot), (barsch, rot)]
        if not all(compatible(a, b) for a, b in pairs):
            continue
        ok = True
        if puzzle.get("row"):
            for i, want in enumerate(puzzle["row"]):
                if want is not None and row_counts(all_cells)[i] != want:
                    ok = False
                    break
        if ok and puzzle.get("col"):
            for i, want in enumerate(puzzle["col"]):
                if want is not None and col_counts(all_cells)[i] != want:
                    ok = False
                    break
        if ok and puzzle.get("clues"):
            for fn in puzzle["clues"]:
                if not fn(fleet, all_cells):
                    ok = False
                    break
        if ok:
            results.append(fleet)
    return results


def show(fleet):
    grid = [["." for _ in range(N)] for _ in range(N)]
    marks = {"Wels": "W", "Hecht": "H", "Barsch": "B", "Rotfeder": "R"}
    for name, cells in fleet.items():
        for (r, c) in cells:
            grid[r][c] = marks[name]
    for row in grid:
        print(" ".join(row))


LEVEL1 = {
    "row": [4, 0, 3, 1, 2],
    "col": [3, None, 2, None, 2],
    "clues": [
        lambda fleet, cells: any(r == 0 for r, _ in fleet["Wels"]),      # Wels am Nordufer
        lambda fleet, cells: all(1 <= r <= 3 and 1 <= c <= 3
                                 for r, c in fleet["Barsch"]),           # Barsch nicht am Rand
        lambda fleet, cells: len({r for r, _ in fleet["Hecht"]}) == 3,   # Hecht Nord-Sued
    ],
}

LEVEL0 = {
    "row": [4, 0, 3, 2, 1],
    "col": [3, 1, 3, 1, 2],
    "clues": [],  # Einstiegsraetsel: nur Randzahlen
}

if __name__ == "__main__":
    for name, puzzle in (("LEVEL0", LEVEL0), ("LEVEL1", LEVEL1)):
        uniq = {tuple((k, tuple(sorted(v))) for k, v in f.items()) for f in solve(puzzle)}
        print(f"{name}: {len(uniq)} Loesung(en)")
    sols = solve(LEVEL1)
    print(f"Anzahl Loesungen: {len(sols)}")
    for s in sols[:5]:
        show(s)
        print(row_counts((set().union(*s.values()))), col_counts(set().union(*s.values())))
        print()
