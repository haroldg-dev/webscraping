from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from os import path
import requests, json, time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

@csrf_exempt
def get_webscraping(request):
    if request.method == 'GET':
        try:
            script()
            return JsonResponse({'status': 200})
        except Exception as error:
            print(error)
            return JsonResponse({'status': 400,
                                 'error': error})
    else:
        return JsonResponse({'status': 400})
    
def script():
    i = 0

    while i < 1:
        #url = 'https://www.vega.pe/cuidado-personal-y-salud?page='+str(i)
        #print(url)
        headers = {
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'accept': '*/*',
            'content-type': 'application/json',
            'Referer': 'https://www.vega.pe/cuidado-personal-y-salud?page=5',
            'sec-ch-ua-mobile': '?1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
            'sec-ch-ua-platform': '"Android"',
        }

        params = {
            'workspace': 'master',
            'maxAge': 'short',
            'appsEtag': 'remove',
            'domain': 'store',
            'locale': 'es-PE',
            'operationName': 'productSearchV3',
            'variables': '{}',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"40e207fe75d9dce4dfb3154442da4615f2b097b53887a0ae5449eb92d42e84db","sender":"vtex.store-resources@0.x","provider":"vtex.search-graphql@0.x"},"variables":"eyJoaWRlVW5hdmFpbGFibGVJdGVtcyI6ZmFsc2UsInNrdXNGaWx0ZXIiOiJBTEwiLCJzaW11bGF0aW9uQmVoYXZpb3IiOiJkZWZhdWx0IiwiaW5zdGFsbG1lbnRDcml0ZXJpYSI6Ik1BWF9XSVRIT1VUX0lOVEVSRVNUIiwicHJvZHVjdE9yaWdpblZ0ZXgiOmZhbHNlLCJtYXAiOiJjIiwicXVlcnkiOiJjdWlkYWRvLXBlcnNvbmFsLXktc2FsdWQiLCJvcmRlckJ5IjoiT3JkZXJCeVNjb3JlREVTQyIsImZyb20iOjQwLCJ0byI6NDksInNlbGVjdGVkRmFjZXRzIjpbeyJrZXkiOiJjIiwidmFsdWUiOiJjdWlkYWRvLXBlcnNvbmFsLXktc2FsdWQifV0sIm9wZXJhdG9yIjoiYW5kIiwiZnV6enkiOiIwIiwic2VhcmNoU3RhdGUiOm51bGwsImZhY2V0c0JlaGF2aW9yIjoiU3RhdGljIiwiY2F0ZWdvcnlUcmVlQmVoYXZpb3IiOiJkZWZhdWx0Iiwid2l0aEZhY2V0cyI6ZmFsc2V9"}',
        }

        aux = requests.get('https://www.vega.pe/_v/segment/graphql/v1', params=params, headers=headers)
        response = json.loads(aux.text)

        for product in response['data']['productSearch']['products']:
            save_data(product)

        i = i + 1
    send_email("Te escribo desde mi api")

def save_data(product):

    productName = product['productName']
    description = product['description'].replace('\n', ' ')
    brand = product['brand']
    sellingPrice = product['priceRange']['sellingPrice']['highPrice']
    listPrice = product['priceRange']['listPrice']['highPrice']
    caracteristicas = product['properties'][0]['values'][0]
    if len(product['properties']) > 3:
        contenidoNeto = product['properties'][1]['values'][0]
        tipodeProducto = product['properties'][2]['values'][0]
        undporPaquete = product['properties'][3]['values'][0]
    else:
        contenidoNeto = "None"
        tipodeProducto = "None"
        undporPaquete = "None"
    imagen = product['items'][0]['images'][0]['imageUrl'] 
    seller = product['items'][0]['sellers'][0]['sellerName']
    
    reporte = "./reporteVega.csv"
    linea = productName + ";" + description + ";" + brand + ";" + str(sellingPrice) + ";" + str(listPrice) + ";" + caracteristicas + ";" + str(contenidoNeto) + ";" + tipodeProducto + ";" + undporPaquete + ";" + seller + ";" + imagen + "\n"
    # validamos si existe el archivo de reporte
    if(path.exists(reporte)):
        f = open(reporte, "a")
        f.write(linea)
        f.close()
    else :
        f = open(reporte, "a")
        f.write("productName;description;brand;sellingPrice;listPrice;caracteristicas;contenidoNeto;tipodeProducto;undporPaquete;seller;imagen\n")
        f.write(linea)
        f.close()
    #print(linea)


def send_email(mensajeAux):
    fromaddr = "tabitasrules@gmail.com"
    toaddr = "tabitasrules@gmail.com"
    # instance of MIMEMultipart
    msg = MIMEMultipart()
    # storing the senders email address  
    msg['From'] = fromaddr
    # storing the receivers email address 
    msg['To'] = toaddr
    # storing the subject 
    msg['Subject'] = "Subject of the Mail"
    # string to store the body of the mail
    body = mensajeAux
    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    # open the file to be sent 
    filename = "reporteVega.csv"
    attachment = open("C:\\Users\\Ausoin\\Desktop\\webscraping\\clase3\\serviceone\\reporteVega.csv", "rb")
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
    # To change the payload into encoded form
    p.set_payload((attachment).read())
    # encode into base64
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    # attach the instance 'p' to instance 'msg'
    msg.attach(p)
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    s.starttls()
    # Authentication
    s.login("tabitasrules@gmail.com", "yqzbqabhbushekmw")
    # message to be sent
    message = msg.as_string()
    # sending the mail
    s.sendmail("tabitasrules@gmail.com", "tabitasrules@gmail.com", message)
    # terminating the session
    s.quit()