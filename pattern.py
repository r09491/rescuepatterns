#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.0.0'
__author__ = 'r09491@t-online.de'
__doc__ = ''' Calculates the Ladder, Square, and Sector rescue patterns '''

import sys,getopt

from math import sqrt,sin,cos,atan2,asin,radians,degrees,pi,log

#NM to minutes
NM2MIN=1.0/60.0


def calcBrg(latFrom,lonFrom,latTo,lonTo):
    """
    Calculates the great circle bearing in degrees
    """
    coslatFrom = cos(radians(latFrom))
    coslatTo = cos(radians(latTo))
    sinlatFrom = sin(radians(latFrom))
    sinlatTo = sin(radians(latTo))
    sindlon = sin(radians(lonTo-lonFrom))
    cosdlon = cos(radians(lonTo-lonFrom))
    
    tc = atan2(sindlon*coslatTo, 
               coslatFrom*sinlatTo-sinlatFrom*coslatTo*cosdlon)
    if tc <= 0.0:
        tc = tc + 2*pi
    return degrees(tc)


def calcRng(latFrom,lonFrom,latTo,lonTo):
    """
    Calculate the great circle distance in Nm 
    """
    sindlon = sin(radians(lonTo - lonFrom)/2)
    sindlat = sin(radians(latTo - latFrom)/2)

    coslatFrom = cos(radians(latFrom))
    coslatTo = cos(radians(latTo))

    a = sindlat*sindlat + coslatFrom*coslatTo * sindlon*sindlon
    c = 2 * asin(min(1,sqrt(a)))

    # Radius dependent on latitude only
    R = (6378000.0 - 21000.0 * sin(radians(latFrom +latTo)/2))/1852.0 
    return R * c


def calcBrgRng(latFrom,lonFrom,latTo,lonTo):
    return calcBrg(latFrom,lonFrom,latTo,lonTo),calcRng(latFrom,lonFrom,latTo,lonTo)


def newPoint(hdg,dst,n,e,mid,lat,lon):
    coshdg,sinhdg=cos(radians(hdg)),sin(radians(hdg))
    #Calc cartesian delta vector
    nn,ee=dst*coshdg,dst*sinhdg
    #Calc associated degree (Using always lat=48 would output TA values)
    latnmin,lonemin=nn*NM2MIN,ee*NM2MIN/cos(radians(mid))
    newlat,newlon=lat+latnmin,lon+lonemin
    newbrg,newrng=calcBrgRng(lat,lon,newlat,newlon)
    #TA requires below truncation. This does not make sense here
    #if newlat>84.0:newlat=84.0
    #if newlat<-80.0:newlat=-80;
    #if newlon>180.0:newlon-=360.0
    #if newlon<-180.0:newlon+=360.0
    return {"hdg":hdg,"dst":dst,"n":n+nn,"e":e+ee,"lat":newlat,"lon":newlon,"brg":newbrg,"rng":newrng}


def addOrigin(pts,lat,lon):
    #Set the origin of the list
    pts.append(newPoint(360.0,0.0,0.0,0.0,lat,lat,lon))

    
def addPoint(pts,hdg,dst):
    #Add a new point at the end of the list
    pts.append(newPoint(hdg,dst,pts[-1]["n"],pts[-1]["e"],pts[0]["lat"],pts[-1]["lat"],pts[-1]["lon"]))

    
def turnByAngle(fromDegree,byAngle):
    toDegree=fromDegree+byAngle
    while toDegree>360.0:toDegree-=360.0
    while toDegree<1.0:toDegree+=360.0
    return toDegree


def calcLadder(orient,length,width,spacing,firstToRight,lat,lon):
    """
    Calculates the Ladder pattern! Produces the same results than the operational
    software. The calculation of 'n' might not be correct!
    """
    n,l,pts=0,0.0,[]
    
    if (spacing>0.0) and (length>spacing) and (width>spacing):
        # Calc number of areas (at least two areas required)
        n=int(length/spacing + 0.5) # As per GS! Spacing to boundary nok! ADA integer conversion!
        # n=int(length/spacing) + 1 # As per TN! Spacing to boundary nok!
        # n=int(length/spacing)     # As per ME! Spacing to boundary ok!
        # Calc single leg length in orientation & perpendicular direction
        dl,dw,dw0=spacing,width-spacing,(width-spacing)/2.0
        # Calc sum of leg lengths in orientation & perpendicular direction
        ll,lw=(n-1)*dl,(n-1)*dw+dw0
        # Calc total travel length
        l=ll+lw

        # In the operational code: if n>=2 and n<=25:
        if n>=2:
            if firstToRight:
                # Adapt in order to turn right at first point
                course=turnByAngle(orient,-90.0)
            else:
                # Adapt in order to turn left at first point
                course=turnByAngle(orient,+90.0)

            # Set the origin of the list
            addOrigin(pts,lat,lon)
            # Approach leg to the first point
            addPoint(pts,course,dw0)
            # Approach the next points
            for i in range(1,n):
                addPoint(pts,orient,dl)
                course=turnByAngle(course,+180.0)
                addPoint(pts,course,dw)
        
    return n,l,pts


