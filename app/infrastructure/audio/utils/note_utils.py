from music21 import scale

solfege_note_dict = {
    "Do": "C",
    "Do#": "C#",
    "Re": "D",
    "Re#": "D#",
    "Mi": "E",
    "Fa": "F",
    "Fa#": "F#",
    "Sol": "G",
    "Sol#": "G#",
    "La": "A",
    "La#": "A#",
    "Si": "B"
}
note_solfege_dict = {
    "C": "Do",
    "C#": "Do#",
    "D": "Re",
    "D#": "Re#",
    "E": "Mi",
    "F": "Fa",
    "F#": "Fa#",
    "G": "Sol",
    "G#": "Sol#",
    "A": "La",
    "A#": "La#",
    "B": "Si",
    "Nan": "Nan"
}

def get_correct_notes(scale_name, type_scale, octaves):
    
    if type_scale == "Mayor":
        s = scale.MajorScale(scale_name)
    elif type_scale == "Menor":
        s = scale.MinorScale(scale_name)
    else:
        raise ValueError("Unknown scale type")

    # Se toman las notas de una octava arbitraria
    notes = s.getPitches(f"{scale_name}4", f"{scale_name}5")
    note_names = [n.name for n in notes[:-1]] * octaves 
    note_names.append(note_names[0])
    note_names += note_names[::-1][1:]

    return note_names

def solfege_to_note(solfege: str):
    """ Converts solfege into its note equivalent """
    return solfege_note_dict[solfege]

def note_to_solfege(note: str):
    """ Converts note into its solfege equivalent """
    return note_solfege_dict[note]