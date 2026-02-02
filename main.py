import pygame
import sys

pygame.init()

# ---------------- CONSTANTS ----------------
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8

WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

font = pygame.font.SysFont(None, 48)

# ---------------- CHESS PIECE ----------------
class ChessPiece:
    def __init__(self, color, type_, image):
        self.color = color
        self.type = type_
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (SQUARE_SIZE, SQUARE_SIZE))
        self.has_moved = False

# ---------------- GAME STATE ----------------
board = [[None for _ in range(8)] for _ in range(8)]
current_player = 'white'
selected_piece = None
selected_pos = None
game_over = False
check_message = ""

# ---------------- INIT BOARD ----------------
def init_board():
    for col in range(8):
        board[1][col] = ChessPiece('black', 'pawn', 'images/black_pawn.png')
        board[6][col] = ChessPiece('white', 'pawn', 'images/white_pawn.png')

    board[0][0] = board[0][7] = ChessPiece('black', 'rook', 'images/black_rook.png')
    board[7][0] = board[7][7] = ChessPiece('white', 'rook', 'images/white_rook.png')

    board[0][1] = board[0][6] = ChessPiece('black', 'knight', 'images/black_knight.png')
    board[7][1] = board[7][6] = ChessPiece('white', 'knight', 'images/white_knight.png')

    board[0][2] = board[0][5] = ChessPiece('black', 'bishop', 'images/black_bishop.png')
    board[7][2] = board[7][5] = ChessPiece('white', 'bishop', 'images/white_bishop.png')

    board[0][3] = ChessPiece('black', 'queen', 'images/black_queen.png')
    board[7][3] = ChessPiece('white', 'queen', 'images/white_queen.png')

    board[0][4] = ChessPiece('black', 'king', 'images/black_king.png')
    board[7][4] = ChessPiece('white', 'king', 'images/white_king.png')

# ---------------- DRAW ----------------
def draw_board():
    for r in range(8):
        for c in range(8):
            color = WHITE if (r + c) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color,
                (c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    if selected_piece:
        moves = get_legal_moves(selected_piece, selected_pos[0], selected_pos[1])
        for r, c in moves:
            pygame.draw.circle(
                screen, GREEN,
                (c*SQUARE_SIZE + SQUARE_SIZE//2,
                 r*SQUARE_SIZE + SQUARE_SIZE//2), 12)

        pygame.draw.rect(
            screen, YELLOW,
            (selected_pos[1]*SQUARE_SIZE,
             selected_pos[0]*SQUARE_SIZE,
             SQUARE_SIZE, SQUARE_SIZE), 4)

def draw_pieces():
    for r in range(8):
        for c in range(8):
            if board[r][c]:
                screen.blit(board[r][c].image, (c*SQUARE_SIZE, r*SQUARE_SIZE))

def draw_check_message():
    if check_message:
        text = font.render(check_message, True, RED)
        screen.blit(text, (WIDTH//2 - 150, 10))

# ---------------- MOVE LOGIC ----------------
def slide_moves(row, col, piece, directions):
    moves = []
    for dr, dc in directions:
        r, c = row + dr, col + dc
        while 0 <= r < 8 and 0 <= c < 8:
            if board[r][c] is None:
                moves.append((r, c))
            elif board[r][c].color != piece.color:
                moves.append((r, c))
                break
            else:
                break
            r += dr
            c += dc
    return moves

def get_valid_moves(piece, row, col):
    moves = []

    if piece.type == 'pawn':
        d = -1 if piece.color == 'white' else 1
        if 0 <= row + d < 8 and board[row+d][col] is None:
            moves.append((row+d, col))
            if not piece.has_moved and board[row+2*d][col] is None:
                moves.append((row+2*d, col))
        for dc in [-1, 1]:
            r, c = row+d, col+dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] and board[r][c].color != piece.color:
                    moves.append((r, c))

    elif piece.type == 'rook':
        moves += slide_moves(row, col, piece, [(1,0),(-1,0),(0,1),(0,-1)])

    elif piece.type == 'bishop':
        moves += slide_moves(row, col, piece, [(1,1),(1,-1),(-1,1),(-1,-1)])

    elif piece.type == 'queen':
        moves += slide_moves(row, col, piece,
            [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)])

    elif piece.type == 'knight':
        for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            r, c = row+dr, col+dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None or board[r][c].color != piece.color:
                    moves.append((r, c))

    elif piece.type == 'king':
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr == dc == 0:
                    continue
                r, c = row+dr, col+dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None or board[r][c].color != piece.color:
                        moves.append((r, c))

    return moves

# ---------------- CHECK RULES ----------------
def is_check(color):
    king_pos = None
    for r in range(8):
        for c in range(8):
            if board[r][c] and board[r][c].type == 'king' and board[r][c].color == color:
                king_pos = (r, c)

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.color != color:
                if king_pos in get_valid_moves(piece, r, c):
                    return True
    return False

def get_legal_moves(piece, row, col):
    legal = []
    for r, c in get_valid_moves(piece, row, col):
        temp = board[r][c]
        board[r][c] = piece
        board[row][col] = None
        if not is_check(piece.color):
            legal.append((r, c))
        board[row][col] = piece
        board[r][c] = temp
    return legal

def is_checkmate(color):
    if not is_check(color):
        return False
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.color == color:
                if get_legal_moves(piece, r, c):
                    return False
    return True

# ---------------- INPUT ----------------
def handle_click(pos):
    global selected_piece, selected_pos, current_player
    global check_message, game_over

    if game_over:
        return

    col = pos[0] // SQUARE_SIZE
    row = pos[1] // SQUARE_SIZE

    if selected_piece is None:
        piece = board[row][col]
        if piece and piece.color == current_player:
            selected_piece = piece
            selected_pos = (row, col)
    else:
        moves = get_legal_moves(selected_piece, selected_pos[0], selected_pos[1])
        if (row, col) in moves:
            board[row][col] = selected_piece
            board[selected_pos[0]][selected_pos[1]] = None
            selected_piece.has_moved = True

            if selected_piece.type == 'pawn' and (row == 0 or row == 7):
                board[row][col] = ChessPiece(
                    selected_piece.color, 'queen',
                    f'images/{selected_piece.color}_queen.png'
                )

            current_player = 'black' if current_player == 'white' else 'white'

            if is_check(current_player):
                check_message = f"{current_player.upper()} IN CHECK"
            else:
                check_message = ""

            if is_checkmate(current_player):
                check_message = f"CHECKMATE! {current_player.upper()} LOSES"
                game_over = True

        selected_piece = None
        selected_pos = None

# ---------------- MAIN ----------------
def main():
    init_board()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(pygame.mouse.get_pos())

        draw_board()
        draw_pieces()
        draw_check_message()
        pygame.display.flip()

if __name__ == "__main__":
    main()
