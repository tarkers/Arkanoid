"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    change_D=False
    change=0                #calculate the prediction
    place_check=75          #set the prediction point
    placex=0                #x,y +- about direction
    placey=0 
    ball_place=(95,395)     # frame of ball place
    save_place=0
    check_place=False
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    distance=0
    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False
            ball_place=(95,395)        
            placex=0
            placey=0
            change=0            
            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()           
            continue
       
       
        # 3.3. Put the code here to handle the scene information
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True  
            ball_place=scene_info.ball 
            continue   
        elif ball_served:                     
            tmpx=scene_info.ball[0]-ball_place[0]
            if placex!=tmpx and scene_info.ball[0]>10 and scene_info.ball[0]<185:
                check_place=False
            placex=tmpx  
            placey=scene_info.ball[1]-ball_place[1] 
            ball_place=scene_info.ball 
        # the ball pull up follow the ball
        if  placey< 0:                     
            change_D=False     
            check_place=False
            save_place=0       
            if scene_info.ball[1]<300:              
                if scene_info.platform[0]<80:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                elif scene_info.platform[0]>80:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)              
            else:

                if(placex>0):
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
 
        # the ball going down
        elif scene_info.ball[1]>=260:
            tmpy=395-scene_info.ball[1]
            if check_place==False:
                check_place=True               
                #speed up
                if abs(placex)>7:
                    #save_place=200-save_place
                    if placex>0:
                       save_place=scene_info.ball[0]+tmpy*1.42
                       if save_place>195:
                           save_place=390-save_place
                    else:
                        save_place=abs(scene_info.ball[0]-tmpy*1.42) 
                #not speed up
                else:
                    if placex>0:
                       save_place=scene_info.ball[0]+tmpy
                       if save_place>195:
                           save_place=390-save_place
                    else:
                        save_place=abs(scene_info.ball[0]-tmpy)
                save_place=int(save_place)
                #print(save_place,scene_info.ball[0],placex,scene_info.ball[1]/7,tmpy)
            if scene_info.ball[1]>390:
                    if placex>0:
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                    else:
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif scene_info.platform[0]+20<save_place:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif scene_info.platform[0]+20>save_place:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)  
            if abs(save_place-scene_info.platform[0])<3:
                save_place=scene_info.platform[0]
            print(save_place,scene_info.platform[0],scene_info.ball[0])            
        else:            
             comm.send_instruction(scene_info.frame, PlatformAction.NONE)

           
        
    
    


        
       
         
