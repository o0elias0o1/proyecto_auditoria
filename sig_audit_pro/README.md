# SIG Audit Pro

Aplicación Streamlit de apoyo académico para auditorías integradas ISO 9001, ISO 14001 e ISO 45001.

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en GitHub y Streamlit Community Cloud
1. Cree un repositorio nuevo en GitHub y suba `app.py`, `requirements.txt` y `README.md`.
2. Abra https://share.streamlit.io/ y elija **Create app**.
3. Seleccione el repositorio, rama principal y archivo de entrada `app.py`.
4. Despliegue y abra el enlace público generado.

## Funciones
- Ficha de organización, auditor y alcance.
- Matriz de preguntas orientativas de tres sistemas de gestión.
- Evaluación y registro de evidencias, hallazgos y acciones.
- Indicadores y gráficos por norma.
- Descarga de matriz Excel e informe PDF.

## Advertencias
- Las preguntas son **originales, abreviadas y no exhaustivas**; no reemplazan las normas oficiales ni certifican cumplimiento.
- La información se conserva en la sesión activa de Streamlit. Descargue el Excel antes de cerrar o reiniciar la aplicación. No hay autenticación ni base de datos.
- No cargue información confidencial de empresas en despliegues públicos sin autorización y controles apropiados.
- Verifique la edición aplicable de cada norma antes de una auditoría formal.
