import  sendSteps as ss
import msvcrt



mode=0
increment=1024;
while True:

    c=msvcrt.getch()
    if c==b'\xe0':
        c=msvcrt.getch()
        if mode==0:
            if(c==b"M"):
                print("left")
                ss.do_cardinal(1, -1, increment)
            if(c==b"K"):
                print("right")
                ss.do_cardinal(-1, 1, increment)
            if(c==b"H"):
                print("up")
                ss.do_cardinal(-1,-1,increment)
            if(c==b"P"):
                print("down")
                ss.do_cardinal(1,1,increment)

        if mode==1:
            if (c == b"M"):
                print("left")
                ss.do_cardinal(0, -1, increment)
            if (c == b"K"):
                print("right")
                ss.do_cardinal(0, 1, increment)
            if (c == b"H"):
                print("up")
                ss.do_cardinal(-1, 0, increment)
            if (c == b"P"):
                print("down")
                ss.do_cardinal(1, 0, increment)
    if c==b'+':
        increment*=2;
        print(increment)
    if c==b'-':
        increment=int(increment/2);
        increment=max(1,increment)
        print(increment)
    if c==b'\x1b':
        break
