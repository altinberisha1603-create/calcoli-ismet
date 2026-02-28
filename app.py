import math
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Calcoli Ismet", page_icon="🧰")
st.title("Programma Calcoli - Ismet Berisha Lavoratore Numero 1")

# ------------------ FUNZIONI BASE ------------------

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


# ------------------ SPARTITO LAMIERA RECINZIONE (TRAPEZIO) ------------------

def readable_angle_deg(angle_deg):
    if angle_deg < -90 or angle_deg > 90:
        angle_deg += 180
    return angle_deg

def H_at_x(a, H_left, H_right, x):
    return H_left + (H_right - H_left) * (x / a)

def len_on_bottom_from_dx(dx, a, H_left, H_right):
    slope = (H_right - H_left) / a
    return math.hypot(dx, slope * dx)

def trapezoid_slope_angle_deg(a, H_left, H_right):
    """
    Angolo di pendenza del lato inclinato rispetto all'orizzontale.
    È il complementare dell'angolo tra (lato sinistro verticale) e (lato inclinato).
    """
    dy = (H_right - H_left)
    return math.degrees(math.atan2(abs(dy), a))

def compute_trapezoid_layout(a, H_left, H_right, n, s, x=None):
    """
    Spartito lamiera recinzione
    n = numero spartiti (gap) tra i piantoni
    m = numero piantoni = n+1 (inizia e finisce con piantone)
    vincolo base: a = m*s + n*x
    """
    if a <= 0:
        raise ValueError("La lunghezza totale diritto deve essere > 0")
    if s <= 0:
        raise ValueError("Lo spessore piantone deve essere > 0")
    if n < 0:
        raise ValueError("Il numero spartiti deve essere >= 0")
    if H_left <= 0 or H_right <= 0:
        raise ValueError("Le altezze devono essere > 0")

    m = n + 1

    if x is None:
        if n == 0:
            if abs(a - s) > 1e-9:
                raise ValueError("Con numero spartiti = 0 serve lunghezza totale diritto == spessore piantone.")
            x = 0.0
        else:
            x = (a - m * s) / n
            if x < 0:
                raise ValueError("Impossibile: lo spessore piantone è troppo grande per questa lunghezza.")

    total_base = m * s + n * x
    if abs(total_base - a) > 1e-6:
        raise ValueError(f"VINCOLO BASE NON RISPETTATO: {total_base:.6f} != {a:.6f}")

    # lunghezze "viste" sul bordo inclinato
    s_bottom = len_on_bottom_from_dx(s, a, H_left, H_right)
    x_bottom = len_on_bottom_from_dx(x, a, H_left, H_right) if n > 0 else 0.0

    # "ipotenusa" = lunghezza totale del lato inclinato (bordo inferiore)
    bottom_total = len_on_bottom_from_dx(a, a, H_left, H_right)
    bottom_check = m * s_bottom + n * x_bottom
    if abs(bottom_check - bottom_total) > 1e-6:
        raise ValueError(f"VINCOLO BORDO INFERIORE NON RISPETTATO: {bottom_check:.6f} != {bottom_total:.6f}")

    slats, gaps = [], []
    for k in range(m):
        xl = k * (s + x)
        xr = xl + s
        if xr > a + 1e-9:
            break

        hL = H_at_x(a, H_left, H_right, xl)
        hR = H_at_x(a, H_left, H_right, xr)

        slats.append({
            "idx": k + 1,
            "xl": xl, "xr": xr,
            "hL": hL, "hR": hR,
        })

        if k < m - 1:
            gaps.append({"idx": k + 1, "x0": xr, "x1": xr + x})

    info = {
        "a": a,
        "H_left": H_left,
        "H_right": H_right,
        "n_gaps": n,
        "m_slats": m,
        "s": s,
        "x": x,
        "total_base": total_base,
        "s_bottom": s_bottom,
        "x_bottom": x_bottom,
        "bottom_total": bottom_total,
        "bottom_check": bottom_check,
        "slope_angle_deg": trapezoid_slope_angle_deg(a, H_left, H_right),
    }
    return slats, gaps, info

