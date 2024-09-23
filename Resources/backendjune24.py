
#!backendjune24.py

#Modules
import re
from ortools.sat.python import cp_model

#* Chord Rules and other dictionaries ===========================#
chord_rules = {
    'Maj': [0, 4, 7],
    'Maj6': [0, 4, 7, 9],
    'Maj6/9': [0, 4, 7, 9, 14],
    'Maj7': [0, 4, 7, 11],
    'Maj9': [0, 4, 7, 11, 14],
    'Maj11': [0, 4, 7, 11, 14, 17],
    'Maj13': [0, 4, 7, 11, 14, 17, 21],
    'Min': [0, 3, 7],
    'Min6': [0, 3, 7, 9],
    'Min7': [0, 3, 7, 10],
    'Min9': [0, 3, 7, 10, 14],
    'Min11': [0, 3, 7, 10, 14, 17],
    'Min13': [0, 3, 7, 10, 14, 17, 21],
    'MinMaj7': [0, 3, 7, 11],
    'Dom7': [0, 4, 7, 10],
    'Dom9': [0, 4, 7, 10, 14],
    'Dom11': [0, 4, 7, 10, 14, 17],
    'Dom13': [0, 4, 7, 10, 14, 17, 21],
    'Dim': [0, 3, 6],
    'Dim7': [0, 3, 6, 9],
    'HalfDim': [0, 3, 6, 10],
    'Aug': [0, 4, 8],
    'Aug7': [0, 4, 8, 10],
    'Sus2': [0, 2, 7],
    'Sus4': [0, 5, 7],
    '7Sus4': [0, 5, 7, 10],
    'Add9': [0, 4, 7, 14],
    'Add11': [0, 4, 7, 17],
}

allo_notes = ['E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#']
all_notes = ['C2', 'C#2', 'D2', 'D#2','E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'A#2', 'B2',
            'C3','C#3', 'D3', 'D#3','E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3',
            'C4','C#4', 'D4', 'D#4','E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4',
            'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5']

# Define chord dictionaries
first_position_chords = {
    'A Maj': [0, 0, 2, 2, 2, 0],
    'A Min': [0, 0, 2, 2, 1, 0],
    'B Maj': ['x', 2, 4, 4, 4, 2],
    'B Min': ['x', 2, 4, 4, 3, 2],
    'C Maj': ['x', 3, 2, 0, 1, 0],
    'C Min': ['x', 3, 5, 5, 4, 3],
    'D Maj': ['x', 0, 0, 2, 3, 2],
    'D Min': ['x', 0, 0, 2, 3, 1],
    'E Maj': [0, 2, 2, 1, 0, 0],
    'E Min': [0, 2, 2, 0, 0, 0],
    'F Maj': [1, 3, 3, 2, 1, 1],
    'F Min': [1, 3, 3, 1, 1, 1],
    'G Maj': [3, 2, 0, 0, 0, 3],
    'G Min': [3, 5, 5, 3, 3, 3]
}

barre_chords = {
    'A Maj': [5, 7, 7, 6, 5, 5],
    'A Min': [5, 7, 7, 5, 5, 5],
    'A# Maj': [6, 8, 8, 7, 6, 6],
    'A# Min': [6, 8, 8, 6, 6, 6],
    'B Maj': [7, 9, 9, 8, 7, 7],
    'B Min': [7, 9, 9, 7, 7, 7],
    'C Maj': [8, 10, 10, 9, 8, 8],
    'C Min': [8, 10, 10, 8, 8, 8],
    'C# Maj': [9, 11, 11, 10, 9, 9],
    'C# Min': [9, 11, 11, 9, 9, 9],
    'D Maj': [10, 12, 12, 11, 10, 10],
    'D Min': [10, 12, 12, 10, 10, 10],
    'D# Maj': [11, 13, 13, 12, 11, 11],
    'D# Min': [11, 13, 13, 11, 11, 11],
    'E Maj': [0, 2, 2, 1, 0, 0],
    'E Min': [0, 2, 2, 0, 0, 0],
    'F Maj': [1, 3, 3, 2, 1, 1],
    'F Min': [1, 3, 3, 1, 1, 1],
    'F# Maj': [2, 4, 4, 3, 2, 2],
    'F# Min': [2, 4, 4, 2, 2, 2],
    'G Maj': [3, 5, 5, 4, 3, 3],
    'G Min': [3, 5, 5, 3, 3, 3],
    'G# Maj': [4, 6, 6, 5, 4, 4],
    'G# Min': [4, 6, 6, 4, 4, 4]
}

