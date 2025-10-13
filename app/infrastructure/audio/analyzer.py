import sys
from concurrent.futures import ThreadPoolExecutor
import librosa
import numpy as np
# from basic_pitch.inference import predict
# from basic_pitch import ICASSP_2022_MODEL_PATH
from moviepy import VideoFileClip
import math
import time
from music21 import stream, note, scale, pitch
from app.infrastructure.audio.model_manager import ModelManager



def convert_mp4_to_wav(input_video: str, total_duration: float, split_time: float):
    clip = VideoFileClip(input_video)
    clip_first_half = clip.subclipped(0, split_time)
    clip_second_half = clip.subclipped(split_time, total_duration)

    audio_first_half = clip_first_half.audio
    audio_second_half = clip_second_half.audio

    audio_first_half.write_audiofile("piano_scale_1st.wav", fps=48000, codec="pcm_s24le", logger=None)
    audio_second_half.write_audiofile("piano_scale_2nd.wav", fps=48000, codec="pcm_s24le", logger=None)

def get_correct_notes(scale_name, type_scale, octaves):
    
    if type_scale == "major":
        s = scale.MajorScale(scale_name)
    elif type_scale == "minor":
        s = scale.MinorScale(scale_name)
    else:
        raise ValueError("Unknown scale type")

    # Se toman las notas de una octava arbitraria
    notes = s.getPitches(f"{scale_name}4", f"{scale_name}5")
    note_names = [n.name for n in notes[:-1]] * octaves 
    note_names.append(note_names[0])
    note_names += note_names[::-1][1:]

    return note_names

def basic_pitch_model_executor(audio_path: str, edges: list, n_bins: int):

    predict, ICASSP_2022_MODEL_PATH = ModelManager.get_basic_pitch()

    edges = np.asarray(edges, dtype=float).copy()

    for i in range(1, len(edges)):
        edges[i] = edges[i] - 0.05
    # Creacion de los contenedores
    bins = [[] for _ in range(n_bins)]

    # Umbrales de Basic Pitch (ajustar si no detecta notas suaves/cortas)
    ONSET_TH = 0.2       # más bajo -> más inicios detectados
    FRAME_TH = 0.05      # más bajo -> más frames sostenidos detectados
    MIN_NOTE_LEN_FR = 3  # en frames del modelo; más bajo -> permite notas más cortas
        
    # Ejecucion del modelo basic-pitch en todo el audio
    model_output, midi, note_events = predict(
        audio_path,
        model_or_model_path=ICASSP_2022_MODEL_PATH,
        onset_threshold=ONSET_TH,
        frame_threshold=FRAME_TH,
        minimum_note_length=MIN_NOTE_LEN_FR
    )

    # Esta sección extrae y organiza todas las notas detectadas por Basic Pitch a partir del objeto MIDI:
    """
    start: Cuándo empieza la nota (en segundos desde el inicio)
    end: Cuándo termina la nota (en segundos)
    pitch: Número MIDI (60=C4, 61=C#4, etc.)
    name: Nombre legible de la nota ("C4", "A#3", etc.)
    velocity: Qué tan fuerte se tocó la nota (0=silencio, 127=máximo)
    """
    notes_in_win = []
    for inst in midi.instruments:
        for n in inst.notes:
            notes_in_win.append({
                "start": float(n.start),
                "end": float(n.end),
                "pitch": int(n.pitch),  # numero MIDI
                "name": librosa.midi_to_note(n.pitch, octave=True),
                "velocity": int(n.velocity),
            })

    # Se organiza por tiempo de inicio de las notas
    notes_in_win.sort(key=lambda x: x["start"])

    # Asignar cada nota a su contenedor temporal correspondiente según su tiempo de inicio
    for n in notes_in_win:
        t = float(n["start"])                          # Obtener tiempo de inicio de la nota
        idx = int(np.digitize(t, edges, right=False) - 1)  # Encontrar en qué contenedor temporal va
        # idx = max(0, min(idx, n_bins - 1))                 # Asegurar que el índice esté dentro del rango válido
        bins[idx].append(n)                                # Agregar la nota al contenedor correspondiente

    # A partir de los contenedores con las notas en su correspondiente espacio de tiempo, se seleccionan
    # como nota ejecutada, la mas fuerte dentro del espacio temporal
    extracted_notes = []
    for i in range(n_bins):
        section_start = edges[i]
        section_end = edges[i + 1]
        notes_in_section = bins[i]
        if not notes_in_section:
            continue

        notes_in_section.sort(key=lambda x: x['start'])

        for n in notes_in_section:
            n['name'] = n['name'][:-1].replace("♯", "#")

        sorted_notes = sorted(notes_in_section, key=lambda x: (x["velocity"]), reverse=True)
        if sorted_notes:
            # Solo se elige la nota mas fuerte como la ejecutada, si su potencia('velocity') supera el umbral definido
            # esto se lleva a cabo para manejar el caso en que el usuario no toque ninguna tecla entre beats 
            if sorted_notes[0]['velocity'] > 56:
                extracted_notes.append(sorted_notes[0])
            else:
                strongest_note = sorted_notes[0]
                strongest_note['name'] = "Nan"
                extracted_notes.append(strongest_note)
            

    return extracted_notes

def extract_notes_audio(video_file, tempo, rhythmic_Value, notes_quantity):
    # Blanca (half note):  2 beats
    # Negra (quarter note):  1 beat
    # Corchea (eighth note):  0.5 beats

    # Cantidad de segundos entre notas
    note_length_seconds = (60/tempo) * rhythmic_Value
    # Duracion neta de la ejecucion
    practice_duration = note_length_seconds * notes_quantity
    TIME_SECTION = note_length_seconds 
    # Se crean contenedores sobre la ventana de analisis (Contenedor son espacios de ejecucion de cada nota)
    n_bins = int(math.ceil((practice_duration) / TIME_SECTION))
    # edges representan los espacios de tiempo que se consideraran para la ejecucion de cada nota (Sirve para categorizar las notas
    # en diferentes espacios de tiempo posteriormente)
    edges = np.array([i * TIME_SECTION for i in range(n_bins + 1)], dtype=float)
    
    note_executed_at_half = len(edges)//2

    
    convert_mp4_to_wav(video_file, practice_duration, edges[note_executed_at_half - 1]) 

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_l = executor.submit(
            basic_pitch_model_executor,
            audio_path="piano_scale_1st.wav",
            edges=edges,
            n_bins=n_bins
        )
        future_r = executor.submit(
            basic_pitch_model_executor,
            audio_path="piano_scale_2nd.wav",
            edges=edges,
            n_bins=n_bins
        )

        # Espera a que ambos hilos acaben
        l_res = future_l.result()
        r_res = future_r.result()

    extracted_notes = []
    if isinstance(l_res, list):
        extracted_notes.extend(l_res)
    if isinstance(r_res, list):
        extracted_notes.extend(r_res)
    end_time = time.time()
    print(end_time - start_time)

    extracted_notes[0]['start'] = 0
    for i in range(1, len(edges)-1):
        edges[i] = edges[i] - 0.05
        extracted_notes[i]['start'] = edges[i]

    return extracted_notes

