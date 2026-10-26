# 🎲 Simulación del Juego Yahtzee con el Método de Montecarlo

**Institución Universitaria Digital de Antioquia**  
**Asignatura:** Simulación (`PREICA2602B020045`)  
**Actividad:** S20 - Módulo 1. Actividad Didáctica 2-M1  
**Docente:** Julián Andrés Loaiza  

---

## 👥 Integrantes (Grupo 3)
- **Raúl Santiago Morales Henao**
- **David Octavio Castro Mora**
- **Claudia Dilbani Enríquez Botina**

---

## 📌 Descripción del Proyecto
Este proyecto implementa una simulación computacional del clásico juego de dados **Yahtzee** para **2 jugadores** utilizando **Python** y el **Método de Montecarlo** en Google Colab.

### Características principales:
1. **Distribución de Probabilidad Uniforme Discreta:** Lanzamiento de 5 dados de 6 caras equiprobables ($P(X = k) = \frac{1}{6} \approx 16.67\%$).
2. **Modelado con Cadenas de Markov:** Proceso de decisión por turno de hasta 3 lanzamientos donde la transición al siguiente estado depende exclusivamente de los dados conservados en el estado actual.
3. **Simulación de Montecarlo (10,000 tiradas):** Verificación empírica de la Ley de los Grandes Números en la frecuencia de caras y estimación de probabilidades de jugadas en el primer lanzamiento (*Trío*, *Escalera Menor*, *Full House*, *Escalera Mayor* y *Yahtzee*).
4. **Modo Interactivo para 2 Jugadores:** Gestión completa de las 13 categorías oficiales del juego (Sección Superior e Inferior), relanzamiento selectivo de dados y tabla de puntuación dinámica.

---

## 📂 Estructura del Repositorio
- [`Grupo3_Montecarlo.ipynb`](./Grupo3_Montecarlo.ipynb): Cuaderno interactivo de Google Colab / Jupyter con el fundamento teórico, código fuente, gráficas estadísticas de Montecarlo y partida interactiva.
- [`yahtzee_montecarlo.py`](./yahtzee_montecarlo.py): Script en Python del simulador y juego para 2 jugadores.

---

## 🚀 Cómo Ejecutar
1. Abre el archivo [`Grupo3_Montecarlo.ipynb`](./Grupo3_Montecarlo.ipynb) directamente en **Google Colab** o Jupyter Notebook.
2. Ejecuta las celdas en orden para:
   - Cargar las funciones de lanzamiento y reglas de puntuación.
   - Ejecutar las **10,000 simulaciones de Montecarlo** y visualizar las gráficas.
   - Iniciar una partida interactiva para 2 jugadores en consola.