second_position_barre_chords = {
    'A Maj': ['x', 0, 2, 2, 2, 0],
    'A Min': ['x', 0, 2, 2, 1, 0],
    'A# Maj': ['x', 1, 3, 3, 3, 1],
    'A# Min': ['x', 1, 3, 3, 2, 1],
    'B Maj': ['x', 2, 4, 4, 4, 2],
    'B Min': ['x', 2, 4, 4, 3, 2],
    'C Maj': ['x', 3, 5, 5, 5, 3],
    'C Min': ['x', 3, 5, 5, 4, 3],
    'C# Maj': ['x', 4, 6, 6, 6, 4],
    'C# Min': ['x', 4, 6, 6, 5, 4],
    'D Maj': ['x', 5, 7, 7, 7, 5],
    'D Min': ['x', 5, 7, 7, 6, 5],
    'D# Maj': ['x', 6, 8, 8, 8, 6],
    'D# Min': ['x', 6, 8, 8, 7, 6],
    'E Maj': ['x', 7, 9, 9, 9, 7],
    'E Min': ['x', 7, 9, 9, 8, 7],
    'F Maj': ['x', 8, 10, 10, 10, 8],
    'F Min': ['x', 8, 10, 10, 9, 8],
    'F# Maj': ['x', 9, 11, 11, 11, 9],
    'F# Min': ['x', 9, 11, 11, 10, 9],
    'G Maj': ['x', 10, 12, 12, 12, 10],
    'G Min': ['x', 10, 12, 12, 11, 10],
    'G# Maj': ['x', 11, 13, 13, 13, 11],
    'G# Min': ['x', 11, 13, 13, 12, 11]
}

#* Fretboard Class ===============================================#
# maps notes for each string on fretboard using functions inside class.
class Fretboard:
    def __init__(self, tuning=['E', 'A', 'D', 'G', 'B', 'E']):
        self.tuning = tuning
        self.strings = self.map_fretboard()
        
    def map_fretboard(self):
        strings_mapping = {}
        for string_number, root_note in enumerate(self.tuning, start=1):
            strings_mapping[f'string_{string_number}'] = self.generate_string_notes(root_note)
        return strings_mapping

    def generate_string_notes(self, root_note):
        note_positions = []
        root_index = allo_notes.index(root_note)
        for i in range(15):  # Assuming 15 frets
            note = allo_notes[(root_index + i) % len(allo_notes)]
            note_positions.append(note)
        return note_positions
    
    def find_note_positions(self, note):
        tab = {}
        for string, notes in self.strings.items():
            positions = [i for i, n in enumerate(notes) if n == note]
            tab[string] = positions if positions else ['-']
        return tab

fretboard = Fretboard()  # Initialize fretboard with default tuning

#* Regex dictionaries to sanitize user input===========================#
chord_type_mapping = {
    r'major': 'Maj',
    r'maj': 'Maj',
    r'minor': 'Min',
    r'min': 'Min',
    r'diminished': 'Dim',
    r'dim': 'Dim',
    r'dominant': 'Dom',
    r'dom': 'Dom',
    r'augmented': 'Aug',
    r'aug': 'Aug',
    r'suspended': 'Sus',
    r'sus': 'Sus',
    r'add': 'Add'
}

