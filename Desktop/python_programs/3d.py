from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import json

app = Ursina()

window.size = (1920, 1080)
window.fullscreen = True  

ground = Entity(
    model='plane',
    texture='grass',
    collider='box',
    scale=(200, 1, 200)
)

gallop_sound = Audio('gallop.wav', loop=False, autoplay=False)
mount_prompt = Text(text="Press E to mount", origin=(0,0), scale=2, visible=False)
player = FirstPersonController()
player.position = (5, 1, 5) 
mounted = False 

race_start_time = 0
race_timer = Text(text="", origin=(1, 0.5), position=(0.95, 0.45), scale=2, visible=False)  
finish_line = Entity(
    model='cube',
    color=color.red,
    scale=(10, 3, 10), 
    position=(100, 1.5, 0),  
    collider='box',
    visible=False
)

countdown_time = 5
countdown_text = Text(text="", origin=(1, 0.5), position=(0.95, 0.4), scale=2, visible=False)  
error_text = Text(text="", origin=(0, -0.2), scale=2, color=color.red, visible=False)

results_panel = Entity(
    model='quad', 
    scale=(2, 2),  
    parent=camera.ui,
    position=(0, 0),
    color=color.black,
    visible=False
)
results_text = Text(
    text="", 
    scale=1.5,  
    parent=results_panel,
    position=(0, 0.2),
    color=color.white,
    origin=(0, 0),
    visible=False,
    font='VeraMono.ttf'  
)
highscore_text = Text(
    text="", 
    scale=1.2,  
    parent=results_panel,
    position=(0, 0),
    color=color.white,
    origin=(0, 0),
    visible=False,
    font='VeraMono.ttf' 
)
reset_prompt = Text(
    text="Press Backspace to reset the game",
    scale=1.2,
    parent=results_panel,
    position=(0, -0.2),
    color=color.white,
    origin=(0, 0),
    visible=False,
    font='VeraMono.ttf'
)


try:
    with open('best_time.json', 'r') as f:
        best_time = json.load(f)
except:
    best_time = float('inf')

class Horse(Entity):
    def __init__(self, position=(5, 0, 5)):
        super().__init__(
            parent=scene,
            position=position,
            model='horse',
            texture='horse_texture',
            collider='box',
            scale=1.5,
            rotation_y=180,
            visible=True
        )
       
        self.max_speed = 12
        self.ultra_speed = 50
        self.acceleration = 20
        self.turn_speed = 120
        self.current_speed = 0
        self.deceleration = 10
        self.gallop_sound_delay = 0.4
        self.is_ultra_galloping = False
        self.ultra_gallop_duration = 5
        self.ultra_gallop_timer = 0
        self.camera_pivot = Entity(parent=self, position=(0, 2, 0))
        self.last_gallop_time = 0
        self.is_galloping = False
        self.gallop_count = 10  

horse = Horse()

def start_countdown():
    global countdown_time, race_start_time
    countdown_time = 5
    race_start_time = time.time()  
    countdown_text.visible = True
    finish_line.visible = True
    update_countdown()

def update_countdown():
    global countdown_time
    if countdown_time > 0:
        countdown_text.text = f"Countdown: {countdown_time}s"
        countdown_time -= 1
        invoke(update_countdown, delay=1)
    else:
        countdown_text.visible = False
        mount_prompt.visible = True

def show_error(message):
    error_text.text = message
    error_text.visible = True
    invoke(lambda: setattr(error_text, 'visible', False), delay=2)

def show_results(final_time):
    global best_time
    results_panel.visible = True
    results_text.visible = True
    highscore_text.visible = True
    reset_prompt.visible = True
    
    
    results_text.position = (0, 0.2)
    highscore_text.position = (0, 0)
    reset_prompt.position = (0, -0.2)
    
    results_text.text = f"YOUR TIME: {final_time:.2f} SECONDS"
    
    if final_time < best_time:
        best_time = final_time
        highscore_text.text = "NEW HIGH SCORE ACHIEVED!"
        highscore_text.color = color.green
        with open('best_time.json', 'w') as f:
            json.dump(best_time, f)
    else:
        highscore_text.text = f"BEST TIME: {best_time:.2f} SECONDS"
        highscore_text.color = color.white

