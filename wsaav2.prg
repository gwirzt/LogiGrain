DEFINE CLASS WSAAv2 AS CUSTOM OLEPUBLIC

*	#INCLUDE "WSAA_Cliente.H"
	#DEFINE  CR_LF 	CHR(13) + CHR(10)


	lcUniqueID      = SYS(3)
	lcOrigen        = ""
	lcDestino       = ""
	lfDateTime      = DATETIME()
	lcGenTime       = TTOC(THIS.lfDateTime, 3)
	lcExpTime       = TTOC(THIS.lfDateTime + 12*60*60, 3)
	lcprueba        = ""
	
	
	rutaSsl         = ""
	archivoKey      = ""
	archivoPem      = ""
	archivoCrt		= ""
	
	rutaHomologacion=""
	rutaProduccion  =""
	
	ctoken           =""
	csign            =""	
	cuitInformado    =""
	webservice       =""
	cPrueba          =""    
	
	
	solicitudTA		=""
	TA				=""	 
	
	Comando			=""
	archivoCifrado	=""
	requestWsaa		=""
	
	respuestaWSAA	=""
	estado			=0
	
	generationTime = DATETIME()
	expirationtime = DATETIME()	
	
	ErrorCodigo = "" 
	ErrorDescripcion = ""					

	PROCEDURE INIT( cRutaSsl AS String, cArchivoKey AS String, cArchivoPem AS String, cArchivoCRT as String, nInformado AS Integer, cService as String, cHomologacion  as String, cProduccion as string  , cmodo as string )
		WITH THIS
				
				.rutaSSL        	= cRutaSsl
				.archivoKey			= cArchivoKey
				.archivoPem			= cArchivoPem
				.archivoCrt			= cArchivoCrt
				.cuitInformado		= nInformado
				.webservice			= cService
				.rutaHomologacion	= cHomologacion
				.rutaProduccion		= cProduccion
				.cprueba        	= cmodo
		ENDWITH
	ENDPROC
	*
	*
	FUNCTION cargarToken
		WITH this
			ccadena = "datosWSAA_cargarToken "+.cPrueba+","+sqlparam(.webservice)
			SQLEXEC(nconnect, ccadena,"tokenactivo")
			.ctoken = ALLTRIM(tokenactivo.token)
			.csign = ALLTRIM(tokenactivo.sign)
		ENDWITH 
	ENDFUNC 



	FUNCTION SolicitarToken
	LOCAL loHTTP AS Object
	LOCAL cFechaDesde, cFechaHasta, crespuestaWSAA 
		WITH this 
			.lfDateTime= DATETIME()
			.lcGenTime= TTOC(THIS.lfDateTime, 3)
			.lcExpTime= TTOC(THIS.lfDateTime + 12*60*60, 3)
			.borrar("requestTA.xml")
			.borrar("ArchivoBat.Bat")
			.borrar("MiLoginTicketRequest.xml.cms")
			.borrar("TA.xml")
			.solicitudTA = .makeTARequest()
			STRTOFILE(.solicitudTA,"requestTA.xml" )
			IF .cprueba = "S"
				TEXT TO .Comando TEXTMERGE NOSHOW
				"<<THIS.rutaSSL>>" cms -sign -in requestTA.xml -out MiLoginTicketRequest.xml.cms -signer "<<this.archivoPem>>" -inkey "<<THIS.archivoKey>>"  -nodetach -outform PEM
				ENDTEXT	
			ELSE
				TEXT TO .Comando TEXTMERGE NOSHOW
				"<<THIS.rutaSSL>>" cms -sign -in requestTA.xml -out MiLoginTicketRequest.xml.cms -signer "<<this.archivoCrt>>" -inkey "<<THIS.archivoKey>>"  -nodetach -outform PEM
				ENDTEXT
			ENDIF 	
			SET SAFETY OFF
			STRTOFILE(.Comando, "ArchivoBat.Bat")
			
			DECLARE INTEGER ShellExecute ;
			IN SHELL32.DLL ;
			INTEGER nWinHandle,;
			STRING cOperation,;
			STRING cFileName,;
			STRING cParameters,;
			STRING cDirectory,;
			INTEGER nShowWindow
			
			ShellExecute(0, "Open", "ArchivoBat.Bat" , "", "", 2)
			
			CLEAR DLLS 
			INKEY(2)
			.archivoCifrado = FILETOSTR("MiLoginTicketRequest.xml.cms")
			.archivoCifrado =  LEFT(.archivoCifrado, LEN(.archivoCifrado) - 19)			&& Quito el final ("------END CMS------")
			.archivoCifrado = RIGHT(.archivoCifrado, LEN(.archivoCifrado) - 20)			&& Quito el final ("------END CMS------")
			
			.requestWsaa = 	.makeReqWSAAA()
			STRTOFILE(.requestWsaa,"SolicitudEnviar.xml")
			loHTTP = NULL
			loHTTP = CREATEOBJECT('Msxml2.ServerXMLHTTP.6.0')
			cDireccion = IIF(.cprueba = "S",.rutaHomologacion, .rutaProduccion )
			loHTTP.OPEN("POST",  cDireccion, .F.)	
			
			loHTTP.setRequestHeader("User-Agent", "EjecutandoWSAA desde VFP - JSoftw@re")
			loHTTP.setRequestHeader("SOAPAction:", "None")
			loHTTP.setRequestHeader("Content-Type", "text/xml;charset=utf-8")
			loHTTP.SEND(.requestWsaa)
			.estado = loHTTP.status 
			.respuestaWSAA = loHTTP.ResponseText
			crespuestaWSAA = ALLTRIM(.respuestaWSAA) && pra guardarla en la base en su formato original
			IF  .estado = 200 
				STRTOFILE(.respuestaWSAA,"TA.xml")
				
				.respuestaWSAA = STRTRAN(.respuestaWSAA, "&lt;", "<")
				.respuestaWSAA = STRTRAN(.respuestaWSAA, "&gt;", ">") 
				
				.cToken = STREXTRACT(.respuestaWSAA , "<token>", "</token>")
				.cSign  = STREXTRACT(.respuestaWSAA , "<sign>", "</sign>")
				cFechaDesde = STREXTRACT(.respuestaWSAA, "<generationTime>", "</generationTime>")
				cFechaHasta = STREXTRACT(.respuestaWSAA, "<expirationTime>", "</expirationTime>")
				.generationtime = .genFechaSql(cFechaDesde)
				.expirationTime = .genFechaSql(cFechaHasta)
				
				ccadena = "datosWSAA_Guardar "+sqlparam(.csign)+","+sqlparam(.ctoken)+","+sqlparam(.generationtime )+","+;
						sqlparam(.expirationTime)+","+sqlparam(.cprueba)+","+sqlparam(.webservice)
				SQLEXEC(nconnect, ccadena )
			ELSE
				STRTOFILE(.respuestaWSAA,"TA.xml")				
			ENDIF 
			
			.ErrorCodigo = STREXTRACT( .respuestaWSAA , "<Codigo>", "</Codigo>") 
			.ErrorDescripcion = STREXTRACT( .respuestaWSAA , "<Descripcion>", "</Descripcion>") 
			cServicioLogs = "WSAA"
			
			cCopmandoSql = "logsConeccion_abm "+sqlparam(cServicioLogs)+","+sqlparam(.cPrueba)+","+sqlparam(.estado)+","+sqlparam(.ErrorCodigo )+","+sqlparam(.ErrorDescripcion )
			SQLEXEC(nconnect, cCopmandoSql )
			
		endwith
		RETURN this.estado
	ENDFUNC
	



	
	FUNCTION genFechaSql(cFecha)
	*2024-12-21T19:15:57.560-03:00
	LOCAL cAnio, cMes, cDia, cHora, cMinuto, cSegundo, ret
		cAnio = SUBSTR(cfecha,1,4)
		cMes = strzero(VAL(SUBSTR(cFecha,6,2)),2)	
		cdia = strzero(VAL(SUBSTR(cfecha,9,2)),2)
		cHora = strzero(VAL(SUBSTR(cfecha,12,2)),2)
		cMinuto = strzero(VAL(SUBSTR(cfecha,15,2)),2)
		cSegundo = strzero(VAL(SUBSTR(cfecha,18,2)),2)
		cfechaGen = cDia+"/"+cmes+"/"+cAnio+" "+cHora+":"+cminuto+":"+csegundo
		ret = CTOT(cfechaGen )
		RETURN ret 
	ENDFUNC 

	
	FUNCTION Borrar(tcFile)
		IF FILE(tcFile) THEN
			DELETE FILE (tcFile)
		ENDIF
	ENDFUNC
	
	
	*****************************
	*
	* Funciones para crear XML
	*
	*****************************


	FUNCTION makeTARequest()
	*Solicitud de ticket de acceso
	TEXT TO lcXMLRequest TEXTMERGE NOSHOW
	<loginTicketRequest>
	<header>
	<uniqueId><<THIS.lcUniqueID>></uniqueId>
	<generationTime><<THIS.lcGenTime>></generationTime>
	<expirationTime><<THIS.lcExpTime>></expirationTime>
	</header>
	<service><<THIS.webservice>></service>
	</loginTicketRequest>
	ENDTEXT
	RETURN lcXMLRequest
	ENDFUNC

	FUNCTION makeReqWSAAA()
		TEXT TO lcXMLRequest TEXTMERGE NOSHOW
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsaa="http://wsaa.view.sua.dvadac.desein.afip.gov">
   		<soapenv:Header/>
   		<soapenv:Body>
    	<wsaa:loginCms>
    	<wsaa:in0><<THIS.archivoCifrado>></wsaa:in0>
    	</wsaa:loginCms>
   		</soapenv:Body>
		</soapenv:Envelope>
		ENDTEXT
	RETURN lcXMLRequest
	ENDFUNC
ENDDEFINE 