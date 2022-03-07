import streamlit as st
import pandas as pd
import base64
import io
import plotly.express as px
import numpy as np
from io import BytesIO

st.cache
def show_page ():
    st.write("""
    # Kalkulator Indeks Keragaman dan Status Konservasi Fauna
    Diasumsikan anda telah melakukan pengamatan di plot pengamatan di unit manajemen anda. Tautan unduh format dan template tersedia di laman "Pengantar"
    """)
    st.cache
    with st.sidebar.header('Upload data'):
        uploaded_file_fauna = st.sidebar.file_uploader("Upload data pengamatan satwa dalam excel", type=["xlsx"])
    
    # Displays the dataset
    
    
    
    if uploaded_file_fauna is not None:
        fauna = pd.read_excel(uploaded_file_fauna)
        fauna['Tahun Assessment']=fauna['Tahun Assessment'].dt.strftime('%Y')
        st.subheader('1. Tabel Data Mentah')
        st.markdown('**1.1. Tampilan Tabel Data Mentah**')
        st.write("Ini adalah penampakan tabel data mentah yang telah diupload")
        with st.expander ("Tabel Data Mentah", expanded=False):
            st.write(fauna)
        
        #menentukan total individu per detail lokasi
        sum_ind = fauna.groupby("Detail Lokasi").sum()["Jumlah"].reset_index()

        #menghitung KR, FR, DR, Isatwa_2 = pd.merge(left=satwa, right=sum_ind, how='inner', on=['Detail Lokasi'])

        fauna_2 = pd.merge(left=fauna, right=sum_ind, how='inner', on=['Detail Lokasi'])

        fauna_2.rename({"Jumlah_x": "Jumlah Individu", "Jumlah_y": "Total Individu/Plot" }, axis=1, inplace=True)

        fauna_2['ni/N'] = fauna_2['Jumlah Individu']/fauna_2['Total Individu/Plot']

        fauna_2['Ln ni/N'] = np.log(fauna_2['ni/N'])

        fauna_2["H'"] = abs(fauna_2['ni/N'] * fauna_2['Ln ni/N'])

        #menentukan H' per lokasi    
        h_per_lokasi = fauna_2.groupby(["Tahun Assessment", "Provinsi", "Kabupaten", "Perusahaan", "Detail Lokasi"]).sum()["H'"].reset_index()

        conditions = [
                (h_per_lokasi["H'"] > 3.5),
                (h_per_lokasi["H'"] > 2.5),
                (h_per_lokasi["H'"] > 1.5),
                (h_per_lokasi["H'"] > 1),
                (h_per_lokasi["H'"] <= 1)]

        values = ["SANGAT TINGGI", "TINGGI", "SEDANG", "RENDAH", "SANGAT RENDAH"]

        h_per_lokasi["Kategori H'"] = np.select(conditions, values)
        
        #mengklasifikasikan status IUCN, CITES, dan PP106

        daftar_fauna = pd.read_excel("Daftar Vegetasi dan Satwa.xlsx")

        daftar_2 = pd.merge(left=fauna_2, right=daftar_fauna, how="outer")
        daftar_2.reset_index()
        daftar_2 = daftar_2.dropna(subset=['Tahun Assessment'])

        daftar_2.drop(columns=['No Satwa', 'Total Individu/Plot', 'ni/N', 
                          'Ln ni/N', "H'"], inplace=True)


        st.subheader("2. Indeks Keragaman (H')")
        st.write("**Filter**")
        with st.expander('Filter Tabel Hasilmu Di Sini',expanded=False):
            col1,col2 = st.columns(2)
            with col1:
                tahun = h_per_lokasi["Tahun Assessment"].unique().tolist()
                tahun_choice = st.multiselect("Tahun Assessment", options= tahun, 
                                               default = tahun)
            with col2:
                provinsi = h_per_lokasi["Provinsi"].unique().tolist()
                provinsi_choice = st.multiselect('Provinsi', options = provinsi, default = provinsi)

            col3,col4 = st.columns(2)
            with col3:
                kabupaten = h_per_lokasi["Kabupaten"].unique().tolist()
                kabupaten_choice = st.multiselect('Kabupaten', options =kabupaten, default = kabupaten)

            with col4:
                perusahaan = h_per_lokasi["Perusahaan"].unique().tolist()
                perusahaan_choice = st.multiselect('Perusahaan', options= perusahaan, default = perusahaan)

            lokasi = h_per_lokasi["Detail Lokasi"].unique().tolist()
            lokasi_choice = st.multiselect('Detail Lokasi', options= lokasi, default = lokasi)



        mask_h = (h_per_lokasi["Tahun Assessment"].isin(tahun_choice)) & (h_per_lokasi["Provinsi"].isin(provinsi_choice)) & (h_per_lokasi["Kabupaten"].isin(kabupaten_choice)) & (h_per_lokasi["Perusahaan"].isin(perusahaan_choice)) & (h_per_lokasi["Detail Lokasi"].isin(lokasi_choice))

        h_per_lokasi_selection = h_per_lokasi[mask_h]

        mask_daftar_2 = (daftar_2["Tahun Assessment"].isin(tahun_choice)) & (daftar_2["Provinsi"].isin(provinsi_choice)) & (daftar_2["Kabupaten"].isin(kabupaten_choice)) & (daftar_2["Perusahaan"].isin(perusahaan_choice)) & (daftar_2["Detail Lokasi"].isin(lokasi_choice))

        daftar_2_selection = daftar_2[mask_daftar_2]

        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output)
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            writer.save()
            processed_data = output.getvalue()
            return processed_data

        h_per_lokasi_selection_xlsx = to_excel(h_per_lokasi_selection)
        daftar_2_selection_xlsx = to_excel(daftar_2_selection)

        st.markdown('**2.1. Tabel Hasil Indeks Keragaman**')
        with st.expander('Tabel Indeks Keragaman',expanded=False):
            st.write(h_per_lokasi_selection)
        st.download_button(label="📥 Download Tabel Indeks Keragaman (H')",
                                    data=h_per_lokasi_selection_xlsx ,
                                    file_name= "Indeks Keragaman (H').xlsx")
        
        #graphic Indeks Keragaman
        h_bar = px.bar(h_per_lokasi_selection, x="Detail Lokasi", y="H'", barmode="group",
                       color="Kategori H'", facet_col="Tahun Assessment",
                       width=1000, height=500, title='Indeks Keragaman Menurut Lokasi')

        
        h_line = px.line(h_per_lokasi_selection, x="Tahun Assessment", y="H'",
                         color="Detail Lokasi", title='Indeks Keragaman Setiap Tahun')
                              
        st.markdown('**2.2. Grafik Indeks Keragaman**')
        with st.expander('Grafik Indeks Keragaman',expanded=False):
            st.write(h_bar)
            st.write(h_line)
                        
                         

        
        
                         
        st.subheader("3.Status Konservasi")
        st.markdown('**3.1. Tabel Status Konservasi**')

        with st.expander('Tabel Status Konservasi',expanded=False):
            st.write(daftar_2_selection)
        st.download_button(label="📥 Download Tabel Status Konservasi",
                                    data=daftar_2_selection_xlsx ,
                                    file_name= "Status Konservasi.xlsx")
        #graphic IUCN

        iucn = (daftar_2_selection.groupby(by=["Nama Latin", "IUCN"]).sum()[["Jumlah Individu"]].sort_values(by="Jumlah Individu"))
        iucn = iucn.reset_index()
        iucn_bar = px.bar(iucn, x="Nama Latin", y="Jumlah Individu", 
                             facet_col="IUCN",
                             width=1000, height=500,
                             title='Spesies menurut status IUCN')
        st.markdown('**3.2. Berdasarkan IUCN**')
        with st.expander('Spesies menurut status IUCN',expanded=False):
            st.write(iucn_bar)


        #graphic CITES
        cites = (daftar_2_selection.groupby(by=["Nama Latin", "CITES"]).sum()[["Jumlah Individu"]].sort_values(by="Jumlah Individu"))
        cites = cites.reset_index()
        cites_bar = px.bar(cites, x="Nama Latin", y="Jumlah Individu", 
                             facet_col="CITES",
                             width=1000, height=500,
                             title='Spesies menurut status CITES')
        st.markdown('**3.3. Berdasarakan CITES**')
        with st.expander('Spesies menurut status CITES',expanded=False):
            st.write(cites_bar)


        #graphic PP 106
        pp_106 = (daftar_2_selection.groupby(by=["Nama Latin", "PP 106"]).sum()[["Jumlah Individu"]].sort_values(by="Jumlah Individu"))
        pp_106 = pp_106.reset_index()
        pp_106_bar = px.bar(pp_106, x="Nama Latin", y="Jumlah Individu", 
                             facet_col="PP 106",
                             width=1000, height=500,
                             title='Sepesies menurut status PP 106')
        st.markdown('**3.4. Berdasarkan PP 106**')
        with st.expander('Spesies menurut status PP 106',expanded=False):
            st.write(pp_106_bar)  
    

    else:
        st.info('Menunggu berkasmu diupload.')
        


