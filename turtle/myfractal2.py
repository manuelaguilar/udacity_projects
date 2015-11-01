#!/usr/bin/python

import turtle
import math 
import itertools
from collections import deque

def main_triangle():
  t.right(-60)
  t.begin_fill()
  for i in range(1,4):
    todo.append(t.position())
    t.forward(side)
    t.right(120)
  t.end_fill()


def sierpinski_triangle(a, b, c, s):
 #terminating condition
 n = s / 2
 if n<= (side / 16):
   return 
 #given 3 vertices
 #compute middle points - new vertices
 #call sierpinski_triangle on each new set
 d = 0.5*(a+b)
 e = 0.5*(b+c)
 f = 0.5*(a+c)
 t.penup()
 t.goto(d)
 t.pendown()
 t.begin_fill()
 t.goto(e)
 t.goto(f)
 t.goto(d)
 t.end_fill()
 sierpinski_triangle(a, d, f, n)
 sierpinski_triangle(b, d, e, n)
 sierpinski_triangle(c, f, e, n)

t = turtle.Turtle()
t.speed("fast")
window = turtle.Screen()
side = 240
todo = deque([])
t.color("green")
#main_triangle()
#while todo:
#inner_coords = list(itertools.combinations(todo,2))
#t.penup()
#t.goto(0.5*(inner_coords[2][0]+inner_coords[2][1]))
#t.color("white")
#t.pendown()
#t.begin_fill()
#for pair in inner_coords:
#  print pair
#  t.goto(0.5*(pair[0]+pair[1]))
  #print (0.5*(todo[0]+todo[1]))
#  todo.popleft()
#t.end_fill()

t.begin_fill()
a = t.position()
t.left(60)
t.forward(side)
b = t.position()
t.right(120)
t.forward(side)
c = t.position()
t.right(120)
t.forward(side)
t.end_fill()
t.color("white")
sierpinski_triangle(a, b, c, side)

window.exitonclick()