def restart_race():
    global mounted, race_start_time, countdown_time, results_panel, results_text, highscore_text, reset_prompt
   
    mounted = False
    race_start_time = 0
    countdown_time = 5
    results_panel.visible = False
    results_text.visible = False
    highscore_text.visible = False
    reset_prompt.visible = False
    
    
    horse.position = (5, 0, 5)
    horse.current_speed = 0
    horse.is_ultra_galloping = False
    horse.max_speed = 12
    horse.gallop_count = 10  
    
    
    player.enabled = True
    camera.parent = player
    player.position = (5, 1, 5)  
    
    
    start_countdown()

def input(key):
    global mounted, race_start_time
    if key == 'e':
        if mounted:
            player.enabled = True
            camera.parent = player
            dismount_pos = horse.position + horse.forward * 2 + Vec3(0, 2, 0)
            ray = raycast(dismount_pos, (0,-1,0), distance=3)
            player.position = ray.world_point + Vec3(0, .5, 0) if ray.hit else dismount_pos
            mounted = False
            mouse.locked = False
            mount_prompt.text = "Press E to mount"
            horse.is_galloping = False
            horse.is_ultra_galloping = False
        else:
            if distance(player, horse) < 3:
                if countdown_time > 0:
                    show_error(f"Wait {countdown_time}s to mount!")
                else:
                    player.enabled = False
                    camera.parent = horse.camera_pivot
                    camera.position = (0, 1.8, -2.5)
                    camera.rotation = (0, 0, 0)
                    mounted = True
                    mouse.locked = True
                    mount_prompt.text = "Press E to unmount"
                    race_timer.visible = True

    if key == 'f' and mounted and not horse.is_ultra_galloping and horse.gallop_count > 0:
        horse.is_ultra_galloping = True
        horse.ultra_gallop_timer = horse.ultra_gallop_duration
        horse.max_speed = horse.ultra_speed
        horse.gallop_count -= 1 

    if key == 'backspace':  
        restart_race()

def update():
    global race_start_time, mounted
    if race_start_time > 0:
        race_timer.text = f"Time: {time.time() - race_start_time:.2f}s"

    if mounted:
        horse.rotation_y += mouse.velocity[0] * 60 * 0.1
        horse.camera_pivot.rotation_x -= mouse.velocity[1] * 40 * 0.08
        horse.camera_pivot.rotation_x = clamp(horse.camera_pivot.rotation_x, -60, 60)

        target_speed = horse.current_speed
        if held_keys['w']:
            target_speed = min(horse.max_speed, target_speed + horse.acceleration * time.dt)
            horse.is_galloping = True
        else:
            horse.is_galloping = False
            
        if held_keys['s']:
            target_speed = max(-horse.max_speed/2, target_speed - horse.acceleration * time.dt)
        
        if not held_keys['w'] and not held_keys['s']:
            target_speed = lerp(target_speed, 0, horse.deceleration * time.dt)
        
        turn_input = held_keys['d'] - held_keys['a']
        if turn_input != 0 and horse.current_speed != 0:
            horse.rotation_y += turn_input * horse.turn_speed * time.dt
            target_speed *= 0.95

        horse.current_speed = lerp(horse.current_speed, target_speed, 12 * time.dt)

        if abs(horse.current_speed) > 0.1:
            proposed_position = horse.position + horse.forward * horse.current_speed * time.dt
            if not finish_line.intersects(Entity(position=proposed_position, collider='box')):
                horse.position = proposed_position

        if horse.is_galloping and time.time() - horse.last_gallop_time > horse.gallop_sound_delay:
            gallop_sound.play()
            horse.last_gallop_time = time.time()
            horse.gallop_sound_delay = 0.4 - (horse.current_speed/horse.max_speed * 0.2)

        if horse.is_ultra_galloping:
            horse.ultra_gallop_timer -= time.dt
            if horse.ultra_gallop_timer <= 0:
                horse.is_ultra_galloping = False
                horse.max_speed = 12

        gallop_counter_text.text = f"Gallops Left: {horse.gallop_count}"

        if horse.intersects(finish_line):
            final_time = time.time() - race_start_time
            show_results(final_time)
            race_start_time = 0 
            mounted = False  

    mount_prompt.visible = distance(player, horse) < 3 and not mounted and countdown_time <= 0


gallop_counter_text = Text(
    text="Gallops Left: 10",
    origin=(1, 0.5),
    position=(0.95, 0.35),
    scale=2,
    visible=True
)

start_countdown()
Sky(texture='sky_sunset')
app.run()