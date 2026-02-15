import math
import streamlit as st

st.set_page_config(page_title="Calcoli Ismet", page_icon="🧰")

st.title("Programma Calcoli - Ismet Berisha Lavoratore Numero 1")

# ------------------ FUNZIONI ------------------

def sviluppo(lunghezza_esterna, laterale_lamiera, spessore_lamiera):
    lunghezza_totale = lunghezza_esterna + (laterale_lamiera * 2) - (4 * spessore_lamiera)
    lunghezza_totale_interna = lunghezza_esterna + (laterale_lamiera * 2) + (4 * spessore_lamiera)
    return lunghezza_totale, lunghezza_totale_interna


def scala_babi(cateto1, cateto2, pedate):
    ipotenusa = (cateto1**2 + cateto2**2) ** 0.5
    lunghezza = pedate * ipotenusa

    angolo = math.acos(cateto1 / ipotenusa)
    angolo_gradi = math.degrees(angolo)
    angolo_esterno = 90 - angolo_gradi

    return lunghezza, angolo_gradi, angolo_esterno


# ------------------ MENU SCELTA ------------------

scelta = st.selectbox(
    "Scegli quale calcolo vuoi usare:",
    ("Sviluppo Lamiera", "Calcolo Scala")
)

# ------------------ SEZIONE LAMIERA ------------------

if scelta == "Sviluppo Lamiera":

    st.subheader("Calcolo Sviluppo Lamiera")

    lunghezza = st.number_input("Lunghezza esterna", min_value=0.0)
    laterale = st.number_input("Laterale lamiera", min_value=0.0)
    spessore = st.number_input("Spessore lamiera", min_value=0.0)

    if st.button("Calcola sviluppo"):
        esterno, interno = sviluppo(lunghezza, laterale, spessore)

        st.success("Risultati")
        st.write("Sviluppo esterno:", round(esterno, 3))
        st.write("Sviluppo interno:", round(interno, 3))


# ------------------ SEZIONE SCALA ------------------

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
