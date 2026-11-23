import io
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

st.set_page_config(page_title='SIG Audit Pro', page_icon='🛡️', layout='wide')
st.markdown('''<style>.block-container{padding-top:1.5rem;max-width:1450px}h1,h2,h3{letter-spacing:-.025em}div[data-testid="stMetric"]{background:#f3f6fb;border:1px solid #e0e7f0;padding:16px;border-radius:12px}</style>''', unsafe_allow_html=True)

# Preguntas originales, orientativas. No reproducen el texto de las normas ISO.
COMMON = [
('4.1','¿Se han identificado las cuestiones internas y externas relevantes para el sistema?'),
('4.2','¿Se identifican las partes interesadas y sus necesidades pertinentes?'),
('4.3','¿Está documentado el alcance del sistema de gestión?'),
('4.4','¿Se han definido los procesos e interacciones del sistema?'),
('5.1','¿La alta dirección demuestra liderazgo y compromiso?'),
('5.2','¿Existe una política aprobada, comunicada y disponible?'),
('5.3','¿Se han asignado responsabilidades y autoridades?'),
('6.1','¿Se planifican acciones frente a riesgos y oportunidades?'),
('6.2','¿Existen objetivos medibles y planes para lograrlos?'),
('7.1','¿Se proporcionan recursos suficientes para operar el sistema?'),
('7.2','¿Se evalúa y asegura la competencia del personal?'),
('7.3','¿El personal conoce la política y su contribución al sistema?'),
('7.4','¿Se han establecido mecanismos de comunicación interna y externa?'),
('7.5','¿Se controla la información documentada y sus versiones?'),
('8.1','¿Se planifican y controlan las actividades operativas pertinentes?'),
('9.1','¿Se monitorea, mide y analiza el desempeño del sistema?'),
('9.2','¿Existe un programa de auditorías internas y se ejecuta?'),
('9.3','¿La dirección revisa periódicamente el desempeño del sistema?'),
('10.2','¿Se gestionan las no conformidades y acciones correctivas?'),
('10.3','¿Se impulsa la mejora continua del sistema?'),
]
SPECIAL = {
'ISO 9001': [
('5.1.2','¿Se consideran sistemáticamente los requisitos y la satisfacción del cliente?'),
('6.3','¿Los cambios del sistema se planifican de manera controlada?'),
('7.1.5','¿Se controlan los recursos de seguimiento y medición?'),
('8.2','¿Se determinan y revisan los requisitos de productos y servicios?'),
('8.3','¿Se controla el diseño y desarrollo cuando corresponde?'),
('8.4','¿Se controlan los productos, procesos y servicios suministrados externamente?'),
('8.5','¿Se controla la prestación del servicio o la producción?'),
('8.6','¿Se verifica la conformidad antes de liberar productos o servicios?'),
('8.7','¿Se controlan las salidas no conformes?'),
('9.1.2','¿Se hace seguimiento de la percepción y satisfacción del cliente?')],
'ISO 14001': [
('6.1.2','¿Se identifican aspectos ambientales y sus impactos asociados?'),
('6.1.3','¿Se identifican y actualizan las obligaciones de cumplimiento ambiental?'),
('6.1.4','¿Se planifican acciones sobre aspectos significativos y obligaciones?'),
('8.1','¿Se consideran controles ambientales y perspectiva de ciclo de vida?'),
('8.2','¿Existen procedimientos para responder a emergencias ambientales?'),
('9.1.2','¿Se evalúa periódicamente el cumplimiento de obligaciones ambientales?')],
'ISO 45001': [
('5.4','¿Se consulta y permite la participación de los trabajadores?'),
('6.1.2.1','¿Se identifican peligros de seguridad y salud en el trabajo?'),
('6.1.2.2','¿Se evalúan los riesgos de SST y otros riesgos del sistema?'),
('6.1.3','¿Se identifican los requisitos legales y otros requisitos de SST?'),
('8.1.2','¿Se aplica la jerarquía de controles para reducir riesgos?'),
('8.1.3','¿Se gestionan los cambios que pueden afectar la SST?'),
('8.1.4','¿Se controlan las compras, contratistas y externalización pertinentes?'),
('8.2','¿Se prepara y prueba la respuesta ante emergencias de SST?'),
('9.1.2','¿Se evalúa el cumplimiento legal y otros requisitos de SST?'),
('10.2','¿Se investigan incidentes y se implementan acciones correctivas?')]
}
NORMS = list(SPECIAL)
ROWS = []
for norm in NORMS:
    for clause, question in COMMON + SPECIAL[norm]:
        ROWS.append({'ID': f'{norm[-4:]}-{clause}', 'Norma': norm, 'Cláusula': clause, 'Pregunta': question,
                     'Estado':'No evaluado','Evidencia':'','Hallazgo':'','Acción correctiva':'','Responsable':'','Fecha límite':''})
