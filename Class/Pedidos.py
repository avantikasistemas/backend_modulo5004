from Utils.tools import Tools, CustomException
from Utils.querys import Querys

class Pedidos:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)

    # Función para consultar un pedido
    def consultar_pedido(self, data: dict):
        """ Api que realiza la consulta del pedido. """

        # Asignamos nuestros datos de entrada a sus respectivas variables
        numero_pedido = data["numero_pedido"]

        try:
            # Consultamos el activo en la base de datos
            datos = self.querys.consultar_pedido(numero_pedido)
            
            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", datos)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función guardar masivo
    def actualizar_registros(self, data: dict):
        """ Api que realiza la consulta de los estados. """
        try:
            # Asignamos los valores a las variables
            numero_pedido = int(data['numero_pedido'])
            registros = data["registros"]
            
            # Validamos que haya datos
            if not registros:
                raise CustomException(
                    "No se encontraron registros para actualizar.")

            # Iteramos y procedemos a actualizar
            for reg in registros:
                self.querys.actualizar_registros(numero_pedido, reg)

            # Retornamos la información.
            return self.tools.output(200, "Proceso exitoso.")

        except CustomException as e:
            print(f"Error al actualizar masivo: {e}")
            raise CustomException(f"{e}")

    # Función para actualizar la fecha individual de un item de un pedido
    def actualizar_registro_individual(self, data: dict):
        """ Api que realiza la consulta de los estados. """
        try:
            # Asignamos los datos a las variables
            numero_pedido = int(data['numero_pedido'])
            registro_detalle = data["registro_detalle"]
            
            # Validamos que el item tenga información
            if not registro_detalle:
                raise CustomException('No hay registro a actualizar.')
            
            # Procedemos a actualizar
            self.querys.actualizar_registros(
                numero_pedido, registro_detalle)

            # Retornamos la información.
            return self.tools.output(200, "Proceso exitoso.")

        except CustomException as e:
            print(f"Error al actualizar masivo: {e}")
            raise CustomException(f"{e}")

    # Función para consultar un pedido cabecera
    def consultar_pedido_cabecera(self, data: dict):
        """ Api que realiza la consulta del pedido. """

        # Asignamos nuestros datos de entrada a sus respectivas variables
        numero_pedido = data["numero_pedido"]

        try:
            # Consultamos el pedido en la base de datos
            pedido = self.querys.consultar_pedido_cabecera(numero_pedido)

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", pedido)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función guardar masivo
    def actualizar_documento(self, data: dict):
        """ Api que realiza la consulta de los estados. """
        try:
            # Asignamos los valores a las variables
            numero_pedido = int(data['numero_pedido'])
            adicional = data["adicional"]
            documento = data["documento"]
            direccion = data["direccion"]

            if not adicional and not documento and (not direccion and direccion != 0):
                raise CustomException(
                    "Debe llenar al menos un campo para actualizar.")

            # Iteramos y procedemos a actualizar
            self.querys.actualizar_documento(numero_pedido, adicional, documento, direccion)

            # Retornamos la información.
            return self.tools.output(200, "Proceso exitoso.")

        except CustomException as e:
            print(f"Error al actualizar masivo: {e}")
            raise CustomException(f"{e}")

    # Función para remisión factura
    def consultar_remision_factura(self, data: dict):
        """ Api que realiza la consulta de remision y factura. """

        # Asignamos nuestros datos de entrada a sus respectivas variables
        numero_pedido = data["numero_pedido"]

        try:
            # Consultamos el pedido en la base de datos
            pedido = self.querys.consultar_remision_factura(numero_pedido)

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", pedido)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para adicionar pedido oc
    def adicionar_pedido_oc(self, data: dict):
        """ Api que realiza la adición de un pedido OC. """

        # Asignamos nuestros datos de entrada a sus respectivas variables
        numero_pedido = data["numero_pedido"]
        nuevo_pedido = data["nuevo_pedido"]
        
        # Validamos que se hayan enviado los datos
        if not numero_pedido and not nuevo_pedido:
            raise CustomException(
                "Debe llenar ambos campos.")

        try:
            # Consultamos el pedido en la base de datos
            pedido = self.querys.adicionar_pedido_oc(numero_pedido, nuevo_pedido)

            # Retornamos la información.
            return self.tools.output(200, "Adición ejecutada con éxito.", pedido)

        except CustomException as e:
            raise CustomException(f"{e}")