def showLadderInput(orient,length,width,spacing,isRight,lat,lon):
    print("#LADDER has start lat:%.4f lon:%.4f orientation:%03.0f length:%.1f width:%.1f spacing:%.2f right:%d" % \
          (lat,lon,orient,length,width,spacing,isRight))

    
def showLadderResult(n,l,pts):
    if n<2:
        print("#LADDER is not implementable (n=%d)" % (n))
        return

    # print(the legs.)
    minLat,maxLat,minLon,maxLon=+90.0,-90.0,180.0,-180.0
    minN,maxN,minE,maxE=+999.0,-999.0,+999.0,-999.0
    for i,p in enumerate(pts):
        if p["n"]<minN:minN=p["n"]
        if p["n"]>maxN:maxN=p["n"]
        if p["e"]<minE:minE=p["e"]
        if p["e"]>maxE:maxE=p["e"]

        if p["lat"]<minLat:minLat=p["lat"]
        if p["lat"]>maxLat:maxLat=p["lat"]
        if p["lon"]<minLon:minLon=p["lon"]
        if p["lon"]>maxLon:maxLon=p["lon"]
        
        print("@%03d %03.0f/%05.1f %7.2f %7.2f %8.4f %9.4f %03.0f/%05.1f" % \
              (i, p["hdg"],p["dst"],p["n"],p["e"],p["lat"],p["lon"],p["brg"],p["rng"]))

    print()
    print()
    print(minN,0.0)
    print(maxN,0.0)
    print()
    print(0.0,minE)
    print(0.0,maxE)
    print()
    print()

    if int(60*(maxLon-minLon)/4):
        for h in range(int(60*(minLon-pts[0]["lon"])),int(60*(maxLon-pts[0]["lon"])),int(60*(maxLon-minLon)/4)):
            print(minN,h*cos(radians(pts[0]["lat"]+minN/60.0)))
            print(maxN,h*cos(radians(pts[0]["lat"]+maxN/60.0)))
            print()
    else:
        print(minN,0.0)
        print(maxN,0.0)
        print()

    if int(60*(maxLat-minLat)/4)>0:
        for v in range(int(60*(minLat-pts[0]["lat"])),int(60*(maxLat-pts[0]["lat"])),int(60*(maxLat-minLat)/4)):
            print(v,minE)
            print(v,maxE)
            print()
        else:
            print(0.0,minE)
            print(0.0,maxE)
            print()
    

    # Epilogue
    print("#LADDER has %d areas with %d legs and a planned travel distance of %.1f." % (n,2*n-1,l))

    if n>25:
        print("#LADDER is restricted in the operational code (areas=%d,legs=%d,coverage=%.1f%%)." % (25,2*25-1,2500.0/n))


def calcSquare(orient,length,width,spacing,firstToRight,lat,lon):
    """
    Calculates the Square pattern! Produces the same results than the operational
    software. The calculation of 'n' might not be correct!
    """
    n,l,pts=0,0.0,[]
    
    if (spacing>0.0) and (length>spacing) and (width>spacing):
        # Calc number of areas (at least two areas required)
        n=int(length/spacing + 0.5) + 1 # As implemented in ADA! Not as per TN !!!
        # Calc single leg increments in orientation & width direction
        dl,dw=spacing,width/length*spacing
        # Calc sum of leg lengths in orientation & perpendicular direction
        ll,lw=n*(n+1)/2*dl-dl,(n-1)*n/2*dw
        # Calc total travel length
        l=ll+lw

        # In the operational code: if n>=2 and n<=24:
        if n>=2:
            if firstToRight:
                # Adapt in order to turn right at first point
                offset=90.0
            else:
                # Adapt in order to turn left at first point
                offset=-90.0

            course=orient

            # Set the origin of the list
            addOrigin(pts,lat,lon) 
            # Approach leg to the first point
            addPoint(pts,course,dl)
            # Approach the next points
            for i in range(1,n):
                course=turnByAngle(course,offset)
                addPoint(pts,course,i*dw)
                course=turnByAngle(course,offset)
                if i<n-1:
                    addPoint(pts,course,(i+1)*dl)
                else:
                    addPoint(pts,course,i*dl)

    return n,l,pts


