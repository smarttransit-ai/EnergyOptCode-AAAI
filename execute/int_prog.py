import os
import sys

sys.path.append(os.getcwd())

from algo.int_prog.IPAssist import generic_program, create_ip_assist

ip_assist = create_ip_assist()
generic_program(func=ip_assist.run, args=("ip",))
