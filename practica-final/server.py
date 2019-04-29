import http.server
import http.client
import json
import socketserver

puerto = 8000 # Aqui lanzamos el servidor.

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    ENLACE_OPENFDA = "api.fda.gov"
    JSON_OPENFDA = "/drug/label.json"
    MEDICAMENTO_OPENFDA = '&search=active_ingredient:'
    EMPRESA_OPENFDA = '&search=openfda.manufacturer_name:'


    def pantalla_inicial(self): #Crea un documento html que ve el cliente ya como un formulario.
        pantalla_inicial = 'formulario-openfda.html'
        with open(pantalla_inicial) as f:
            pantalla_inicial = f.read()
        return pantalla_inicial

    def obtener_resultados (self, limit=10): #Conseguimos toda la informacion.
        headers = {'User-Agent': 'http-client'}
        connection = http.client.HTTPSConnection(self.ENLACE_OPENFDA)
        connection.request("GET", self.JSON_OPENFDA + "?limit="+str(limit))
        print (self.JSON_OPENFDA + "?limit="+str(limit))
        r1 = connection.getresponse()
        informacion_codificada = r1.read().decode("utf8")
        info_buena = json.loads(informacion_codificada)
        resultados_obtenidos = info_buena['results']
        return resultados_obtenidos

    def imprime_info_pedida (self, lista):#metodo que crea una pagina en la que aparece el recurso solicitado(cuando clickeas en el formulario se utiliza este

        lista_pedida = """
                                <html>
                                    <head>
                                        <title>Aplicacion de OpenFDA</title>
                                    </head>
                                    <body>
                                        <ul>
                            """
        for elemento in lista:
            lista_pedida += "<li>" + elemento + "</li>"

        lista_pedida += """
                                        </ul>
                                    </body>
                                </html>
                            """
        return lista_pedida

    def do_GET(self):
        lista_info_introducida = self.path.split("?") #separamos el recurso por la interrogacion, para estudiar los parametros.
        if len(lista_info_introducida) > 1:
            parameters = lista_info_introducida[1]
        else:
            parameters = ""

        if parameters:
            limite_parameters = parameters.split("=") #De esta forma, nos quedamos con el valor del limit.
            try:
                if limite_parameters[0] == "limit": #limit esta en la posicion 0.
                    limit = int(limite_parameters[1])
                    if limit > 100:                  #si  es mayor que 100, el limite será 1.
                        limit = 1
            except ValueError: #Si te pasas del limite, el numero que tomara el programa sera el 1.
                limit = 1

        if self.path =='/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = self.pantalla_inicial()
            self.wfile.write(bytes(html, "utf8"))


        elif 'listDrugs' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            list_drugs = []
            resultados_obtenidos = self.obtener_resultados(limit) #llamamos a la funcion para obtener los datos.
            for result in resultados_obtenidos:
                if ('generic_name' in result['openfda']):
                    list_drugs.append (result['openfda']['generic_name'][0])
                else:
                    list_drugs.append('Nombre del medicamento desconocido.')
            html_info = self.imprime_info_pedida (list_drugs) #llamamos al metodo info_pedida para realizar la pagina web.
            self.wfile.write(bytes(html_info, "utf8"))


        elif 'listCompanies' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            list_companies = []
            resultados_obtenidos = self.obtener_resultados (limit)
            for result in resultados_obtenidos:
                if ('manufacturer_name' in result['openfda']):
                    list_companies.append (result['openfda']['manufacturer_name'][0])
                else:
                    list_companies.append('El nombre de la fábrica de medicamentos es desconocido')
            final_html = self.imprime_info_pedida(list_companies)
            self.wfile.write(bytes(final_html, "utf8"))


        elif 'listWarnings' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            list_warnings = []
            resultados_obtenidos = self.obtener_resultados (limit)
            for result in resultados_obtenidos:
                if ('warnings' in result):
                    list_warnings.append (result['warnings'][0])
                else:
                    list_warnings.append('El "WARNING" es desconocido.')
            final_html = self.imprime_info_pedida(list_warnings)
            self.wfile.write(bytes(final_html, "utf8"))


        elif 'searchDrug' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            limit = 10
            drug = self.path.split('=')[1]
            list_drugs = []
            connection = http.client.HTTPSConnection(self.ENLACE_OPENFDA)
            connection.request("GET", self.JSON_OPENFDA + "?limit="+str(limit) + self.MEDICAMENTO_OPENFDA + drug)
            r1 = connection.getresponse()
            info_adquirida = r1.read()
            informacion_codificada = info_adquirida.decode("utf8")
            info_buena = json.loads(informacion_codificada)
            try:
                find_drugs = info_buena['results']
                for result in find_drugs:
                    if ('substance_name' in result['openfda']):
                        list_drugs.append(result['openfda']['generic_name'][0])

                    else:
                        list_drugs.append('El medicamento con ese compuesto es desconocido.')
            except KeyError:
                list_drugs.append('El nombre del compuesto que ha introducido es erroneo, por favor vuelva a la pantalla inicial.')
            final_html = self.imprime_info_pedida(list_drugs)
            self.wfile.write(bytes(final_html, "utf8"))


        elif 'searchCompany' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            limit = 10
            company = self.path.split('=')[1]
            list_companies = []
            connection = http.client.HTTPSConnection(self.ENLACE_OPENFDA)
            connection.request("GET", self.JSON_OPENFDA + "?limit=" + str(limit) + self.EMPRESA_OPENFDA + company)
            r1 = connection.getresponse()
            info_adquirida = r1.read()
            informacion_codificada = info_adquirida.decode("utf8")
            info_buena = json.loads(informacion_codificada)
            try:
                find_company = info_buena['results']
                for result in find_company:
                    if ('manufacturer_name' in result['openfda']):
                        list_companies.append(result['openfda']['manufacturer_name'][0])
                    else:
                        list_companies.append('El nombre de la fábrica de medicamentos que ha introducido es desconocido.')
            except KeyError:
                list_companies.append('El nombre de compania incorrecto, por favor vuelva a la pagina de inicio e introduzca un nombre correcto.')
            final_html = self.imprime_info_pedida(list_companies)
            self.wfile.write(bytes(final_html, "utf8"))

        elif 'secret' in self.path: #Al introducir esta palabra provocamos un error 401.
            self.send_error(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()


        elif 'redirect' in self.path: #Al introducir esta palbra vuelves a la pagina principal.
            self.send_response(302)
            self.send_header('Location', 'http://localhost:'+str(puerto))
            self.end_headers()

        else: # Si el recurso solicitado no se encuentra en el servidor, recibiremos un mensaje de error 404.
            self.send_error(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(". Recurso no encontrado: '{}'.".format(self.path).encode())
        return



socketserver.TCPServer.allow_reuse_address= True


clase_manejadora = testHTTPRequestHandler #Establecemos como manejador nuestra propia clase, llamada Handler (objeto).

nuestro_servidor = socketserver.TCPServer(("", puerto), clase_manejadora)# Configuramos el socket del servidor, esperando conexiones
# de clientes.
print("El servidor está abierto a conexiones en el puerto", puerto)
# Entramos en el bucle principal, atendiendo las peticiones desde nuestro manejador (cada vez que ocurra un 'GET'
# se invocará nuestro método do_GET)
try:
    nuestro_servidor.serve_forever()

except KeyboardInterrupt:
    print("Uste ha decidido parar el servidor con control C.")
exit(1)