DEFAULT = pd.DataFrame(ROWS)
if 'matrix' not in st.session_state:
    st.session_state.matrix = DEFAULT.copy()

with st.sidebar:
    st.title('🛡️ SIG Audit Pro')
    st.caption('Auditoría integrada · Calidad · Ambiente · SST')
    page = st.radio('Navegación', ['📊 Panel de control','📋 Lista de verificación','🛠️ Plan de acción','📄 Informe y exportación','ℹ️ Metodología'])
    st.divider()
    st.warning('Plantilla académica orientativa: valide cada pregunta con la edición oficial aplicable de las normas ISO.')

st.title(page)
with st.expander('🏢 Datos generales de la auditoría', expanded=(page=='📊 Panel de control')):
    a,b,c = st.columns(3)
    company = a.text_input('Organización', value='Empresa de ejemplo', key='company')
    auditor = b.text_input('Auditor/a', value='', key='auditor')
    audit_date = c.date_input('Fecha de auditoría', date.today(), key='date')
    d,e = st.columns(2)
    scope = d.text_input('Alcance / proceso auditado', value='Sistema integrado de gestión', key='scope')
    sector = e.text_input('Sector / sede', value='', key='sector')

DF = st.session_state.matrix.copy()
EVAL = DF[DF['Estado'].isin(['Conforme','Parcialmente conforme','No conforme'])]
N_EVAL = len(EVAL)
SCORE = (100*(EVAL['Estado'].map({'Conforme':1,'Parcialmente conforme':0.5,'No conforme':0}).sum()/N_EVAL)) if N_EVAL else 0
COVERAGE = 100*(len(DF)-len(DF[DF['Estado']=='No evaluado'])-len(DF[DF['Estado']=='No aplica']))/max(1,(len(DF)-len(DF[DF['Estado']=='No aplica'])))

def norm_summary(df):
    data=[]
    for norm,g in df.groupby('Norma',sort=False):
        valid=g[g['Estado'].isin(['Conforme','Parcialmente conforme','No conforme'])]
        n=len(valid)
        value=100*valid['Estado'].map({'Conforme':1,'Parcialmente conforme':.5,'No conforme':0}).sum()/n if n else 0
        data.append({'Norma':norm,'Cumplimiento (%)':round(value,1),'Evaluados':n,'Total aplicables':len(g[g['Estado']!='No aplica'])})
    return pd.DataFrame(data)

if page=='📊 Panel de control':
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Cumplimiento ponderado',f'{SCORE:.1f}%')
    c2.metric('Requisitos evaluados',f'{N_EVAL}/{len(DF[DF.Estado!="No aplica"])}')
    c3.metric('No conformidades',int((DF.Estado=='No conforme').sum()))
    c4.metric('Sin evaluar',int((DF.Estado=='No evaluado').sum()))
    st.caption('El cumplimiento considera Conforme = 100 %, Parcial = 50 %, No conforme = 0 %. No aplica y No evaluado se excluyen. La cobertura mide el avance de evaluación de requisitos aplicables.')
    st.progress(min(1,max(0,COVERAGE/100)),text=f'Cobertura de evaluación: {COVERAGE:.1f}%')
    left,right=st.columns(2)
    with left:
        ns=norm_summary(DF)
        fig=px.bar(ns,x='Norma',y='Cumplimiento (%)',color='Norma',text='Cumplimiento (%)',range_y=[0,100],title='Cumplimiento por norma')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        states=DF['Estado'].value_counts().rename_axis('Estado').reset_index(name='Cantidad')
        fig=px.pie(states,names='Estado',values='Cantidad',hole=.55,title='Distribución de estados')
        st.plotly_chart(fig,use_container_width=True)
    st.subheader('Resumen de auditoría')
    st.dataframe(norm_summary(DF),hide_index=True,use_container_width=True)

