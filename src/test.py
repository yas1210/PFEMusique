import pygame.midi
pygame.midi.init()

for i in range(pygame.midi.get_count()):
    print(i, pygame.midi.get_device_info(i))

out_id = pygame.midi.get_default_output_id()
print("default:", out_id)

player = pygame.midi.Output(out_id)
player.set_instrument(0)
player.note_on(60, 100)
import time
time.sleep(1)
player.note_off(60, 100)
player.close()
pygame.midi.quit()