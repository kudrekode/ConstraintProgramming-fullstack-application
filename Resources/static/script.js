// // * For generating chord via button: 

// Show the help form on page load for the new site survery functionaltiy
document.addEventListener("DOMContentLoaded", function() {
    openForm();
});

function openForm() {
    document.getElementById("myForm").style.display = "block";
    document.addEventListener('click', closeFormOnClickOutside);
}

function closeForm() {
    document.getElementById("myForm").style.display = "none";
    document.removeEventListener('click', closeFormOnClickOutside);
}

function closeFormOnClickOutside(event) {
    var form = document.getElementById("myForm");
    if (!form.contains(event.target) && !event.target.matches('.help-button')) {
        closeForm();
    }
}
// Finished===========================


// hand span and fret diff interacxrtive elements interactivity defined
var slider_handspan = document.getElementById("max_fret_diff");
var output = document.getElementById("handspan_value");

output.innerHTML = slider_handspan.value;
slider_handspan.setAttribute('data-value', slider_handspan.value);

slider_handspan.oninput = function() {
    output.innerHTML = this.value;
    this.setAttribute('data-value', this.value);
}
// finished ===========================


// button listeners ===========================
document.getElementById('newposition').addEventListener('click', async function(event) {
    event.preventDefault();
    generateChord('newposition');
});

document.getElementById('newchord').addEventListener('click', async function(event) {
    event.preventDefault();
    await resetState();
    generateChord('newchord');
});

document.getElementById('newfingers').addEventListener('click', async function(event) {
    event.preventDefault();
    await generateFingering();
});
//finished===========================


// for switching betwen L R ===========================
// !new
document.getElementById('hand-switch').addEventListener('change', function() {
    if (isChordDisplayed) {
        flipChordDisplay();
    }
});

let isChordDisplayed = false;
let currentChordPositions = null;
let currentFingerPositions = null;
// !done
// finished ===========================


// time out functions so user can stop search
let continueSearchFlag = false;
let currentButtonType = '';
let isRequestInProgress = false;

function openTimeoutModal() {
    document.getElementById("timeoutModal").style.display = "block";
}

function closeTimeoutModal() {
    document.getElementById("timeoutModal").style.display = "none";
}

function openNoMoreSolutionsModal() {
    document.getElementById("noMoreSolutionsModal").style.display = "block";
}

function closeNoMoreSolutionsModal() {
    document.getElementById("noMoreSolutionsModal").style.display = "none";
}

function continueSearch() {
    continueSearchFlag = true;
    closeTimeoutModal();
    if (currentButtonType === 'newposition') {
        generateChord('newposition');
    } else if (currentButtonType === 'newfingers') {
        generateFingering();
    }
}

function stopSearch() {
    continueSearchFlag = false;
    closeTimeoutModal();
}
// finished ===========================

// select fingers in use to send via JSONIFTTYTTT
function getSelectedFingers() {
    return Array.from(document.querySelectorAll('input[name="finger"]:checked')).map(checkbox => checkbox.value);
}
// finished ===========================


