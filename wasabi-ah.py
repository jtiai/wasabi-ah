import random

from wasabi2d import Scene, run, event, clock, animate, Vector2

scene = Scene()


class Bubble:
    def __init__(self, layer):
        x = random.randint(50, 590)
        y = random.randint(50, 430)
        self.pos = Vector2(x, y)
        self.angle = random.uniform(0, 360)
        self.rotation = random.uniform(-2.0, 2.0) * 1.5
        self.bubble = layer.add_sprite("normal_ball", pos=(x, y), angle=self.angle)
        self.animation = None

    def update(self, dt):
        self.bubble.angle += self.rotation * dt

    @property
    def radius(self):
        return self.bubble.width * self.bubble.scale / 2.0


class Player:
    def __init__(self, layer):
        x, y = (random.randint(90, 550), random.randint(70, 410))
        self.parts = [
            layer.add_sprite("slimeball_100", pos=(x, y)),
            layer.add_sprite("slimeball_80", pos=(x + 18, y)),
            layer.add_sprite("slimeball_64", pos=(x + 28, y)),
            layer.add_sprite("slimeball_51", pos=(x + 38, y)),
            layer.add_sprite("slimeball_40", pos=(x + 48, y)),
        ]
        self.position = Vector2(x, y)
        self.tail_positions = [Vector2(part.pos[0], part.pos[1]) for part in self.parts]
        self.destination = Vector2(self.position)
        self.direction = Vector2(0, 0)
        self.speed = 0.0

    def update(self, dt):
        self.position += self.direction * self.speed * dt
        self.parts[0].pos = self.position
        self.tail_positions[0] = self.position

        # Make tail to follow the head
        for i in range(1, len(self.tail_positions)):
            dst = self.tail_positions[i - 1]
            src = self.tail_positions[i]
            src = src.lerp(dst, 0.1)
            tgt = dst - src
            length = tgt.length_squared()
            if length > 20 * 20:
                t = Vector2(tgt)
                tgt.scale_to_length(20)
                src += t - tgt
            elif length < 10 * 10:
                t = Vector2(tgt)
                tgt.scale_to_length(10)
                src += t - tgt
            self.tail_positions[i] = src
            self.parts[i].pos = src

        # Slow down the speed
        if self.speed > 0:
            self.speed *= 0.98
            if self.speed < 0.06:
                self.speed = 0

    def on_mouse_down(self, pos):
        self.destination = Vector2(pos)
        self.direction = self.destination - self.position
        self.direction.normalize_ip()

        if self.speed <= 300.0:
            self.speed += 60.0


class Game:
    def __init__(self, scene: Scene):
        self.scene = scene
        self.bubbles = []
        self.spawn_bubble()
        self.player = Player(scene.layers[1])

    def destroy_bubble(self, bubble: Bubble):
        bubble.animation.stop()
        bubble.bubble.delete()
        self.bubbles.remove(bubble)

    def spawn_bubble(self):
        bubble = Bubble(self.scene.layers[0])
        bubble.animation = animate(bubble.bubble, tween="linear", duration=8.0, on_finished=lambda: self.destroy_bubble(bubble), scale=0.2 )
        self.bubbles.append(bubble)
        next_bubble = 0.5 + random.random() * 1.5
        clock.schedule_unique(self.spawn_bubble, next_bubble)

    def update(self, dt, keyboard):
        self.player.update(dt)

        for bubble in self.bubbles[:]:
            # Collision detection
            sep = bubble.pos - self.player.position
            min_dist = bubble.radius + 12.0
            if sep.length_squared() < min_dist * min_dist:
                bubble.animation.stop()
                bubble.bubble.delete()
                self.bubbles.remove(bubble)
            else:
                bubble.update(dt)


game = Game(scene)


@event
def update(dt, keyboard):
    game.update(dt, keyboard)


@event
def on_mouse_down(pos):
    game.player.on_mouse_down(pos)


run()
