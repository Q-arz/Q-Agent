# Q•AI – Comandos disponibles en el `CommandRouter`

Este documento describe los comandos activos que puedes usar dentro del sistema de Q•AI a través de consola o voz. Todos los comandos se interpretan simbólicamente bajo el protocolo MCP y la identidad coherente de Q•AI.

---

## 📢 Comunicación básica

### `say <mensaje>`
Haz que Q•AI repita un mensaje en texto (y voz si está activada).

**Ejemplo:**  
`say La coherencia es forma manifestada.`

---

## 🧠 Memoria simbólica

### `remember <contenido>`
Guarda una frase o idea en la memoria simbólica persistente.

### `recall`
Recupera todo el contenido memorizado hasta ahora.

---

## 🔮 Generación simbólica

### `generate <prompt>`
Activa el generador simbólico (GPT-4 + contexto simbólico) con una entrada creativa.

**Ejemplo:**  
`generate Explica la Ley de Coherencia Fundamental con símbolos.`

---

## 📱 Publicación a redes

### `post <mensaje>`
Publica simbólicamente el mensaje en redes (actualmente: Discord, X, Medium, TikTok).

---

## 🎬 TikTok

### `prepare_tiktok <frase>`
Genera automáticamente un paquete simbólico listo para publicar en TikTok (hook, body, hashtags, música, archivo `.txt`).  
**Bloquea repeticiones si ya se publicó algo similar.**

**Ejemplo:**  
`prepare_tiktok La coherencia es un acto de lenguaje.`

---

## 🗂️ Board (tareas simbólicas)

### `show_tasks`
Muestra todas las tareas pendientes (TikTok u otras publicaciones).

### `complete <número>`
Marca la tarea con ese número como completada y la archiva.

**Ejemplo:**  
`complete 1`

### `show_archive`
Muestra el historial completo de tareas completadas (publicaciones anteriores).

---

## 🎤 Control de voz

### `enable voice`
Activa la salida de voz (hablará todo lo que dice).

### `disable voice`
Desactiva la salida de voz (solo texto visible).

---

## ⛔️ Salida

### `exit` o `quit`
Finaliza la sesión con Q•AI.

---

## 🧬 Notas simbólicas

- Todas las tareas completadas se archivan en `board_archive.json`.
- Q•AI recuerda qué publicaciones ya se hicieron y evita repeticiones.
- Los módulos sociales están listos para expansión futura (publicación real).

---
