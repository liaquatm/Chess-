import pygame as p
import engine


WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_images():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bp', 'wp', 'wR', 'wN', 'wB', 'wQ', 'wK',]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+piece+".png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    clock = p.time.Clock()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    #screen.set_caption("Chess -by Omair")
    screen.fill(p.Color("white"))
    gs = engine.GameState()
    valid_moves = gs.getValidMoves()
    move_made = False
    animate = False
    load_images()
    running = True
    game_over = False
    sq_selected = ()
    player_clicks = []
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2:
                        move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.makeMove(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    move_made = True
                    animate = False
                elif e.key == p.K_r:
                    gs = engine.GameState()
                    valid_moves = gs.getValidMoves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over=False
        if move_made:
            if animate:
                animate_move(move, screen, gs.board, clock)
            valid_moves = gs.getValidMoves()
            move_made = False
            animate = False
        draw_gamestate(screen, gs, valid_moves, sq_selected)
        if gs.checkMate:
            game_over = True
            if gs.whiteToMove:
                draw_text(screen, 'Black wins by checkmate! Press R to play again')
            else:
                draw_text(screen, 'White wins by checkmate! Press R to play again')
        elif gs.staleMate:
            game_over = True
            draw_text(screen, 'Stalemate! Press R to play again')

        clock.tick(MAX_FPS)
        p.display.flip()

def draw_gamestate(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)

def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected:
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))

def animate_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    framesPerSquare = 6
    frameCount = (abs(dR)+abs(dC))*framesPerSquare
    for frame in range(frameCount+1):
        r,c = (move.start_row+ dR*frame/frameCount, move.start_col + dC*frame/frameCount)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row+move.end_col)%2]
        endSquare = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], endSquare)
        screen.blit(IMAGES[move.piece_moved], (p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)))
        p.display.flip()
        clock.tick(60)

def draw_text(screen, text):
    font = p.font.SysFont('Helvetica', 25, True, False)
    text_object = font.render(text, 0, p.Color('black'))
    text_location = p.Rect(0,0,WIDTH, HEIGHT).move(WIDTH//2 - text_object.get_width()//2, HEIGHT//2 - text_object.get_height()//2)
    screen.blit(text_object, text_location)

def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == '__main__':
    main()