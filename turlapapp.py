#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 17:16:22 2022

@author: genta
"""
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
#import shapely 
#from osmnx.projection import project_gdf
from streamlit_geolocation import streamlit_geolocation
#import pyperclip
st.set_page_config(layout="wide", page_icon="📍")
from math import radians, cos, sin, asin, sqrt
def haversine(lon1, lat1, lon2, lat2):
    
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def distancing(center, points):
    distances=[]
    for p in points:
        distances.append(haversine(center[0], center[-1], p[0], p[-1]))
    return distances



file1="grid_data_forqgis.gpkg"
file2="hayashidata_within.gpkg"
kebo="kebo.gpkg"
notkebo="notkebo.gpkg"
#f=gpd.read_file(file2)
#f.plot("LocalMoranHotCold:All RSBs")

options_list=["hotspot portal (kampung)", "hotspot portal (komplek)",
            "coldspot portal(kampung)", "coldspot portal(komplek)", "kosan (gak boleh kumpul kebo)", "kosan (gak larang kumpul kebo)"]
@st.cache(suppress_st_warning=True,allow_output_mutation=True) 
def data():
    gdf=gpd.read_file(file1).to_crs("epsg:4326")
    hayashi=gpd.read_file(file2).to_crs("epsg:4326")
    

    dictio={}
    dictio["hotspot portal (kampung)"]=gpd.sjoin(hayashi[hayashi["BE_2016"]=="カンポン"], gdf[gdf["LocalMoranHotCold:All RSBs"]=="HH"])
    dictio["hotspot portal (komplek)"]=gpd.sjoin(hayashi[hayashi["BE_2016"]=="計画"], gdf[gdf["LocalMoranHotCold:All RSBs"]=="HH"])
    dictio["coldspot portal (komplek)"]=gpd.sjoin(hayashi[hayashi["BE_2016"]=="計画"], gdf[gdf["LocalMoranHotCold:All RSBs"]=="LL"])
    dictio["coldspot portal (kampung)"]=gpd.sjoin(hayashi[hayashi["BE_2016"]=="カンポン"], gdf[gdf["LocalMoranHotCold:All RSBs"]=="LL"])

    dictio["kosan (gak boleh kumpul kebo)"]=gpd.read_file(kebo)
    dictio["kosan (gak larang kumpul kebo)"]=gpd.read_file(notkebo)
    return dictio
dictio=data()



left, space1=st.columns(2)
#genre = right.radio("Mode",('Links Isian', 'Peta', "Terdekat"))
if  left.button("clear cache"):
    st.experimental_singleton.clear()


place=st.empty()

with space1:
    currtent_location =streamlit_geolocation()
if currtent_location["latitude"] is None:
    with space1:
        st.header("cek lokasi dulu")
else:

    #left, nspace, right=place.columns([1,5,1])
    with space1:
        index=st.radio("index",  list(dictio.keys()))   
    m=dictio[index]
    m=m.reset_index(drop=True)
    m["selected"]=False
    #m=dictio['hotspot portal (komplek)']
    lat, long=currtent_location["latitude"], currtent_location["longitude"]
    #lat,long=-6.239999325231135, 106.81222830181815
    points=[(x, y) for x, y in zip(m.centroid.x, m.centroid.y)]
    location=pd.Series(distancing(center=(long, lat), points=points)).idxmin()
    m.loc[location, "selected"]=True
    m["selected"]= m["selected"].replace({True:10, False:0}).astype(float).fillna(0)
    m.plot("selected")
    location=m.loc[location].geometry.centroid
    location=location.y, location.x
    
    with left:
        st.write(f"lokasi terdekat adalah {location} ")
        st.write("(isi kordinat ini pada 'tempat tinggal saat ini dalam form isian')")
        location=f"https://www.google.com/maps?saddr=My+Location&daddr={location[0]},{location[-1]}"
        
        

    #place2=st.empty()
    #location = streamlit_geolocation()
   
        color="#FD504D"
        st.markdown(
        f"""
        <a href="{location}" target="_blank">
            <div style="
                display: inline-block;
                padding: 0.5em 1em;
                color: #FFFFFF;
                background-color: {color};
                border-radius: 3px;
                text-decoration: none;">
                {"liat rute  ke "+index + " terdekat"}
            </div>
        </a>
        """,
        unsafe_allow_html=True
        )

        st.text("")
        st.text("")
        with st.expander("form isian"):
            newplace=st.empty()
            form='''
            <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSd3XVCYMsamR62e22XK86_Mt-K9MeWZiLipOOceAEYauwOCkg/viewform?embedded=true" 
            width="355" height="515" 
            frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>
            '''
            st.markdown(form, unsafe_allow_html=True)
        with st.expander("liat peta"):
            #index=st.sidebar.selectbox("index",  options_list) 
            m=dictio[index]
            m=m.reset_index(drop=True)
            m["selected"]=False
            #m=dictio['hotspot portal (komplek)']
            lat, long=currtent_location["latitude"], currtent_location["longitude"]
            #lat,long=-6.239999325231135, 106.81222830181815
            points=[(x, y) for x, y in zip(m.centroid.x, m.centroid.y)]
            location=pd.Series(distancing(center=(long, lat), points=points)).idxmin()
            m.loc[location, "selected"]=True
            m["selected"]= m["selected"].replace({True:10, False:0}).astype(float).fillna(0)
            m.plot("selected")
            location=m.loc[location].geometry.centroid
            location=location.y, location.x

            
            st.write(f"peta {index} keseluruhan")
            m=m.explore(column="selected")
            folium_static(m, width=400, height=400)
        with st.expander("upload file rekaman atau foto kalo ada"):
            st.file_uploader("")


