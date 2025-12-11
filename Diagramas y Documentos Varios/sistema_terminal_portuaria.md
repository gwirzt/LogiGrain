# Sistema informático para terminal portuaria

## Versión del documento

-   Versión: 0.1 (borrador inicial)
-   Fecha: 29/11/2025

## 1. Objetivo general del sistema

Diseñar y desarrollar un sistema informático integrado para una terminal
portuaria que permita gestionar de forma eficiente, trazable y segura
todas las operaciones relacionadas con el ingreso, permanencia y egreso
de cargas, camiones, contenedores y buques, facilitando la coordinación
entre sectores y brindando información en tiempo real para la toma de
decisiones.

## 2. Alcance inicial del documento

Este documento se centrará en: - Identificar los sectores que
interactúan en la operación de la terminal. - Definir los tipos de
usuarios por sector. - Redactar historias de usuario para cada tipo de
usuario. - Servir como base para análisis funcional, diseño técnico y
desarrollo.

## 3. Sectores que interactúan en la terminal portuaria (versión ajustada)

### 3.1 Playa de Camiones (20 km del puerto)

-   Recepción de camiones.
-   Registro inicial y validación mediante WebServices de ARCA.
-   Cobro de estadía.
-   Organización de camiones en espera.
-   Envío de información al puerto para posterior ordenamiento y
    llamados.

### 3.2 Operaciones

-   Monitoreo en tiempo real.
-   Priorización y llamado de camiones.
-   Coordinación entre sectores.
-   Gestión del flujo general.

### 3.3 Portería de Ingreso (Precalado)

-   Control de acceso.
-   Verificación documental.
-   Derivación a Playa de Precalado.

### 3.4 Playa de Precalado

-   Organización de camiones.
-   Avance hacia Calada según llamado.

### 3.5 Calada

-   Inspección de mercadería.
-   Clasificación por calidad.
-   Asignación a playas internas.

### 3.6 Playa de Espera post-Calada

-   Ordenamiento por calidad.
-   Espera hasta disponibilidad de plataforma.

### 3.7 Báscula -- Peso Bruto

-   Registro de peso bruto.
-   Validaciones previas.

### 3.8 Plataformas de Descarga

-   Descarga de mercadería.
-   Confirmación de cierre.

### 3.9 Báscula -- Peso Tara

-   Registro de peso tara.
-   Determinación del peso neto.

### 3.10 Portería de Salida

-   Control de egreso.
-   Confirmación de finalización del circuito.

## 4. Tipos de usuario por sector

### 4.1 Roles operativos principales

1.  Operador de Playa de Camiones
2.  Operador de Portería de Ingreso
3.  Operador de Calada
4.  Operador de Balanza - Peso Bruto
5.  Operador de Plataforma de Descarga
6.  Operador de Balanza - Peso Tara
7.  Operador de Portería de Salida
8.  Operador de Operaciones

## 6. Historias de usuario

### 6.1 Playa de Camiones

### Ingreso de camiones a la playa
- **Como** operador  
    - **quiero** recibir al conductor,solicitarle el QR de su carta de porte, leerlo y obtener los datos desde
        el webservice de ARCA 
    - **para** Guardarlos en la base de datos, de esta manera queda ingresado al sistema.
- **como** operador 
    - **quiero** al ingresarlo emitir la factura correspondiente 
    - **para** comunicarle al conductor que agurade a ser llamado para ir a la terminal portuaria
- **como** encargado de playa
    - **quiero** ver la posicion de camiones en la playa, ingresados, salidos y en espera
    - **para** comunicarle a quein lo solicite

### Envío de camiones al puerto
- **Como** Operador de Playa de Camiones
    - **quiero** recibir una solicitud de cantidad y tipo de camiones desde Operaciones
    - **para** seleccionar los camiones correspondientes y marcar su estado como **"En Viaje (al Puerto)"** escaneando su QR, iniciando el conteo de camiones en tránsito y marcando su salida de playa.

---

### 6.2 Operaciones

### Monitoreo y Análisis de Flujo
- **Como** Operador de Operaciones
    - **quiero** visualizar la cantidad de camiones en Playa de Camiones (3.1) agrupados por **Exportador**, **Producto** y **Tipo de Almacenaje** (pérdida de identidad o especial)
    - **para** analizar la demanda de descarga y planificar los llamados.

### Solicitud y Llamado de Camiones
- **Como** Operador de Operaciones
    - **quiero** seleccionar una cantidad y tipo de camiones necesarios (ej: "10 camiones de Maíz")
    - **para** enviar una orden de solicitud al Operador de Playa de Camiones (3.1) para que proceda a enviarlos al puerto.

