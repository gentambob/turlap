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
st.set_page_config(layout="wide")





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
    """
    file="/Volumes/HDPH-UT/DATA/scraping/ruko_indonesia/2022-07-09_mamikos.csv"
    gdf=gpd.GeoDataFrame(pd.read_csv(file), geometry=pd.read_csv(file)["geometry"].apply(shapely.wkt.loads),
                    crs= "EPSG:3395")

    cols=gdf.dtypes.rename("type")
    for i, c in zip(cols.index,cols):
        if c.name=='bool':
            gdf["dummy"+str(i)]=gdf[i].replace({True:1, False:0})

    gdf["dummymarried_couple_allowed"]=gdf["dummymarried_couple_allowed"].replace({0:1, 1:0})
    kebo=gdf[gdf[["dummyopposite_sex_not_allowed", "dummygendered","dummymarried_couple_allowed"]].sum(1)>0]
    notkebo=gdf.loc[gdf.index.isin(kebo.index)==False]
    kebo.to_crs("epsg:4326")[["geometry", "name_slug"]].to_file("kebo.gpkg",  driver="GPKG")
    notkebo.to_crs("epsg:4326")[["geometry", "name_slug"]].to_file("notkebo.gpkg",  driver="GPKG")
    #cctv=gdf[gdf["dummyCCTV"]>0]
    #guard=gdf[gdf[ 'dummyguard']>0]
 
    """
    dictio["kosan (gak boleh kumpul kebo)"]=gpd.read_file(kebo)
    dictio["kosan (gak larang kumpul kebo)"]=gpd.read_file(notkebo)
    return dictio
dictio=data()



left, space1, s,right=st.columns(4)
#genre = right.radio("Mode",('Links Isian', 'Peta', "Terdekat"))
if  left.button("clear cache"):
    st.experimental_singleton.clear()


place=st.empty()
st.write("cek lokasi dulu")

currtent_location =streamlit_geolocation()
print(currtent_location)
if currtent_location:

    left, nspace, right=place.columns([1,5,1])
    index=st.sidebar.selectbox("index",  options_list)   
    with nspace:
        m=dictio[index]
        lat, long=currtent_location["latitude"], currtent_location["longitude"]
        print(gpd.points_from_xy(x=[lat], y=[long]))
        location=m.distance(gpd.points_from_xy(x=[lat], y=[long])[0]).idxmin()
        location=m.loc[location].geometry.centroid
        location=location.y, location.x
        st.write(f"lokasi terdekat adalah {location} ")
        st.write("(isi kordinat ini pada 'tempat tinggal saat ini dalam form isian')")
        location=f"https://www.google.com/maps?saddr=My+Location&daddr={location[0]},{location[-1]}"
        
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

    #place2=st.empty()
    #location = streamlit_geolocation()
    with st.expander("form isian"):
        newplace=st.empty()
        form='''
        <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSd3XVCYMsamR62e22XK86_Mt-K9MeWZiLipOOceAEYauwOCkg/viewform?embedded=true" 
        width="640" height="6463" 
        frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>
        '''
        st.markdown(form, unsafe_allow_html=True)
    with st.expander("liat peta"):
        #index=st.sidebar.selectbox("index",  options_list) 
        m=dictio[index]
        st.write(f"peta {index} seseluruhan")
        m=m.explore()
        folium_static(m, width=400, height=400)
    with st.expander("upload file rekaman atau foto kalo ada"):
        st.file_uploader("")


