import streamlit as st
import pandas as pd
import base64
import io
import plotly.express as px
import numpy as np
from io import BytesIO

def show_page ():
    st.write("""
    # Kalkulator Indeks Keragaman dan Indeks Nilai Penting Flora
    Diasumsikan anda telah melakukan pengukuran diameter dan jumlah vegetasi di plot pengukuran di unit manajemen anda. Tautan unduh format dan template tersedia di laman "Pengantar"
    """)
    
    with st.sidebar.header('Upload data'):
        uploaded_file_flora = st.sidebar.file_uploader("Upload data pengamatan vegetasi dalam excel", type=["xlsx"])
    
    # Displays the dataset
    

    
       
    if uploaded_file_flora is not None:
        flora = pd.read_excel(uploaded_file_flora)
        flora['Tahun Assessment']=flora['Tahun Assessment'].dt.strftime('%Y')
        st.subheader('1. Tabel Data Mentah')
        st.markdown('**1.1. Tabel Data Mentah**')
        st.write("Ini adalah penampakan tabel data mentah yang telah diupload")
        with st.expander ("Tabel Data Mentah", expanded=False):
            st.write(flora)

            
            

        #menentukan Ø (cm)
        flora['Ø (cm)'] = flora['Diameter (cm)']*flora['Diameter (cm)']*0.25*3.14

        #menentukan 'Lbds (ha)'
        flora['Lbds (ha)'] = flora['Ø (cm)']/100000000

        # menentukan Lbds satu detail lokasi
        flora_1 = flora.pivot_table(index = ['Tahun Assessment',"Provinsi","Kabupaten","Perusahaan",'Detail Lokasi', 'Kelas Vegetasi'],
                                    columns='Kelas Vegetasi', aggfunc = {'Lbds (ha)':sum})
        flora_1.columns = [f'{x} {y}' for x,y in flora_1.columns]
        flora_1 = flora_1.reset_index()

        #menentukan lbds R: lbds per jenis/lbds per detail lokasi
        flora_1 = pd.merge(left=flora_1, right=flora, how='inner', on=['Tahun Assessment', "Provinsi",
                                                                       "Kabupaten","Perusahaan",'Detail Lokasi', "Kelas Vegetasi"])
        flora_1["Lbds R (ha) Semai"] = flora_1["Lbds (ha)"]/flora_1["Lbds (ha) Semai"]
        flora_1["Lbds R (ha) Pancang"] = flora_1["Lbds (ha)"]/flora_1["Lbds (ha) Pancang"]
        flora_1["Lbds R (ha) Tiang"] = flora_1["Lbds (ha)"]/flora_1["Lbds (ha) Tiang"]
        flora_1["Lbds R (ha) Pohon"] = flora_1["Lbds (ha)"]/flora_1["Lbds (ha) Pohon"]
        flora_1=flora_1.reset_index()
        flora_1 =flora_1.pivot_table(index= ['Tahun Assessment', "Provinsi","Kabupaten","Perusahaan", 
                                             'Detail Lokasi', "Kelas Vegetasi", "Nama Latin"], 
                                     aggfunc ={"Lbds R (ha) Semai":sum, "Lbds R (ha) Pancang":sum, 
                                               "Lbds R (ha) Tiang": sum, "Lbds R (ha) Pohon": sum})
        flora_1=flora_1.reset_index()

        #menentukan jumlah individu per spesies per kelas vegetasi, jumlah plot number per spesies, dan Lbds per spesies per kelas vegetasi
        flora_2 = flora.pivot_table(index = ["Tahun Assessment", "Provinsi","Kabupaten","Perusahaan","Detail Lokasi", "Nama Latin", 
                                             "Kelas Vegetasi"], columns='Kelas Vegetasi', 
                                    aggfunc = {'Jumlah':sum, 'Plot Number': "nunique"})
        flora_2.columns = [f'{x} {y}' for x,y in flora_2.columns]
        flora_2 =flora_2.reset_index()
        flora_2 = pd.merge(left=flora_2, right=flora_1, how='inner', on=['Tahun Assessment', "Provinsi","Kabupaten","Perusahaan",
                                                                         'Detail Lokasi', "Kelas Vegetasi", "Nama Latin"])

        #menentukan jumlah total plot number per kelas vegetasi per detail lokasi dan luas plot
        flora_3 = flora.pivot_table(index = ['Tahun Assessment',"Provinsi","Kabupaten","Perusahaan","Detail Lokasi", 
                                             'Kelas Vegetasi'], columns='Kelas Vegetasi',
                                    aggfunc = {'Plot Number': "nunique", "Jumlah":sum})
        flora_3.columns = [f'{x} {y}' for x,y in flora_3.columns]
        flora_3 =flora_3.reset_index()
        flora_3["Luas Plot Semai"] = flora_3["Plot Number Semai"]*4/10000
        flora_3["Luas Plot Pancang"] = flora_3["Plot Number Pancang"]*25/10000
        flora_3["Luas Plot Tiang"] = flora_3["Plot Number Tiang"]*100/10000
        flora_3["Luas Plot Pohon"] = flora_3["Plot Number Pohon"]*400/10000

        #menghitung K, F, dan D
        flora_4 = pd.merge(left=flora_2, right=flora_3, how='inner', on=['Tahun Assessment', "Provinsi","Kabupaten","Perusahaan","Detail Lokasi"])
        flora_4['K (∑ind/ha) Semai'] = flora_4['Jumlah Semai_x']/flora_4['Luas Plot Semai']
        flora_4['K (∑ind/ha) Pancang'] = flora_4['Jumlah Pancang_x']/flora_4['Luas Plot Pancang']
        flora_4['K (∑ind/ha) Tiang'] = flora_4['Jumlah Tiang_x']/flora_4['Luas Plot Tiang']
        flora_4['K (∑ind/ha) Pohon'] = flora_4['Jumlah Pohon_x']/flora_4['Luas Plot Pohon']

        flora_4['F Semai'] = flora_4['Plot Number Semai_x']/flora_4['Plot Number Semai_y']
        flora_4['F Pancang'] = flora_4['Plot Number Pancang_x']/flora_4['Plot Number Pancang_y']
        flora_4['F Tiang'] = flora_4['Plot Number Tiang_x']/flora_4['Plot Number Tiang_y']
        flora_4['F Pohon'] = flora_4['Plot Number Pohon_x']/flora_4['Plot Number Pohon_y']

        flora_4['D Semai'] = flora_4['Lbds R (ha) Semai']/1
        flora_4['D Pancang'] = flora_4['Lbds R (ha) Pancang']/1
        flora_4['D Tiang'] = flora_4['Lbds R (ha) Tiang']/1
        flora_4['D Pohon'] = flora_4['Lbds R (ha) Pohon']/1

        flora_4.drop(columns=['Jumlah Semai_x', 'Jumlah Pancang_x', 'Jumlah Tiang_x', 'Jumlah Pohon_x', 
                          'Jumlah Semai_y', 'Jumlah Pancang_y', 'Jumlah Tiang_y', 'Jumlah Pohon_y',
                          'Plot Number Semai_x', 'Plot Number Pancang_x', 'Plot Number Tiang_x', 
                          'Plot Number Pohon_x', 'Plot Number Semai_y', 'Plot Number Pancang_y', 
                          'Plot Number Tiang_y', 'Plot Number Pohon_y', 'Luas Plot Semai', 'Luas Plot Pancang',
                          'Luas Plot Tiang','Luas Plot Pohon', 'Lbds R (ha) Semai', 'Lbds R (ha) Pancang', 'Lbds R (ha) Tiang',
                         'Lbds R (ha) Pohon'], inplace=True)

        flora_4 = flora_4.reset_index()

        flora_5 = flora_4.pivot_table(index = ['Tahun Assessment',"Provinsi","Kabupaten","Perusahaan",'Detail Lokasi'],
                        aggfunc = {"K (∑ind/ha) Semai": sum, "K (∑ind/ha) Pancang":sum, "K (∑ind/ha) Tiang":sum, 
                                   "K (∑ind/ha) Pohon": sum, "F Semai": sum, "F Pancang":sum, "F Tiang":sum, 
                                   "F Pohon":sum, "D Semai":sum, "D Pancang":sum, "D Tiang":sum, "D Pohon":sum})
        flora_5 =flora_5.reset_index()

        #menghitung KR, FR, DR, INP, Pi, LnPi, dan H'
        flora_6 = pd.merge(left=flora_4, right=flora_5, how='inner', on=['Tahun Assessment', "Provinsi","Kabupaten",
                                                                         "Perusahaan",'Detail Lokasi'])

        flora_6['KR Semai'] = flora_6['K (∑ind/ha) Semai_x']/flora_6['K (∑ind/ha) Semai_y']*100
        flora_6['KR Pancang'] = flora_6['K (∑ind/ha) Pancang_x']/flora_6['K (∑ind/ha) Pancang_y']*100
        flora_6['KR Tiang'] = flora_6['K (∑ind/ha) Tiang_x']/flora_6['K (∑ind/ha) Tiang_y']*100
        flora_6['KR Pohon'] = flora_6['K (∑ind/ha) Pohon_x']/flora_6['K (∑ind/ha) Pohon_y']*100

        flora_6['FR Semai'] = flora_6['F Semai_x']/flora_6['F Semai_y']*100
        flora_6['FR Pancang'] = flora_6['F Pancang_x']/flora_6['F Pancang_y']*100
        flora_6['FR Tiang'] = flora_6['F Tiang_x']/flora_6['F Tiang_y']*100
        flora_6['FR Pohon'] = flora_6['F Pohon_x']/flora_6['F Pohon_y']*100

        flora_6['DR Semai'] = flora_6['D Semai_x']*100
        flora_6['DR Pancang'] = flora_6['D Pancang_x']*100
        flora_6['DR Tiang'] = flora_6['D Tiang_x']*100
        flora_6['DR Pohon'] = flora_6['D Pohon_x']*100

        flora_6['INP Semai'] = flora_6['KR Semai']+flora_6['FR Semai']
        flora_6['INP Pancang'] = flora_6['KR Pancang']+flora_6['FR Pancang']
        flora_6['INP Tiang'] = flora_6['KR Tiang']+flora_6['FR Tiang']+flora_6['DR Tiang']
        flora_6['INP Pohon'] = flora_6['KR Pohon']+flora_6['FR Pohon']+flora_6['DR Pohon']

        flora_6['Pi Semai'] = flora_6 ['KR Semai']/100
        flora_6['Pi Pancang'] = flora_6 ['KR Pancang']/100
        flora_6['Pi Tiang'] = flora_6 ['KR Tiang']/100
        flora_6['Pi Pohon'] = flora_6 ['KR Pohon']/100

        flora_6['Ln Pi Semai'] = np.log(flora_6['Pi Semai'])
        flora_6['Ln Pi Pancang'] = np.log(flora_6['Pi Pancang'])
        flora_6['Ln Pi Tiang'] = np.log(flora_6['Pi Tiang'])
        flora_6['Ln Pi Pohon'] = np.log(flora_6['Pi Pohon'])

        flora_6["H' Semai"] = abs(flora_6['Pi Semai']*flora_6['Ln Pi Semai'])
        flora_6["H' Pancang"] = abs(flora_6['Pi Pancang']*flora_6['Ln Pi Pancang'])
        flora_6["H' Tiang"] = abs(flora_6['Pi Tiang']*flora_6['Ln Pi Tiang'])
        flora_6["H' Pohon"] = abs(flora_6['Pi Pohon']*flora_6['Ln Pi Pohon'])

        #mengkategorikan H'    
        flora_7 = flora_6.pivot_table(index = ['Tahun Assessment', "Provinsi","Kabupaten","Perusahaan", 'Detail Lokasi'],
                        aggfunc = {"H' Semai": sum, "H' Pancang":sum, "H' Tiang": sum, "H' Pohon": sum})

        flora_8 = flora_7.reset_index()
        flora_8 = pd.melt(flora_8, id_vars=['Tahun Assessment', "Provinsi","Kabupaten","Perusahaan",'Detail Lokasi'], 
                          value_vars=["H' Semai", "H' Pancang", "H' Tiang", "H' Pohon"], var_name="Kelas Vegetasi")
        flora_8.rename({'value': "Nilai H'"}, axis=1, inplace=True)

        conditions = [
            (flora_8["Nilai H'"] > 3.5),
            (flora_8["Nilai H'"] > 2.5),
            (flora_8["Nilai H'"] > 1.5),
            (flora_8["Nilai H'"] > 1),
            (flora_8["Nilai H'"] <= 1)]

        values = ["SANGAT TINGGI", "TINGGI", "SEDANG", "RENDAH", "SANGAT RENDAH"]

        flora_8["Kategori H'"] = np.select(conditions, values)

        flora_8["Kelas Vegetasi"] = flora_8["Kelas Vegetasi"].apply(lambda x: x.split("H' ")[1]).astype("object")
        flora_8["Nilai H'"] = round(flora_8["Nilai H'"], 2)

        #mengambil INP
        inp= flora_6[['Tahun Assessment', "Provinsi","Kabupaten","Perusahaan",'Detail Lokasi', "Nama Latin", "INP Semai", 
                  "INP Pancang", "INP Tiang", "INP Pohon"]]
        inp= pd.melt(inp, id_vars=['Tahun Assessment', "Provinsi","Kabupaten","Perusahaan",'Detail Lokasi', "Nama Latin"], 
                     value_vars=["INP Semai", "INP Pancang", "INP Tiang", "INP Pohon"], var_name="Kelas Vegetasi")
        inp.rename({'value': "INP"}, axis=1, inplace=True)

        inp["Kelas Vegetasi"] = inp["Kelas Vegetasi"].apply(lambda x: x.split("INP ")[1]).astype("object")
        inp["INP"] = round(inp["INP"], 2)
        inp = inp.dropna(axis=0, how="any")

        inp=inp.set_index(['Tahun Assessment', "Provinsi","Kabupaten","Perusahaan",'Detail Lokasi', "Nama Latin"])
        inp=inp.reset_index()
        
        st.subheader("2. Indeks Keragaman (H')")
        st.write("**Filter**")
        
        with st.expander('Filter Tabel Hasilmu Di Sini',expanded=False):
            col1,col2 = st.columns(2)
            with col1:
                tahun = flora_8["Tahun Assessment"].unique().tolist()
                tahun_choice = st.multiselect("Tahun Assessment", options= tahun, 
                                   default = tahun)
            with col2:    
                provinsi = flora_8["Provinsi"].unique().tolist()
                provinsi_choice = st.multiselect('Provinsi', options = provinsi, default = provinsi)
                
            col3,col4 = st.columns(2)
            with col3:
                kabupaten = flora_8["Kabupaten"].unique().tolist()
                kabupaten_choice = st.multiselect('Kabupaten', options =kabupaten, default = kabupaten)
            with col4:    
                perusahaan = flora_8["Perusahaan"].unique().tolist()
                perusahaan_choice = st.multiselect('Perusahaan', options= perusahaan, default = perusahaan)

            lokasi = flora_8["Detail Lokasi"].unique().tolist()
            lokasi_choice = st.multiselect('Detail Lokasi', options= lokasi, default = lokasi)

        # membuat dataframe baru berdasarkan filter
        mask_h = (flora_8["Tahun Assessment"].isin(tahun_choice)) & (flora_8["Provinsi"].isin(provinsi_choice)) & (flora_8["Kabupaten"].isin(kabupaten_choice)) & (flora_8["Perusahaan"].isin(perusahaan_choice)) & (flora_8["Detail Lokasi"].isin(lokasi_choice))
        
        flora_8_selection = flora_8[mask_h]
        
        mask_inp = (inp["Tahun Assessment"].isin(tahun_choice)) & (inp["Provinsi"].isin(provinsi_choice)) & (inp["Kabupaten"].isin(kabupaten_choice)) & (inp["Perusahaan"].isin(perusahaan_choice)) & (inp["Detail Lokasi"].isin(lokasi_choice))

        inp_selection = inp[mask_inp]
        inp_selection.sort_values("INP", ascending=False, inplace=True)

        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output)
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            writer.save()
            processed_data = output.getvalue()
            return processed_data
        flora_8_selection_xlsx = to_excel(flora_8_selection)
        inp_selection_xlsx = to_excel(inp_selection)

        st.markdown("**2.1. Tabel Indeks Keragaman**")
        with st.expander('Tabel Indeks Keragaman',expanded=False):
            st.write(flora_8_selection)
        st.download_button(label="📥 Download Tabel Indeks Keragaman (H')",
                                    data=flora_8_selection_xlsx ,
                                    file_name= "Indeks Keragaman (H').xlsx")
        
        #graphic Indeks Keragaman per lokasi
        
        h_bar = px.bar(flora_8_selection, x="Detail Lokasi", y="Nilai H'", barmode="group",
                       color="Kategori H'", facet_col="Tahun Assessment", facet_row="Perusahaan",
                       width=1000, height=500, title='Indeks Keragaman Menurut Lokasi')
           
        h_line = px.line(flora_8_selection, x="Tahun Assessment", y="Nilai H'",
                         color="Detail Lokasi", title='Indeks Keragaman Setiap Tahun')
        
        #graphic Indeks Keragaman per kelas vegetasi
        h_kelas_vegetasi = (flora_8_selection.groupby(by=["Tahun Assessment", "Kelas Vegetasi"]).sum()[["Nilai H'"]].sort_values(by="Tahun Assessment"))
        h_kelas_vegetasi = h_kelas_vegetasi.reset_index()
        h_kelas_vegetasi_line = px.line(h_kelas_vegetasi, x="Tahun Assessment", y="Nilai H'",
                                               color="Kelas Vegetasi", 
                                               title='Indeks Keragaman Per Tahun Per Kelas Vegetasi')
                              
        st.markdown('**2.2. Grafik Indeks Keragaman Per Lokasi**')
        with st.expander('Grafik Indeks Keragaman Per Lokasi',expanded=False):
            st.write(h_bar)
            st.write(h_line)
            st.write(h_kelas_vegetasi_line)
        
        st.subheader("3. Indeks Nilai Penting")
        st.markdown("**3.1. Tabel Indeks Nilai Penting**")

        with st.expander('Tabel Indeks Nilai Penting',expanded=False):
            st.write(inp_selection[:40])
        st.download_button(label="📥 Download Tabel Indeks Nilai Penting",
                                    data=inp_selection_xlsx ,
                                    file_name= "Indeks Nilai Penting.xlsx")
        
        #graphic Indeks Nilai Penting
        inp_graph = (inp_selection[:40].groupby(by=["Tahun Assessment", "Kelas Vegetasi", "Nama Latin"]).sum()[["INP"]].sort_values(by="INP"))
        inp_graph = inp_graph.reset_index()
        bar_inp = px.bar(inp_graph, x="Nama Latin", y="INP", barmode="group", 
                         facet_row="Tahun Assessment", facet_col="Kelas Vegetasi",
                         category_orders={"Kelas Vegetasi": ["Semai", "Pancang", "Tiang", "Pohon"]},
                         width=1000, height=500,
                         title='Indeks Nilai Penting Per Kelas Vegetasi')
        
        st.markdown('**3.2. Grafik Indeks Nilai Penting**')
        with st.expander('Grafik Indeks Nilai Penting',expanded=False):
            st.write(bar_inp)
            
    else:
        st.info('Menunggu berkasmu diupload.')
