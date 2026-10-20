"""
Yahtzee clásico para 2 jugadores simulado con el método de Montecarlo.

Modelo probabilístico: cada dado es uniforme discreta sobre {1,...,6} y los
lanzamientos son independientes. Un turno tiene hasta 3 lanzamientos de 5 dados.
Estado de un turno (cadena de Markov): (dados conservados, lanzamientos restantes);
la siguiente tirada depende solo de ese estado.

Uso:
    python yahtzee_montecarlo.py --demo                 # una partida con hojas de puntaje
    python yahtzee_montecarlo.py --partidas 300 --k 30  # experimento Montecarlo vs voraz
    python yahtzee_montecarlo.py --prob-yahtzee         # convergencia de P(Yahtzee en un turno)
"""
import argparse
import csv
import math
import random
import statistics
from collections import Counter

# ----------------------------------------------------------------- Reglas
SUPERIOR = ["unos", "doses", "treses", "cuatros", "cincos", "seises"]
INFERIOR = ["trio", "poker", "full", "escalera_pequena", "escalera_grande",
            "chance", "yahtzee"]
CATEGORIAS = SUPERIOR + INFERIOR

# Valor de referencia (puntaje medio aproximado de cada casilla). Se usa como
# "costo de oportunidad": gastar una casilla con menos de su media es perder.
BASE = {"unos": 2.1, "doses": 5.3, "treses": 8.6, "cuatros": 12.2,
        "cincos": 15.7, "seises": 19.2, "trio": 21.7, "poker": 13.1,
        "full": 22.6, "escalera_pequena": 29.5, "escalera_grande": 32.7,
        "chance": 22.0, "yahtzee": 16.9}


def tirar(n):
    """Lanza n dados: muestreo uniforme sobre {1..6} (núcleo del Montecarlo)."""
    return [random.randint(1, 6) for _ in range(n)]


def puntaje(dados, cat):
    c = Counter(dados)
    total = sum(dados)
    if cat in SUPERIOR:
        v = SUPERIOR.index(cat) + 1
        return v * c[v]
    if cat == "trio":
        return total if max(c.values()) >= 3 else 0
    if cat == "poker":
        return total if max(c.values()) >= 4 else 0
    if cat == "full":
        return 25 if sorted(c.values()) == [2, 3] else 0
    if cat == "escalera_pequena":
        s = set(dados)
        return 30 if any({a, a + 1, a + 2, a + 3} <= s for a in (1, 2, 3)) else 0
    if cat == "escalera_grande":
        return 40 if sorted(dados) in ([1, 2, 3, 4, 5], [2, 3, 4, 5, 6]) else 0
    if cat == "chance":
        return total
    if cat == "yahtzee":
        return 50 if len(c) == 1 else 0
    raise ValueError(cat)


def puntaje_comodin(dados, cat):
    """Yahtzee extra: full y escaleras valen su puntaje completo."""
    return {"full": 25, "escalera_pequena": 30,
            "escalera_grande": 40}.get(cat, puntaje(dados, cat))


class Hoja:
    """Hoja de puntaje de un jugador (diccionario categoría -> puntaje o None)."""

    def __init__(self):
        self.p = {c: None for c in CATEGORIAS}
        self.bono_yahtzee = 0

    def abiertas(self):
        return [c for c, v in self.p.items() if v is None]

    def opciones(self, dados):
        """Devuelve {categoría legal: puntaje} aplicando la regla del comodín."""
        abiertas = self.abiertas()
        if len(set(dados)) == 1 and self.p["yahtzee"] is not None:
            sup = SUPERIOR[dados[0] - 1]
            cand = [sup] if sup in abiertas else abiertas  # colocación forzada
            return {c: puntaje_comodin(dados, c) for c in cand}
        return {c: puntaje(dados, c) for c in abiertas}

    def registrar(self, dados, cat):
        opts = self.opciones(dados)
        if len(set(dados)) == 1 and self.p["yahtzee"] == 50:
            self.bono_yahtzee += 100
        self.p[cat] = opts[cat]

    def subtotal(self):
        return sum(self.p[c] or 0 for c in SUPERIOR)

    def bono_superior(self):
        return 35 if self.subtotal() >= 63 else 0

    def total(self):
        return (self.subtotal() + self.bono_superior()
                + sum(self.p[c] or 0 for c in INFERIOR) + self.bono_yahtzee)


# ----------------------------------------------------------- Estrategias
def mantener_moda(dados):
    """Política simple: conservar el valor más repetido (empate: el mayor)."""
    c = Counter(dados)
    v = max(c, key=lambda x: (c[x], x))
    return [d for d in dados if d == v]


def valor(dados, hoja):
    """Utilidad de unos dados finales: mejor (puntaje - media de la casilla)."""
    return max(s - BASE[c] for c, s in hoja.opciones(dados).items())


def subconjuntos(dados):
    """Todas las formas distintas de conservar dados (como multiconjuntos)."""
    vistos = set()
    for mask in range(32):
        vistos.add(tuple(sorted(d for i, d in enumerate(dados) if mask >> i & 1)))
    return [list(s) for s in vistos]


