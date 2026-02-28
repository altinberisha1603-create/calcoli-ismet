import math
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Calcoli Ismet", page_icon="🧰")

st.title("Programma Calcoli - Ismet Berisha Lavoratore Numero 1")

# ------------------ FUNZIONI ------------------

def sviluppo(lunghezza_esterna, laterale_lamiera1, laterale_lamiera2, spessore_lamiera):
    lunghezza_totale = lunghezza_esterna + (laterale_lamiera1 + laterale_lamiera2) - (4 * spessore_lamiera)
    lunghezza_totale_interna = lunghezza_esterna + (laterale_lamiera1 + laterale_lamiera2) + (4 * spessore_lamiera)
    return lunghezza_totale, lunghezza_totale_interna


def scala_babi(cateto1, cateto2, pedate):
    ipotenusa = (cateto1**2 + cateto2**2) ** 0.5
    lunghezza = pedate * ipotenusa

    angolo = math.acos(cateto1 / ipotenusa)
    angolo_gradi = math.degrees(angolo)
    angolo_esterno = 90 - angolo_gradi

    return lunghezza, angolo_gradi, angolo_esterno


# ======== TRIANGOLO + STANGHETTE ========

def y_on_hypotenuse(a, b, x):
    return (b / a) * x

def vertical_len_from_base(a, b, x):
    return b - y_on_hypotenuse(a, b, x)

def hyp_point(a, b, x):
    return (x, y_on_hypotenuse(a, b, x))

def len_on_hypotenuse_from_dx(dx, a, c):
    return dx * (c / a)

def readable_angle_deg(angle_deg):
    if angle_deg < -90 or angle_deg > 90:
        angle_deg += 180
    return angle_deg

def compute_layout(a, b, c, m, s, x=None):
    """
    NUOVA LOGICA:
      m = numero stanghette
      m = numero spazi (gap)
      vincolo base: m*s + m*x = a  --> x = a/m - s
    """
    c_calc = math.hypot(a, b)
    warn = None
    if abs(c - c_calc) > 1e-6:
        warn = f"ATTENZIONE: c dato={c:.3f} mm, ma sqrt(a^2+b^2)={c_calc:.3f} mm"

    if m <= 0:
        raise ValueError("Serve m >= 1 (almeno 1 stanghetta e 1 spazio).")

    if x is None:
        x = a / m - s
        if x < 0:
            raise ValueError("Impossibile: con questi m e s risulta x < 0.")

    # Vincolo base
    total_base = m * s + m * x
    if abs(total_base - a) > 1e-9:
        raise ValueError(f"VINCOLO BASE NON RISPETTATO: {total_base} != {a}")

    # Conversione su ipotenusa
    s_c = len_on_hypotenuse_from_dx(s, a, c)
    x_c = len_on_hypotenuse_from_dx(x, a, c)

    # Vincolo ipotenusa
    total_hyp = m * s_c + m * x_c
    if abs(total_hyp - c) > 1e-6:
        raise ValueError(f"VINCOLO IPOTENUSA NON RISPETTATO: {total_hyp} != {c}")

    slats, gaps = [], []

    # m stanghette, e dopo ognuna 1 gap (m gap, incluso l'ultimo fino a x=a)
    for k in range(1, m + 1):
        xl = (k - 1) * (s + x)
        xr = xl + s

        hL = vertical_len_from_base(a, b, xl)
        hR = vertical_len_from_base(a, b, xr)
        oblique = math.hypot(s, (hL - hR))

        slats.append({
            "idx": k,
            "xl": xl, "xr": xr,
            "hL": hL, "hR": hR,
            "oblique": oblique
        })

        gaps.append({
            "idx": k,
            "x0": xr,
            "x1": xr + x
        })

    info = {
        "m": m,
        "a": a, "b": b, "c": c,
        "s": s, "x": x,
        "s_c": s_c, "x_c": x_c,
        "total_base": total_base,
        "total_hyp": total_hyp,
        "warning": warn,
    }
    return slats, gaps, info