elif page=='📋 Lista de verificación':
    st.info('Seleccione una norma, edite el estado y registre evidencias. Los cambios se guardan durante la sesión y pueden exportarse.')
    selected=st.selectbox('Norma a evaluar',NORMS)
    st.caption('Los requisitos comunes aparecen por separado en cada norma para permitir evidencias y resultados distintos.')
    cols=['ID','Cláusula','Pregunta','Estado','Evidencia','Hallazgo','Acción correctiva','Responsable','Fecha límite']
    edited=st.data_editor(DF.loc[DF.Norma==selected,cols],hide_index=True,use_container_width=True,num_rows='fixed',height=600,
        disabled=['ID','Cláusula','Pregunta'],column_config={
            'Estado':st.column_config.SelectboxColumn(options=['No evaluado','Conforme','Parcialmente conforme','No conforme','No aplica'],required=True),
            'Evidencia':st.column_config.TextColumn(width='large'),
            'Hallazgo':st.column_config.TextColumn(width='large'),
            'Acción correctiva':st.column_config.TextColumn(width='large')},key=f'editor_{selected}')
    if st.button('💾 Guardar evaluación',type='primary'):
        indices=DF.index[DF.Norma==selected]
        st.session_state.matrix.loc[indices,cols]=edited[cols].to_numpy()
        st.success('Evaluación actualizada. Consulte el panel o exporte el informe.')
        st.rerun()

elif page=='🛠️ Plan de acción':
    problems=DF[DF.Estado.isin(['No conforme','Parcialmente conforme'])]
    st.write(f'Hallazgos que requieren seguimiento: **{len(problems)}**')
    st.dataframe(problems[['Norma','Cláusula','Estado','Hallazgo','Acción correctiva','Responsable','Fecha límite']],hide_index=True,use_container_width=True)
    st.caption('Para modificar acciones y responsables, utilice la Lista de verificación y guarde los cambios.')

def make_excel(df):
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine='openpyxl') as writer:
        df.to_excel(writer,index=False,sheet_name='Verificacion')
        norm_summary(df).to_excel(writer,index=False,sheet_name='Indicadores')
        ws=writer.sheets['Verificacion']
        ws.freeze_panes='D2'
        ws.auto_filter.ref=ws.dimensions
        from openpyxl.styles import Font,PatternFill
        for cell in ws[1]:
            cell.fill=PatternFill('solid',fgColor='183153');cell.font=Font(color='FFFFFF',bold=True)
        for letter,width in {'A':19,'B':17,'C':16,'D':78,'E':23,'F':48,'G':48,'H':48,'I':25,'J':20}.items():
            ws.column_dimensions[letter].width=width
    return buf.getvalue()

