import streamlit as st
import pandas as pd
from pymongo.mongo_client import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns
import qrcode
from io import BytesIO
from pymongo.server_api import ServerApi


# Ställ in sidan som första sak
st.set_page_config(page_title="Produkter som Behöver Beställas")

# Anslut till MongoDB
uri = "mongodb+srv://demafalihdata24hel:AuAbsHQpjfJHABAl@cluster0.j199w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["inventory_db"]
collection = db["products"]

# Hämta produkter som behöver beställas
products = list(collection.find({}, {"_id": 0}))
df = pd.DataFrame(products)
to_reorder = df[df["ReorderLevel"] > (df["UnitsInStock"] + df["UnitsOnOrder"])]

# Streamlit UI
st.title("Produkter som behöver beställas")
st.markdown("""
    Här kan du se en lista över produkter som behöver beställas. 
    Du kan också generera en QR-kod för att beställa produkterna direkt från leverantören.
""")

# Förbättra tabellutseendet med röda nyanser
st.subheader("Produkter som behöver beställas:")
st.dataframe(to_reorder[["ProductName", "CompanyName", "ContactName", "Phone"]].style.format({
    'ProductName': lambda x: f"{x}",
    'Phone': lambda x: f"{x}"
}).set_table_styles([{
    'selector': 'thead th',
    'props': [('background-color', '#D32F2F'), ('color', 'white'), ('font-size', '14px')]
}, {
    'selector': 'tbody td',
    'props': [('background-color', '#FFCDD2'), ('font-size', '12px')]
}])) # alla dessa färger syns när man trycker på cellerna

# Lägg till QR-kod för att beställa produkterna
def generate_qr_code(contact_info):
    qr = qrcode.make(contact_info)
    buf = BytesIO()
    qr.save(buf)
    return buf.getvalue()

# Lägg till QR-kod och information för varje produkt
for index, row in to_reorder.iterrows():
    contact_info = f"Beställ {row['ProductName']} från {row['CompanyName']} via telefon: {row['Phone']}"
    qr_code = generate_qr_code(contact_info)
    st.image(qr_code, width=150, caption=f"QR-kod för att beställa {row['ProductName']}")

# Visualisera lagerstatus med hjälp av ett diagram
st.subheader("Lagerstatus: Reorder Level per Produkt")
fig, ax = plt.subplots(figsize=(12, 6))

# Använd en anpassad röd färgpalett
reds = sns.color_palette("Reds", len(to_reorder))

# Skapa stapeldiagram med röda nyanser
sns.barplot(x="ProductName", y="ReorderLevel", data=to_reorder, ax=ax, palette=reds)

ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
ax.set_title("Reorder Level per Produkt", fontsize=16, weight="bold")
ax.set_xlabel("Produktnamn", fontsize=12)
ax.set_ylabel("Reorder Level", fontsize=12)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
st.pyplot(fig)

# Bara för lite mer interaktivitet - Visa mer detaljer med en knapp
if st.button('Visa mer detaljer'):
    st.write(to_reorder)

# För att va lite trevlig mot användaren
st.markdown("""
    ---
    **Kundtjänst:** Om du behöver hjälp, vänligen kontakta oss på support@inventory.com
    ### Tack för att du använder vår app!
""")