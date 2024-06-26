import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import mysql.connector
import base64

# get the information from image to text
def image_to_text(path):
    input_image=Image.open(path)

    #converting image data into array
    image_array=np.array(input_image)

    Reader=easyocr.Reader(['en'])
    text=Reader.readtext(image_array,detail=0)

    return text, input_image


# extract the text from the image
def extract_text(text):

    extracted_dict={"NAME":[],"DESIGNATION":[],"CONTACT":[],"EMAIL":[],"WEBSITE":[],"ADDRESS":[],"COMPANY_NAME":[],"PINCODE":[]}

    extracted_dict["NAME"].append(text[0])
    extracted_dict["DESIGNATION"].append(text[1])

    for i in range(2,len(text)):
        if text[i].startswith("+") or (text[i].replace("-","").isdigit() and "-" in text[i]):
            extracted_dict["CONTACT"].append(text[i])

        elif "@" in text[i] and ".com" in text[i]:
            extracted_dict["EMAIL"].append(text[i])

        elif "WWW" in text[i] or "www" in text[i] or "Www" in text[i] or "wWw" in text[i] or "wwW" in text[i]:
            lower_case=text[i].lower()
            extracted_dict["WEBSITE"].append(lower_case)

        elif "Tamil Nadu" in text[i] or "TamilNadu" in text[i] or text[i].isdigit():
            extracted_dict["PINCODE"].append(text[i])

        elif re.match(r'^[A-Za-z]',text[i]):
            extracted_dict["COMPANY_NAME"].append(text[i])

        else:
            colon_removal=re.sub(r'[,;]','',text[i])
            extracted_dict["ADDRESS"].append(colon_removal)

    for key,value in extracted_dict.items():
        if len(value)>0 :
            concadenate=" ".join(value)
            extracted_dict[key]= [concadenate]

        else:
            value="Not available"
            extracted_dict[key]=[value]
 

    return extracted_dict




st.set_page_config(page_title="My Streamlit App",page_icon=":blue_circle:",layout="wide",initial_sidebar_state="expanded")
st.title("EXTRACT BUSINESS CARD DATA WITH EASYOCR")
select=option_menu(menu_title=None,
                    options=["HOME","UPLOAD & MODIFY","DELETE"],
                    default_index=0,
                    orientation="horizontal",
                    styles={"container":{"padding":"0!important","background-color":"viloet","size":"cover","width":"100%"},
                            "icon":{"color":"viloet","font-size":"20px","font-color":"black"},
                            "nav-link":{"font-size":"20px","text-align":"center","margin":"-2px","--hover-color":"#8000ff"},
                            "nav-link-selected":{"background-color":"#8000ff"}})

if select=="HOME":
    st.image(Image.open(r'C:\Users\rdavi\OneDrive\Desktop\Bizcard analysis\images\1_SNbnIm3UKzi9ndq-xKp8Yg.png'))
    st.write(" ")
    st.header("INTRODUCTION")
    st.write(" ")
    st.write("EasyOCR is a Python computer language Optical Character Recognition (OCR) module that is both flexible and easy to use. OCR technology is useful for a variety of tasks, including data entry automation and image analysis. It enables computers to identify and extract text from photographs or scanned documents.EasyOCR stands out for its dedication to making OCR implementation easier for developers. It’s made to be user-friendly even for people with no background in OCR or computer vision. Multiple language support, pre-trained text detection and identification models, and a focus on speed and efficiency in word recognition inside images are all provided by the library.")
    st.write("")
    st.write(" ")
    st.write(" ")
    st.header("Basic Usage")
    st.write(" ")
    st.subheader("Here’s a simple example of how to use EasyOCR to read an image and extract text:")
    st.write(" ")
    st.write("1.Import EasyOCR and create a reader object. You need to specify the languages you want to use as a list of language codes.")
    st.write("2.Load an image file and perform OCR on it. You can use the readtext method of the reader object to get the text and its coordinates from the image")
    st.write("3.The readtext method returns a list of results, where each result contains information about the recognized text, its bounding box, and the probability of accuracy. You can iterate through the results and access this information")
    st.write(" ")
    st.write(" ")
    st.subheader("for example, using this code for")
    st.image(Image.open(r"C:\Users\rdavi\OneDrive\Desktop\Bizcard analysis\images\1_MJRmxGnSNV6tbMK1Jhl7eg.webp"))
    st.write(" ")
    st.write(" ")
    st.subheader("we get output as:")
    st.image(Image.open(r'C:\Users\rdavi\OneDrive\Desktop\Bizcard analysis\images\1_0yn4NnuOzh-UjJsV2rtn0A.webp'))
    
