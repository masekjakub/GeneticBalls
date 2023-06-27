import pygame
import random

windowSize = (1200, 850)
ticks = 100
foodPerRound = 15
ballsInFirstGeneration = 10
foodSize = 5
stepLambda = lambda ball: 2 - ball.size/64
visionLambda = lambda ball: 90 + ball.size*4

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode(windowSize)
pygame.display.set_caption("Genetic Balls")
font = pygame.font.Font('freesansbold.ttf', 15)


class Ball:
    def __init__(self, color, size, invDirectionChangeChance):
        self.x = windowSize[0]/2
        self.y = windowSize[1]/2
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) if color == None else color
        self.size = random.randint(5, 50) if size == None else size
        self.direction = random.randint(0, 7)
        self.invDirectionChangeChance = random.randint(1,200) if invDirectionChangeChance == None else invDirectionChangeChance
        self.foodEaten = 0

        self.step = stepLambda(self)
        self.vision = visionLambda(self)

    def getRandomBall():
        return Ball((0, 0, 255), None, None)
    
    def getFitness(self):
        return self.foodEaten
    
    def reproduce(self, secondParent):
        color = self.color if random.randint(0,1)==0 else secondParent.color
        size = self.size if random.randint(0,1)==0 else secondParent.size
        invDirectionChangeChance = self.invDirectionChangeChance if random.randint(0,1)==0 else secondParent.invDirectionChangeChance

        babyBall = Ball(color, size, invDirectionChangeChance)
        return self.mutate(babyBall)
    
    def mutate(self, ball):
        if random.randint(0,10) == 0:
            ball.color = (random.randint(10, 255), random.randint(10, 255), random.randint(10, 255))
            ball.size += random.normalvariate(0,15)
            ball.size = ball.size if ball.size > 1 else 1 
            self.step = stepLambda(self)
            self.vision = visionLambda(self)
            
        if random.randint(0,10) == 0:
            ball.color = (random.randint(10, 255), random.randint(10, 255), random.randint(10, 255))
            ball.invDirectionChangeChance += random.normalvariate(0,20)
            ball.invDirectionChangeChance = ball.invDirectionChangeChance if ball.invDirectionChangeChance > 0 else 1 

        return ball
    
    # 4 3 2
    # 5   1
    # 6 7 0
    def goInDirection(self, direction):
        if 0 <= direction <= 2:
            self.x += self.step
        elif 4 <= direction <= 6:
            self.x -= self.step
        if 2 <= direction <= 4:
            self.y += self.step
        elif 6 <= direction <= 7 or direction == 0:
            self.y -= self.step

    def isInside(self):
        return self.x >= 0 and self.x <= windowSize[0] and self.y >= 0 and self.y <= windowSize[1]
    
    def goBackIn(self):
        if self.x < 0:
            self.x = 0
        elif self.x > windowSize[0]:
            self.x = windowSize[0]
        if self.y < 0:
            self.y = 0
        elif self.y > windowSize[1]:
            self.y = windowSize[1]

class Food:
    def __init__(self):
        self.x = random.randint(0, windowSize[0])
        self.y = random.randint(0, windowSize[1])

class Round:
    def __init__(self, foodCount, balls, generation, board):
        self.foodList = []
        self.balls = balls
        self.generation = generation
        self.board = board

        self.foodList = [Food() for _ in range(0,foodCount)]

    def nextStep(self):
        for ball in self.balls:
            closestFood = lambda food: ((food.x - ball.x)**2 + (food.y - ball.y)**2)**0.5
            self.foodList.sort(key=closestFood)

            if ball.x - ball.size - foodSize/2 <= self.foodList[0].x <= ball.x + ball.size + foodSize/2 and ball.y - ball.size - foodSize/2 <= self.foodList[0].y <= ball.y + ball.size + foodSize/2:
                ball.foodEaten += 1
                self.foodList.remove(self.foodList[0])

            if len(self.foodList) == 0:
                return Round(foodPerRound, self.nextGeneration(), self.generation+1, self.board)
            
            if ((self.foodList[0].x - ball.x)**2 + (self.foodList[0].y - ball.y)**2)**0.5 > ball.vision:
                if random.randint(0,int(ball.invDirectionChangeChance)) == 0:
                    ball.direction += random.randint(-1,1)
                    ball.direction %= 8

                ball.goInDirection(ball.direction)

                if not ball.isInside():
                    ball.goBackIn()
                    ball.direction += random.randint(-1,1)
                    ball.direction %= 8
                    ball.goInDirection(ball.direction)
                    
            else:
                if self.foodList[0].x > ball.x:
                    ball.x += ball.step
                elif self.foodList[0].x < ball.x:
                    ball.x -= ball.step
                if self.foodList[0].y > ball.y:
                    ball.y += ball.step
                elif self.foodList[0].y < ball.y:
                    ball.y -= ball.step

        self.board.draw(self)
        return self

    def nextGeneration(self)->Ball:
        newBalls = []
        self.orderBalls(lambda ball: ball.getFitness(), True)

        isSecondParent = False
        for index,ball in enumerate(self.balls):
            if ball.getFitness() == 0:
                return newBalls
            
            newBalls.append(Ball(ball.color, ball.size, ball.invDirectionChangeChance))
            if isSecondParent:
                newBalls.append(ball.reproduce(self.balls[index-1]))
                isSecondParent = False
            else:
                isSecondParent = True
        return newBalls
        
    def orderBalls(self, key,reverse):
        self.balls.sort(key=key, reverse=reverse)

class Board:
    def draw(self, round: Round):
        screen.fill((0, 0, 0))

        for ball in round.balls:
            pygame.draw.circle(screen, ball.color, (ball.x, ball.y), ball.size)
            pygame.draw.ellipse(screen, (60, 60, 60), (ball.x - ball.vision, ball.y - ball.vision, ball.vision*2, ball.vision*2), 1)

        for food in round.foodList:
            pygame.draw.circle(screen, (255, 0, 0), (food.x, food.y), 5)

        board.drawText("Generation: " + str(round.generation))
        board.drawText("No balls: " + str(len(round.balls)), y=30)
        board.drawText("Avg size: " + str(sum(b.size for b in round.balls)/len(round.balls))[:6],y=50)
        board.drawText("Avg invDirChange: " + str(sum(b.invDirectionChangeChance for b in round.balls)/len(round.balls))[:6],y=70)

        board.drawText("Ticks: " + str(ticks), x=windowSize[0]-90)

        pygame.display.flip()

    def drawText(self,text,x=10,y=10):
        textRen = font.render(text, True, (255, 255, 255))
        screen.blit(textRen, (x, y))


def handleEvents(ticks):
    running = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            ticks += 100
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            ticks -= 100
    return running, ticks
            
if __name__ == "__main__":
    balls = [Ball.getRandomBall() for i in range(0, ballsInFirstGeneration)]
    board = Board()
    round = Round(foodPerRound, balls, 1, board)

    running = True
    while running:
        running, ticks = handleEvents(ticks)
        round = round.nextStep()
        clock.tick(ticks)
    pygame.quit()