flat_to_sharp = {
    'Ab': 'G#',
    'Bb': 'A#',
    'Cb': 'B',
    'Db': 'C#',
    'Eb': 'D#',
    'Fb': 'E',
    'Gb': 'F#'
}

def sanitize_chord_input(user_input):
    user_input = user_input.strip().lower()
    match = re.search(r'(\d+)', user_input)
    number_part = match.group(0) if match else ''
    chord_base = user_input.replace(number_part, '')
    for pattern, abbreviation in chord_type_mapping.items():
        if re.search(pattern, chord_base):
            return abbreviation + number_part
    return None

def sanitize_root_note_input(user_input):
    user_input = user_input.strip().capitalize()
    if re.match(r'^[A-Ga-g]b$', user_input):
        user_input = flat_to_sharp.get(user_input, user_input)
    return user_input

#* Generating chord notes and positions ===========================#
# using modulo in chord notes fn due to cyclical nature of music notes in octave.

def get_chord_notes(root_note, chord_type):
    root_index = allo_notes.index(root_note)
    intervals = chord_rules[chord_type]
    chord_notes = [allo_notes[(root_index + interval) % len(allo_notes)] for interval in intervals]
    return chord_notes

def get_chord_positions(chord_notes):
    positions_dict = {}
    for note in chord_notes:
        positions = fretboard.find_note_positions(note)
        positions_dict[note] = positions
    return positions_dict

#* Initialising Solvers with prior solutions and output format functions ===============#

# Check if previous (tab) solution already exists (no duplicate solutions generated!)
def is_new_tab_solution(previous_solutions, new_solution):
    return not any(new_solution == prev for prev in previous_solutions)

# Check if previous (fingering) solution already exists (no duplicate solutions generated!)
def is_new_fingering_solution(tab, previous_fingerings, new_fingering):
    return not any(new_fingering == prev_fingering for prev_fingering in previous_fingerings.get(tab, []))

# Returns the solutions as a lists so get full tab 
def get_solution_as_list(solver, string_states):
    return [solver.Value(fret_var) for fret_var in string_states.values()]


#* CPT Solver One (tab output) ===========================#

#note: IntVar from CP takes (lb, ub, name). 
# BoolVar: just takes name and is T/F.

