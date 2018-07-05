#SpnTUI.py

"""
Asciimatics colours
BLACK
BLUE
CYAN
GREEN
MAGENTA
RED
WHITE
YELLOW
"""


import traceback
import better_exceptions
import asciimatics
from asciimatics.screen import Screen
from spoon_logging import D, L, W, E
import SpoonModes
SM = SpoonModes.SpoonSliceModes()
LM = SpoonModes.SpoonLoopModes()

#12345678901234567890123456789012345678901234567890
DESC_NAME = """
░█▀▀░█▀█░█▀█░█▀█░█▀█░░░█▀▀░▀█▀░█▀▀░█░█░▀█▀
░▀▀█░█▀▀░█░█░█░█░█░█░░░█▀▀░░█░░█░█░█▀█░░█░
░▀▀▀░▀░░░▀▀▀░▀▀▀░▀░▀░░░▀░░░▀▀▀░▀▀▀░▀░▀░░▀░

 """
 
DESC_LINE1="""░█▀▀░█▀█░█▀█░█▀█░█▀█░░░█▀▀░▀█▀░█▀▀░█░█░▀█▀"""
DESC_LINE2="""░▀▀█░█▀▀░█░█░█░█░█░█░░░█▀▀░░█░░█░█░█▀█░░█░"""
DESC_LINE3="""░▀▀▀░▀░░░▀▀▀░▀▀▀░▀░▀░░░▀░░░▀▀▀░▀▀▀░▀░▀░░▀░"""
 
 # Logo width is 41??

#this sets 

global_status = None
the_screen = None

first_time_draw = True

def fill_line(screen,line,char=' ', background=Screen.COLOUR_BLACK):
    for i in range(screen.width):
        screen.print_at(char,i,line,bg=background)
    return

LOOP_BLOCK_HEIGHT=2
LOOP_START_LINE=1

def get_loop_fg_colour(loop_mode):
    switcher={
        LM.PLAY : Screen.COLOUR_BLACK,  #bg is green
        LM.STOP : Screen.COLOUR_WHITE,
        LM.RANDOM : Screen.COLOUR_WHITE,
        LM.REVERSE : Screen.COLOUR_RED,
        LM.PLAY_SLAVE : Screen.COLOUR_WHITE,
        LM.PLAY_MASTER : Screen.COLOUR_WHITE
    }
    if loop_mode in switcher.keys():
        return switcher.get(loop_mode)
    else:
        return Screen.COLOUR_WHITE

def get_loop_bg_colour(loop_mode):
    switcher={
        LM.PLAY : Screen.COLOUR_GREEN,  #bg is green
        LM.STOP : Screen.COLOUR_BLACK,
        LM.RANDOM : Screen.COLOUR_BLUE,
        LM.REVERSE : Screen.COLOUR_CYAN,
        LM.PLAY_SLAVE : Screen.COLOUR_BLACK,
        LM.PLAY_MASTER : Screen.COLOUR_RED
    }
    if loop_mode in switcher.keys():
        return switcher.get(loop_mode)
    else:
        return Screen.COLOUR_WHITE

def get_slice_fg_colour(slice_mode):
    # returns forground colour of the slice
    switcher={
        SM.PLAY : Screen.COLOUR_BLACK,  #bg is green
        SM.MUTE : Screen.COLOUR_WHITE, #bg is red
        SM.RANDOM : Screen.COLOUR_WHITE, #bg is white 
        SM.SKIP : Screen.COLOUR_WHITE, #bg is black
        SM.REVERSE : Screen.COLOUR_RED, #bg is yellow
        SM.DOUBLE : Screen.COLOUR_WHITE, #bg is magenta
        SM.HALF : Screen.COLOUR_WHITE    #bg is cyan  
    }  
    if slice_mode in switcher.keys():
        return switcher.get(slice_mode)
    # else return as default
    return Screen.COLOUR_WHITE

def get_slice_bg_colour(slice_mode):
    # returns forground colour of the slice
    switcher={
        SM.PLAY : Screen.COLOUR_GREEN,  #bg is green
        SM.MUTE : Screen.COLOUR_RED, #bg is red
        SM.RANDOM : Screen.COLOUR_BLUE, #bg is white 
        SM.SKIP : Screen.COLOUR_BLACK, #bg is black
        SM.REVERSE : Screen.COLOUR_YELLOW, #bg is yellow
        SM.DOUBLE : Screen.COLOUR_MAGENTA, #bg is magenta
        SM.HALF : Screen.COLOUR_CYAN    #bg is cyan  
    }    
    if slice_mode in switcher.keys():
        return switcher.get(slice_mode)
    # else return as default
    return Screen.COLOUR_BLACK


