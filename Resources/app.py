

from flask import Flask, request, jsonify, send_from_directory, session
from backendjune24 import (
    # generate_chord,
    sanitize_chord_input,
    sanitize_root_note_input,
    get_chord_notes,
    solve_chord_positions_from_dict,
    solve_chord_positions,
    solve_fingering,
    fretboard,
    first_position_chords,
    barre_chords,
    second_position_barre_chords,
    is_new_fingering_solution,
    is_new_tab_solution,
    display_solution
)
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

#couldnt get flask to work with directories well so hard coded paths to ensure.
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/styles.css')
def styles():
    return send_from_directory('static', 'styles.css')

@app.route('/script.js')
def script_js():
    return send_from_directory('static', 'script.js')

@app.route('/image-generation.js')
def image_js():
    return send_from_directory('static', 'image-generation.js')

@app.route('/Resources/<path:filename>')
def resources(filename):
    return send_from_directory('static/Resources', filename)

#to ensure that new combinations could be generated by resetting the backend code.
@app.route('/reset_state', methods=['POST'])
def reset_state():
    session.pop('state', None)
    return jsonify({"status": "success"})

#often tuples are needed as doesnt work otherwise so functions to convert to and back from tuple/string
def tuple_to_str(tup):
    return str(tup)

def str_to_tuple(s):
    return eval(s)

from threading import Timer

#for generating the new chord each time
def generate_chord_positions(root_note, chord_type, allow_muted_strings, max_fret_diff, state, timeout=10, resume=False, max_retries=3):
    chord_dictionaries = [first_position_chords, barre_chords, second_position_barre_chords]
    max_iterations = 100

    #init timeout error incase taking too long to generate chord so user can stop process
    class TimeoutError(Exception):
        pass

    def timeout_handler():
        print("Timer expired: Chord generation timed out.")
        raise TimeoutError("Chord generation timed out.")

    # Ensure the timeout is a numeric value as doesnt work otherwise for some reason
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        timeout = 10

    print("Starting chord generation with timeout:", timeout)
    timer = Timer(timeout, timeout_handler)
    timer.start()

    #adding a certain amount of rtries incase no solutions found
    #for some reason doing this allowed for solutions but removing just led to no solutions at all...
    retry_count = 0
    try:
        while retry_count < max_retries:
            state['dictionary_index'] = 0  # Reset dictionary index for each retry
            while state['found_solutions'] < max_iterations:
                print(f"Attempt {retry_count + 1} of {max_retries}, Current dictionary index:", state['dictionary_index'])
                if state['dictionary_index'] < len(chord_dictionaries):
                    chord_positions = solve_chord_positions_from_dict(state['chord_notes'], chord_dictionaries[state['dictionary_index']])
                    if chord_positions:
                        print(f"Found chord positions from dictionary {state['dictionary_index'] + 1}: {chord_positions}")
                    else:
                        print(f"No more positions for dictionary {state['dictionary_index'] + 1}, moving on")
                        state['dictionary_index'] += 1
                        continue
                else:
                    chord_positions = solve_chord_positions(state['chord_notes'], fretboard, allow_muted_strings=allow_muted_strings, max_fret_diff=max_fret_diff)
                    if not chord_positions:
                        print("No chord positions found using solver")
                        break

                if is_new_tab_solution(state['previous_tabs'], chord_positions):
                    print("New tab solution found:", chord_positions)
                    state['previous_tabs'].append(chord_positions)
                    state['chord_positions'] = chord_positions
                    timer.cancel()
                    return state

                state['dictionary_index'] += 1

            retry_count += 1
            print(f"No feasible chord positions found, retrying... ({retry_count}/{max_retries})")

    except TimeoutError as e:
        print("Exception occurred:", e)
        return {"error": "timeout"}
    finally:
        print("Cancelling timer.")
        timer.cancel()

    return None