def solve_chord_positions(chord_notes, fretboard, allow_muted_strings = True, max_fret_diff = 3):
    model = cp_model.CpModel()
    string_states = {}
  # creating variables of strings which takes notes/fret as values (different if muted strings allowed). 
    for string in fretboard.strings:
        if allow_muted_strings:
            string_states[string] = model.NewIntVar(-1, 15, f"{string}_state")  # Allow -1 for muted strings
        else:
            string_states[string] = model.NewIntVar(0, 15, f"{string}_state")  # Do not allow muted strings

    # Ensure each string plays only notes in the chord or is muted
    # allo notes are all notes in octave without octave information for modulo purposes.
    for string, fret_var in string_states.items():
        allowed_frets = [(-1,)] if allow_muted_strings else []  # Add -1 for muted string if allowed
        for fret in range(16):  # Including 15 frets plus open string
            #Horrible code below! finds index of open string so then to index allo notes to ecah string so can acurately return fret position of each note on string
            note = allo_notes[(allo_notes.index(fretboard.strings[string][0]) + fret) % len(allo_notes)]
            #Then checks if fret is in the chord provided and removes unallowed frets from each string.
            if note in chord_notes:
                allowed_frets.append((fret,))  # Each allowed fret needs to be a tuple?

        #constraints model to only solutions with allowed frets to prevent wrong notes.
        if allowed_frets:
            model.AddAllowedAssignments([fret_var], allowed_frets)

    #initialsie new variabels for min and max relative fret to calculate hand span
    frets_pressed = [model.NewBoolVar(f"{string}_pressed") for string in string_states]
    min_fret = model.NewIntVar(0, 15, 'min_fret')
    max_fret = model.NewIntVar(0, 15, 'max_fret')

    for i, (string, fret_var) in enumerate(string_states.items()):
        is_pressed = frets_pressed[i]
        model.Add(fret_var != -1).OnlyEnforceIf(is_pressed)
        model.Add(fret_var == -1).OnlyEnforceIf(is_pressed.Not())
        model.Add(min_fret <= fret_var).OnlyEnforceIf(is_pressed)
        model.Add(max_fret >= fret_var).OnlyEnforceIf(is_pressed)
    
    fret_diff = model.NewIntVar(0, 15, 'fret_diff')
    model.Add(fret_diff == max_fret - min_fret)
    model.Add(fret_diff <= max_fret_diff)

    # Ensure all chord notes are played on some string
    # consider it almost as a trial and error process that checks if the combination of string/notes satisfies all the conditions set out here.
    for note in chord_notes:
        note_played = model.NewBoolVar(f'note_played_{note}')
        string_has_note = []
        for string, fret_var in string_states.items():
            #checks fret of note played to determined the note on a given string.
            note_on_string = model.NewIntVar(0, len(allo_notes) - 1, f"note_on_string_{string}_{note}")
            #ensures that note is based of first fret/0 fret of each string.
            model.AddModuloEquality(note_on_string, allo_notes.index(fretboard.strings[string][0]) + fret_var, len(allo_notes))
            #indicates whether individual string returns a note in chord.
            string_has_note_var = model.NewBoolVar(f'string_{string}_has_note_{note}')
            #appends to a list that aggregates all strings.
            string_has_note.append(string_has_note_var)
            #implied constraint: enforces constraint if chord note on string and not if not
            model.Add(note_on_string == allo_notes.index(note)).OnlyEnforceIf(string_has_note_var)
            model.Add(note_on_string != allo_notes.index(note)).OnlyEnforceIf(string_has_note_var.Not())
        #ensures at least one string plays note in chord and non chord notes are not
        model.AddBoolOr(string_has_note).OnlyEnforceIf(note_played)
        model.AddBoolAnd([x.Not() for x in string_has_note]).OnlyEnforceIf(note_played.Not())
        #the final check that all notes are on at least one string. 
        model.Add(note_played == True)  
    
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0  # Sets a reasonable search limit/come back to? 
    status = solver.Solve(model)
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = [solver.Value(var) for var in string_states.values()]
        return solution
    
    return None

#* CPT Solver Two (Finger output) ===========================#

