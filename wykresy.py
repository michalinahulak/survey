import streamlit as st
import streamlit.components.v1 as components
import os
import csv
import pymongo


# Ścieżka do pliku CSV
csv_file_path = 'responses.csv'


# Funkcja do zapisywania danych do CSV
def save_to_csv(data):
    # Sprawdzenie, czy plik już istnieje
    file_exists = os.path.isfile(csv_file_path)

    # Zapisywanie danych do pliku CSV
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Dodanie nagłówków, jeśli plik nie istnieje
            headers = titles + ['best_model', 'user_type']
            writer.writerow(headers)
        # Zapisywanie odpowiedzi
        row = ratings + [data['best_representation'], data['user_type']]
        writer.writerow(row)

# Ustawienie trybu wide
st.set_page_config(layout="wide")

# Lista plików HTML z wykresami
files = [
    "1_allegro_herbert-large-cased.html",
    "2_intfloat_multilingual-e5-base.html",
    "3_ipipan_silver-retriever-base-v1.1.html",
    "4_llama_3_0_embeddings.html",
    "5_sdadas_polish-roberta-large-v2.html"
]

# Tytuły wykresów odpowiadające plikom
titles = [
    "1. allegro/herbert-large-cased",
    "2. intfloat/multilingual-e5-base",
    "3. ipipan/silver-retriever-base-v1.1",
    "4. llama_3_0_embeddings",
    "5. sdadas/polish-roberta-large-v2"
]

titles_numerate = [
    "model 1",
    "model 2",
    "model 3",
    "model 4",
    "model 5"
]

ratings = []
rating_options = [
    "model bezbłędny",
    "1 błąd",
    "2-3 błędy",
    "4-5 błędy",
    "powyżej 5 błędów"
]

st.markdown(
    """
    <style>
    .justified-text {
        text-align: justify;
    }
    </style>
    """, unsafe_allow_html=True
)

# Wprowadzenie do ankiety
st.title("Ankieta oceny wizualizacji danych")
st.markdown("""
<div class="justified-text">
Dziękujemy za udział w naszej ankiecie, której celem jest ocena wizualizacji danych z różnych modeli tzw. "embeddingów". W uproszczeniu, teksty artykułów, które znamy z życia codziennego, zostały zamienione na reprezentacje liczbowe (embeddingi), a następnie odwzorowane na wykresie przy użyciu metody UMAP. 
W efekcie, <strong>podobne tematycznie artykuły powinny znaleźć się blisko siebie na wykresie, a te różniące się tematycznie — w większej odległości.</strong> Chcemy, abyś pomógł nam ocenić, który z przedstawionych wykresów najlepiej oddaje te relacje.
</br></br>
<strong>Oceń reprezentację:</strong> Na każdym wykresie zobaczysz punkty, które reprezentują różne artykuły. 
Oceń, czy artykuły z podobnych tematów (np. artykuły sportowe) znajdują się blisko siebie, tworząc spójne grupy.  

**Każdy wykres przeglądaj przez 1 minutę i oceń według poniższej skali:**

* model bezbłędny
* 1 błąd
* 2-3 błędy
* 4-5 błędy
* powyżej 5 błędów

</div>
""", unsafe_allow_html=True)

# Wyświetlenie filmu
video_html = f"""
    <div style="display: flex; justify-content: left;">
        <iframe width="560" height="315" src="https://www.youtube.com/embed/8QDNFvJfY7Y?si=kgfPpsn5NcrZ39ep&amp;controls=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
"""



# Wyświetlenie filmiku
st.markdown(video_html, unsafe_allow_html=True)

# Tworzenie ankiety dla każdego wykresu
ratings = []
for i, file_name in enumerate(files):
    st.header(f"Wykres: {titles_numerate[i]}")

    # Wczytanie wykresu HTML z lokalnego folderu "wykresy"
    file_path = os.path.join(file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Wyświetlenie wykresu
    st.components.v1.html(html_content, height=600)

    # # Prośba o ocenę wykresu
    # rating = st.slider(f"Oceń wykres {i + 1}", 1, 5, 3)
    # ratings.append(rating)

    # Prośba o ocenę wykresu
    rating = st.radio(f"Oceń wykres {i + 1}", options=rating_options, index=0)
    ratings.append(rating)

    # Dodanie odstępu po wykresie
    st.markdown('<div class="spacer"></br></br></br></div>', unsafe_allow_html=True)

# Dodatkowe pytanie
st.header("Na którym z wykresów najlepiej odwzorowany jest podział artykułów ze względu na tematykę?")
best_representation = st.radio(
    "Wybierz jeden wykres:",
    options=titles_numerate,
    index=0
)

# Pytanie o typ użytkownika
st.header("Jestem osobą:")
user_type = st.radio(
    "Wybierz jeden typ:",
    options=[
        "techniczną (analityk danych, programista, Data Scientist, AI specialist lub pokrewne)",
        "nietechniczną"
    ],
    index=0
)

# Wyświetlenie wyników po przesłaniu
if st.button("Prześlij odpowiedzi"):
    st.header("**Twoje oceny:**")
    for i, rating in enumerate(ratings):
        st.write(f"Wykres {titles[i]}: {rating}/5")
    st.write(f"Najlepiej odwzorowany wykres: {best_representation}")
    st.write(f"Typ użytkownika: {user_type}")

    # Zapisz odpowiedzi do pliku CSV
    save_to_csv({'ratings': ratings, 'best_representation': best_representation, 'user_type': user_type})

    # Przygotowanie danych do zapisania w MongoDB
    user_data = {
        'ratings': ratings,
        'best_representation': best_representation,
        'user_type': user_type
    }

    from pymongo.mongo_client import MongoClient
    from pymongo.server_api import ServerApi
    try:
        with MongoClient(st.secrets["mongo"], server_api=ServerApi('1')) as client:
            db = client.survey
            collection = db.app
            collection.insert_one(user_data)
            st.session_state.inserted16 = True
    except pymongo.errors.OperationFailure as e:
        st.error(f"Błąd operacji MongoDB: {e.details}")
    except Exception as e:
        st.error(f"Wystąpił nieoczekiwany błąd: {str(e)}")
    st.header("Twoje wyniki zostały pomyślnie przesłane. Dziękujemy za udział w ankiecie! ")