// generate chord button functionality:
async function generateChord(buttonType) {
    if (isRequestInProgress) return; // Prevent multiple requests
    isRequestInProgress = true;

    const rootNote = document.getElementById('root_note').value;
    const chordType = document.getElementById('chord_type').value;
    const allowMutedStrings = document.getElementById('allow_muted_strings').checked;
    const maxFretDiff = document.getElementById('max_fret_diff').value;
    const isLeftHanded = document.getElementById('hand-switch').checked;

    const selectedFingers = getSelectedFingers();
    console.log('Selected Fingers:', selectedFingers);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
        controller.abort();
        openTimeoutModal();
    }, 10000);

    // POST form with information:
    try {
        const response = await fetch('/generate_chord', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                root_note: rootNote, 
                chord_type: chordType,
                allow_muted_strings: allowMutedStrings,
                max_fret_diff: maxFretDiff,
                resume: continueSearchFlag,
                selected_fingers: selectedFingers
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (response.ok) {
            const result = await response.json();

            // input sanitation:
            const capitalizedrootNote = rootNote.charAt(0).toUpperCase() + rootNote.slice(1);
            const capitalizedchordType = chordType.charAt(0).toUpperCase() + chordType.slice(1);

            // get the returned values from result into right vars
            let chord_positions = result.chord_positions; 
            let finger_positions = result.finger_positions;

            // initialisation necessary of fingers first
            let fingers = [[1,0],[2,0],[3,0],[4,0],[5,0],[6,0]];

            // allow for diff finger types (x)
            for (let i = 0; i < fingers.length && i < chord_positions.length; i++) {
                if (chord_positions[i] === -1) {
                    fingers[i][1] = 'x';
                } else {
                    fingers[i][1] = chord_positions[i];
                }
            }
            console.log(result.finger_positions);

            // key for the transpose fn
            let fret_list = fingers.map(sublist => sublist[1]).filter(fret => fret !== 'x');
            let min_fret = Math.min(...fret_list);
            let max_fret = Math.max(...fret_list);
            let frets = (max_fret - min_fret) + 1;

            let positions;
            if (min_fret <= 1) {
                positions = 1;
            } else if (min_fret > 1) {
                positions = min_fret;
            }

            if (frets > 4) {
                frets = (max_fret - positions) + 1; 
            } else {
                frets = 4;
            }

            // ensures the image is transposed so that not everything is at top of fretboard
            // but number (e.g., 4frt on side is updated properly)
            function transpose(fingers, positions) {
                return fingers.map(finger => {
                    if (finger[1] !== 'x') {
                        return [finger[0], finger[1] - (positions - 1)];
                    }
                    return finger;
                });
            }

            fingers = transpose(fingers, positions);
            console.log("fingers are "+ fingers);

            function addfingertext(fingers, finger_positions) {
                let adjusted_finger_positions = {};
                for (let key in finger_positions) {
                    adjusted_finger_positions[parseInt(key) + 1] = finger_positions[key];
                }

                console.log("Adjusted finger positions:", adjusted_finger_positions);

                for (let i = 0; i < fingers.length; i++) {
                    let string = fingers[i][0];
                    if (adjusted_finger_positions[string] !== undefined) {
                        fingers[i].push(adjusted_finger_positions[string].toString());
                    }
                }

                console.log("Updated fingers list:", fingers);
                return fingers;
            }

            let text_fingers = addfingertext(fingers, finger_positions);

            console.log("current fingers now are :" + text_fingers);

            if (isLeftHanded) {
                text_fingers = text_fingers.map(f => [7 - f[0], ...f.slice(1)]); // Flip strings for left-handed players
            }

            currentChordPositions = chord_positions;
            currentFingerPositions = finger_positions;

            drawChord(capitalizedrootNote, capitalizedchordType, text_fingers, frets, positions);
            isChordDisplayed = true;

        } else {
            const error = await response.json();
            console.error(`Error: ${error.error}`);
            if (error.error === 'No feasible fingering found' || error.error === 'No chord positions found' || error.error === 'timeout') {
                openNoMoreSolutionsModal();
            }
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('An error occurred:', error);
        }
    } finally {
        isRequestInProgress = false; // Reset the flag
    }
}

document.getElementById('newfingers').addEventListener('click', async function(event) {
    event.preventDefault();
    await generateFingering();
});

async function generateFingering() {
    if (isRequestInProgress) return; // Prevent multiple requests
    isRequestInProgress = true;

    const selectedFingers = getSelectedFingers(); // Capture selected fingers
    console.log('Selected Fingers:', selectedFingers); // Debug statement
    const isLeftHanded = document.getElementById('hand-switch').checked;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
        controller.abort();
        openTimeoutModal();
    }, 10000);

    try {
        const response = await fetch('/generate_new_fingering', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ selected_fingers: selectedFingers }), // Include selected fingers
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (response.ok) {
            const result = await response.json();
            console.log('Finger positions received:', result.finger_positions);

            updateFingeringUI(result.chord_positions, result.finger_positions, isLeftHanded);
        } else {
            const error = await response.json();
            console.error(`Error: ${error.error}`);
            if (error.error === 'No feasible fingering found' || error.error === 'No chord positions found' || error.error === 'timeout') {
                openNoMoreSolutionsModal();
            }
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('An error occurred:', error);
        }
    } finally {
        isRequestInProgress = false; // Reset the flag
    }
}

