import streamlit as st
import pandas as pd
from numpy import  array
import VRPSolverEasy as vrpse
from geopy.geocoders import Nominatim

# insstruções gerais sobre a utilização da ferramenta
st.sidebar.image('download.png',use_column_width=True)
st.header('Otimização de rota')
st.subheader('''Este programa tem como objetivo determinar o menor caminho a ser percorrido pela cooperativa enquanto faz a coleta de óleo vegetal usado que posteriormente será utilizado para a produção de biodiesel. ''')

st.subheader('''É considerado que cada ponto de coleta de óleo será percorrido uma única vez e que o local de início e fim do trajeto é a sede da cooperativa, para que o programa seja executado da forma que foi planejado  por favor coloque a sede da cooperativa como o primeiro valor da tabela em excel.''' )

st.subheader('''Para isso é preciso fazer o upload de um arquivo excel contendo uma coluna com o nome do estabelecimento e outra coluna com a latitude e longitude do local. É possível obter a latitude e longitude de um local pelo google maps através de dispositivo Android, computador, IPhone ou IPad seguindo o tutorial: https://support.google.com/maps/answer/18539?hl=pt-BR&co=GENIE.Platform%3DAndroid&oco=0 ''')

st.subheader('''Como exemplo para o ENEGEP será utilizada uma planilha ilustrativa''')


#st.subheader('Faça o upload do arquivo excel:')
#uploaded_file=st.file_uploader('.', type='xlsx')

#if uploaded_file!=None:

df=pd.read_excel(r'Locais (1).xlsx', engine='openpyxl')
df.dropna(inplace=True)

def cid(x):
    return Nominatim(user_agent="geoapiforenegep").reverse(x).raw['address']['city']

df['Cidade']=df['Latitude e Longitude'].apply(cid)
df['Latitude e Longitude'] = df['Latitude e Longitude'].apply(lambda x: tuple(map(float, x.split(', '))))
st.write(df)



if st.button("Calcular Rota"):
    st.subheader('''A distância entre os locais foi obtida com a API do Google Maps e utiliza a distância de carro.''' )
    matriz_locais=pd.read_excel(r'matriz_distancias.xlsx', engine='openpyxl',index_col='Nome do estabelecimento')
    st.write(matriz_locais)

    janela_tempo_fim = 5000000 # Usei uma janela imensa para garantir... apenar de que a solução é apresentada em 314 para a instância de 10 clientes.
    custo_por_dist = 1
    janela_tempo_inicio = 0
    janela_tempo_fim = 5000000 # Usei uma janela imensa para garantir... apenar de que a solução é apresentada em 314 para a instância de 10 clientes.
    numero_pontos = len(df['Nome do estabelecimento'])

    # Map with names and coordinates
    #coordenadas

    # Demands of points
    demandas = [1 for i in range((numero_pontos))]

    # Initialisation
    modelo = vrpse.Model()

    # Add vehicle type
    modelo.add_vehicle_type(
        id = 1,
        start_point_id = 0,
        end_point_id = 0,
        name="Caminhão_1",
        capacity = numero_pontos + 1,
        max_number = 1, # apenas um veículo
        var_cost_dist = custo_por_dist,
        tw_end = janela_tempo_fim)

    # Add depot
    modelo.add_depot(id=0, name = "Sede", tw_begin = janela_tempo_inicio, tw_end = janela_tempo_fim) # Ele pegará a primeira entrada como sede

    coordenadas_nomes = list(df['Nome do estabelecimento'])

    # Add customers
    for i in range(1, numero_pontos):
        modelo.add_customer(
            id=i,
            name= df['Nome do estabelecimento'][i],
            demand = demandas[i],
            tw_begin = janela_tempo_inicio,
            tw_end = janela_tempo_fim)

    # Add links
    #Como a distância de carro de um ponto A a um ponto B não é necessariamente a mesma distância BA o loop ocorre para todos os pontos 
    for i in range(numero_pontos):
        for j in range(numero_pontos):
            if i == j:
                modelo.add_link(
                start_point_id = i,
                end_point_id = j,
                distance = 0,
                time = 0)
                continue
            modelo.add_link(
            start_point_id = i,
            end_point_id = j,
            distance = matriz_locais.loc[df['Nome do estabelecimento'][i],df['Nome do estabelecimento'][j]],
            time = matriz_locais.loc[df['Nome do estabelecimento'][i],df['Nome do estabelecimento'][j]])
            
    #matriz_locais.loc[df['Nome do estabelecimento'][0],df['Nome do estabelecimento'][1]]
    # solve model
    modelo.solve()
    modelo.export()
    #print(modelo.solution.routes)
    var=str(modelo.solution.routes[0])
    # Extract the line containing the number of orders
    order_line = [line for line in var.split('\n') if 'Name' in line][0]
    order_line=order_line[8:]
    # Split the line by ' --> ' and count the number of elements
    number_of_orders = (order_line.split(' --> '))
    df_final_vrpse=pd.DataFrame({'Local' : number_of_orders})
    df_final_vrpse.index.name = 'Ordem'

    st.write(df_final_vrpse)