def make_trapezoid_figure(a, H_left, H_right, slats, gaps, info, label_every=1):
    Y_TOP = max(H_left, H_right)

    fig, ax = plt.subplots(figsize=(18, 10), dpi=150)

    # Contorno trapezio
    ax.plot(
        [0, a, a, 0, 0],
        [Y_TOP, Y_TOP, Y_TOP - H_right, Y_TOP - H_left, Y_TOP],
        linewidth=2
    )

    ax.text(a*0.05, Y_TOP + 0.10*Y_TOP, f"Spessore piantone (base) = {info['s']:.0f} mm", fontsize=10, ha="left")
    ax.text(a*0.05, Y_TOP + 0.16*Y_TOP, f"Piantone sul bordo in pendenza = {info['s_bottom']:.2f} mm",
            fontsize=10, ha="left")

    # Stanghe (piantoni)
    for stt in slats:
        xl, xr = stt["xl"], stt["xr"]
        hL, hR = stt["hL"], stt["hR"]

        A = (xl, Y_TOP)
        B = (xr, Y_TOP)
        D = (xl, Y_TOP - hL)
        C = (xr, Y_TOP - hR)

        ax.plot([A[0], B[0]], [A[1], B[1]], lw=1.2)
        ax.plot([B[0], C[0]], [B[1], C[1]], lw=1.2)
        ax.plot([C[0], D[0]], [C[1], D[1]], lw=1.2)
        ax.plot([D[0], A[0]], [D[1], A[1]], lw=1.2)

        if stt["idx"] % label_every == 0:
            ax.text(xl, Y_TOP - hL/2, f"{hL:.0f}", ha="right", va="center", fontsize=8, rotation=90)
            ax.text(xr, Y_TOP - hR/2, f"{hR:.0f}", ha="left", va="center", fontsize=8, rotation=90)
            ax.text((xl+xr)/2, Y_TOP, f"{info['s']:.0f}", ha="center", va="bottom", fontsize=8)

            mx, my = (C[0]+D[0])/2, (C[1]+D[1])/2
            ang = math.degrees(math.atan2(D[1]-C[1], D[0]-C[0]))
            ang = readable_angle_deg(ang)
            ax.text(mx, my, f"{info['s_bottom']:.1f}", fontsize=8, rotation=ang, ha="center", va="top")

    # Gap su base
    y_gap_label = Y_TOP + 0.03*Y_TOP
    for g in gaps:
        mid = (g["x0"] + g["x1"]) / 2
        ax.plot([g["x0"], g["x0"]], [Y_TOP, Y_TOP + 0.015*Y_TOP], lw=1)
        ax.plot([g["x1"], g["x1"]], [Y_TOP, Y_TOP + 0.015*Y_TOP], lw=1)
        ax.text(mid, y_gap_label, f"x={info['x']:.0f}", ha="center", va="bottom", fontsize=8)

    # Gap su bordo inclinato
    dx = a
    dy = (H_right - H_left)
    nx, ny = -dy, dx
    norm = math.hypot(nx, ny)
    nx, ny = nx/norm, ny/norm
    offset = 0.05 * Y_TOP

    for g in gaps:
        P0 = (g["x0"], Y_TOP - H_at_x(a, H_left, H_right, g["x0"]))
        P1 = (g["x1"], Y_TOP - H_at_x(a, H_left, H_right, g["x1"]))
        mx, my = (P0[0]+P1[0])/2, (P0[1]+P1[1])/2
        ang = math.degrees(math.atan2(P1[1]-P0[1], P1[0]-P0[0]))
        ang = readable_angle_deg(ang)
        ax.text(mx + nx*offset, my + ny*offset, f"x_b={info['x_bottom']:.1f}",
                fontsize=8, rotation=ang, ha="center", va="center")

    ax.text(
        a/2, Y_TOP + 0.22*Y_TOP,
        f"L={a:.0f} | check base: m*s+n*x={info['total_base']:.0f}    "
        f"ipotenusa (bordo)={info['bottom_total']:.1f} | angolo pendenza={info['slope_angle_deg']:.2f}°",
        ha="center", fontsize=10
    )

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-0.02*a, 1.02*a)
    ax.set_ylim(Y_TOP - max(H_left, H_right) - 0.18*Y_TOP, Y_TOP + 0.30*Y_TOP)
    ax.grid(True, alpha=0.22)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Spartito lamiera recinzione", fontsize=12)

    return fig


# ------------------ MENU (SOLO 3 OPZIONI) ------------------

scelta = st.selectbox(
    "Scegli quale calcolo vuoi usare:",
    ("Sviluppo Lamiera", "Calcolo Scala", "Spartito lamiera recinzione")
)

# ------------------ SEZIONI ------------------

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

elif scelta == "Spartito lamiera recinzione":
    st.subheader("Spartito lamiera recinzione")

    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("Lunghezza totale diritto (mm)", min_value=1.0, value=8200.0, step=10.0)
        H_left = st.number_input("Altezza finita piantone (mm)", min_value=1.0, value=1000.0, step=10.0)
        H_right = st.number_input("Altezza in fondo con pendenza (mm)", min_value=1.0, value=600.0, step=10.0)

    with col2:
        n = st.number_input("Numero spartiti", min_value=0, value=10, step=1)
        s = st.number_input("Spessore piantone (mm)", min_value=1.0, value=40.0, step=1.0)
        label_every = st.number_input("Etichetta ogni quanti piantoni", min_value=1, value=1, step=1)

    extra_calc = st.checkbox("Calcola ipotenusa e angolo di pendenza automaticamente", value=True)

    if st.button("Calcola spartito"):
        try:
            slats, gaps, info = compute_trapezoid_layout(a, H_left, H_right, int(n), s, x=None)

            st.success("Calcolo riuscito ✅")
            st.write(f"Numero piantoni = n+1 = {info['m_slats']}")
            st.write(f"Spazio tra piantoni (x) = {info['x']:.3f} mm")
            st.write(f"Larghezza piantone sul bordo in pendenza = {info['s_bottom']:.3f} mm")
            st.write(f"Spazio sul bordo in pendenza = {info['x_bottom']:.3f} mm")

            if extra_calc:
                direzione = "scende verso destra" if (H_right > H_left) else ("sale verso destra" if (H_right < H_left) else "piatto")
                st.info(
                    f"Ipotenusa (lunghezza lato inclinato) = {info['bottom_total']:.3f} mm\n\n"
                    f"Angolo di pendenza = {info['slope_angle_deg']:.3f}° ({direzione})"
                )

            fig = make_trapezoid_figure(a, H_left, H_right, slats, gaps, info, label_every=int(label_every))
            st.pyplot(fig)

            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)

            st.download_button(
                label="⬇️ Scarica grafico spartito (PNG)",
                data=buf,
                file_name="spartito_lamiera_recinzione.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"Errore: {e}")