def solve_fingering(chord_positions, forbidden_fingerings, previous_fingerings, selected_fingers):
    
    model = cp_model.CpModel()
    num_fingers = 5 #including thumb but not working currently!

    #initialising all the variables ==============#
    finger_map = {
        # "thumb": 1,
        "index": 2,
        "middle": 3,
        "ring": 4,
        "pinky": 5
    }
    available_fingers = [finger_map[finger] for finger in selected_fingers]
    print(f"Available fingers: {available_fingers}")

    pressed_strings = [i for i, fret in enumerate(chord_positions) if fret not in [0, 'x', -1]]
    muted_strings = [i for i, fret in enumerate(chord_positions) if fret in ['x', -1]]

    finger_positions = {string: model.NewIntVarFromDomain(cp_model.Domain.FromValues(available_fingers), f"finger_{string}_position") for string in pressed_strings}

    for string_index in pressed_strings:
        bool_vars = []
        for finger in available_fingers:
            bool_var = model.NewBoolVar(f"finger_{finger}_on_string_{string_index + 1}")
            model.Add(finger_positions[string_index] == finger).OnlyEnforceIf(bool_var)
            model.Add(finger_positions[string_index] != finger).OnlyEnforceIf(bool_var.Not())
            bool_vars.append(bool_var)
        model.Add(sum(bool_vars) == 1)

    #finished var init ===================================#
    #constraints begin......

    #CONSTRAINT 1: preferred fingers! 
    # Add penalty variables for not using preferred fingers
    # preferred fingers index and middle (2 and 3)
    penalty_vars = []
    for string_index in pressed_strings:
        is_finger_2 = model.NewBoolVar(f"is_finger_2_{string_index}")
        is_finger_3 = model.NewBoolVar(f"is_finger_3_{string_index}")
        penalty_var = model.NewBoolVar(f"penalty_{string_index}")
        penalty_vars.append(penalty_var)
        #adds penalaty each time preferred finger note used 
        model.Add(finger_positions[string_index] == 2).OnlyEnforceIf(is_finger_2)
        model.Add(finger_positions[string_index] != 2).OnlyEnforceIf(is_finger_2.Not())
        model.Add(finger_positions[string_index] == 3).OnlyEnforceIf(is_finger_3)
        model.Add(finger_positions[string_index] != 3).OnlyEnforceIf(is_finger_3.Not())
        #if penalties not exisitng for string must be 2 or 3 
        model.AddBoolOr([is_finger_2, is_finger_3]).OnlyEnforceIf(penalty_var.Not())
        model.AddBoolAnd([is_finger_2.Not(), is_finger_3.Not()]).OnlyEnforceIf(penalty_var)
    #guides solver to solutions where penalties are minimsed.
    model.Minimize(sum(penalty_vars))

    # Determine the minimum fret to use as the reference point for relative positioning
    min_fret = min(fret for fret in chord_positions if fret not in [0, 'x', -1])

    # CONSTRAINT 2: Natural Fingering Positions
    # Hard constraining certain fingers to certain relative positions
    for string_index, fret in enumerate(chord_positions):
        if string_index in pressed_strings:
            relative_fret = fret - min_fret
            if relative_fret == 0:
                is_thumb = model.NewBoolVar(f"is_thumb_{string_index}")
                is_index = model.NewBoolVar(f"is_index_{string_index}")
                
                if string_index == 0:
                    model.Add(finger_positions[string_index] == 1).OnlyEnforceIf(is_thumb)
                    model.Add(finger_positions[string_index] != 1).OnlyEnforceIf(is_thumb.Not())
                
                model.Add(finger_positions[string_index] == 2).OnlyEnforceIf(is_index)
                model.Add(finger_positions[string_index] != 2).OnlyEnforceIf(is_index.Not())
                
                model.AddBoolOr([is_thumb, is_index] if string_index == 0 else [is_index])
            elif relative_fret == 1:
                #!changed so ring is not included on relative fret 1 [IGNORE THIS, SAVED AS DONT WANT TO LOSE THIS PART BUT IRRELEVANT!]
                is_middle = model.NewBoolVar(f"is_middle_{string_index}")
                # is_ring = model.NewBoolVar(f"is_ring_{string_index}")
                
                model.Add(finger_positions[string_index] == 3).OnlyEnforceIf(is_middle)
                model.Add(finger_positions[string_index] != 3).OnlyEnforceIf(is_middle.Not())
                
                # model.Add(finger_positions[string_index] == 4).OnlyEnforceIf(is_ring)
                # model.Add(finger_positions[string_index] != 4).OnlyEnforceIf(is_ring.Not())
                
                # model.AddBoolOr([is_middle, is_ring])
                #!added this to ensure that C major works - may have to remove. Explicitly removes possibility of other fingers on rel fret 1
                model.Add(finger_positions[string_index] != 1)
                model.Add(finger_positions[string_index] != 2)
                model.Add(finger_positions[string_index] != 4)
                model.Add(finger_positions[string_index] != 5)
            elif relative_fret == 2:
                is_middle = model.NewBoolVar(f"is_middle_{string_index}")
                is_ring = model.NewBoolVar(f"is_ring_{string_index}")
                is_pinky = model.NewBoolVar(f"is_pinky_{string_index}")
                
                model.Add(finger_positions[string_index] == 3).OnlyEnforceIf(is_middle)
                model.Add(finger_positions[string_index] != 3).OnlyEnforceIf(is_middle.Not())
                
                model.Add(finger_positions[string_index] == 4).OnlyEnforceIf(is_ring)
                model.Add(finger_positions[string_index] != 4).OnlyEnforceIf(is_ring.Not())
                
                model.Add(finger_positions[string_index] == 5).OnlyEnforceIf(is_pinky)
                model.Add(finger_positions[string_index] != 5).OnlyEnforceIf(is_pinky.Not())
                
                model.AddBoolOr([is_middle, is_ring, is_pinky])
            elif relative_fret == 3:
                is_ring = model.NewBoolVar(f"is_ring_{string_index}")
                is_pinky = model.NewBoolVar(f"is_pinky_{string_index}")
                
                model.Add(finger_positions[string_index] == 4).OnlyEnforceIf(is_ring)
                model.Add(finger_positions[string_index] != 4).OnlyEnforceIf(is_ring.Not())
                
                model.Add(finger_positions[string_index] == 5).OnlyEnforceIf(is_pinky)
                model.Add(finger_positions[string_index] != 5).OnlyEnforceIf(is_pinky.Not())
                
                model.AddBoolOr([is_ring, is_pinky])
            elif relative_fret >= 4:
                model.Add(finger_positions[string_index] == 5)  # Pinky on higher frets

    #CONSTRAINT 3: SINGLE FINGER EXCLUDED FROM SPANNING MULTIPLE FRETS
    for i in range(len(pressed_strings)):
            for j in range(i + 1, len(pressed_strings)):
                string_i = pressed_strings[i]
                string_j = pressed_strings[j]
                model.Add(finger_positions[string_i] != finger_positions[string_j]).OnlyEnforceIf(chord_positions[string_i] != chord_positions[string_j])
    same_fret = {}
    for fret in set(chord_positions):
        if fret not in [0, 'x', -1]:
            same_fret[fret] = [i for i, f in enumerate(chord_positions) if f == fret]

    print(f"Same fret positions are now: {same_fret}")

    # CONSTRAINT 4: NON-ADJACENT BARRING EXCLUSION
    lowest_fret = min(same_fret.keys())
    
    for fret, strings in same_fret.items():
        if len(strings) > 1 and fret != lowest_fret:
            strings.sort()
            for i in range(len(strings)):
                for j in range(i + 1, len(strings)):
                    if strings[j] - strings[i] > 1:  # Non-adjacent strings
                        # Check for any conflicting note between strings[i] and strings[j]
                        conflict = any(chord_positions[k] != fret and chord_positions[k] not in [0, 'x', -1] for k in range(strings[i] + 1, strings[j]))
                        if conflict:
                            model.Add(finger_positions[strings[i]] != finger_positions[strings[j]])
                            print(f"Enforcing non-adjacent constraint: {strings[i]} and {strings[j]} cannot share the same finger on fret {fret}")
                        else:
                            print(f"Allowing barre: {strings[i]} and {strings[j]} can share the same finger on fret {fret}")

    # CONSTRAINT 5: encourage barring with one finger
    penalty_same_finger = model.NewIntVar(0, 100, 'penalty_same_finger')
    penalty_sum_same_finger = []
    for i, string_index in enumerate(pressed_strings):
        for j, next_string_index in enumerate(pressed_strings):
            if i != j and chord_positions[string_index] == chord_positions[next_string_index]:
                violation = model.NewBoolVar(f"violation_same_finger_{i}_{j}")
                model.Add(finger_positions[string_index] != finger_positions[next_string_index]).OnlyEnforceIf(violation)
                model.Add(finger_positions[string_index] == finger_positions[next_string_index]).OnlyEnforceIf(violation.Not())
                penalty_sum_same_finger.append(violation)
    model.Add(penalty_same_finger == sum(penalty_sum_same_finger))
    model.Minimize(penalty_same_finger)

    # Add hard constraint to ensure thumb is only used on the low E string NOT WORKING!
    for string_index in pressed_strings:
        if string_index != 0:
            model.Add(finger_positions[string_index] != 1)  # Thumb must not be used on strings other than the low E string
    print("Checking forbidden fingerings...")
    for forbidden_fingering in forbidden_fingerings:
        print(f"Forbidden fingering: {forbidden_fingering}")
        forbidden_conditions = []
        for string, finger in forbidden_fingering.items():
            forbidden_var = model.NewBoolVar(f'forbidden_finger_{finger}_on_string_{string}')
            model.Add(finger_positions[string] == finger).OnlyEnforceIf(forbidden_var)
            model.Add(finger_positions[string] != finger).OnlyEnforceIf(forbidden_var.Not())
            forbidden_conditions.append(forbidden_var)
        model.AddBoolOr([var.Not() for var in forbidden_conditions])


    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0  # Set a reasonable search limit
    status = solver.Solve(model)
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = {string: solver.Value(finger_positions[string]) for string in pressed_strings}
        print(f"New finger positions: {solution}")
        return solution
    print("No feasible solution found")
    return None


