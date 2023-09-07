import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up display
screen_info = pygame.display.Info()
width, height = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption("2D Farmer Game")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)  # Added for mute button color

# Fonts
font = pygame.font.Font(None, 36)

class Block:
    def __init__(self, x, y, width, height, image):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class MuteButton:
    def __init__(self):
        self.rect = pygame.Rect(10, height - 50, 40, 40)
        self.is_muted = False
        self.image = None
        self.update_image()

    def update_image(self):
        if self.is_muted:
            self.image = pygame.Surface((40, 40))
            self.image.fill(red)  # Red color to indicate mute
        else:
            self.image = pygame.Surface((40, 40))
            self.image.fill(green)  # Green color to indicate unmute

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.update_image()
        if self.is_muted:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class FarmerGame:
    def __init__(self):
        self.gold = 50
        self.crops = 0
        self.day = 1
        self.is_fullscreen = True
        self.player_x = 150
        self.player_y = 750
        self.target_x = self.player_x
        self.target_y = self.player_y
        self.move_speed = 15

        # Load the PNG image for the farmer character
        self.farmer_image = pygame.image.load('farmer.png')
        player_size = 250
        self.farmer_image = pygame.transform.scale(self.farmer_image, (player_size, player_size))

        # Load the PNG image for the farmer's house
        self.farmer_house_image = pygame.image.load('farmer_house.png')
        house_size = 350  # Adjust the size as needed
        self.farmer_house_image = pygame.transform.scale(self.farmer_house_image, (house_size, house_size))

        self.farmer_shop_image = pygame.image.load('shop.png')
        shop_size = 350  # Adjust the size as needed
        self.farmer_shop_image = pygame.transform.scale(self.farmer_shop_image, (shop_size, shop_size))

        # Place the house image in the top-left corner
        self.house_x1 = 100
        self.house_y1 = 300

        self.shop_x = 1500
        self.shop_y = 300

        self.house_x3 = 1100
        self.house_y3 = 700

        self.house_x4 = 1500
        self.house_y4 = 700

        self.button = pygame.Rect(width - 350, 200, 200, 100)  # Button position (top right corner)
        self.font = pygame.font.Font(None, 36)
        self.button_text = font.render("Click me!", True, (255, 255, 255))

        # Load the JPEG background image
        self.background_image = pygame.image.load('background.jpeg')
        self.background_image = pygame.transform.scale(self.background_image, (width, height))
        self.start_image = pygame.image.load("start_screen.jpg")
        self.start_image = pygame.transform.scale(self.start_image, (width, height))

        # Load the "ricefield.png" image and resize it
        block_width = 150
        block_height = 150
        self.ricefield_image = pygame.image.load('ricefield.png')
        self.ricefield_image = pygame.transform.scale(self.ricefield_image, (block_width, block_height))

        # Create blocks in a 3x3 grid, centered on the screen, with the "ricefield.png" image
        self.blocks = []
        grid_width = 3 * block_width + 2 * 20
        grid_height = 3 * block_height + 2 * 20
        start_x = (width - grid_width) // 2 - 200
        start_y = (height - grid_height) // 2 + 200
        for row in range(3):
            for col in range(3):
                x = start_x + col * (block_width + 20)
                y = start_y + row * (block_height + 20)
                self.blocks.append(Block(x, y, block_width, block_height, self.ricefield_image))

        self.start_screen = True
        self.loading_start_time = None

        self.house1 = pygame.Rect(self.house_x1, self.house_y1, house_size, house_size)
        self.shop = pygame.Rect(self.shop_x, self.shop_y, shop_size, shop_size)
        self.house3 = pygame.Rect(self.house_x3, self.house_y3, house_size, house_size)
        self.house4 = pygame.Rect(self.house_x4, self.house_y4, house_size, house_size)

        # Building variables
        self.building_rects = [
            self.house1,
            self.shop,
            self.house3,
            self.house4
        ]
        self.building_highlighted = [True] * len(self.building_rects)  # Tất cả các building đều có viền trắng ban đầu

        # Tạo một danh sách boolean để theo dõi trạng thái của từng khối
        self.block_highlighted = [True] * len(self.blocks)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((width, height))

    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y

    def move_player(self):
        dx = self.target_x - self.player_x
        dy = self.target_y - self.player_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > self.move_speed:
            ratio = self.move_speed / distance
            new_x = self.player_x + int(dx * ratio)
            new_y = self.player_y + int(dy * ratio)

            if all(not block.rect.collidepoint(new_x, new_y) for block in self.blocks):
                self.player_x = new_x
                self.player_y = new_y
        else:
            self.player_x = self.target_x
            self.player_y = self.target_y

        if self.player_x < 0:
            self.player_x = width
        elif self.player_x > width:
            self.player_x = 0

        # Cập nhật trạng thái của từng khối
        for i, block in enumerate(self.blocks):
            if block.rect.collidepoint(self.player_x, self.player_y):
                self.block_highlighted[i] = True
            else:
                self.block_highlighted[i] = False

    def display_status(self):
        text = f"Day: {self.day} | Gold: {self.gold} | Crops: {self.crops}"
        text_surface = font.render(text, True, white)
        screen.blit(text_surface, (10, 10))

        exit_button = font.render("X", True, white)
        exit_button_rect = exit_button.get_rect(topright=(width - 10, 10))
        pygame.draw.rect(screen, green, exit_button_rect)
        screen.blit(exit_button, exit_button_rect)

        for i, building_rect in enumerate(self.building_rects):
            if self.building_highlighted[i]:
                pygame.draw.rect(screen, white, building_rect, 2)  # Vẽ viền trắng
                if self.building_highlighted[1]:
                    pygame.draw.rect(screen, (0, 0, 255), self.button)  # Display the button
                    button_text_rect = self.button_text.get_rect(center=self.button.center)
                    screen.blit(self.button_text, button_text_rect)  # Display button text

        screen.blit(self.farmer_house_image, (self.house_x1, self.house_y1))
        screen.blit(self.farmer_shop_image, (self.shop_x, self.shop_y))
        screen.blit(self.farmer_house_image, (self.house_x3, self.house_y3))
        screen.blit(self.farmer_house_image, (self.house_x4, self.house_y4))

        screen.blit(self.farmer_image, (self.player_x - 30, self.player_y - 30))

        # Vẽ viền trắng cho các khối có trạng thái được cập nhật
        for i, block in enumerate(self.blocks):
            if self.block_highlighted[i]:
                pygame.draw.rect(screen, white, block.rect, 2)

    def display_start_screen(self):
        larger_font = pygame.font.Font(None, 100)
        screen.blit(self.start_image, (0, 0))
        text = "Click any button to start"
        text_surface = larger_font.render(text, True, white)
        text_rect = text_surface.get_rect(center=(width // 2, height // 2))
        screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    game = FarmerGame()
    mute_button = MuteButton()

    clock = pygame.time.Clock()
    running = True

    keys_pressed = set()

    pygame.mixer.init()
    pygame.mixer.music.load('background_music.mp3')
    pygame.mixer.music.play(-1)

    loading_text = font.render("Loading...", True, white)

    while running:
        exit_button_size = 40
        exit_button_rect = pygame.Rect(width - exit_button_size - 10, 10, exit_button_size, exit_button_size)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game.start_screen and event.type == pygame.MOUSEBUTTONDOWN:
                game.start_screen = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                x, y = event.pos
                game.set_target(x, y)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if exit_button_rect.collidepoint(event.pos):
                    running = False

            if event.type == pygame.KEYDOWN:
                keys_pressed.add(event.key)

            if event.type == pygame.KEYUP:
                keys_pressed.discard(event.key)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mute_button.rect.collidepoint(event.pos):
                    mute_button.toggle_mute()

        screen.blit(game.background_image, (0, 0))

        if game.start_screen:
            game.display_start_screen()
        else:
            if game.day == 1:
                if game.loading_start_time is None:
                    game.loading_start_time = pygame.time.get_ticks()

                loading_time_elapsed = pygame.time.get_ticks() - game.loading_start_time
                if loading_time_elapsed < 3000:
                    screen.blit(game.background_image, (0, 0))
                    loading_rect = loading_text.get_rect(center=(width // 2, height // 2))
                    screen.blit(loading_text, loading_rect)
                else:
                    movement_x = 0
                    movement_y = 0

                    if pygame.K_w in keys_pressed:
                        movement_y -= game.move_speed
                    if pygame.K_a in keys_pressed:
                        movement_x -= game.move_speed
                    if pygame.K_s in keys_pressed:
                        movement_y += game.move_speed
                    if pygame.K_d in keys_pressed:
                        movement_x += game.move_speed

                    game.set_target(game.player_x + movement_x, game.player_y + movement_y)

                    if pygame.mouse.get_pressed()[2]:
                        x, y = pygame.mouse.get_pos()
                        game.set_target(x, y)

                    game.move_player()

                    # Update building highlighting
                    for i, building_rect in enumerate(game.building_rects):
                        if building_rect.collidepoint(game.player_x, game.player_y):
                            game.building_highlighted[i] = True
                        else:
                            game.building_highlighted[i] = False

                    game.display_status()

                    for block in game.blocks:
                        block.draw(screen)

                    exit_button = font.render("X", True, white)
                    exit_button_text_rect = exit_button.get_rect(center=exit_button_rect.center)
                    pygame.draw.rect(screen, green, exit_button_rect)
                    screen.blit(exit_button, exit_button_text_rect)

        mute_button.draw(screen)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