function updateFingeringUI(chordPositions, fingerPositions, isLeftHanded) {
    const capitalizedrootNote = document.getElementById('root_note').value.charAt(0).toUpperCase() + document.getElementById('root_note').value.slice(1);
    const capitalizedchordType = document.getElementById('chord_type').value.charAt(0).toUpperCase() + document.getElementById('chord_type').value.slice(1);

    let fingers = [[1,0],[2,0],[3,0],[4,0],[5,0],[6,0]];

    for (let i = 0; i < fingers.length && i < chordPositions.length; i++) {
        if (chordPositions[i] === -1) {
            fingers[i][1] = 'x';
        } else {
            fingers[i][1] = chordPositions[i];
        }
    }

    let fret_list = fingers.map(sublist => sublist[1]).filter(fret => fret !== 'x');
    let min_fret = Math.min(...fret_list);
    let max_fret = Math.max(...fret_list);
    let frets = (max_fret - min_fret) + 1;

    let positions;
    if (min_fret <= 1) {
        positions = 1;
    } else if (min_fret > 1) {
        positions = min_fret;
    }

    if (frets > 4) {
        frets = (max_fret - positions) + 1; 
    } else {
        frets = 4;
    }

    function transpose(fingers, positions) {
        return fingers.map(finger => {
            if (finger[1] !== 'x') {
                return [finger[0], finger[1] - (positions - 1)];
            }
            return finger;
        });
    }

    fingers = transpose(fingers, positions);

    function addfingertext(fingers, finger_positions) {
        let adjusted_finger_positions = {};
        for (let key in finger_positions) {
            adjusted_finger_positions[parseInt(key) + 1] = finger_positions[key];
        }

        for (let i = 0; i < fingers.length; i++) {
            let string = fingers[i][0];
            if (adjusted_finger_positions[string] !== undefined) {
                fingers[i].push(adjusted_finger_positions[string].toString());
            }
        }

        return fingers;
    }

    let text_fingers = addfingertext(fingers, fingerPositions);

    if (isLeftHanded) {
        text_fingers = text_fingers.map(f => [7 - f[0], ...f.slice(1)]); // Flip strings for left-handed players
    }

    drawChord(capitalizedrootNote, capitalizedchordType, text_fingers, frets, positions);
}

function drawChord(rootNote, chordType, fingers, frets, positions) {
    const fretimageContainer = document.getElementById('fretimage');
    fretimageContainer.innerHTML = '';

    $(document).ready(function() {
        var initialSettings = {
            title: `${rootNote} ${chordType}`,
            color: '#000000',
            strings: 6,
            frets: frets,
            position: positions,
            nutSize: 0.65,
            strokeWidth: 2,
            style: 'normal',
            orientation: 'vertical',
        };

        var initialChord = {
            fingers: fingers,
            barres: [],
        };

        var chart = new svguitar.SVGuitarChord('#fretimage')
            .configure(initialSettings)
            .chord(initialChord)
            .draw();
    });
}

// actual flipping from L to R
function flipChordDisplay() {
    const isLeftHanded = document.getElementById('hand-switch').checked;

    let fingers = [[1,0],[2,0],[3,0],[4,0],[5,0],[6,0]];

    for (let i = 0; i < fingers.length && i < currentChordPositions.length; i++) {
        if (currentChordPositions[i] === -1) {
            fingers[i][1] = 'x';
        } else {
            fingers[i][1] = currentChordPositions[i];
        }
    }

    let fret_list = fingers.map(sublist => sublist[1]).filter(fret => fret !== 'x');
    let min_fret = Math.min(...fret_list);
    let max_fret = Math.max(...fret_list);
    let frets = (max_fret - min_fret) + 1;

    let positions;
    if (min_fret <= 1) {
        positions = 1;
    } else if (min_fret > 1) {
        positions = min_fret;
    }

    if (frets > 4) {
        frets = (max_fret - positions) + 1; 
    } else {
        frets = 4;
    }

    function transpose(fingers, positions) {
        return fingers.map(finger => {
            if (finger[1] !== 'x') {
                return [finger[0], finger[1] - (positions - 1)];
            }
            return finger;
        });
    }

    fingers = transpose(fingers, positions);

    function addfingertext(fingers, finger_positions) {
        let adjusted_finger_positions = {};
        for (let key in finger_positions) {
            adjusted_finger_positions[parseInt(key) + 1] = finger_positions[key];
        }

        for (let i = 0; i < fingers.length; i++) {
            let string = fingers[i][0];
            if (adjusted_finger_positions[string] !== undefined) {
                fingers[i].push(adjusted_finger_positions[string].toString());
            }
        }

        return fingers;
    }

    let text_fingers = addfingertext(fingers, currentFingerPositions);

    if (isLeftHanded) {
        text_fingers = text_fingers.map(f => [7 - f[0], ...f.slice(1)]); // Flip strings for left-handed players
    }

    const capitalizedrootNote = document.getElementById('root_note').value.charAt(0).toUpperCase() + document.getElementById('root_note').value.slice(1);
    const capitalizedchordType = document.getElementById('chord_type').value.charAt(0).toUpperCase() + document.getElementById('chord_type').value.slice(1);

    drawChord(capitalizedrootNote, capitalizedchordType, text_fingers, frets, positions);
}
document.getElementById('newposition').addEventListener('click', async function(event) {
    event.preventDefault();
    generateChord('newposition');
});