# Use Chord dictionaaries before Solver 1 ===========================#

chord_dictionaries = [first_position_chords, barre_chords, second_position_barre_chords]  # Current chord dictionaries

def solve_chord_positions_from_dict(chord_notes, chord_dict):
    print(f"Solving chord positions for chord notes: {chord_notes}")  # Debugging statement

    for chord_name, chord_positions in chord_dict.items():
        if set(chord_notes) == set(get_chord_notes(chord_name.split()[0], chord_name.split()[1])):
            print(f"Match found: {chord_name} -> {chord_positions}")  # Debugging statement

            return chord_positions
    print("No match found in dictionary.")  # Debugging statement

    return None

#! DONT BELIEVE THIS DOES ANYTHING BUT KEEPING INCASE :/!
# def generate_chord(root_note, chord_type):

#     chord_notes = get_chord_notes(root_note, chord_type)
    
#     # Try to find chord positions in the predefined dictionaries
#     chord_dictionaries = [first_position_chords, barre_chords, second_position_barre_chords]
#     for chord_dict in chord_dictionaries:
#         chord_positions = solve_chord_positions_from_dict(chord_notes, chord_dict)
#         if chord_positions:
#             break
#     else:
#         # If no positions found in dictionaries, use the solver
#         chord_positions = solve_chord_positions(chord_notes, fretboard)
    
