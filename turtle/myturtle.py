#!/usr/bin/python

import turtle

def draw_square():
  t.color("red")
  deg = 360
  inc = 10
  while deg >= 0:
    i=3
    while i>=0:
      t.right(90)
      t.forward(100)
      i = i - 1
    t.right(inc)
    deg = deg - inc


def draw_circle():
  t.color("green")
  deg = 360
  inc = 10
  while deg >= 0:
    t.circle(100)
    t.right(inc)
    deg = deg - inc

def draw_triangle():
  t.color("blue")
  deg = 360
  inc = 10
  while deg >= 0:
    i=2
    while i>= 0 :
      t.right(120)
      t.forward(100)
      i = i - 1
    t.right(inc)
    deg = deg -inc

window = turtle.Screen()
t = turtle.Turtle()
t.speed("fastest")
draw_square()
draw_circle()
draw_triangle()
window.exitonclick()
