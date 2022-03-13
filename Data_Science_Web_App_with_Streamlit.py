import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

#st.title("hello world!")
#st.markdown("## my first streamlit dashboard!")

# Dataset con 1.67 million rows y 29 columns
data_url = ("data/Motor_Vehicle_Collisions_-_Crashes.csv")

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used "
"to analyze motor vehicle collisions in NYC. 🗽💥🚗")

# Para que sea más eficiente cuando se tiene muchos datos.
# st.cache trabaja de forma inteligente, solo hace rerun del
# código cuando el código o sus inputs cambian.
@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(data_url, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    # No puede faltar info en las columnas de lat y lon
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    # Cambiar a lowercase los títulos de las columnas
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data

# Preguntas que aparecerán en el dashboard
st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19)
# Para usar st.map tienen que existir columns en los datos que 
# se llamen latitude y longitude o lat y lon
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

# Preguntas que aparecerán en el dashboard
st.header("How many collisions occur during a given time of day?")
#hour = st.selectbox("Hour to look at", range(1,25), 1)
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]

# Preguntas que aparecerán en el dashboard
st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour+1) % 24))
# Punto medio de lat y lon para la posición inicial del mapa
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
# Mapa 3D + layer
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data = data[['date/time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0,1000],
        ),
    ],
))

# Preguntas que aparecerán en el dashboard
st.subheader("Breakdown by minute between %i:00 and %i:00" %(hour, (hour+1)%24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(0,60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

# Preguntas que aparecerán en el dashboard
st.header("Top 5 dangerous street by affected type")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[['on_street_name', 'injured_pedestrians']].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])
elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[['on_street_name', 'injured_cyclists']].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])
elif select == 'Motorists':
    st.write(original_data.query("injured_motorists >= 1")[['on_street_name', 'injured_motorists']].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])

# Checkbox para que se vean los datos raw o no
if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)