### Monitoreo del Flujo General
- **Como** Operador de Operaciones
    - **quiero** ver la posición de todos los camiones en el circuito: **En Playa**, **En Viaje**, **En Ingreso**, **En Precalado**, **En Calada**, **Post-Calada**, **En Báscula Bruto**, **Descargando**, **En Báscula Tara** y **Saliendo**
    - **para** tener trazabilidad completa y gestionar el flujo general en tiempo real, observando el rendimiento y posibles cuellos de botella.

### Llamado para Descarga
- **Como** Operador de Operaciones
    - **quiero** visualizar la lista de camiones en la Playa Post-Calada (3.6) ordenada por **Calidad, Cereal y FIFO**
    - **para** realizar la llamada de avance a la Báscula de Peso Bruto (3.7) respetando el orden de la fila de pre-descarga.

---

### 6.3 Portería de Ingreso (Precalado)

### Control y Registro de Acceso
- **Como** Operador de Portería de Ingreso
    - **quiero** escanear el código QR de la carta de porte del camión que llega
    - **para** validar que el camión fue previamente marcado como **"En Viaje (al Puerto)"** por el Operador de Playa.
- **Como** Operador de Portería de Ingreso
    - **quiero** marcar el camión como **"Ingresado a Terminal"** automáticamente luego de la validación
    - **para** actualizar su estado en el sistema, descontándolo del estado "En Viaje" y poniéndolo a disposición en la **Playa de Precalado (3.4)**.

---

### 6.4 Playa de Precalado

### Visualización y Ordenamiento
- **Como** Operador de Operaciones (o encargado de playa)
    - **quiero** visualizar los camiones que se encuentran en la Playa de Precalado (3.4) ordenados por **Cereal** y luego por **orden de Ingreso (FIFO)**
    - **para** conocer la lista de espera priorizada para el avance a la Calada.

### Llamado a Calada
- **Como** Operador de Operaciones
    - **quiero** tener la capacidad de enviar una orden de llamado al sector de Playa de Precalado (3.4) indicando qué tipo de camión (Cereal) debe avanzar
    - **para** garantizar que el flujo de muestreo en la Calada se ajuste al tráfico de descarga de camiones definido (ej: Maíz o Trigo).

### Avance a Calada
- **Como** Operador de Playa de Precalado
    - **quiero** recibir la orden de llamado y escanear el QR del camión siguiente en la fila FIFO del Cereal solicitado
    - **para** marcar su estado como **"En Calada"** y permitirle el avance físico hacia el puesto de inspección.

---

### 6.5 Calada

### Identificación de Camión y Registro de Muestra
- **Como** Operador de Calada
    - **quiero** escanear el QR del camión que se presenta en el puesto de Calada
    - **para** identificarlo en el sistema y registrar la hora de inicio del proceso de muestreo.
- **Como** Operador de Calada
    - **quiero** registrar los **datos del análisis de calidad** (humedad, impurezas, cuerpos extraños, etc.) en el formulario del sistema
    - **para** que el sistema determine la calidad final del cereal y quede asociado al camión para el posterior ordenamiento.

### Finalización y Envío a Espera
- **Como** Operador de Calada
    - **quiero** finalizar la carga de datos del análisis
    - **para** marcar el estado del camión como **"Post-Calada"** y enviarlo a la **Playa de Espera post-Calada (3.6)**, indicándole al conductor su destino.

### Administración de Muestras (Flujo posterior)
- **Como** Operador de Calada (o Rol de Laboratorio/Administrativo)
    - **quiero** que el sistema asocie un **ID de Muestra único** a los datos de calidad registrados
    - **para** facilitar la trazabilidad posterior y la administración física de esa muestra (contramuestras, revisión, etc.).

---

### 6.6 Playa de Espera post-Calada

### Ordenamiento de Camiones
- **Como** Operador de Operaciones
    - **quiero** que el sistema muestre automáticamente los camiones en esta playa ordenados por su **Calidad** (resultado de Calada), **Cereal** y por **Orden de Ingreso (FIFO)**
    - **para** garantizar que el camión que lleva más tiempo en esa categoría sea el siguiente en ser llamado.

### Llamado a Báscula de Peso Bruto
- **Como** Operador de Operaciones
    - **quiero** seleccionar el camión que se encuentra en la primera posición de la lista ordenada para la descarga y asignarle la **Báscula de Peso Bruto (3.7)**
    - **para** iniciar la fase de pesaje del circuito de descarga.