def make_figure(a, b, c, slats, gaps, info, label_every=1):
    fig, ax = plt.subplots(figsize=(18, 10), dpi=150)

    # Triangolo ruotato
    ax.plot([0, a, 0, 0], [b, b, 0, b], linewidth=2)

    ax.text(a*0.12, b + 0.08*b, f"stanga sulla base: s = {info['s']:.0f} mm", fontsize=10, ha="left")
    ax.text(a*0.12, b + 0.14*b, f"stanga vista su ipotenusa: s_c = {info['s_c']:.1f} mm", fontsize=10, ha="left")

    for stt in slats:
        xl, xr = stt["xl"], stt["xr"]
        hL, hR = stt["hL"], stt["hR"]

        yL_bot = y_on_hypotenuse(a, b, xl)
        yR_bot = y_on_hypotenuse(a, b, xr)

        A = (xl, b)
        Bp = (xr, b)
        Cpt = (xr, yR_bot)
        D = (xl, yL_bot)

        ax.plot([A[0], Bp[0]], [A[1], Bp[1]], lw=1.2)
        ax.plot([Bp[0], Cpt[0]], [Bp[1], Cpt[1]], lw=1.2)
        ax.plot([Cpt[0], D[0]], [Cpt[1], D[1]], lw=1.2)
        ax.plot([D[0], A[0]], [D[1], A[1]], lw=1.2)

        if stt["idx"] % label_every == 0:
            ax.text(xl, b - hL/2, f"{hL:.0f}", ha="right", va="center", fontsize=8, rotation=90)
            ax.text(xr, b - hR/2, f"{hR:.0f}", ha="left", va="center", fontsize=8, rotation=90)
            ax.text((xl+xr)/2, b, f"{info['s']:.0f}", ha="center", va="bottom", fontsize=8)

            mx, my = (Cpt[0]+D[0])/2, (Cpt[1]+D[1])/2
            ang = math.degrees(math.atan2(D[1]-Cpt[1], D[0]-Cpt[0]))
            ang = readable_angle_deg(ang)
            ax.text(mx, my, f"{info['s_c']:.1f}", fontsize=8, rotation=ang,
                    ha="center", va="top")

    # gap su base
    y_base_label = b + 0.03 * b
    for g in gaps:
        mid = (g["x0"] + g["x1"]) / 2
        ax.plot([g["x0"], g["x0"]], [b, b + 0.015*b], lw=1)
        ax.plot([g["x1"], g["x1"]], [b, b + 0.015*b], lw=1)
        ax.text(mid, y_base_label, f"x={info['x']:.0f}", ha="center", va="bottom", fontsize=8)

    # gap su ipotenusa
    nx, ny = -b, a
    norm = math.hypot(nx, ny)
    nx, ny = nx/norm, ny/norm
    offset = 0.05 * b

    for g in gaps:
        P0 = hyp_point(a, b, g["x0"])
        P1 = hyp_point(a, b, g["x1"])
        mx, my = (P0[0]+P1[0])/2, (P0[1]+P1[1])/2
        ang = math.degrees(math.atan2(P1[1]-P0[1], P1[0]-P0[0]))
        ang = readable_angle_deg(ang)
        ax.text(mx + nx*offset, my + ny*offset, f"x_c={info['x_c']:.1f}",
                fontsize=8, rotation=ang, ha="center", va="center")

    ax.text(a/2, b + 0.22*b,
            f"a={a:.0f} | check base: m*s+m*x={info['total_base']:.0f}   "
            f"c={c:.0f} | check hyp: m*s_c+m*x_c={info['total_hyp']:.0f}",
            ha="center", fontsize=10)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-0.02*a, 1.02*a)
    ax.set_ylim(-0.15*b, 1.30*b)
    ax.grid(True, alpha=0.22)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Triangolo ruotato: base sopra, ipotenusa sotto (layout congruo)", fontsize=12)

    return fig


