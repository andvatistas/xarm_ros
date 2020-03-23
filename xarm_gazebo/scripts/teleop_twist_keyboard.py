#!/usr/bin/env python

from __future__ import print_function

import rospy

from geometry_msgs.msg import Twist

import sys, select, termios, tty

msg = """

----------------------------------
Keyboard Commands
-----------------------------------

j:left l:right

anything else : stop

q/z : increase/decrease only linear speed by 10%

CTRL-C to quit
"""

moveBindings = {
        'l':-1,
        'j':1,
    }

speedBindings={
        'q':1.1,
        'z':.9,
    }

def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def vels(speed):
    return "currently:\tspeed %s" % (speed)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
    rospy.init_node('teleop_twist_keyboard')

    speed = rospy.get_param("~speed", 0.05)
    y = 0
    status = 0

    try:
        print(msg)
        print(vels(speed))
        while(1):
            key = getKey()
            if key in moveBindings.keys():
                y = moveBindings[key]
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key]

                print(vels(speed))
                if (status == 14):
                    print(msg)
                status = (status + 1) % 15
            else:
                y = 0
                if (key == '\x03'):
                    break

            twist = Twist()
            twist.linear.y = y*speed
            pub.publish(twist)

    except Exception as e:
        print(e)

    finally:
        twist = Twist()
        twist.linear.y = 0
        pub.publish(twist)

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