def draw_loop_slices(screen, loop_to_display, x_start, y_start):
    # 
    index = 0
    PRNT ="={}="
    
    for s in loop_to_display.audio_slices:
        x_loc = x_start + 5*index
        screen.print_at(PRNT.format(s.play_mode), x_loc, y_start, colour=get_slice_fg_colour(s.play_mode),bg=get_slice_bg_colour(s.play_mode))
        index+=1
    
    return

def draw_loop_box(screen,loop_to_display, loop_number):
    loop_y_offset = (LOOP_BLOCK_HEIGHT+1)*loop_number+LOOP_START_LINE
    fill_line(screen, loop_y_offset, background=Screen.COLOUR_WHITE)
    fill_line(screen, loop_y_offset+1, background=Screen.COLOUR_WHITE)
    screen.print_at(loop_to_display.name, 0, loop_y_offset, colour=Screen.COLOUR_BLUE, bg=Screen.COLOUR_WHITE)
    screen.print_at(":{}".format(loop_to_display.current_slice),7, loop_y_offset, colour=Screen.COLOUR_RED, bg=Screen.COLOUR_WHITE)
    screen.print_at(":[",9, loop_y_offset, colour=Screen.COLOUR_BLACK, bg=Screen.COLOUR_WHITE )
    screen.print_at("]",51, loop_y_offset, colour=Screen.COLOUR_BLACK, bg=Screen.COLOUR_WHITE )
    screen.print_at(loop_to_display.audio_file_name, 0, loop_y_offset+1, colour=Screen.COLOUR_BLACK,bg=Screen.COLOUR_WHITE )  
    
    screen.print_at(":[",52, loop_y_offset, colour=Screen.COLOUR_BLACK, bg=Screen.COLOUR_WHITE )
    fgc = get_loop_fg_colour(loop_to_display.loop_mode)
    bgc = get_loop_bg_colour(loop_to_display.loop_mode)
    
    screen.print_at(loop_to_display.loop_mode, 54, loop_y_offset, colour=fgc, bg=bgc)
    screen.print_at("]",60, loop_y_offset, colour=Screen.COLOUR_BLACK, bg=Screen.COLOUR_WHITE )
    
    draw_loop_slices( screen, loop_to_display, 11, loop_y_offset)    
    return

def display_messages(screen, the_status):
    y_offset = 17
    
    #clean the area
    for i in range(5):
        fill_line(screen, y_offset+i, background=Screen.COLOUR_BLACK)
    
    # lets display the last 5 messages
    if( len(the_status.event_history)>4 ):
        for mes_s in the_status.event_history[-5:]:
            screen.print_at(mes_s,1, y_offset, colour=Screen.COLOUR_WHITE, bg=Screen.COLOUR_BLACK )
            y_offset+=1
    else:
        for mes_s in the_status.event_history:
            screen.print_at(mes_s,1, y_offset, colour=Screen.COLOUR_WHITE, bg=Screen.COLOUR_BLACK )
            y_offset+=1
    
    return
    
def draw_the_tui(screen, the_status ):
    # draw top border
    #screen.move(0,0)
    #fill_line(screen,0)
        
    global first_time_draw
    
    if(first_time_draw):
        #draw LOGO
        screen.move(0,0)
        screen.centre(DESC_LINE1,0)
        screen.centre(DESC_LINE2,1)
        screen.centre(DESC_LINE3,2)
        #draw bottom border
        fill_line(screen,screen.height-1,background=Screen.COLOUR_YELLOW)
        # write the quite message
        screen.print_at(u'☠  press q to quit  ☠    press m to mute', 2, screen.height-1, attr=Screen.A_BOLD, colour=Screen.COLOUR_RED,bg=Screen.COLOUR_YELLOW)
      
        #draw seperator line
        fill_line(screen,3,char='=')
        #draw slice identifier names
        screen.print_at("0----1----2----3----4----5----6----7", 13,3,colour=Screen.COLOUR_WHITE, bg=Screen.COLOUR_BLACK)
        #draw seperator line
        fill_line(screen,15,char='=')
        
        first_time_draw = False
        
    
    draw_loop_box(screen, the_status.loops['/loop/1'] , 1)
    draw_loop_box(screen, the_status.loops['/loop/2'] , 2)
    draw_loop_box(screen, the_status.loops['/loop/3'] , 3)
    draw_loop_box(screen, the_status.loops['/loop/4'] , 4)
    display_messages(screen, the_status) 
    #draw content
    return 1