### Avance a Báscula
- **Como** Operador de Playa de Espera post-Calada (o sistema automático de llamado)
    - **quiero** que el sistema notifique al camión seleccionado por Operaciones
    - **para** que avance físicamente a la Báscula de Peso Bruto (3.7) y su estado cambie a **"En Báscula Bruto"**.

---

### 6.7 Báscula – Peso Bruto

### Identificación y Validación
- **Como** Operador de Balanza - Peso Bruto
    - **quiero** escanear el QR de la carta de porte del camión que ingresa a la báscula
    - **para** recuperar sus datos y **validar visualmente** que la patente que aparece en pantalla coincida con la patente del vehículo.

### Registro de Peso Bruto
- **Como** Operador de Balanza - Peso Bruto
    - **quiero** ingresar el valor de la balanza en el sistema
    - **para** registrar el peso bruto del camión asociado a su carta de porte y calidad.

### Asignación Final de Plataforma
- **Como** Operador de Balanza - Peso Bruto
    - **quiero** que el sistema me sugiera (o me permita seleccionar) una **Plataforma de Descarga (3.8)** disponible que sea compatible con el **Cereal** y la **Calidad** del camión
    - **para** comunicar al conductor la plataforma a la que debe dirigirse inmediatamente después de pesar, cambiando el estado del camión a **"En Plataforma de Descarga"**.

---

### 6.8 Plataformas de Descarga

### Confirmación de Recepción e Inicio de Descarga
- **Como** Operador de Plataforma de Descarga
    - **quiero** escanear el QR del camión que llega a mi plataforma asignada
    - **para** verificar su identidad y, en el mismo evento, registrar el **inicio de la descarga** en la base de datos, lo que cambia el estado del camión a **"Descargando"** y marca la plataforma como ocupada.

### Finalización y Envío a Tara
- **Como** Operador de Plataforma de Descarga
    - **quiero** notificar la finalización de la descarga mediante el sistema
    - **para** que el estado del camión se actualice a **"En Báscula Tara"** y el conductor sea dirigido a la **Báscula de Peso Tara (3.9)**.

---

### 6.9 Báscula – Peso Tara

### Identificación y Registro de Peso Tara
- **Como** Operador de Balanza - Peso Tara
    - **quiero** escanear el QR del camión que llega vacío
    - **para** acceder a los datos de la pesada bruta y del cereal descargado, y registrar el peso tara del camión en ese momento.

### Cálculo de Peso Neto y Validación de Diferencias
- **Como** Operador de Balanza - Peso Tara
    - **quiero** que el sistema calcule automáticamente el **Peso Neto (Bruto - Tara)** y lo compare con el **Peso de Origen (Carta de Porte)**
    - **para** identificar si existe una diferencia que supere el umbral de tolerancia.

### Gestión de Diferencia de Peso
- **Como** Operador de Balanza - Peso Tara
    - **quiero** que, si se detecta una diferencia significativa de peso, el sistema **notifique automáticamente** a los "entregadores" (representantes del exportador)
    - **para** que estos puedan convalidar la diferencia (ya sea por mercadería adherida o condiciones de pesaje de origen) antes de que el camión egrese.

### Emisión Documental y Cierre de Pesada
- **Como** Operador de Balanza - Peso Tara
    - **quiero** al finalizar el proceso (y de ser necesario, convalidada la diferencia), emitir un **Ticket de Pesada** con los pesos Bruto, Tara y Neto finales
    - **para** entregárselo al conductor y marcar el estado del camión como **"Habilitado para Salida"**, indicándole que avance a la **Portería de Salida (3.10)**.

---

### 6.10 Portería de Salida

### Verificación de Finalización del Circuito
- **Como** Operador de Portería de Salida
    - **quiero** escanear el QR del camión que se presenta para egresar de la terminal
    - **para** verificar en el sistema si el camión ha **descargado exitosamente** (existe Peso Bruto y Peso Tara) o si debe egresar con la mercadería porque fue **rechazado en Calada** (solo existe Peso Bruto).

### Cierre de Carta de Porte y Egreso
- **Como** Operador de Portería de Salida
    - **quiero** al validar que el proceso del camión está completo (descarga o rechazo), marcar la **Carta de Porte como terminada** en el sistema
    - **para** registrar la hora de egreso y finalizar el circuito de trazabilidad del camión en la terminal, cambiando su estado a **"Salido de Planta"**.