# ------------------ MENU ------------------

scelta = st.selectbox(
    "Scegli quale calcolo vuoi usare:",
    ("Sviluppo Lamiera", "Calcolo Scala", "Triangolo + Stanghette")
)

# ------------------ LAMIERA ------------------

if scelta == "Sviluppo Lamiera":
    st.subheader("Calcolo Sviluppo Lamiera")

    lunghezza_esterna = st.number_input("Lunghezza esterna", min_value=0.0)
    laterale_lamiera1 = st.number_input("Laterale lamiera 1", min_value=0.0)
    laterale_lamiera2 = st.number_input("Laterale lamiera 2", min_value=0.0)
    spessore_lamiera = st.number_input("Spessore lamiera", min_value=0.0)

    if st.button("Calcola sviluppo"):
        esterno, interno = sviluppo(lunghezza_esterna, laterale_lamiera1, laterale_lamiera2, spessore_lamiera)
        st.success("Risultati")
        st.write("Sviluppo esterno:", round(esterno, 3))
        st.write("Sviluppo interno:", round(interno, 3))

# ------------------ SCALA ------------------

elif scelta == "Calcolo Scala":
    st.subheader("Calcolo Scala")

    cateto1 = st.number_input("Cateto 1 (adiacente)", min_value=0.0)
    cateto2 = st.number_input("Cateto 2", min_value=0.0)
    pedate = st.number_input("Numero pedate", min_value=0.0)

    if st.button("Calcola scala"):
        if cateto1 == 0 or cateto2 == 0:
            st.error("Inserisci valori maggiori di 0")
        else:
            lunghezza, angolo, angolo_esterno = scala_babi(cateto1, cateto2, pedate)
            st.success("Risultati")
            st.write("Lunghezza scala:", round(lunghezza, 3))
            st.write("Angolo interno:", round(angolo, 3), "°")
            st.write("Angolo esterno:", round(angolo_esterno, 3), "°")

# ------------------ TRIANGOLO + STANGHETTE ------------------

elif scelta == "Triangolo + Stanghette":
    st.subheader("Triangolo ruotato + stanghette (spazi = stanghette)")

    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("a (base superiore) [mm]", min_value=1.0, value=8200.0, step=10.0)
        b = st.number_input("b (altezza) [mm]", min_value=1.0, value=1000.0, step=10.0)
        m = st.number_input("m = numero stanghette = numero spazi", min_value=1, value=10, step=1)

    with col2:
        s = st.number_input("s (larghezza stanghetta sulla base) [mm]", min_value=1.0, value=80.0, step=1.0)
        use_custom_c = st.checkbox("Inserisci c manuale (ipotenusa)", value=False)

        if use_custom_c:
            c = st.number_input("c (ipotenusa) [mm]", min_value=1.0, value=float(math.hypot(a, b)), step=10.0)
        else:
            c = float(math.hypot(a, b))
            st.info(f"c calcolata automaticamente: {c:.3f} mm")

    label_every = st.number_input("Etichetta ogni quante stanghette", min_value=1, value=1, step=1)

    if st.button("Calcola e disegna"):
        try:
            slats, gaps, info = compute_layout(a, b, c, int(m), s, x=None)

            if info.get("warning"):
                st.warning(info["warning"])

            st.success("Calcolo riuscito ✅")
            st.write(f"m = {info['m']}")
            st.write(f"x (gap sulla base) = {info['x']:.3f} mm")
            st.write(f"s_c (stanga su ipotenusa) = {info['s_c']:.3f} mm")
            st.write(f"x_c (gap su ipotenusa) = {info['x_c']:.3f} mm")

            fig = make_figure(a, b, c, slats, gaps, info, label_every=int(label_every))
            st.pyplot(fig)

            # ---- DOWNLOAD GRAFICO ----
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)

            st.download_button(
                label="⬇️ Scarica grafico (PNG)",
                data=buf,
                file_name="triangolo_stanghette.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"Errore: {e}")