def showSquareInput(orient,length,width,spacing,isRight,lat,lon):
    print("#SQUARE has start lat:%.4f lon:%.4f orientation:%03.0f length:%.1f width:%.1f spacing:%.2f right:%d" % \
          (lat,lon,orient,length,width,spacing,isRight))

    
def showSquareResult(n,l,pts):
    minLat,maxLat,minLon,maxLon=+90.0,-90.0,180.0,-180.0
    minN,maxN,minE,maxE=+999.0,-999.0,+999.0,-999.0
    for i,p in enumerate(pts):
        if p["n"]<minN:minN=p["n"]
        if p["n"]>maxN:maxN=p["n"]
        if p["e"]<minE:minE=p["e"]
        if p["e"]>maxE:maxE=p["e"]

        if p["lat"]<minLat:minLat=p["lat"]
        if p["lat"]>maxLat:maxLat=p["lat"]
        if p["lon"]<minLon:minLon=p["lon"]
        if p["lon"]>maxLon:maxLon=p["lon"]
        
        print("@%03d %03.0f/%05.1f %7.2f %7.2f %8.4f %9.4f %03.0f/%05.1f" % \
              (i, p["hdg"],p["dst"],p["n"],p["e"],p["lat"],p["lon"],p["brg"],p["rng"]))

    print()
    print()
    print(minN,0.0)
    print(maxN,0.0)
    print()
    print(0.0,minE)
    print(0.0,maxE)
    print()
    print()
    for h in range(int(60*(minLon-pts[0]["lon"])),int(60*(maxLon-pts[0]["lon"])),int(60*(maxLon-minLon)/4)):
        print(minN,h*cos(radians(pts[0]["lat"]+minN/60.0)))
        print(maxN,h*cos(radians(pts[0]["lat"]+maxN/60.0)))
        print()
    for v in range(int(60*(minLat-pts[0]["lat"])),int(60*(maxLat-pts[0]["lat"])),int(60*(maxLat-minLat)/4)):
        print(v,minE)
        print(v,maxE)
        print()

    # Epilogue
    if n<2:
        print("#SQUARE is not implementable (n=%d)" % (n))
    else:
        print("#SQUARE has %d areas with %d legs and a planned travel distance of %.1f." % (n,2*n-1,l))
    if n>24:
        print("#SQUARE is restricted in the operational code (areas=%d,legs=%d,coverage=%.1f%%)." % (24,2*24-1,2400.0/n))


def calcSector(orient,angle,radius,firstToRight,lat,lon):
    np,l,pts=0,0.0,[]

    if (angle > 0.0) and (radius > 0.0):
        # No division by zero

        betaDeg = angle
        betaDeg2 = angle / 2.0
        betaRad2 = radians(betaDeg2)
        betaSin2 = sin (betaRad2)
        
        r = radius;
        s = 2.0*r*betaSin2;

        np=int(360.0/betaDeg)+1

    #In the operation code: if np >= 2 and np <= 49:
    if np >= 2: 
        course=orient

        offset=turnByAngle(90.0,betaDeg2)
        if not firstToRight: offset=-offset;

        # Set the origin of the list
        addOrigin(pts,lat,lon)
        # Approach to first corner point
        addPoint(pts,course,r)
        for i in range(np/2):
            course=turnByAngle(course,offset)
            addPoint(pts,course,s)
            course=turnByAngle(course,offset)
            addPoint(pts,course,2.0*r)
        l=(np/2)*s+np*r 

    return np,l,pts


def showSectorInput(orient,angle,radius,isRight,lat,lon):
    print("SECTOR has start lat:%.4f lon:%.4f orientation:%03.0f radius:%.1f angle:%.1f right:%d " % \
          (lat,lon,orient,radius,angle,isRight))

    