def pdf_report(df):
    buf=io.BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=40,leftMargin=40,topMargin=42,bottomMargin=42)
    styles=getSampleStyleSheet();styles['Title'].alignment=TA_CENTER
    story=[Paragraph('INFORME DE AUDITORÍA INTEGRADA',styles['Title']),Spacer(1,12),
        Paragraph(f'<b>Organización:</b> {escape(company)}',styles['Normal']),
        Paragraph(f'<b>Auditor:</b> {escape(auditor or "No consignado")}',styles['Normal']),
        Paragraph(f'<b>Fecha:</b> {audit_date.isoformat()}',styles['Normal']),
        Paragraph(f'<b>Sector/sede:</b> {escape(sector or "No consignado")}',styles['Normal']),
        Paragraph(f'<b>Alcance:</b> {escape(scope)}',styles['Normal']),Spacer(1,14),
        Paragraph('1. Resumen ejecutivo',styles['Heading2']),
        Paragraph(f'Cumplimiento ponderado: {SCORE:.1f} %. Requisitos evaluados: {N_EVAL}. No conformidades: {int((df.Estado=="No conforme").sum())}. Requisitos sin evaluar: {int((df.Estado=="No evaluado").sum())}.',styles['Normal']),Spacer(1,12),
        Paragraph('2. Resultados por norma',styles['Heading2'])]
    summary=norm_summary(df)
    data=[['Norma','Cumplimiento','Evaluados']]+[[r['Norma'],f"{r['Cumplimiento (%)']:.1f}%",str(r['Evaluados'])] for _,r in summary.iterrows()]
    t=Table(data,colWidths=[170,140,110]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#183153')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.whitesmoke,colors.white]),('GRID',(0,0),(-1,-1),.3,colors.lightgrey),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8)]));story.append(t)
    story += [Spacer(1,14),Paragraph('3. Hallazgos y acciones',styles['Heading2'])]
    findings=df[df.Estado.isin(['No conforme','Parcialmente conforme'])]
    if findings.empty:story.append(Paragraph('No se registraron hallazgos en los requisitos evaluados.',styles['Normal']))
    for _,r in findings.iterrows():
        story.append(Paragraph(f"<b>{escape(r['Norma'])} · {escape(r['Cláusula'])} · {escape(r['Estado'])}</b>",styles['Normal']))
        for field in ['Pregunta','Evidencia','Hallazgo','Acción correctiva','Responsable','Fecha límite']:
            story.append(Paragraph(f'<b>{field}:</b> {escape(str(r[field]) or "No consignado")}',styles['Normal']))
        story.append(Spacer(1,8))
    story += [Spacer(1,10),Paragraph('4. Criterio y limitaciones',styles['Heading2']),
       Paragraph('Índice orientativo: Conforme = 1, Parcialmente conforme = 0,5, No conforme = 0. Los estados No aplica y No evaluado se excluyen del denominador. El resultado no representa una certificación ISO ni sustituye la verificación de los textos normativos oficiales.',styles['Normal']),
       Spacer(1,10),Paragraph('5. Recomendación general',styles['Heading2']),
       Paragraph('Priorizar el cierre documentado de no conformidades, verificar la eficacia de las acciones y completar los requisitos pendientes antes de emitir conclusiones definitivas.',styles['Normal'])]
    doc.build(story);return buf.getvalue()

from xml.sax.saxutils import escape
if page=='📄 Informe y exportación':
    st.write('Descargue la matriz editable o el informe de resultados de la sesión actual.')
    a,b=st.columns(2)
    a.download_button('📥 Descargar matriz Excel',make_excel(DF),file_name='SIG_Audit_Pro_Matriz.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
    b.download_button('📄 Descargar informe PDF',pdf_report(DF),file_name='SIG_Audit_Pro_Informe.pdf',mime='application/pdf',use_container_width=True)
    st.warning('Si no completó toda la evaluación, el informe es preliminar. Descargue el Excel para conservar los datos fuera de la sesión.')

elif page=='ℹ️ Metodología':
    st.markdown('''### Alcance de la herramienta
Esta es una **lista académica de preguntas originales y orientativas** alineadas temáticamente con los capítulos de ISO 9001, ISO 14001 e ISO 45001. No es una transcripción de normas ISO ni garantiza cobertura exhaustiva de todos los subrequisitos.

**Estados:** Conforme (1), Parcialmente conforme (0,5), No conforme (0), No aplica (excluido), No evaluado (pendiente y excluido).

**Cumplimiento:** suma de puntuaciones de requisitos evaluados y aplicables / número de requisitos evaluados y aplicables × 100.

**Cobertura:** requisitos evaluados / requisitos aplicables × 100. Una cobertura baja impide interpretar el porcentaje de cumplimiento como evaluación integral.

**Nota:** Se utilizan etiquetas de cláusulas como guía de organización. Antes de usar la aplicación para auditorías formales, revise los textos oficiales de las ediciones vigentes, sus modificaciones y la correspondencia precisa de cada pregunta. Los requisitos compartidos se registran por norma para evitar que una sola respuesta oculte diferencias de implementación.''')
