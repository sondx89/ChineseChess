import pygame

def load_image(file_path):
    """Load an image from the specified file path."""
    try:
        image = pygame.image.load(file_path)
        return image
    except pygame.error as e:
        print(f"Unable to load image at {file_path}: {e}")
        return None

def resize_images(images, size):
    resized_images = {}
    for code, img in images.items():
        resized_images[code] = pygame.transform.smoothscale(img, (size, size))
    return resized_images


def handle_input(event):
    """Handle user input events."""
    if event.type == pygame.QUIT:
        return False
    return True

def update_game_state(state, action):
    """Update the game state based on the action taken."""
    # Implement game state update logic here
    pass

def reset_game():
    """Reset the game to its initial state."""
    # Implement reset logic here
    pass

# Các hàm tiện ích khác
def position_to_coordinates(position):
    """
    Chuyển đổi vị trí (ví dụ: 'A1') thành tọa độ mảng (hàng, cột).
    """
    column = ord(position[0].upper()) - ord('A')
    row = int(position[1]) - 1
    return row, column

def coordinates_to_position(row, column):
    """
    Chuyển đổi tọa độ mảng (hàng, cột) thành vị trí (ví dụ: 'A1').
    """
    column_letter = chr(column + ord('A'))
    row_number = row + 1
    return f"{column_letter}{row_number}"