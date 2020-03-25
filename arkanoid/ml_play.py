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
    place_check=75
    placex=0
    placey=0 
    bricks=[]
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
   
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
            change_D=False
            ball_place=(95,395)        
            placex=0
            placey=0 
            bricks=scene_info.bricks
            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()           
            continue
       
       
        # 3.3. Put the code here to handle the scene information
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True  
            ball_place=scene_info.ball 
            bricks=scene_info.bricks
            #print(len(scene_info.bricks),scene_info.bricks)
            continue   
        elif ball_served:
            if placex!=scene_info.ball[0]-ball_place[0] or placey>scene_info.ball[1]-ball_place[1]:
                change_D=True
            placex=scene_info.ball[0]-ball_place[0]             
            placey=scene_info.ball[1]-ball_place[1] 
            ball_place=scene_info.ball 
        # the ball pull up
        if  placey<0:
            change_D=True
            if(placex>0):
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                #print("UR")
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                #print("UL")
        # the ball going down
        else:
            if change_D==True:
                change_D=False
                #ball - platform length
                dy= (395-scene_info.ball[1])//placey
                # ball play to right
                if placex>0:
                    dx=(200-scene_info.ball[0])//placex   #ball to right length
                    if(dx>dy):
                        place_check=scene_info.ball[0]+dy*placex 
                    else:
                        place_check=(dy-dx)*placex % 200                                                         
                        if (dy-dx)*placex//200%2==0:
                            place_check=200-place_check
                        #print("pp")                                                                                   
                # ball play to left                   
                else:
                    dx=scene_info.ball[0]//abs(placex)
                    if(dx>dy):
                        place_check=scene_info.ball[0]-dy*abs(placex)
                        #print("q")  
                    else:
                        place_check=(dy-dx)*abs(placex)%200
                        if (dy-dx)*abs(placex)//200%2==1:
                            place_check=200-place_check
                        #print("qq")  
               # print(placex,placey)
            #check if there is barrier on the path
            #move the platform  
            if scene_info.platform[0]+10>place_check :
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                #print("DL")
            elif scene_info.platform[0]+30<place_check:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                #print("DR")
        if len(bricks)>len(scene_info.bricks):
            retD = list(set(bricks).difference(set(scene_info.bricks)))
           # print(scene_info.ball)
           # print(retD[0],"==")
            
            bricks=scene_info.bricks
    


        
       
         