document.getElementById('newchord').addEventListener('click', async function(event) {
    event.preventDefault();
    await resetState();
    generateChord('newchord');
});

async function resetState() {
    const response = await fetch('/reset_state', {
        method: 'POST',
    });

    if (!response.ok) {
        console.error('Failed to reset state');
    }
}

// ! Toggle for oirentation:
document.getElementById('hand-switch').addEventListener('change', function() {
    const switchLabel = this.nextElementSibling;
    if (this.checked) {
        switchLabel.setAttribute('data-content', 'R');
    } else {
        switchLabel.setAttribute('data-content', 'L');
    }
});





//for survey function:
document.addEventListener("DOMContentLoaded", function() {
    let state = {
        uniqueChords: new Set(),
        generatedTab: false,
        generatedFingering: false,
        usedCustomization: false
    };

    // Function to update the progress
    function updateProgress() {
        const uniqueChordCheckbox = document.getElementById("uniqueChordCheckbox");
        const newTabCheckbox = document.getElementById("newTabCheckbox");
        const newFingeringCheckbox = document.getElementById("newFingeringCheckbox");
        const customizationCheckbox = document.getElementById("customizationCheckbox");
        const nextPageButton = document.getElementById("nextPageButton");

        uniqueChordCheckbox.checked = state.uniqueChords.size >= 3;
        newTabCheckbox.checked = state.generatedTab;
        newFingeringCheckbox.checked = state.generatedFingering;
        customizationCheckbox.checked = state.usedCustomization;
// allows for aggregation so that survey button is acticvated when completed
        const allConditionsMet = state.uniqueChords.size >= 3 && state.generatedTab && state.generatedFingering && state.usedCustomization;
        nextPageButton.disabled = !allConditionsMet;
    }

    // Event listeners for buttons
    document.getElementById("newchord").addEventListener("click", function() {
        const newChord = `Chord${Math.floor(Math.random() * 100)}`; 
        state.uniqueChords.add(newChord);
        updateProgress();
    });

    document.getElementById("newposition").addEventListener("click", function() {
        state.generatedTab = true;
        updateProgress();
    });

    document.getElementById("newfingers").addEventListener("click", function() {
        state.generatedFingering = true;
        updateProgress();
    });

    // Function to call when any customization tool is used
    function customizationUsed() {
        state.usedCustomization = true;
        updateProgress();
    }

    // Event listeners for customization tools
    document.getElementById("max_fret_diff").addEventListener("change", customizationUsed);
    document.querySelectorAll("input[name='finger']").forEach(element => {
        element.addEventListener("change", customizationUsed);
    });
    document.getElementById("allow_muted_strings").addEventListener("change", customizationUsed);

    // Function to go to the next page 
    // essentially to sureey website
    window.goToNextPage = function() {
        window.location.href = "https://docs.google.com/forms/d/e/1FAIpQLSceHP1TtU_GriPFWEqAN18XqVZjZQzpp9oHBcnMA0v47brmYw/viewform?usp=sf_link"; // Replace with your external survey URL
    };
});
