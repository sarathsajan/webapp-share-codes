import random
import os

# Get random number for selecting an image from the given game images folder present in the Static directory
def get_random_image(game_name):
    rand_img_id = str(random.randint(1, len([name for name in os.listdir(f'./static/images/{game_name}/')])))
    rand_img_id = rand_img_id + '_' + rand_img_id + '_11zon.jpeg'
    return rand_img_id