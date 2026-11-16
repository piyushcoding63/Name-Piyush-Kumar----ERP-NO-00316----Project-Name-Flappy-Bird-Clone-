"""Flappy Bird Clone - PS 50
Run game:   python flappy_bird.py
Run tests:  python flappy_bird.py --test
Controls:   SPACE = flap (also restarts after Game Over), ESC = quit
"""

import random
import sys

import pygame

W, H = 400, 600
GROUND_Y = 600
BIRD_SIZE = 30
BIRD_X = 100
PIPE_W = 60
GAP = 150
PIPE_SPEED = 3
PIPE_SPACING = 220
FLAP_VELOCITY = -10
GRAVITY = 1


class Bird:
    def __init__(self, y=300, velocity=0):
        self.x = BIRD_X
        self.y = y
        self.velocity = velocity

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, BIRD_SIZE, BIRD_SIZE)

    def update(self, space_pressed):
        # SPACE sets velocity = -10 BEFORE the frame update
        if space_pressed:
            self.velocity = FLAP_VELOCITY
        self.velocity += GRAVITY  # velocity += 1
        self.y += self.velocity  # then y += velocity


class Pipe:
    def __init__(self, x, gap_y=None):
        self.x = x
        self.gap_y = (
            gap_y if gap_y is not None else random.randint(100, GROUND_Y - GAP - 100)
        )
        self.passed = False

    @property
    def rects(self):
        top = pygame.Rect(self.x, 0, PIPE_W, self.gap_y)
        bottom = pygame.Rect(
            self.x, self.gap_y + GAP, PIPE_W, GROUND_Y - (self.gap_y + GAP)
        )
        return top, bottom

    def update(self):
        self.x -= PIPE_SPEED


def hit_ground(bird):
    return bird.rect.bottom >= GROUND_Y


def hit_top(bird):
    return bird.y < 0


def hit_pipe(bird, pipes):
    r = bird.rect
    return any(r.colliderect(p) for pipe in pipes for p in pipe.rects)


def update_score(bird, pipes, score):
    for pipe in pipes:
        if not pipe.passed and pipe.x + PIPE_W < bird.x:
            pipe.passed = True
            score += 1
    return score


# ---------------------------------------------------------------- tests
def run_tests():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS" if cond else "FAIL"), "-", name)
        ok &= cond

    # Test 1: normal input
    b = Bird(300, 0)
    b.update(False)
    f1 = (b.velocity, b.y)
    b.update(False)
    check("TC1 frame1 v=1 y=301", f1 == (1, 301))
    check("TC1 frame2 v=2 y=303", (b.velocity, b.y) == (2, 303))

    # Test 2: boundary
    b = Bird(570, 0)
    check("TC2a ground collision", hit_ground(b))
    b = Bird(5, 0)
    b.update(True)
    check("TC2b v=-9 y=-4 top exit", (b.velocity, b.y) == (-9, -4) and hit_top(b))

    # Test 3: invalid key ignored (Z is not SPACE)
    b = Bird(300, 0)
    b.update(False)
    check("TC3 key ignored v=1 y=301", (b.velocity, b.y) == (1, 301))

    # Test 4: different valid scenario
    b = Bird(300, 5)
    b.update(True)
    check("TC4a v=-9 y=291", (b.velocity, b.y) == (-9, 291))
    b = Bird(300, 0)
    p = Pipe(39, gap_y=200)
    score = update_score(b, [p], 0)
    check("TC4b pipe passed score=1", score == 1)

    print("\nALL TESTS PASSED" if ok else "\nSOME TESTS FAILED")
    return ok


# ---------------------------------------------------------------- game
def reset():
    pipes = [Pipe(W + i * PIPE_SPACING) for i in range(3)]
    return Bird(), pipes, 0, False


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Flappy Bird Clone")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 40)
    big = pygame.font.SysFont(None, 56)

    bird, pipes, score, game_over = reset()

    while True:
        space = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if e.key == pygame.K_SPACE:  # any other key is ignored
                    if game_over:
                        bird, pipes, score, game_over = reset()
                    else:
                        space = True

        if not game_over:
            bird.update(space)
            for p in pipes:
                p.update()
            # remove pipes that left the screen, add new ones on the right
            if pipes and pipes[0].x + PIPE_W < 0:
                pipes.pop(0)
                pipes.append(Pipe(pipes[-1].x + PIPE_SPACING))
            score = update_score(bird, pipes, score)
            if hit_ground(bird) or hit_top(bird) or hit_pipe(bird, pipes):
                game_over = True

        # draw
        screen.fill((135, 206, 235))
        for p in pipes:
            for r in p.rects:
                pygame.draw.rect(screen, (34, 139, 34), r)
        pygame.draw.rect(screen, (255, 215, 0), bird.rect)
        pygame.draw.rect(screen, (139, 90, 43), (0, H - 10, W, 10))
        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
        if game_over:
            t = big.render("Game Over", True, (200, 0, 0))
            s = font.render("Press SPACE to restart", True, (0, 0, 0))
            screen.blit(t, t.get_rect(center=(W // 2, H // 2 - 20)))
            screen.blit(s, s.get_rect(center=(W // 2, H // 2 + 25)))

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.exit(0 if run_tests() else 1)
    main()
