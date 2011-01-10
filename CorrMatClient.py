from CorrMatSettings import *
import socket
import sys

data_req = "gF"; # Give the Frs and some cells to work with to me!
data_back = "rF"; # get The updates Frs back
noDeathSignal = True;


def CorranDiff(Frs):
    Nn = Frs.shape[1];
    D = 0;
    c = zeros((Nn, Nn));
    d = zeros((Nn, Nn));
    #print Frs.shape
    for ic in range(0,Nn):
        for jc in range(ic, Nn):
            if ic == jc :
                c[ic, jc] = 1;
                d[ic, jc] = 0;
            else:
                #print ic, jc
                c[ic, jc] = pearsonr(Frs[:,ic], Frs[:,jc])[0];
                c[jc, ic] = c[ic, jc];
                d[ic, jc] = abs(c[ic, jc] - CorrMat[ic, jc]);
                d[jc, ic] = d[ic, jc];
            D = D + d[ic, jc]; 
    D = D / (Nn * Nn);
    return D;

def CorranDiffMinimal(Frs, theN, doItAnyWay):# pass the Neuron number that you are working on and avoid doing unnecessary correlatoin calculations 
    global currCorrMat;
    Nn = Frs.shape[1];
    D = 0;
    d = zeros((Nn, Nn));
    for ic in range(0,Nn):
        for jc in range(ic, Nn):
            if ((ic == theN) | (jc == theN) | doItAnyWay):
                if ic == jc :
                    currCorrMat[ic, jc] = 1;
                else:
                    currCorrMat[ic, jc] = pearsonr(Frs[:,ic], Frs[:,jc])[0];
                    currCorrMat[jc, ic] = currCorrMat[ic, jc];
                
            d[ic, jc] = abs(currCorrMat[ic, jc] - CorrMat[ic, jc]);
            d[jc, ic] = d[ic, jc];
            D = D + d[ic, jc]; 
    D = D / (Nn * Nn);
    return D;


if __name__ == "__main__":
    f = open('ServerHostName.ali');
    HOST = f.readline();
    f.close();
    print "FYI I know that Server Host Name is %s " % HOST

    while noDeathSignal:
        sleep(randint(5,65));
        # GET THE DATA
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        sock.connect((HOST, PORT));
        sock.send(data_req);
        received = '';
        data = 'dummy';
        while data:
            data = sock.recv(BUFF_SIZE);
            received += data;

        sock.close();

        print "received : %s" % received.__len__()
        Frs   = numpyLoads(received.partition("CELLSFROMHERE")[0]);
        #[1] is the separator itself (partiion doc for more info
        Cells = numpyLoads(received.partition("CELLSFROMHERE")[2]);

        print "received data shape: %s" % Frs.shape.__str__()
        print "Cells: %s" % Cells.__str__()

        # Do the job!
        FrsDiff = zeros((Cells.size));
        global currCorrMat;
        currCorrMat = zeros((Nn, Nn));
        D = CorranDiffMinimal(Frs, -1, False);# -1 could be anything as the DoItAnyWay is True     
        Nn = Frs.shape[1];
        for bb in range(0, Cells.size):
            bx = Cells[bb] / Nn; by = Cells[bb] % Nn;  
            #Tn = Frs.shape[0];
            #bx = Cells[bb] % Tn; by = Cells[bb] / Tn;  
            print bx, by 
            #D = CorranDiffMinimal(Frs, -1, False);# -1 could be anything as the DoItAnyWay is True     
            e = Frs[bx, by] / 10;
            Frs[bx, by] += e;
            it = 0;
            D2 = CorranDiffMinimal(Frs, by, False);
            while (D > D2) & (it < AllowedIt):
                it +=1;
                Frs[bx, by] += e;
                D = D2;
                D2 = CorranDiffMinimal(Frs, by, False);
        
            Frs[bx, by] -= 2 * e;
            it = 0;
            D2 = CorranDiffMinimal(Frs, by, False);
            while (D > CorranDiffMinimal(Frs, by, False)) & (it < AllowedIt):
                it +=1;
                Frs[bx, by] -= e;
                D = D2;
                D2 = CorranDiffMinimal(Frs, by, False);

            FrsDiff[bb] = Frs[bx, by];


        savemat('FrsDiff' + int(time()).__str__() +'.mat', {'FrsDiff':FrsDiff, 'Cells': Cells});    
        try:
            f = open('DeathSignal.ali');
            L = f.read().strip('\n').strip();
            f.close();
            print  "Still Alive, are we : %s" % L + aReset
            if L == 'live':
                noDeathSignal = True;
            else:
                noDeathSignal = False;
        except:
            noDeathSignal = False;