#     if chord_positions:
#         forbidden_fingerings = []
#         previous_fingerings = {tuple(chord_positions): []}
#         finger_positions = solve_fingering(chord_positions, forbidden_fingerings, previous_fingerings)
#         if finger_positions:
#             return {
#                 "chord_notes": chord_notes,
#                 "chord_positions": chord_positions,
#                 "finger_positions": finger_positions
#             }
#     return None

#* Display solution in readable format ===========================#
def display_solution(chord_positions, finger_positions, fretboard):
    string_mapping = {
    0: 'low E string',
    1: 'A string',
    2: 'D string',
    3: 'G string',
    4: 'B string',
    5: 'high E string'
    }
    finger_mapping = {
    1: 'thumb',
    2: 'index finger',
    3: 'middle finger',
    4: 'ring finger',
    5: 'pinky finger'
    }
    
    tab_positions = chord_positions
    print(f"Tab Generated: {tab_positions}")
    
    for string_index, fret in enumerate(chord_positions):
        string = string_mapping[string_index]
        if fret == 0:
            print(f"For the {string}, use open string")
        elif fret in [-1, 'x']:
            print(f"For the {string}, mute the string")
        else:
            finger = finger_positions.get(string_index, None)
            if finger:
                finger_name = finger_mapping.get(finger, f"unknown finger {finger}")
                print(f"For the {string}, use {finger_name} on fret {fret}")
            else:
                print(f"For the {string}, no finger assigned on fret {fret}")
            