def showSectorResult(n,l,pts):
    # Print the legs.
    minLat,maxLat,minLon,maxLon=+90.0,-90.0,180.0,-180.0
    minN,maxN,minE,maxE=+999.0,-999.0,+999.0,-999.0
    for i,p in enumerate(pts):
        if p["n"]<minN:minN=p["n"]
        if p["n"]>maxN:maxN=p["n"]
        if p["e"]<minE:minE=p["e"]
        if p["e"]>maxE:maxE=p["e"]

        if p["lat"]<minLat:minLat=p["lat"]
        if p["lat"]>maxLat:maxLat=p["lat"]
        if p["lon"]<minLon:minLon=p["lon"]
        if p["lon"]>maxLon:maxLon=p["lon"]

        print("@%03d %03.0f/%05.1f %7.2f %7.2f %8.4f %9.4f %03.0f/%05.1f" % \
              (i, p["hdg"],p["dst"],p["n"],p["e"],p["lat"],p["lon"],p["brg"],p["rng"]))

    print()
    print()
    print(minN,0.0)
    print(maxN,0.0)
    print()
    print(0.0,minE)
    print(0.0,maxE)
    print()
    print()
    for h in range(int(60*(minLon-pts[0]["lon"])),int(60*(maxLon-pts[0]["lon"])),int(60*(maxLon-minLon)/4)):
        print(minN,h*cos(radians(pts[0]["lat"]+minN/60.0)))
        print(maxN,h*cos(radians(pts[0]["lat"]+maxN/60.0)))
        print()
    for v in range(int(60*(minLat-pts[0]["lat"])),int(60*(maxLat-pts[0]["lat"])),int(60*(maxLat-minLat)/4)):
        print(v,minE)
        print(v,maxE)
        print()

    # Epilogue
    if n<2:
        print("#SECTOR is not implementable (n=%d)" % (n))
    else:
        print("#SECTOR has %d areas with %d legs and a planned travel distance of %.1f." % (n,2*n-1,l))
    if n>24:
        print("#SECTOR is restricted in the operational code (areas=%d,legs=%d,coverage=%.1f%%)." % (24,2*24-1,2400.0/n))

    
def usage():
    print('pattern.py [-p <ladder|square|sector>] [-o <orient>] [-l <length>] [-w <width>] [-s <spacing>] [-a <angle] [-n lat] [-e lon]')
    sys.exit()


def main(argv):

    pattern,orient,length,width,spacing,angle,isRight,lat,lon = \
        "ladder",360.0,10.0,10.0,1.0,60.0,True,48.0,11.0

    try:
        opts, args = getopt.getopt(argv,"p:o:l:w:h:s:r:a:n:e:")
    except getopt.GetoptError:
        usage()

    if len(argv) > 1:
        for opt, arg in opts:
            if opt in ("-p"):
                pattern = arg.lower()
            elif opt in ("-o"):
                try:
                    f = float(arg)
                    if (f>=1.0) and (f<=360.0):
                        orient=f;
                    else:
                        usage()
                except:
                    usage()
            elif opt in ("-l"):
                try:
                    f = float(arg)
                    if (f>0.0) and (f<=999.0):
                        length=f;
                    else:
                        usage()
                except:
                    usage()
            elif opt in ("-w"):
                try:
                    f = float(arg)
                    if (f>0.0) and (f<=999.0):
                        width=f;
                    else:
                        usage()
                except:
                    usage()
            elif opt in ("-s"):
                try:
                    f = float(arg)
                    if (f>0.0):
                        spacing=f;
                    else:
                        usage()
                except:
                    usage()
            elif opt in ("-a"):
                try:
                    f = float(arg)
                    if (f>=1.0) and (f<=180.0):
                        angle=f;
                    else:
                        usage()
                except:
                    usage()
            elif opt in ("-n"):
                try:
                    f = float(arg)
                    #TA requires
                    if (f<=84.0) and (f>=-80.0):
                        lat=f;
                    else:
                        usage()
                except:
                    usage()
            elif opt in ("-e"):
                try:
                    f = float(arg)
                    if (f>=-180.0) and (f<=180.0):
                        lon=f;
                    else:
                        usage()
                except:
                    usage()
            elif opt in ("-r"):
                b = arg.lower()
                if b == "false":
                    isRight = False
                elif b == "true":
                    isRight = True
                else:
                    usage()
    else:
        usage()

    if pattern == "ladder":
        n,l,pts=calcLadder(orient,length,width,spacing,isRight,lat,lon)
        showLadderResult(n,l,pts)
        showLadderInput(orient,length,width,spacing,isRight,lat,lon)
    elif pattern == "square":
        n,l,pts=calcSquare(orient,length,width,spacing,isRight,lat,lon)
        showSquareResult(n,l,pts)
        showSquareInput(orient,length,width,spacing,isRight,lat,lon)
    elif pattern == "sector":
        n,l,pts=calcSector(orient,angle,length,isRight,lat,lon)
        showSectorResult(n,l,pts)
        showSectorInput(orient,angle,length,isRight,lat,lon)
    else:
        usage()

        
if __name__ == "__main__":
    main(sys.argv[1:])
