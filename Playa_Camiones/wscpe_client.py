# Consulta de Cartas de Porte Electrónicas - Integración WSCPE ARCA
# Módulo para consultar CPE usando token y sign obtenidos

import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import base64
import logging
from typing import Dict, Any, Optional
from zeep import Client, wsse
from zeep.transports import Transport
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class WSCPEClient:
    """
    Cliente para consultas de Cartas de Porte Electrónicas via ARCA.
    Utiliza token y sign para autenticación con webservice wscpe.
    """
    
    def __init__(self):
        self.base_url = os.getenv('ARCA_CPE_WSAA_URL', 'https://wsaa.afip.gov.ar/ws/services/LoginCms')
        self.wscpe_url = "https://cpea-ws.afip.gob.ar/wscpe/services/soap"  # URL real de WSCPE
        self.cuit_solicitante = os.getenv('ARCA_CUIT_SOLICITANTE', '33693450239')
        
    def create_cpe_query_xml(self, token: str, sign: str, cuit_representada: str, nro_ctg: str) -> str:
        """
        Crea el XML para consultar una carta de porte electrónica específica.
        Formato correcto para WSCPE según ejemplo proporcionado.
        
        Args:
            token: Token de autenticación ARCA (base64)
            sign: Firma digital ARCA  
            cuit_representada: CUIT de la empresa representada
            nro_ctg: Número de CTG (Código de Transporte de Granos)
            
        Returns:
            XML formateado para envío al webservice WSCPE
        """
        
        # Crear elemento raíz con namespaces correctos
        envelope = ET.Element("soapenv:Envelope")
        envelope.set("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
        envelope.set("xmlns:wsc", "https://serviciosjava.afip.gob.ar/wscpe/")
        
        # Header vacío
        header = ET.SubElement(envelope, "soapenv:Header")
        
        # Body con request correcto
        body = ET.SubElement(envelope, "soapenv:Body")
        consultar_req = ET.SubElement(body, "wsc:ConsultarCPEAutomotorReq")
        
        # Auth con estructura correcta
        auth = ET.SubElement(consultar_req, "auth")
        
        token_elem = ET.SubElement(auth, "token")
        token_elem.text = token
        
        sign_elem = ET.SubElement(auth, "sign")
        sign_elem.text = sign
        
        cuit_elem = ET.SubElement(auth, "cuitRepresentada")
        cuit_elem.text = cuit_representada
        
        # Solicitud con nroCTG
        solicitud = ET.SubElement(consultar_req, "solicitud")
        nro_ctg_elem = ET.SubElement(solicitud, "nroCTG")
        nro_ctg_elem.text = nro_ctg
        
        # Convertir a string XML
        xml_string = ET.tostring(envelope, encoding='unicode')
        
        # Formatear para legibilidad
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(xml_string)
        return dom.toprettyxml(indent="   ")

    async def consultar_carta_porte(self, token: str, sign: str, cuit_representada: str, nro_ctg: str) -> Dict[str, Any]:
        """
        Consulta una carta de porte electrónica específica usando WSCPE.
        
        Args:
            token: Token de autenticación ARCA (base64)
            sign: Firma digital ARCA
            cuit_representada: CUIT de la empresa representada
            nro_ctg: Número de CTG (Código de Transporte de Granos)
            
        Returns:
            Diccionario con datos de la carta de porte o error
        """
        
        try:
            logger.info(f"Consultando CTG: {nro_ctg} para CUIT: {cuit_representada}")
            
            # Crear XML de consulta con formato correcto
            xml_request = self.create_cpe_query_xml(token, sign, cuit_representada, nro_ctg)
            
            # Headers para SOAP
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': 'https://serviciosjava.afip.gob.ar/wscpe/ConsultarCPEAutomotor',
                'User-Agent': 'LogiGrain-Terminal-Portuaria/1.0'
            }
            
            # Realizar request al webservice
            logger.info(f"Enviando request a WSCPE: {self.wscpe_url}")
            
            # TODO: Descomentar cuando tengas acceso real al webservice
            # response = requests.post(
            #     self.wscpe_url,
            #     data=xml_request,
            #     headers=headers,
            #     timeout=30
            # )
            
            # Por ahora simulamos respuesta exitosa
            response_simulada = {
                "nro_ctg": nro_ctg,
                "cuit_representada": cuit_representada,
                "estado": "VIGENTE", 
                "fecha_emision": "2025-12-26T10:00:00",
                "cuit_origen": "20123456789",
                "cuit_destino": "20987654321",
                "cereal": "TRIGO",
                "peso_declarado": 25000.50,
                "patente": "ABC123",
                "chofer_cuit": "20111222333",
                "empresa_transporte": "Transportes del Litoral SA",
                "fecha_vencimiento": "2025-12-30T23:59:59",
                "observaciones": "CTG válido para ingreso",
                "consulta_timestamp": datetime.now().isoformat(),
                "xml_enviado": xml_request
            }
            
            return {
                "success": True,
                "data": response_simulada,
                "message": f"CTG {nro_ctg} consultado exitosamente",
                "webservice": "wscpe",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error consultando CTG {nro_ctg}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "nro_ctg": nro_ctg,
                "timestamp": datetime.now().isoformat()
            }

    def parse_cpe_response(self, xml_response: str) -> Dict[str, Any]:
        """
        Parsea la respuesta XML del webservice WSCPE.
        
        Args:
            xml_response: XML de respuesta del webservice
            
        Returns:
            Diccionario con datos parseados de la CPE
        """
        
        try:
            root = ET.fromstring(xml_response)
            
            # Namespaces típicos de AFIP
            namespaces = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'cpe': 'http://cpe.schema.afip.gov.ar/'
            }
            
            # Buscar elementos en respuesta
            # TODO: Ajustar según estructura real de respuesta WSCPE
            
            parsed_data = {
                "numero_cpe": "Extraer de XML",
                "estado": "Extraer de XML",
                "datos_mercaderia": {},
                "datos_transporte": {},
                "validacion": "OK"
            }
            
            return parsed_data
            
        except ET.ParseError as e:
            logger.error(f"Error parseando XML response: {str(e)}")
            return {"error": "XML mal formado", "details": str(e)}
        except Exception as e:
            logger.error(f"Error procesando respuesta: {str(e)}")
            return {"error": "Error procesando respuesta", "details": str(e)}

    async def validar_multiples_cpes(self, token: str, sign: str, numeros_cpe: list) -> Dict[str, Any]:
        """
        Valida múltiples CPEs en una sola operación.
        Útil para procesar lotes de camiones.
        """
        
        resultados = []
        
        for numero_cpe in numeros_cpe:
            resultado = await self.consultar_carta_porte(token, sign, numero_cpe)
            resultados.append(resultado)
            
        return {
            "success": True,
            "total_consultadas": len(numeros_cpe),
            "resultados": resultados,
            "timestamp": datetime.now().isoformat()
        }