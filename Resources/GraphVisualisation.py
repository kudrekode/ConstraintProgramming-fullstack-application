
#!For Chord Solver Constraint Function visualisation
#using graphiz to create a node diagram for the first constraint solver (tab generator)
from graphviz import Digraph

def create_constraint_graph():
    dot = Digraph(comment='Simplified Guitar Tablature Constraints', engine='dot')
    dot.attr(rankdir='LR')  # Left to right instead of top to bottom

    dot.node('String_1', 'String 1 (E)')
    dot.node('String_2', 'String 2 (A)')
    dot.node('String_3', 'String 3 (D)')
    dot.node('String_4', 'String 4 (G)')
    dot.node('String_5', 'String 5 (B)')
    dot.node('String_6', 'String 6 (e)')

    dot.node('Note_C', 'Chord Note: C', shape='ellipse')
    dot.node('Note_E', 'Chord Note: E', shape='ellipse')
    dot.node('Note_G', 'Chord Note: G', shape='ellipse')

    # Hand span constraint
    dot.node('Min_Fret', 'Min Fret', shape='box')
    dot.node('Max_Fret', 'Max Fret', shape='box')
    dot.node('Fret_Diff', 'Fret Difference', shape='box')

    # Connection between strings and chord notes
    for string in ['String_1', 'String_2', 'String_3', 'String_4', 'String_5', 'String_6']:
        dot.edge(string, 'Note_C')
        dot.edge(string, 'Note_E')
        dot.edge(string, 'Note_G')

    # Connection between string frets to fret diff
    for string in ['String_1', 'String_2', 'String_3', 'String_4', 'String_5', 'String_6']:
        dot.edge(string, 'Min_Fret')
        dot.edge(string, 'Max_Fret')

    dot.edge('Min_Fret', 'Fret_Diff')
    dot.edge('Max_Fret', 'Fret_Diff')

    # Render the actual file and show by default too
    dot.render('simplified_constraint_graph.gv', view=True) 

create_constraint_graph()


#!For Fingering Generator Constraint Function visualisation
#using graphiz to create a node diagram for the second constraint solver (finger assigner)
from graphviz import Digraph

def create_compact_vertical_graph():
    dot = Digraph(comment='Compact Vertical Soft and Hard Constraints', engine='dot')

    # Changed the dimensions so it fits into my word doc lol
    dot.attr(size="3,8", ranksep='.5', nodesep='0.2', rankdir='LR')  
    
    # String and fingers init
    dot.node('String X', 'String X')
    dot.node('Fingers_X', 'Fingers for String X\n(Index, Middle, Ring, Pinky)', width="2")  # Multiline to reduce width
    dot.edge('String X', 'Fingers_X')

    # Constraints with different edge styles (dotted for soft, solid for hard) for formatting/readability in my word doc
    # Soft constraints
    dot.node('Finger Priority (Index/Middle)', 'Finger Priority\n(Index/Middle)', shape='ellipse', style='dotted', width="1.5")
    dot.edge('Fingers_X', 'Finger Priority (Index/Middle)', style='dotted')
    
    dot.node('Natural Fingering', 'Natural Fingering\n(Index on Fret 1, etc.)', shape='ellipse', style='dotted', width="1.5")
    dot.edge('Fingers_X', 'Natural Fingering', style='dotted')
    
    dot.node('Encourage Barring', 'Encourage Barring', shape='ellipse', style='dotted', width="1.5")
    dot.edge('Fingers_X', 'Encourage Barring', style='dotted')

    # Hard constraints
    dot.node('First Position Constraint', 'First Position Constraint', shape='ellipse', style='solid', width="1.5")
    dot.edge('Fingers_X', 'First Position Constraint', style='solid')

    dot.node('Exclude Finger Bridges', 'Exclude Finger Bridges', shape='ellipse', style='solid', width="1.5")
    dot.edge('Fingers_X', 'Exclude Finger Bridges', style='solid')

    dot.node('Exclude Span Multiple Frets', 'Exclude Finger Span Multiple Frets', shape='ellipse', style='solid', width="1.5")
    dot.edge('Fingers_X', 'Exclude Span Multiple Frets', style='solid')

    # Render the actual file and show by default too
    dot.render('compact_vertical_graph.gv', view=True)

create_compact_vertical_graph()



