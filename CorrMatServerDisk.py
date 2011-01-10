from CorrMatSettings import *
import SocketServer
import socket
from random import gauss, shuffle
from os import listdir, remove

# Global Lock file name
LockFileName = 'CorrMatGlobalLock.ali';

def ReadLock():
    f = open(LockFileName);
    L = f.read().strip('\n').strip();
    f.close();
    print aMagenta + "Lock is : %s" % L + aReset
    if L <> 'open':
        return 'close'
    else:
        return('open');

def SetLock(state):
    f = open(LockFileName, 'w');
    f.write(state);
    f.close();

Sarkhat = 0;
def getSomeRandomCells(nc):
    global Sarkhat;
    pp = range(0, Frs.size);
    shuffle(pp);
    Sarkhat = Sarkhat + nc;
    print "Sar e khat :" + aStrikeT + " %s" % Sarkhat + aStrOff + aReset
    return pp[0:nc];

def initFrs(fileName):
    if (fileName==""):
        Frs = zeros((Tn, Nn)); 
        for i in range(0, Nn):
            for j in range(0, Tn):
                Frs[j, i] = gauss(PopmFr, PopmFr);
    else :
        a = loadmat(fileName);
        Frs = a['Frs'];
    return Frs;


def mergeFrs(f, fdiff, cells):
    d = 0;
    Nn = f.shape[1]
    for i in range(0, cells.size):
        d += abs(f[cells[i]/Nn, cells[i]%Nn] - fdiff[i]);
        f[cells[i]/Nn, cells[i]%Nn] = fdiff[i];
        #d += abs(f[cells[i]%Tn, cells[i]/Tn] - fdiff[i]);
        #f[cells[i]%Tn, cells[i]/Tn] = fdiff[i];
    print aCyan + "This time diff is % s" % d.__str__() + aReset
    return f;

LatestFrsUpdate = 0;
LatestFrsSave = 0;

def saveFrs(filename):
    global LatestFrsSave;
    if ((time() - LatestFrsSave)> 1500):
        LatestFrsSave = time();
        savemat(filename + int(time()).__str__() +'.mat', {'Frs':Frs});    
        print aBGBlue + aRed + 'Matrix Saved to disk' + aReset

def writeHostName():
    global HOST
    HOST = socket.gethostname();
    f = open('ServerHostName.ali', 'w');
    f.write(HOST);
    f.close();
    print "Server Host Name is : %s for your information!" %HOST

def updateFrs():
    global LatestFrsUpdate;
    if ((time() - LatestFrsUpdate) > 0.01) : 
        global Frs;
        ls = listdir('./');
        for f in ls:
            if f.find('FrsDiff')==0:
                try:
                    a = loadmat(f);
                    Frs = mergeFrs(Frs, a['FrsDiff'], a['Cells']);
                    remove(f);
                    LatestFrsUpdate = time();
                except Exception as e:
                    print aRed + 'Maybe later : ' + f + aReset
                    print type(e)
        saveFrs('Frs');
        print aGreen + 'Matrix reloaded!' + aReset

class CorrMatTCPHandler(SocketServer.BaseRequestHandler):#StreamRequestHandler):
    def handle(self):
        global Frs;
        self.received = self.request.recv(BUFF_SIZE);
        #print 'received : %s' % self.received.__len__()
        if self.received[0:2] == "gF": # give them the current Frs
            src = getSomeRandomCells(30);
            updateFrs();
            self.request.send(Frs.dumps() + "CELLSFROMHERE" + array(src).dumps()); 
            print aBlue + "%s Do it!" % self.client_address[0] + aReset

        else: 
            print aRed + "What do you want No one is here !" + aReset

    def finish(self):
        try:
            f = open('DeathSignal.ali');
            L = f.read().strip('\n').strip();
            f.close();
            if L == 'die':
                print aRed + "Going Down in 10 seconds" + aReset;
                sleep(10);
                saveFrs('FrsFinal.mat');
                print "Going Down, Down, Down ...  if not kill me!";
                self.shutdown();
                print "I am dead! right?"
        except:
            pass;



if __name__ == "__main__":
    # save the "server" hostname to disk for clients to find it
    writeHostName();
    # Initial values of trial by trial firing rates
    global Frs;
    Frs = initFrs("Frs1286663509.mat"); #"Frs1285614290.mat");
    saveFrs('FrsInit');
    server = SocketServer.TCPServer((HOST, PORT), CorrMatTCPHandler)
    SetLock('open');
    print aYellow + aBGMagen + "Bring it on! I am doing it on the DISK !!" + aReset
    server.serve_forever()
    print aBGGreen + aYellow + "Are we there yet!?"  + aReset;
