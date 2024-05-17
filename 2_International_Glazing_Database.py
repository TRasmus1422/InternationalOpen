'''
Created on 15. maj 2024

@author: rn
'''


import streamlit as st
import requests
import plotly.graph_objs as go

def InternationLibary(api_token, headers):
    st.set_page_config(
        layout= "wide",
        page_title="International Glazing Database",
        page_icon=":book:",
    )
    
    st.title("Find Glazing in the International Glazing Database")
    
    searchDict = {
        "manufacture": "manufacturer_name",
        "glazingName": "name"
    }

    manufacturers = ["Saint-Gobain Glass", "Pilkington", "Glas Trosch AG", "AGC Glass Europe"]
    APImanu = ["Saint-Gobain%20Glass", "Pilkington", "Glas%20Tr%C3%B6sch%20AG", "AGC%20Glass%20Europe"]

    # Add a Reset button
    if st.button("Push to Reset", use_container_width=True, key="ResetButton"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

    if "results" not in st.session_state:
        st.session_state.results = None
    if "glass_info" not in st.session_state:
        st.session_state.glass_info = None
    if "searchword" not in st.session_state:
        st.session_state.searchword = ""

    col1, col2 = st.columns(2)

    with col1:
        manufacturer = st.selectbox("Select Manufacturer:", manufacturers, key="manufacturer1")

    with col2:
        st.markdown("<div style='width: 1px; height: 28px'></div>", unsafe_allow_html=True)
        if st.button(label="Find Glazings",use_container_width=True):
            index = manufacturers.index(manufacturer)
            manufacture_choosen = APImanu[index]
            url = f"https://igsdb.lbl.gov/api/v1/products/?{searchDict['manufacture']}={manufacture_choosen}"
            response = requests.get(url, headers=headers)
            st.session_state.manufacturer = manufacture_choosen
            st.session_state.results = response.json()
            st.session_state.glass_info = None  # Reset glass info when manufacturer changes

    if st.session_state.results is not None:
        col1, col2 = st.columns(2)

        with col1:
            emptyList = [res["name"] for res in st.session_state.results]

            glass = st.selectbox("Select Glass:", ["None"] + emptyList, key="glass1")

            if glass != "None":
                index = emptyList.index(glass)
                choosen_glass = st.session_state.results[index]
                url_single_product = "https://igsdb.lbl.gov/api/v1/products/{id}"
                response_glass = requests.get(url_single_product.format(id=choosen_glass["product_id"]), headers=headers)
                st.session_state.glass_info = response_glass.json()

        with col2:
            st.session_state.searchword = st.text_input(label="Search for glazing", placeholder=None, value=st.session_state.searchword)

            if st.session_state.searchword:
                url = f"https://igsdb.lbl.gov/api/v1/products/?{searchDict['glazingName']}={st.session_state.searchword}&{searchDict['manufacture']}={st.session_state.manufacturer}"
                response = requests.get(url, headers=headers)
                st.session_state.results = response.json()
                emptyList = [res["name"] for res in st.session_state.results]

                glass = st.selectbox("Select Glass:", ["None"] + emptyList, key="glass2")

                if glass != "None":
                    index = emptyList.index(glass)
                    choosen_glass = st.session_state.results[index]
                    url_single_product = "https://igsdb.lbl.gov/api/v1/products/{id}"
                    response_glass = requests.get(url_single_product.format(id=choosen_glass["product_id"]), headers=headers)
                    st.session_state.glass_info = response_glass.json()

    if st.session_state.glass_info:
        glassInfo = st.session_state.glass_info
        T = [d["T"] for d in glassInfo["spectral_data"]['spectral_data']]
        Rb = [d["Rb"] for d in glassInfo["spectral_data"]['spectral_data']]
        Rf = [d["Rf"] for d in glassInfo["spectral_data"]['spectral_data']]
        W = [d["wavelength"] for d in glassInfo["spectral_data"]['spectral_data']]

        # Define a session state variable to store the toggle state
        if "show_full_data" not in st.session_state:
            st.session_state.show_full_data = False
        
        # Create a button to toggle between full and truncated datasets
        if st.button("Show Full Data Set"):
            st.session_state.show_full_data = not st.session_state.show_full_data
        
        # Create the Plotly figure based on the toggle state
        fig = create_figure(W, T, Rf, Rb, st.session_state.show_full_data,glassInfo)
        
        # Display the Plotly figure using Streamlit
        st.plotly_chart(fig, use_container_width=True)
    
        col1, col2, col3, col4 = st.columns(4)
        
        md = glassInfo["measured_data"]
        irs = glassInfo["integrated_results_summary"][0]
        
        with col1:
            st.markdown("**Glazing Information**")
            st.write('Name')
            st.write("Manufacturer")
            st.write("Conductivity")
            st.write("Coated Side")
            st.write("Coating Nam")
            st.write("Subtype")
            st.write("Thickness (mm)")
            st.write("Emissivity front")
            st.write("Emissivity back ")
        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write(glassInfo["name"])
            st.write(glassInfo["manufacturer_name"])
            st.write(md["conductivity"])
            st.write(glassInfo["coated_side"])
            st.write(glassInfo["coating_name"])
            st.write(glassInfo["subtype"])
            st.write(md["thickness"])
            st.write(md["emissivity_front"])
            st.write(md["emissivity_back"])
        with col3:
            st.markdown("**Glazing Propeties**")
            st.write("Tf Sol")
            st.write("Rf Sol")
            st.write("Rb Sol")
            st.write("Tf Vis")
            st.write("Rf Vis")
            st.write("Rb Vis")
            st.write("TUV")
            
            st.write("Front Transmitted Color ")
            st.write("TCIEX")
            st.write("TCIEY")
            st.write("TCIEZ")
            
            st.write("Front Reflected Color ")
            st.write("RFCIEX")
            st.write("RFCIEY")
            st.write("RFCIEZ")
        with col4:
            st.write("")
            st.write("")
            st.write(irs["tfsol"])
            st.write(irs["rfsol"])
            st.write(irs["rbsol"])
            st.write(irs["tfvis"])
            st.write(irs["rfvis"])
            st.write(irs["rbvis"])
            st.write(irs["tuv"])
            
            st.write(" ")
            st.write(" ")
            st.write(" ")
            st.write(irs["tciex"])
            st.write(irs["tciey"])
            st.write(irs["tciez"])
            
            st.write(" ")
            st.write(" ")
            st.write(" ")
            st.write(irs["rfciex"])
            st.write(irs["rfciey"])
            st.write(irs["rfciez"])

        return glassInfo
    
def create_figure(W, T, Rf, Rb, full_data,glassInfo):
    fig = go.Figure()

    # Determine the range of data based on the toggle state
    data_range = slice(None) if full_data else slice(0, 92)
    WW = [w * 1000 for w in W[data_range]]

    # Add the three curves to the figure
    fig.add_trace(go.Scatter(x=WW, y=T[data_range], mode='lines', name='T'))
    fig.add_trace(go.Scatter(x=WW, y=Rf[data_range], mode='lines', name='Rf'))
    fig.add_trace(go.Scatter(x=WW, y=Rb[data_range], mode='lines', name='Rb'))

    # Set plot layout
    fig.update_layout(title=glassInfo["name"],
                      xaxis_title='Wavelength',
                      yaxis_title='Value')

    return fig


if __name__ == "__main__":
    api_token = 'fa46434f489400ef7e671211f00250838305f04e'
    headers = {"Authorization": f"Token {api_token}"}
    InternationLibary(api_token, headers)



