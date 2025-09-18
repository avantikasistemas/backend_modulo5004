from Utils.tools import Tools, CustomException
from sqlalchemy import text
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from Utils.constants import CAMPOS_MONETARIOS

class Querys:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.query_params = dict()

    # Query para obtener la información del activo por código
    def consultar_pedido(self, numero_pedido: int):
        try:
            sql = """ SELECT r.descripcion as nombre_producto, dlp.* 
            FROM documentos_lin_ped dlp
            INNER JOIN referencias r ON r.codigo = dlp.codigo
            WHERE numero = :numero_pedido 
            and sw = 1"""
            result = self.db.execute(text(sql), {"numero_pedido": numero_pedido}).fetchall()
            
            if not result:
                raise CustomException("Número de pedido no encontrado.")
            
            data = [dict(row._mapping) for row in result] if result else []
            if data:
                for row in data:
                    for k, v in row.items():
                        if isinstance(v, date):
                            row[k] = v.strftime('%Y-%m-%d')
                        if isinstance(v, (int, float, Decimal)) and not isinstance(v, bool):
                            # Opción A: formatear solo si es un campo monetario
                            if k.lower() in CAMPOS_MONETARIOS:
                                nuevo_valor = self.tools.formato_peso(v, symbol="$", decimals=0) 
                    if nuevo_valor is not None:
                        row["valor_unitario_formateado"] = nuevo_valor
                        
            sql2 = """
                SELECT t.nombres, dp.* 
                FROM documentos_ped dp
                INNER JOIN terceros t ON t.nit = dp.nit
                WHERE dp.numero = :numero_pedido AND dp.sw = 1;
            """
            response = self.db.execute(text(sql2), {"numero_pedido": numero_pedido}).fetchone()
            
            if not response:
                raise CustomException("Número de pedido no encontrado.")

            sql2_response = dict(response._mapping) if response else {}
            
            final_response = {"cabecera": sql2_response, "registros": data}
            return final_response

        except CustomException as e:
                raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para guardar masivo
    def actualizar_registros(self, numero_pedido: int, registro: dict):
        try:
            sql = """
                UPDATE documentos_lin_ped 
                SET valor_unitario = :nuevo_valor_unitario, cantidad = :nueva_cantidad
                WHERE id = :id AND numero = :numero_pedido 
                AND sw = 1 AND seq = :seq AND codigo = :codigo
            """
            self.db.execute(
                text(sql), 
                {
                    "nuevo_valor_unitario": registro["nuevo_valor_unitario"] if registro["nuevo_valor_unitario"] != '' else registro['valor_unitario'], 
                    "nueva_cantidad": registro["nueva_cantidad"] if registro["nueva_cantidad"] != '' else registro['cantidad'], 
                    "id": registro["id"], 
                    "numero_pedido": numero_pedido, 
                    "seq": registro["seq"],
                    "codigo": registro["codigo"],
                }
            )
            self.db.commit()
            return True
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para consultar pedido cabecera
    def consultar_pedido_cabecera(self, numero_pedido: int):
        try:
            sql = """
                SELECT t.nombres, tt.nombres AS vendedor_nombre,
                CASE 
                    WHEN dp.codigo_direccion IS NULL OR dp.codigo_direccion = 0
                        THEN CONCAT(LTRIM(RTRIM(COALESCE(t.direccion, ''))), ' ', LTRIM(RTRIM(COALESCE(t.contacto_1, ''))))
                    ELSE
                        CONCAT(LTRIM(RTRIM(COALESCE(td.direccion, ''))), ' ', LTRIM(RTRIM(COALESCE(td.notas, ''))))
                END AS direccion, dp.*
                FROM documentos_ped AS dp
                INNER JOIN terceros       AS t  ON t.nit  = dp.nit
                INNER JOIN terceros       AS tt ON tt.nit = dp.vendedor
                LEFT  JOIN terceros_dir   AS td ON td.nit = dp.nit 
                AND td.codigo_direccion = dp.codigo_direccion
                WHERE dp.numero = :numero_pedido
                AND dp.sw = 1;
            """
            result = self.db.execute(text(sql), {
                "numero_pedido": numero_pedido
            }).fetchone()
            
            if not result:
                raise CustomException("Número de pedido no encontrado.")
            
            row = dict(result._mapping)
            
            for k, v in row.items():
                if isinstance(v, date):
                    row[k] = v.strftime('%Y-%m-%d')
                if isinstance(v, (int, float, Decimal)) and not isinstance(v, bool):
                    # Opción A: formatear solo si es un campo monetario
                    if k.lower() in CAMPOS_MONETARIOS:
                        row[k] = self.tools.formato_peso(v, symbol="$", decimals=0)
                        
            direcciones = list()
            
            nit = row["nit"]
                        
            sql2 = """
                SELECT direccion, contacto_1 FROM terceros WHERE nit = :nit
            """
            result2 = self.db.execute(text(sql2), {"nit": nit}).fetchone()
            if result2:
                direcciones.append({"codigo_direccion": 0, "direccion": f"{result2.direccion} {result2.contacto_1}"})
                
            sql3 = """
                SELECT codigo_direccion, direccion, notas FROM terceros_dir WHERE nit = :nit;
            """
            result3 = self.db.execute(text(sql3), {"nit": nit}).fetchall()
            if result3:
                direcciones.extend([{"codigo_direccion": row.codigo_direccion, "direccion": f"{row.direccion} {row.notas}"} for row in result3])

            row["direcciones"] = direcciones

            return row

        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para actualizar documento
    def actualizar_documento(self, numero_pedido: int, adicional: str, 
                             documento: str, direccion: str):
        try:
            # Lógica dinámica para el UPDATE con adicional, documento y direccion (codigo_direccion)
            campos = []
            params = {"numero_pedido": numero_pedido}
            if adicional:
                campos.append("adicional = :adicional")
                params["adicional"] = adicional
            if documento:
                campos.append("documento = :nuevo_documento")
                params["nuevo_documento"] = documento
            if direccion or direccion == 0:
                campos.append("codigo_direccion = :codigo_direccion")
                params["codigo_direccion"] = direccion
            if not campos:
                # No hay nada que actualizar
                return False
            sql = f"""
                UPDATE documentos_ped 
                SET {', '.join(campos)}
                WHERE numero = :numero_pedido 
                AND sw = 1
            """
            self.db.execute(text(sql), params)
            self.db.commit()
            return True
        except CustomException as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para consultar remisión y factura asociada a un pedido
    def consultar_remision_factura(self, numero_pedido: int):
        try:
            sql = """
                SELECT pedido,codigo,
                (SELECT descripcion FROM referencias WHERE codigo=documentos_lin.codigo) AS Descripcion,
                cantidad,
                tipo,numero,fec,
                (SELECT TOP 1 nombres FROM terceros WHERE nit=documentos_lin.nit) AS Cliente, 
                (SELECT TOP 1 d.numero FROM documentos_lin d WHERE d.tipo_link=documentos_lin.tipo AND d.numero_link=documentos_lin.numero AND d.codigo=documentos_lin.codigo AND d.sw in ('1','12')) AS NumeroDocumento,
                (SELECT TOP 1 d.tipo FROM documentos_lin d WHERE d.tipo_link=documentos_lin.tipo AND d.numero_link=documentos_lin.numero AND d.codigo=documentos_lin.codigo AND d.sw in ('1','12')) AS TipoDocumento,
                documentos_lin.valor_unitario
                FROM documentos_lin WHERE pedido IN (:numero_pedido) AND sw IN ('12','11') 
                ORDER BY pedido,numero
            """
            result = self.db.execute(text(sql), {
                "numero_pedido": numero_pedido
            }).fetchall()
            
            if not result:
                raise CustomException("No hay información para este pedido.")

            rows = [dict(row._mapping) for row in result] if result else []
            for row in rows:
                for k, v in row.items():
                    if isinstance(v, date):
                        row[k] = v.strftime('%Y-%m-%d')
                    if isinstance(v, (int, float, Decimal)) and not isinstance(v, bool):
                        # Opción A: formatear solo si es un campo monetario
                        if k.lower() in CAMPOS_MONETARIOS:
                            row[k] = self.tools.formato_peso(v, symbol="$", decimals=0)
            return rows

        except Exception as e:
            print(f"Error al consultar remisión y factura: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para adicionar pedido OC
    def adicionar_pedido_oc(self, pedidobuscar: int, pedidoincluir: int) -> int:
        try:
            sql = text("""
                SET NOCOUNT ON;
                DECLARE @return_value INT;

                EXEC @return_value = dbo.adicionar_pedido_OC
                    @pedidobuscar = :pedidobuscar,
                    @pedidoincluir = :pedidoincluir;

                SELECT CAST(@return_value AS INT) AS return_value;
            """)

            res = self.db.execute(sql, {
                "pedidobuscar": pedidobuscar,
                "pedidoincluir": pedidoincluir,
            })

            # Toma el valor devuelto por el SELECT final
            ret = res.scalar()
            self.db.commit()
            return int(ret) if ret is not None else None

        except Exception as ex:
            self.db.rollback()
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para consultar valores extras asociados a un pedido
    def consultar_valores_extras(self, numero_pedido: int):
        try:
            sql = """
                SELECT * 
                FROM documentos_ped 
                WHERE numero = :numero_pedido AND sw = 1;
            """
            result = self.db.execute(text(sql), {
                "numero_pedido": numero_pedido
            }).fetchone()
            
            response = dict(result._mapping) if result else None

            for k, v in response.items():
                if isinstance(v, date):
                    response[k] = v.strftime('%Y-%m-%d')
                if isinstance(v, (int, float, Decimal)) and not isinstance(v, bool):
                    # Opción A: formatear solo si es un campo monetario
                    if k.lower() in CAMPOS_MONETARIOS:
                        response[k] = self.tools.formato_peso(v, symbol="$", decimals=0)
                        
            return response

        except Exception as e:
            print(f"Error al consultar valores extras: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()
