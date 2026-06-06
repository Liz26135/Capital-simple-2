# Strategic Capital Allocation Optimizer

Proyecto académico para aplicar conceptos de:

- Teoría de Markowitz
- Frontera eficiente
- Simulación Monte Carlo
- Asignación de capital

## Estructura del Excel

Columnas mínimas requeridas:

- Proyecto
- Volatilidad

Columnas financieras obligatorias en la app:

- CAPEX
- ROI esperado

Si el archivo Excel cargado no incluye `CAPEX` o `ROI esperado`, la aplicación las agrega automáticamente con valor `0.0` en la tabla editable. El usuario puede completar o corregir esos valores antes de ejecutar la simulación.

## Ejecución

```bash
pip install -r requirements.txt
streamlit run app.py
```