elif select=="UPLOAD & MODIFY":
    image=st.file_uploader("upload the image",type=["png","jpg","jpeg"])
    if image is not None:
        st.image(image,width=250)
        text_image,input_img=image_to_text(image)
        txt_dict=extract_text(text_image)
        
        if txt_dict:
            st.success("TEXT IS SUCESSFULLY EXTRACTED")
        df=pd.DataFrame(txt_dict)

        # image data to bytes conversion

        img_bytes=io.BytesIO()
        input_img.save(img_bytes,format="PNG")

        img_data=img_bytes.getvalue()

        # dictionary creation

        dt={"IMAGE(bytes)":[img_data]}
        df_1=pd.DataFrame(dt)

        concat=pd.concat([df,df_1],axis=1)
        st.dataframe(concat)

        butt=st.button("SAVE TO SQL")
        if butt:
            connection=mysql.connector.connect(
            host="localhost",
            port='3306',
            username='root',
            password='root',
            database='bizcard_db'
            
            )
            cursor=connection.cursor()
            #create table

            table_query='''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(225),
                                                                    designation varchar(225),
                                                                    contact varchar(225),
                                                                    email varchar(225),
                                                                    website text,
                                                                    address text,
                                                                    company_name varchar(225),
                                                                    pincode varchar(225),
                                                                    bytes longtext)'''

            cursor.execute(table_query)
            connection.commit()

            insert_query='''INSERT INTO bizcard_details(name,designation,contact,email,website,address,company_name,pincode,bytes)
                    Values (%s,%s,%s,%s,%s,%s,%s,%s,%s)''' 

            datas=concat.values.tolist()[0]
            binary_data = datas[-1]  # assuming the binary data is the last element
            encoded_data = base64.b64encode(binary_data).decode('utf-8')
            datas[-1] = encoded_data  # replace the binary data with the encoded string

            cursor.execute(insert_query, datas)
            connection.commit()

            st.success("uploaded sucessfully")

    
    select=st.selectbox("Select the method",["READ","Modify"])
    if select=="READ":
        connection=mysql.connector.connect(
            host="localhost",
            port='3306',
            username='root',
            password='root',
            database='bizcard_db'
            )
        cursor = connection.cursor()

        # Execute a SELECT query
        cursor.execute("SELECT * FROM bizcard_details")

        # Fetch the data
        data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        df_4 = pd.DataFrame(data, columns=['name', 'designation','contact','email','website','address','company_name','pincode','bytes']) 
        st.write(df_4)   
        
    elif select == "Modify":
        connection=mysql.connector.connect(
            host="localhost",
            port='3306',
            username='root',
            password='root',
            database='bizcard_db'
            )
        cursor = connection.cursor()

        # Execute a SELECT query
        cursor.execute("SELECT * FROM bizcard_details")

        # Fetch the data
        data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        df_5 = pd.DataFrame(data, columns=['name', 'designation','contact','email','website','address','company_name','pincode','bytes']) 
        st.write(df_5)
        col1,col2=st.columns(2)
        with col1:

            sel_name=st.selectbox("select the name",df_5['name'])
        df_6=df_5[df_5['name']==sel_name]
        st.write(df_6)
        df_7=df_6.copy()
        

        col1,col2=st.columns(2)
        with col1:
            name_holder=st.text_input('Name',df_6['name'].unique()[0])
            designation_holder=st.text_input('Designation',df_6['designation'].unique()[0])
            contact_holder=st.text_input('Contact',df_6['contact'].unique()[0])
            email_holder=st.text_input('Email',df_6['email'].unique()[0])

            df_7['name']=name_holder
            df_7['designation']=designation_holder
            df_7['contact']=contact_holder
            df_7['email']=email_holder
        with col2:
            website_holder=st.text_input('Website',df_6['website'].unique()[0])
            address_holder=st.text_input('Address',df_6['address'].unique()[0])
            company_name_holder=st.text_input('Company Name',df_6['company_name'].unique()[0])
            pincode_holder=st.text_input('Pincode',df_6['pincode'].unique()[0])
            bytes_holder=st.text_input('Bytes',df_6['bytes'].unique()[0])

            df_7['website']=website_holder
            df_7['address']=address_holder
            df_7['company_name']=company_name_holder
            df_7['pincode']=pincode_holder
            df_7['bytes']=bytes_holder
        
        st.write(df_7)

        col1,col2=st.columns(2)
        with col1:
            button_1=st.button("Modify",use_container_width=True)
        if button_1:
    # Establish a connection to the database
            connection = mysql.connector.connect(
            host="localhost",
            port='3306',
            username='root',
            password='root',
            database='bizcard_db'
            )
            cursor = connection.cursor()

            try:
                # Delete the existing record
                cursor.execute(f"DELETE FROM bizcard_details WHERE name='{sel_name}'")
                connection.commit()

                # Insert a new record
                insert_query = '''INSERT INTO bizcard_details(name, designation, contact, email, website, address, company_name, pincode, bytes)
                                Values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''

                datas = df_7.values.tolist()[0]
                binary_data = datas[-1]  # assuming the binary data is the last element

                # Encode the string to bytes using UTF-8 encoding
                binary_data_bytes = binary_data.encode('utf-8')

                # Encode the bytes using base64
                encoded_data = base64.b64encode(binary_data_bytes).decode('utf-8')

                datas[-1] = encoded_data  # replace the binary data with the encoded string

                cursor.execute(insert_query, datas)
                connection.commit()

                st.success("Modified successfully")
            except mysql.connector.Error as err:
                st.error(f"Error: {err}")
            finally:
                # Close the cursor and connection
                cursor.close()
                connection.close()

            
        
elif select=="DELETE":
    connection=mysql.connector.connect(
    host="localhost",
    port='3306',
    username='root',
    password='root',
    database='bizcard_db'
    
    )
    cursor=connection.cursor()
    col1,col2=st.columns(2)
    with col1:
        select_query="SELECT name FROM bizcard_details"
        cursor.execute(select_query)
        result=cursor.fetchall()
        connection.commit()
        names=[]
        for i in result:
            names.append(i[0])
        name=st.selectbox("Select Name",names)
    with col2:
        select_query=f'''SELECT designation FROM bizcard_details WHERE name="{name}"'''
        cursor.execute(select_query)
        result_1=cursor.fetchall()
        connection.commit()
        designations=[]
        for k in result_1:
            designations.append(k[0])
        designation=st.selectbox("Select designations",options=designations)

    if name and designation:
        col1,col2,col3=st.columns(3)
        with col1:
            pass
        with col2:
            st.write("")
            st.write("")
            st.write("")
            delete=st.button("Delete",use_container_width=True)

            if delete:
                cursor.execute(f'''DELETE FROM bizcard_details WHERE name ={'name'} AND designation={'designation'}''')
                connection.commit()

                st.write("DELETED")