#send the data to the JS with all the information for the image generation and recieve to send to backend right inpt
@app.route('/generate_chord', methods=['POST'])
def generate_chord_endpoint():
    data = request.json
    chord_type = sanitize_chord_input(data.get('chord_type'))
    root_note = sanitize_root_note_input(data.get('root_note'))
    allow_muted_strings = data.get('allow_muted_strings', False)
    max_fret_diff = int(data.get('max_fret_diff', 4))
    resume = data.get('resume', False)
    max_retries = data.get('max_retries', 3)  # Add max_retries parameter for chord generation

    if chord_type is None or root_note is None:
        return jsonify({"error": "Invalid chord type or root note"}), 400

    if 'state' not in session:
        session['state'] = {
            'found_solutions': 0,
            'previous_tabs': [],
            'previous_fingerings': {},
            'dictionary_index': 0,
            'chord_notes': get_chord_notes(root_note, chord_type)
        }
    state = session['state']

    retry_count = 0
    while retry_count < max_retries:
        print(f"Attempt {retry_count + 1} of {max_retries} to generate chord.")
        state = generate_chord_positions(root_note, chord_type, allow_muted_strings, max_fret_diff, state, resume, max_retries)
        if state is None:
            retry_count += 1
            continue
        elif "error" in state:
            return jsonify({"error": state["error"]}), 408

        chord_positions = state['chord_positions']
        chord_positions_tuple = tuple_to_str(tuple(chord_positions))
        if chord_positions_tuple not in state['previous_fingerings']:
            state['previous_fingerings'][chord_positions_tuple] = []

        forbidden_fingerings = state['previous_fingerings'].get(chord_positions_tuple, [])
        selected_fingers = data.get('selected_fingers', ['index', 'middle', 'ring', 'pinky'])
        finger_positions = solve_fingering(chord_positions, forbidden_fingerings, state['previous_fingerings'][chord_positions_tuple], selected_fingers)

        if finger_positions:
            state['previous_fingerings'][chord_positions_tuple].append(finger_positions)
            session['state'] = state
            return jsonify({
                "chord_notes": state['chord_notes'],
                "chord_positions": chord_positions,
                "finger_positions": finger_positions
            })

        retry_count += 1
        print(f"No feasible fingering found, retrying... ({retry_count}/{max_retries})")

    return jsonify({"error": "No feasible chord positions found after max retries"}), 500

@app.route('/generate_new_fingering', methods=['POST'])
#just for new fingering only 
def generate_new_fingering_endpoint():
    print("Received request to generate new fingering")

    #new:
    data = request.json
    selected_fingers = data.get('selected_fingers', ["thumb", "index", "middle", "ring", "pinky"])
    print('Selected Fingers:', selected_fingers)  # Debug statement
    #end:

    state = session.get('state')
    if not state or 'chord_positions' not in state:
        print("Error: No chord positions found in session")
        return jsonify({"error": "No chord positions found in session"}), 400

    chord_positions = state['chord_positions']
    print(f"Chord positions from session: {chord_positions}")
    chord_positions_tuple = tuple_to_str(tuple(chord_positions))

    if chord_positions_tuple not in state['previous_fingerings']:
        state['previous_fingerings'][chord_positions_tuple] = []

    forbidden_fingerings = state['previous_fingerings'].get(chord_positions_tuple, [])
    print(f"Forbidden fingerings before solving: {forbidden_fingerings}")

    # Ensure forbidden fingerings are in the correct format
    forbidden_fingerings_corrected = []
    for fingering in forbidden_fingerings:
        corrected_fingering = {int(k): int(v) for k, v in fingering.items()}
        forbidden_fingerings_corrected.append(corrected_fingering)
    
    finger_positions = solve_fingering(chord_positions, forbidden_fingerings_corrected, state['previous_fingerings'], selected_fingers)
    
    if finger_positions:
        print(f"Generated new finger positions: {finger_positions}")
        state['previous_fingerings'][chord_positions_tuple].append(finger_positions)
        print(f"Updated forbidden fingerings: {state['previous_fingerings'][chord_positions_tuple]}")
        session['state'] = state
        return jsonify({
            "chord_positions": chord_positions,
            "finger_positions": finger_positions
        })

    print("Error: No feasible fingering found")
    return jsonify({"error": "No feasible fingering found"}), 500

if __name__ == '__main__':
    app.run(debug=True)