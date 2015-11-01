#!/usr/bin/python

import turtle
import math 
from collections import deque

def main_triangle():
  t.begin_fill()
  for i in range(1,4):
    if i == 1 :
        todo.append(t.position())
    if i == 2 :
        todo.append(t.position()-(side/2,0))
    if i == 3 :
        #print t.position()
        #print math.sqrt((side/2)**2-(side/4)**2)
        todo.append(t.position()+(-(side/4),math.sqrt((side/2)**2-(side/4)**2)))
    t.forward(side)
    t.right(120)
  t.end_fill()

def draw_triangle(side):
    t.penup()
    top = todo.popleft()
    #print top
    t.goto(top)
    t.pendown()
    for i in range(1,4):
      if i == 1 :
          todo.append(t.position())
      if i == 2 :
          todo.append(t.position()-(side/2,0))
      if i == 3 :
          #print t.position()
          #print math.sqrt((side/2)**2-(side/4)**2)
          todo.append(t.position()+(-(side/4),math.sqrt((side/2)**2-(side/4)**2)))
      t.forward(side)
      t.right(120)

t = turtle.Turtle()
t.speed("fast")
window = turtle.Screen()
side = 240
todo = deque([])
t.color("white")
main_triangle()
n=1
t.color("green")
while (todo):
  side = side / 2
  if n>=3:
    t.color("green")
    t.begin_fill()
  for i in range(1,(3**n+1)):
    #print side, i
    draw_triangle(side)
  n = n + 1
  #print todo.pop()
  if ( 3**n > 81 ):
    t.end_fill()
    exit(1)
window.exitonclick()
