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
    bricks=[]               #to see if bricks have decrease
    ball_place=(95,395)     # frame of ball place
   
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
            change=0 
            bricks=scene_info.bricks.copy()
            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()           
            continue
       
       
        # 3.3. Put the code here to handle the scene information
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True  
            ball_place=scene_info.ball 
            bricks=scene_info.bricks.copy() +scene_info.hard_bricks.copy()  
            continue   
        elif ball_served:         
            placex=scene_info.ball[0]-ball_place[0]                
            placey=scene_info.ball[1]-ball_place[1] 
            ball_place=scene_info.ball 
        # the ball pull up follow the ball
        if  placey< 0:              
            change_D=True 
            if scene_info.ball[1]<300:
                if(scene_info.platform[0]<80):
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else:

                if(placex>0):
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
 
        # the ball going down
        else:
            if(abs(placex)>abs(change)): #check if the ball is speeding up
                change_D=True             
            if change_D==True  and scene_info.ball[1]>250 : # latter one avoid frame delay
                change_D=False                        
                Y=scene_info.ball[1]    #get the ball place
                X=scene_info.ball[0]  
                if abs(placex)<7 and abs(placex)!=10:
                    if placex>0: 
                        change=7
                    else:
                        change=-7
                else:
                    change=placex   
                Num=int((395-scene_info.ball[1])/placey)+1  #count the ball step to plateform
                '''---------------check the route----------------------'''
                for i in  range(Num):                                 
                    if change >0:
                        for item in bricks:
                            if(Y>=item[1]-5 and Y<=item[1]+10 and X<=item[0] and X>=item[0]-change):
                                change=-change
                                X=item[0]-5                                
                                break                            
                    else:
                        for item in bricks:                         
                            if(Y>=item[1]-5 and Y<=item[1]+10 and X<=item[0]+25 and X>=item[0]-change ):
                                change=-change
                                X=item[0]+25
                                break
                    Y+=placey
                    X+=change
                    if X>=195 or X<=0:
                        change=-change 
                        if X>180:
                            X=195
                        else:
                            X=0    
                place_check=X
            elif scene_info.ball[1]<250:  #get the platform back to center
                place_check=80
            '''
            if scene_info.ball[1]>390:
                    if placex>0:
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                    else:
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            # move the platform 
            '''  
            if scene_info.platform[0]+10>place_check:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
             
            elif scene_info.platform[0]+30<place_check:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)

        #if hit the brick recheck the place
        if len(bricks)!=len(scene_info.bricks)+len(scene_info.hard_bricks):
            #retD = list(set(bricks).difference(set(scene_info.bricks)))
            change_D=True                       
            bricks=scene_info.bricks.copy()+scene_info.hard_bricks.copy()
        
    
    


        
       
         
