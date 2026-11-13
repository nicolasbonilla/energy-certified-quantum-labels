# Certification map (phase 3, full run): RESULTS

**Paper-grade run, declared and hashed before any computation at n ≥ 19** (`DECLARATION.md`, SHA-256
a08178012e860ac49e8b8081ee4386e13f411d70cceaaddb631939451d2f030c, hashed 2026-10-30T02:23:12Z). Batch
20261030T022613Z on cj-runner-1b. Units: J, with H = ¼Σ_edges(XX + YY + Jz ZZ) on `heavy_hex_graph(d)`. No QPU. Every
number comes from `out_20261030T022613Z/` (fetched, every file verified against `OUT_SHA256SUMS.txt`) or from the
laptop re-executions listed in §12. Written 2026-10-30, 14:30-15:30 UTC.

## Resumen en español sencillo

1. Calculamos el mapa completo de garantías para el conjunto de datos de IBM con 57 y 115 cúbits, con las reglas selladas antes de calcular. Usamos 11,96 horas de máquina (unos 7,1 €; 8,9 € con el recargo del programa), dentro del tope de 15. La máquina quedó apagada y los registros sellados no cambiaron.
2. **Resultado positivo (veredicto declarado: MAPA POSITIVO).** El orden magnético y la correlación media entre vecinos quedan garantizados al ±3 % desde Jz ≈ 3,2 con 57 cúbits y desde Jz ≈ 3,1 con 115. Son 29-30 de los 45 puntos de entrenamiento. La garantía se mantiene aunque el error real de IBM fuera 3 veces el que leímos en sus gráficas.
3. Por debajo de Jz = 1,6 y en la zona de prueba fuera del entrenamiento no se garantiza nada, para ningún dato y en los dos tamaños. Esta conclusión se mantiene aunque el error real fuera solo el 4 % del leído.
4. Los datos de un sitio, un enlace o un anillo no quedan garantizados en ningún punto con los márgenes declarados. Con 57 cúbits rozan la línea al final del rango (Jz = 5,5-6: zona gris). Con 115 cúbits el error tolerable se reduce a la mitad (0,496 ≈ 57/115), tal como dice la regla de los datos locales.
5. La correlación a segundos vecinos queda garantizada desde Jz ≈ 4,0 (57 cúbits) y ≈ 3,8 (115).
6. La regla δe* = τ²/(8χ) acierta entre el 0 y el 5 % en 57 de 63 puntos de promedios. Falla para el orden magnético con Jz ≥ 5 (sobrestima el margen hasta 1,8 veces) porque allí aparece un salto de nivel. No cambia ninguna conclusión, porque IBM queda 10-37 veces por debajo.
7. Una segunda lectura independiente de las gráficas de IBM coincide con la primera: el error de energía sale entre 0,93 y 1,02 veces el anterior, y el mapa da lo mismo con las dos lecturas. Los estados testigo son sencillos: con dimensión de enlace 32 ya se obtiene el 97 % del efecto. Además construimos explícitamente un testigo puro.
8. Para no pasar del coste, quitamos en el orden declarado los datos locales de 115 cúbits (salvo Z_bulk en Jz = 4) y los puntos extra de J* con 115. Todas las comprobaciones pasan. Lo positivo sigue dependiendo de la lectura de las gráficas y del cálculo clásico de referencia (el mismo que usa IBM).

---