def evaluar_mantener(mant, lanzamientos_restantes, hoja, k):
    """Montecarlo: promedio de k simulaciones del resto del turno."""
    acum = 0.0
    for _ in range(k):
        d = mant + tirar(5 - len(mant))
        for _ in range(lanzamientos_restantes - 1):
            m = mantener_moda(d)
            d = m + tirar(5 - len(m))
        acum += valor(d, hoja)
    return acum / k


def turno_montecarlo(hoja, k=30):
    dados = tirar(5)
    for restantes in (2, 1):
        mejor = max(subconjuntos(dados),
                    key=lambda m: evaluar_mantener(m, restantes, hoja, k))
        dados = mejor + tirar(5 - len(mejor))
    opts = hoja.opciones(dados)
    return dados, max(opts, key=lambda c: opts[c] - BASE[c])


def turno_voraz(hoja):
    """Línea base: conserva la moda y anota la casilla de mayor puntaje bruto."""
    dados = tirar(5)
    for _ in range(2):
        m = mantener_moda(dados)
        dados = m + tirar(5 - len(m))
    opts = hoja.opciones(dados)
    return dados, max(opts, key=lambda c: opts[c])


# ------------------------------------------------------------ Simulación
def partida(est1, est2):
    hojas = [Hoja(), Hoja()]
    for _ in range(13):
        for h, est in zip(hojas, (est1, est2)):
            dados, cat = est(h)
            h.registrar(dados, cat)
    return hojas


def imprimir(hojas, nombres):
    print(f"{'Categoría':<18}{nombres[0]:>14}{nombres[1]:>14}")
    for c in CATEGORIAS:
        print(f"{c:<18}{hojas[0].p[c]:>14}{hojas[1].p[c]:>14}")
    print(f"{'bono superior':<18}{hojas[0].bono_superior():>14}{hojas[1].bono_superior():>14}")
    print(f"{'bono yahtzee':<18}{hojas[0].bono_yahtzee:>14}{hojas[1].bono_yahtzee:>14}")
    print(f"{'TOTAL':<18}{hojas[0].total():>14}{hojas[1].total():>14}")


def experimento(n, k, salida_csv=None):
    """n partidas Montecarlo vs voraz, alternando quién inicia."""
    mc, vz, filas = [], [], []
    gana_mc = empates = 0
    for i in range(n):
        if i % 2 == 0:
            hojas = partida(lambda h: turno_montecarlo(h, k), turno_voraz)
            a, b = hojas[0].total(), hojas[1].total()
        else:
            hojas = partida(turno_voraz, lambda h: turno_montecarlo(h, k))
            b, a = hojas[0].total(), hojas[1].total()
        mc.append(a)
        vz.append(b)
        filas.append((i + 1, a, b))
        gana_mc += a > b
        empates += a == b

    def resumen(nombre, xs):
        m = statistics.mean(xs)
        ic = 1.96 * statistics.stdev(xs) / math.sqrt(len(xs))
        print(f"{nombre:<12} media = {m:6.1f} ± {ic:4.1f} (IC 95 %)  "
              f"mín = {min(xs)}  máx = {max(xs)}")

    print(f"\n{n} partidas simuladas (k = {k} réplicas por decisión)")
    resumen("Montecarlo", mc)
    resumen("Voraz", vz)
    print(f"Victorias Montecarlo: {100 * gana_mc / n:.1f} %   "
          f"Voraz: {100 * (n - gana_mc - empates) / n:.1f} %   "
          f"Empates: {100 * empates / n:.1f} %")
    if salida_csv:
        with open(salida_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["partida", "montecarlo", "voraz"])
            w.writerows(filas)
        print(f"Resultados guardados en {salida_csv}")


def prob_yahtzee(ns=(100, 1000, 10000, 100000)):
    """Convergencia de P(Yahtzee en un turno) con la política 'conservar moda'."""
    print("n turnos    P(Yahtzee) estimada   (referencia teórica ≈ 4,6 %)")
    exitos = 0
    hecho = 0
    for n in ns:
        for _ in range(n - hecho):
            d = tirar(5)
            for _ in range(2):
                m = mantener_moda(d)
                d = m + tirar(5 - len(m))
            exitos += len(set(d)) == 1
        hecho = n
        print(f"{n:>8}    {100 * exitos / n:6.2f} %")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true", help="una partida con hojas")
    ap.add_argument("--partidas", type=int, default=0, help="partidas del experimento")
    ap.add_argument("--k", type=int, default=30, help="réplicas Montecarlo por decisión")
    ap.add_argument("--prob-yahtzee", action="store_true")
    ap.add_argument("--semilla", type=int, default=None)
    ap.add_argument("--csv", default=None, help="guardar puntajes en CSV")
    a = ap.parse_args()
    random.seed(a.semilla)
    if a.demo:
        imprimir(partida(lambda h: turno_montecarlo(h, a.k), turno_voraz),
                 ("Montecarlo", "Voraz"))
    if a.partidas:
        experimento(a.partidas, a.k, a.csv)
    if a.prob_yahtzee:
        prob_yahtzee()
    if not (a.demo or a.partidas or a.prob_yahtzee):
        ap.print_help()
